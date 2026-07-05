"""
notebook_src/mystery.py
A self-contained murder-mystery knowledge graph for the Hands-on B KG-RAG demo.

Everything is fictional and hand-authored so the case is fully solvable from the
graph alone. The same facts drive three things:
  - a knowledge graph (build via notebook_src.graph.build_graph)
  - semantic retrieval (embed the clues, search them for a question)
  - LLM reasoning (ground a chain-of-thought over the retrieved facts)
"""
from __future__ import annotations

CASE = {
    "title":  "The Ashworth Manor Murder",
    "victim": "Lord Edmund Ashworth",
    "scene":  "the Study",
    "time":   "9:00 PM",
    "weapon": "the letter opener",
    "solution": {
        "culprit": "Ms. Vivian Scarlett",
        "weapon":  "the letter opener",
        "motive":  "financial ruin",
    },
    "suspects": [
        {"name": "Ms. Vivian Scarlett", "role": "Business partner", "emoji": "💼",
         "motive": "Ashworth planned to dissolve their partnership — she faced bankruptcy",
         "alibi":  "None — a maid saw her leaving the Study at 9:10 PM"},
        {"name": "Colonel Grey", "role": "Old army friend", "emoji": "🎖️",
         "motive": "Ashworth was blackmailing him over a wartime secret",
         "alibi":  "Playing cards in the Library 8:30–9:30 PM (2 witnesses)"},
        {"name": "Dr. Plum", "role": "Family physician", "emoji": "🩺",
         "motive": "Feared exposure of a malpractice case",
         "alibi":  "In the Library with Colonel Grey"},
        {"name": "Mrs. Beatrice Ashworth", "role": "The widow", "emoji": "👑",
         "motive": "Stood to inherit the entire estate",
         "alibi":  "In the Conservatory with the gardener at 9:00 PM"},
        {"name": "Mr. Hargrove", "role": "The butler", "emoji": "🤵",
         "motive": "Dismissed by Ashworth that very morning",
         "alibi":  "Serving drinks in the Dining Room at 9:00 PM (3 guests)"},
    ],
}

# Natural-language case facts — the corpus we retrieve over.
CLUES = [
    "Lord Edmund Ashworth was found dead in the Study at 9:00 PM.",
    "The murder weapon was a silver letter opener found beside the body in the Study.",
    "Ms. Vivian Scarlett was Lord Ashworth's business partner, and he planned to dissolve the partnership, which would have left her bankrupt.",
    "A maid saw Ms. Vivian Scarlett hurrying out of the Study at 9:10 PM, looking flustered.",
    "Ms. Vivian Scarlett owned a silver letter opener identical to the murder weapon.",
    "Colonel Grey was being blackmailed by Lord Ashworth over a secret from the war.",
    "Colonel Grey and Dr. Plum played cards together in the Library from 8:30 PM until 9:30 PM, confirmed by two footmen.",
    "Dr. Plum feared Lord Ashworth would expose a medical malpractice case against him.",
    "Mrs. Beatrice Ashworth, the victim's wife, stood to inherit his entire estate.",
    "Mrs. Beatrice Ashworth was in the Conservatory tending orchids with the gardener at 9:00 PM.",
    "Mr. Hargrove, the butler, had been dismissed by Lord Ashworth earlier that morning.",
    "Mr. Hargrove was serving drinks in the Dining Room at 9:00 PM, witnessed by three dinner guests.",
]

# Colours for the mystery graph (passed to render_kg as group_colours).
MYSTERY_COLOURS = {
    "Suspect": "#ef4444", "Victim": "#0f172a", "Room": "#3b82f6",
    "Weapon": "#64748b", "Motive": "#f59e0b",
}


def _t(s, p, o, st, ot, clue):
    return {"subject": s, "predicate": p, "object": o,
            "subject_type": st, "object_type": ot, "predicate_type": "mystery",
            "confidence": 1.0, "sentence": clue, "section": "CASE"}


MYSTERY_TRIPLES = [
    _t("Lord Edmund Ashworth", "was murdered in", "the Study", "Victim", "Room", CLUES[0]),
    _t("the letter opener", "was found in", "the Study", "Weapon", "Room", CLUES[1]),
    _t("Ms. Vivian Scarlett", "had motive", "financial ruin", "Suspect", "Motive", CLUES[2]),
    _t("Ms. Vivian Scarlett", "was seen in", "the Study", "Suspect", "Room", CLUES[3]),
    _t("Ms. Vivian Scarlett", "owned", "the letter opener", "Suspect", "Weapon", CLUES[4]),
    _t("Colonel Grey", "had motive", "blackmail", "Suspect", "Motive", CLUES[5]),
    _t("Colonel Grey", "had alibi in", "the Library", "Suspect", "Room", CLUES[6]),
    _t("Dr. Plum", "had motive", "malpractice cover-up", "Suspect", "Motive", CLUES[7]),
    _t("Dr. Plum", "had alibi in", "the Library", "Suspect", "Room", CLUES[6]),
    _t("Mrs. Beatrice Ashworth", "had motive", "inheritance", "Suspect", "Motive", CLUES[8]),
    _t("Mrs. Beatrice Ashworth", "had alibi in", "the Conservatory", "Suspect", "Room", CLUES[9]),
    _t("Mr. Hargrove", "had motive", "revenge", "Suspect", "Motive", CLUES[10]),
    _t("Mr. Hargrove", "had alibi in", "the Dining Room", "Suspect", "Room", CLUES[11]),
]


def mystery_triples() -> list[dict]:
    return [dict(t) for t in MYSTERY_TRIPLES]


def clues() -> list[str]:
    return list(CLUES)


# ── retrieval (semantic search over the clues) ────────────────────────── #

def retrieve(question: str, k: int = 4) -> list[dict]:
    """Return the top-k case facts most similar to the question."""
    import numpy as np
    from sentence_transformers import util
    from notebook_src.validation import _model
    m = _model()   # all-MiniLM-L6-v2 (same model used elsewhere)
    qe = m.encode([question], normalize_embeddings=True)
    ce = m.encode(CLUES, normalize_embeddings=True)
    sims = util.cos_sim(qe, ce).numpy()[0]
    order = np.argsort(sims)[::-1][:k]
    return [{"clue": CLUES[i], "score": float(sims[i])} for i in order]


# ── grounded vs ungrounded answering (prompt engineering) ─────────────── #

def answer(question: str, context_clues: list[str], api_key: str,
           model: str = "gpt-4.1-nano", grounded: bool = True) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    if grounded:
        ctx = "\n".join(f"- {c}" for c in context_clues)
        system = ("You are a detective's assistant. Answer ONLY using the case facts "
                  "provided below. Quote the specific fact(s) you relied on. If the "
                  "facts do not support an answer, say you cannot determine it.")
        user = f"Case facts:\n{ctx}\n\nQuestion: {question}"
    else:
        system = ("You are a detective's assistant. Answer the question using your own "
                  "knowledge only. Do not ask for more information.")
        user = f"Question: {question}"
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}])
    return (r.choices[0].message.content or "").strip()


# ── chain-of-thought solving (grounded reasoning) ─────────────────────── #

def solve(api_key: str, model: str = "gpt-4.1-nano") -> dict:
    """Reason step-by-step over all case facts to name the murderer."""
    import json
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    facts = "\n".join(f"{i+1}. {c}" for i, c in enumerate(CLUES))
    system = (
        "You are a master detective. Using ONLY the numbered case facts, reason step "
        "by step: (1) establish the crime, weapon and time; (2) go through each suspect "
        "and eliminate anyone with a confirmed alibi; (3) identify who alone had motive, "
        "means AND opportunity. Be explicit about which fact supports each step.\n"
        'Return JSON: {"reasoning": ["step 1", "step 2", ...], '
        '"culprit": "full name", "weapon": "...", "motive": "..."}'
    )
    r = client.chat.completions.create(
        model=model, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": f"Case facts:\n{facts}\n\nSolve the murder."}])
    raw = r.choices[0].message.content or "{}"
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        d = {}
    reasoning = [str(s) for s in d.get("reasoning", []) if str(s).strip()]
    culprit = str(d.get("culprit", "")).strip()
    # robustness: if the model left culprit blank, recover the name it concluded
    if not _find_suspect(culprit):
        culprit = _find_suspect(" ".join(reasoning[-2:]) or raw) or culprit
    return {
        "reasoning": reasoning,
        "culprit": culprit,
        "weapon":  str(d.get("weapon", "")).strip() or CASE["weapon"],
        "motive":  str(d.get("motive", "")).strip(),
    }


def _find_suspect(text: str) -> str:
    """Return the first suspect whose surname appears in `text`, else ''."""
    for s in CASE["suspects"]:
        if s["name"].split()[-1].lower() in (text or "").lower():
            return s["name"]
    return ""


def is_correct(culprit: str) -> bool:
    """True if the accused matches the ground-truth murderer (by surname)."""
    return "scarlett" in (culprit or "").lower()
