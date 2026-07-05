"""
notebook_src/extraction.py
Knowledge graph triple extraction strategies (both use OpenAI structured output).
  - extract_obie  : ontology-constrained — subject/object mapped to MeSH concepts
  - extract_openie: schema-free — every (subject, predicate, object) the LLM sees
"""
from __future__ import annotations
import textwrap
from typing import List

from pydantic import BaseModel, Field, field_validator


# ── shared helpers ────────────────────────────────────────────────── #

def _get_nlp():
    import spacy
    return spacy.load("en_core_web_sm")


class _TripleBase(BaseModel):
    """Shared coercion so a stray null / number from the LLM never crashes parsing."""

    @field_validator("*", mode="before")
    @classmethod
    def _coerce(cls, v, info):
        if info.field_name == "confidence":
            try:
                return float(v)
            except (TypeError, ValueError):
                return 0.8
        return "" if v is None else str(v)


# ── OBIE ──────────────────────────────────────────────────────────── #

class _Triple(_TripleBase):
    subject:      str   = Field("",  description="Subject entity")
    subject_mesh: str   = Field("",  description="MeSH concept the subject maps to ('' if none)")
    predicate:    str   = Field("",  description="Normalised relation verb")
    object:       str   = Field("",  description="Object entity")
    object_mesh:  str   = Field("",  description="MeSH concept the object maps to ('' if none)")
    confidence:   float = Field(0.8, description="Extraction confidence 0-1")

class _TripleList(BaseModel):
    triples: List[_Triple] = Field(default_factory=list, description="Extracted triples")


_OBIE_SYSTEM = textwrap.dedent("""
    You are a biomedical knowledge graph builder.
    Extract triples that conform strictly to a provided MeSH ontology schema.

    Rules:
    - Subject and object MUST be present in or directly implied by the sentence.
    - Subject and object SHOULD map to one of the provided MeSH concepts when possible.
    - For every subject and object, also return which MeSH concept it maps to in the
      "subject_mesh" / "object_mesh" fields. Copy the concept EXACTLY as given in the
      provided list. If an entity maps to none of the concepts, use an empty string "".
    - Predicate MUST be a concise normalised relation verb (e.g. "plays role in",
      "is part of", "causes", "inhibits", "regulates", "is associated with").
    - Only emit triples with confidence >= 0.7.
    - Do NOT hallucinate entities or relations not supported by the sentence.

    Return a JSON object with key "triples" containing a list of triple objects.
    Each triple object must have:
      subject, subject_mesh, predicate, object, object_mesh, confidence.
""").strip()


def extract_obie(
    contexts: list[str],
    labels: list[str],
    ontology_terms: list[str],
    api_key: str,
    model: str = "gpt-4.1-nano",
) -> list[dict]:
    """
    Extract KG triples constrained by a MeSH ontology using OpenAI.

    Args:
        contexts:       Abstract sections (list of paragraph strings).
        labels:         Section label for each context (e.g. "BACKGROUND").
        ontology_terms: MeSH terms that define the allowed entity types.
        api_key:        OpenAI API key.
        model:          OpenAI model name (default gpt-4.1-nano).

    Returns:
        List of triple dicts with keys:
            subject, subject_mesh, predicate, object, object_mesh,
            confidence, sentence, section.
    """
    from openai import OpenAI

    nlp     = _get_nlp()
    client  = OpenAI(api_key=api_key)
    schema  = ", ".join(f'"{t}"' for t in ontology_terms)
    allowed = set(ontology_terms)
    triples: list[dict] = []

    for section_label, paragraph in zip(labels, contexts):
        doc = nlp(paragraph)
        for sent in doc.sents:
            response = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _OBIE_SYSTEM},
                    {
                        "role": "user",
                        "content": (
                            f"MeSH ontology concepts: [{schema}]\n\n"
                            f"Section: {section_label}\n"
                            f"Sentence: {sent.text}\n\n"
                            "Extract all triples anchored to the MeSH concepts, "
                            "tagging each entity with the concept it maps to."
                        ),
                    },
                ],
            )
            raw = response.choices[0].message.content or ""
            parsed = _TripleList.model_validate_json(raw)
            for t in parsed.triples:
                if not (t.subject.strip() and t.predicate.strip() and t.object.strip()):
                    continue
                if t.confidence >= 0.7:
                    # keep only MeSH tags that actually exist in the ontology
                    s_mesh = t.subject_mesh if t.subject_mesh in allowed else ""
                    o_mesh = t.object_mesh  if t.object_mesh  in allowed else ""
                    triples.append({
                        "subject":      t.subject,
                        "subject_mesh": s_mesh,
                        "predicate":    t.predicate,
                        "object":       t.object,
                        "object_mesh":  o_mesh,
                        "confidence":   t.confidence,
                        "sentence":     sent.text.strip(),
                        "section":      section_label,
                    })

    return triples


# ── OpenIE ────────────────────────────────────────────────────────── #

class _OpenTriple(_TripleBase):
    subject:        str   = Field("",  description="Subject noun phrase")
    subject_type:   str   = Field("",  description="Guessed ontological type of the subject")
    predicate:      str   = Field("",  description="Relation verb phrase")
    predicate_type: str   = Field("",  description="Guessed relationship type")
    object:         str   = Field("",  description="Object noun phrase")
    object_type:    str   = Field("",  description="Guessed ontological type of the object")
    confidence:     float = Field(0.8, description="Extraction confidence 0-1")

class _OpenTripleList(BaseModel):
    triples: List[_OpenTriple] = Field(default_factory=list, description="All triples found")


# __TYPE_BLOCK__ is filled in at call time from ONTOLOGY_TYPES.
_OPENIE_SYSTEM = textwrap.dedent("""
    You are an open-domain information extraction engine.
    Extract ALL (subject, predicate, object) triples from the sentence with NO
    predefined schema — capture every factual relationship the sentence expresses.

    For EVERY entity (subject and object) also GUESS its ontological type, and for
    EVERY relationship GUESS its relationship type.

    Entity ontological types — choose exactly one of:
    __TYPE_BLOCK__
      - Other (only when none of the above genuinely fits)

    Relationship types — choose the single best of:
      causal, part-whole, spatial, functional/role, temporal, attributive, definitional, other.

    Rules:
    - Be exhaustive: emit a separate triple for every distinct relationship,
      including nested or coordinated ones. Do not limit yourself to one per sentence.
    - Subject and object should be concrete noun phrases (as specific as the text allows).
    - Predicate should be a concise verb phrase (lemmatised, drop auxiliaries/tense).
    - Resolve obvious pronouns/anaphora ("it", "they", "this") to their referent
      when the referent is clear from the sentence.
    - Confidence reflects how explicitly the relationship is stated (0.0-1.0).
    - Do NOT invent facts that are not supported by the sentence.

    Return a JSON object with key "triples" containing a list of triple objects.
    Each triple object must have:
      subject, subject_type, predicate, predicate_type, object, object_type, confidence.
""").strip()


def extract_openie(
    contexts: list[str],
    labels: list[str],
    api_key: str,
    model: str = "gpt-4.1-nano",
) -> list[dict]:
    """
    Extract KG triples without a predefined schema, using OpenAI.
    The LLM returns every relationship it can find in each sentence.

    Args:
        contexts:  Abstract sections (list of paragraph strings).
        labels:    Section label for each context.
        api_key:   OpenAI API key.
        model:     OpenAI model name (default gpt-4.1-nano).

    Returns:
        List of triple dicts with keys:
            subject, subject_type, predicate, predicate_type, object, object_type,
            confidence, sentence, section.
        (subject_type / object_type / predicate_type are the LLM's inline guesses.)
    """
    from openai import OpenAI

    nlp    = _get_nlp()
    client = OpenAI(api_key=api_key)
    triples: list[dict] = []

    # inject the canonical ontological types into the system prompt
    type_block = "\n".join(
        f"      - {t['type']} (UMLS {t['umls']}): {t['reason']}" for t in ONTOLOGY_TYPES
    )
    system = _OPENIE_SYSTEM.replace("__TYPE_BLOCK__", type_block)

    for section_label, paragraph in zip(labels, contexts):
        doc = nlp(paragraph)
        for sent in doc.sents:
            response = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": (
                            f"Section: {section_label}\n"
                            f"Sentence: {sent.text}\n\n"
                            "Extract every factual triple, tagging each entity with "
                            "its ontological type and each relationship with its type."
                        ),
                    },
                ],
            )
            raw = response.choices[0].message.content or ""
            parsed = _OpenTripleList.model_validate_json(raw)
            for t in parsed.triples:
                if not (t.subject.strip() and t.predicate.strip() and t.object.strip()):
                    continue
                triples.append({
                    "subject":        t.subject,
                    "subject_type":   t.subject_type,
                    "predicate":      t.predicate,
                    "predicate_type": t.predicate_type,
                    "object":         t.object,
                    "object_type":    t.object_type,
                    "confidence":     t.confidence,
                    "sentence":       sent.text.strip(),
                    "section":        section_label,
                })

    return triples


# ── Ontological types (the schema behind OBIE) ────────────────────────── #
# For this example the five MeSH descriptors collapse into four broad
# ontological categories. We name each after its UMLS Semantic Type (the
# canonical biomedical type system) and cross-reference the MeSH descriptor(s)
# that instantiate it in this abstract.
ONTOLOGY_TYPES = [
    {
        "type": "Organism",
        "umls": "T002",
        "reason": "The taxa under study — the living things the paper is about. "
                  "In UMLS these are 'Plant'; here the lace plant / its family.",
        "mesh":  ["Alismataceae"],
    },
    {
        "type": "Anatomical Structure",
        "umls": "T017",
        "reason": "The physical body / plant parts where the biology plays out — "
                  "the spatial scaffolding of the process.",
        "mesh":  ["Plant Leaves"],
    },
    {
        "type": "Cell Component",
        "umls": "T026",
        "reason": "Sub-cellular organelles implicated mechanistically in the "
                  "process (the paper's central question is about one of these).",
        "mesh":  ["Mitochondria"],
    },
    {
        "type": "Biological Process",
        "umls": "T043",
        "reason": "The dynamic cellular functions being investigated — the verbs "
                  "of the biology, not the nouns.",
        "mesh":  ["Apoptosis", "Cell Differentiation"],
    },
]


def ontology_type_names() -> list[str]:
    """The allowed ontological type labels (excludes the catch-all 'Other')."""
    return [t["type"] for t in ONTOLOGY_TYPES]


def mesh_to_type() -> dict[str, str]:
    """Map each MeSH descriptor to the ontological type it instantiates."""
    out: dict[str, str] = {}
    for t in ONTOLOGY_TYPES:
        for m in t["mesh"]:
            out[m] = t["type"]
    return out


# ── Biomedical-embedding grounding to the MeSH ontology ──────────────── #
# BioLORD is trained specifically for biomedical ONTOLOGY concept similarity,
# so it is well suited to deciding whether a free-text entity denotes the same
# concept as a MeSH heading.
BIOMED_EMBED_MODEL = "FremyCompany/BioLORD-2023-C"
_EMBEDDERS: dict = {}


def _get_embedder(model_name: str = BIOMED_EMBED_MODEL):
    if model_name not in _EMBEDDERS:
        from sentence_transformers import SentenceTransformer
        _EMBEDDERS[model_name] = SentenceTransformer(model_name)
    return _EMBEDDERS[model_name]


def ground_to_mesh(
    triples: list[dict],
    mesh_headings: list[str],
    threshold: float = 0.8,
    model_name: str = BIOMED_EMBED_MODEL,
):
    """
    Ground every entity to the MeSH ontology with a biomedical embedding model.
    For each entity we take its most similar MeSH heading; if cosine similarity
    >= `threshold` we treat them as the same concept and adopt that heading's
    ontological type. Entities that already carry an explicit MeSH tag (OBIE) are
    matched directly (score 1.0); anything unmatched falls back to the LLM's inline
    guessed type (OpenIE) or 'Other'.

    Returns (typed_triples, grounding_rows), where each row is
        {entity, guess, mesh, score, mapped_type, via}
    describing how that entity was grounded (for display).
    """
    from sentence_transformers import util

    m2t       = mesh_to_type()
    canonical = set(ontology_type_names())
    valid     = [m for m in mesh_headings if m]

    explicit: dict[str, str] = {}   # entity -> MeSH tag it already carries
    guess:    dict[str, str] = {}   # entity -> LLM's inline type guess
    seen:     list[str] = []
    for t in triples:
        for role in ("subject", "object"):
            e = (t.get(role) or "").strip()
            if not e:
                continue
            seen.append(e)
            em = t.get(f"{role}_mesh", "")
            if em in valid and e not in explicit:
                explicit[e] = em
            g = (t.get(f"{role}_type", "") or "").strip()
            if g and e not in guess:
                guess[e] = g
    uniq = sorted(set(seen))

    # embed only entities that lack an explicit MeSH tag
    need = [e for e in uniq if e not in explicit]
    best_mesh:  dict[str, str]   = {}
    best_score: dict[str, float] = {}
    if need and valid:
        model = _get_embedder(model_name)
        ev = model.encode(need,  normalize_embeddings=True)
        mv = model.encode(valid, normalize_embeddings=True)
        sim = util.cos_sim(ev, mv)
        for i, e in enumerate(need):
            j = int(sim[i].argmax())
            best_mesh[e]  = valid[j]
            best_score[e] = float(sim[i][j])

    final_type: dict[str, str] = {}
    rows = []
    for e in uniq:
        if e in explicit:
            mesh, score = explicit[e], 1.0
            mtype, via  = m2t.get(mesh, "Other"), "exact MeSH tag"
        else:
            mesh, score = best_mesh.get(e, ""), best_score.get(e, 0.0)
            if mesh and score >= threshold:
                mtype, via = m2t.get(mesh, "Other"), f"embedding ≥ {threshold:g}"
            else:
                g = guess.get(e, "")
                mtype = g if g in canonical else "Other"
                via   = "LLM guess" if mtype != "Other" else "unmapped"
        final_type[e] = mtype
        rows.append({"entity": e, "guess": guess.get(e, ""), "mesh": mesh,
                     "score": score, "mapped_type": mtype, "via": via})

    typed = []
    for t in triples:
        d = dict(t)
        for role in ("subject", "object"):
            e = (t.get(role) or "").strip()
            if t.get(f"{role}_type"):                 # preserve LLM guess for display
                d[f"{role}_type_guess"] = t[f"{role}_type"]
            d[f"{role}_type"] = final_type.get(e, "Other")
            if e in explicit:
                d[f"{role}_mesh"], d[f"{role}_score"] = explicit[e], 1.0
            elif e in best_mesh:
                d[f"{role}_mesh"], d[f"{role}_score"] = best_mesh[e], round(best_score[e], 2)
        typed.append(d)

    rows.sort(key=lambda r: -r["score"])
    return typed, rows


def filter_by_types(triples: list[dict], allowed_types: list[str]) -> list[dict]:
    """Keep only triples where BOTH endpoints carry an allowed ontological type."""
    allowed = set(allowed_types)
    return [
        t for t in triples
        if t.get("subject_type") in allowed and t.get("object_type") in allowed
    ]


# ── Mystery / user-defined ontology extraction ───────────────────── #

def _relation_groups(relation_types: list[str], size: int = 4) -> list[list[str]]:
    """Split the relation list into small groups — extraction runs one focused
    pass per group, which is far more reliable than one exhaustive pass."""
    return [relation_types[i:i + size] for i in range(0, len(relation_types), size)]


def _ontology_names(types) -> list[str]:
    """Accept either a list of names or a {name: definition} dict."""
    return list(types)


def _ontology_defs(types) -> dict:
    return dict(types) if isinstance(types, dict) else {}


def mystery_prompt(entity_types, relation_types,
                   focus_relations: list[str] | None = None) -> str:
    """
    Build the IE system prompt for a user-designed ontology.

    This is exactly what gets sent to the LLM — display it to attendees so
    they can see how their entity/relation lists shape the extraction.
    Both arguments accept a plain list of names or a {name: definition} dict;
    definitions are injected into the prompt and dramatically improve
    extraction quality — the model learns what each relation MEANS, not just
    what it is called. When `focus_relations` is given, the prompt tells the
    model to concentrate on that subset (the full relation list stays allowed).
    """
    e_defs = _ontology_defs(entity_types)
    r_defs = _ontology_defs(relation_types)

    if e_defs:
        entity_str = "\n" + "\n".join(f'  - "{n}": {d}' for n, d in e_defs.items())
    else:
        entity_str = ", ".join(_ontology_names(entity_types))

    relation_list = "\n".join(
        f'  - "{n}" — {r_defs[n]}' if n in r_defs else f'  - "{n}"'
        for n in _ontology_names(relation_types)
    )
    focus = ""
    if focus_relations:
        focus = (
            "\n=== FOCUS FOR THIS PASS ===\n"
            "Concentrate on finding EVERY fact expressible with these relations:\n"
            "  " + ", ".join(focus_relations) + "\n"
        )
    return (
        "You are an expert information extraction system. Read the case report "
        "and extract factual relationships using ONLY the ontology below.\n"
        "\n"
        "=== ENTITY TYPES ===\n"
        f"subject_type and object_type must be exactly one of: {entity_str}\n"
        "\n"
        "=== RELATION TYPES ===\n"
        "predicate must be copied EXACTLY (character-for-character) from:\n"
        f"{relation_list}\n"
        f"{focus}"
        "\n"
        "=== RULES ===\n"
        "1. subject / object: short entity names (max 5 words) — never full "
        "sentences, never pronouns.\n"
        "2. predicate: exact string from the list — never invent or paraphrase.\n"
        "3. Be exhaustive: every motive, alibi, sighting, ownership and "
        "relationship the text supports.\n"
        "4. sentence: copy the source sentence verbatim.\n"
        "5. If no allowed predicate fits a fact, skip that fact.\n"
        "6. The murder victim is not a suspect — never assign the deceased a motive."
    )


def extract_mystery_triples(
    narrative: str,
    entity_types,
    relation_types,
    api_key: str,
    model: str = "gpt-4.1-nano",
) -> list[dict]:
    """
    Extract typed triples from a free-text narrative using a caller-supplied
    ontology.

    entity_types / relation_types: a list of names, or better, a
    {name: definition} dict — definitions are injected into the LLM prompt
    (see `mystery_prompt`) so attendees can design their own schema and
    immediately see the effect on the extracted graph. Extraction runs one
    focused pass per group of ~4 relations, then validates: predicates outside
    the ontology are dropped, entity types normalised, sentence-length
    entities discarded, duplicates merged.
    """
    from openai import OpenAI
    from pydantic import BaseModel as _BM

    class _MT(_BM):
        subject:       str
        subject_type:  str
        predicate:     str
        object:        str
        object_type:   str
        confidence:    float = 0.8
        sentence:      str = ""

    class _MTList(_BM):
        triples: list[_MT] = []

    client = OpenAI(api_key=api_key)
    entity_names   = _ontology_names(entity_types)
    relation_names = _ontology_names(relation_types)

    all_raw = []
    for group in _relation_groups(relation_names):
        r = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system",
                 "content": mystery_prompt(entity_types, relation_types, group)},
                {"role": "user", "content": narrative},
            ],
            response_format=_MTList,
        )
        parsed = r.choices[0].message.parsed
        if parsed:
            all_raw += parsed.triples

    valid_predicates = {p.lower(): p for p in relation_names}
    seen: set[tuple] = set()
    result = []
    for t in all_raw:
        d = t.model_dump()

        # keep only valid predicates — drop rather than guess (keeps graph clean)
        pred_norm = d["predicate"].lower().strip()
        if pred_norm not in valid_predicates:
            continue
        d["predicate"] = valid_predicates[pred_norm]

        # normalise entity types
        if d["subject_type"] not in entity_names:
            d["subject_type"] = entity_names[0]
        if d["object_type"] not in entity_names:
            d["object_type"] = entity_names[0]

        # drop sentence-length entities (extraction noise)
        if len(d["subject"].split()) > 7 or len(d["object"].split()) > 7:
            continue

        # deduplicate on (subject, predicate, object) regardless of case
        key = (d["subject"].lower(), d["predicate"], d["object"].lower())
        if key in seen:
            continue
        seen.add(key)

        d.setdefault("section", "CASE")
        result.append(d)
    return result
