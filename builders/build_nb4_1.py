"""
builders/build_nb4_1.py
Build '4.1 - Hands-on A2 (Proposition Pipeline).ipynb' — the dissertation-style
KG pipeline on a pancreatic-cancer corpus, kept next to notebook 4 for comparison:

  Overview → 1 Corpus → 2 Chunking (propositions + OpenIE/OBIE triples) →
  3 Back-translation & 3-model STS-B calibration (+ representation comparison) →
  4 Coreference resolution → 5 Triples from propositions → 6 Entity mapping →
  7 Final KG (propositions in edges, concepts on nodes) → 8 Bridge to Hands-on B

Run: .venv/bin/python builders/build_nb4_1.py
"""
import json, uuid, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "4.1 - Hands-on A2 (Proposition Pipeline).ipynb"


def md(s):
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:8],
            "metadata": {}, "source": s}

def code(s):
    return {"cell_type": "code", "id": uuid.uuid4().hex[:8],
            "metadata": {}, "source": s, "outputs": [], "execution_count": None}

def sub(hashes, border, bg, icon, name, desc):
    return md(
        f"{hashes} {name}\n\n"
        f'<div style="border-left:{4 if hashes=="##" else 3}px solid {border};'
        f'background:{bg};border-radius:0 10px 10px 0;padding:13px 18px;margin-top:4px;'
        f'margin-bottom:10px;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">'
        f'<div style="font-size:14px;font-weight:700;color:#0f172a;">{icon} &nbsp;{name}</div>'
        f'<div style="font-size:12px;color:#475569;margin-top:3px;line-height:1.5">{desc}</div>'
        f'</div>'
    )


TEAL = "#0d9488"; TEALBG = "#f0fdfa"
PUR  = "#7c3aed"; PURBG  = "#f5f3ff"
BLUE = "#1d4ed8"; BLUEBG = "#eff6ff"
AMB  = "#b45309"; AMBBG  = "#fffbeb"
RED  = "#b91c1c"; REDBG  = "#fef2f2"
SLATE = "#475569"; SLATEBG = "#f8fafc"

cells = []

# ─── Title + Setup ─────────────────────────────────────────────────── #
cells.append(md(
"""# Hands-on A.2 — Proposition Pipeline (v4.1)
### IndabaX 2026 · a research-style KG pipeline, side-by-side with notebook 4"""))

cells.append(md("## Setup"))
cells.append(code(
'''# @title Install dependencies { display-mode: "form" }
import sys, subprocess
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "datasets", "openai", "python-dotenv", "spacy",
    "sentence-transformers>=3.0", "networkx", "pyvis>=0.3.2",
    "matplotlib", "scipy"], check=True)
subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm", "-q"], check=True)
print("✅ packages ready")'''))

cells.append(code(
'''# @title Setup { display-mode: "form" }
import sys, os, pathlib

_root = pathlib.Path.cwd()
if not (_root / "notebook_src").exists():
    for _p in sorted(_root.glob("*/notebook_src")):
        _root = _p.parent
        break
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# ── API key (one-time demo) ──────────────────────────────────────────────
# Paste your OpenAI key between the quotes for the demo, then DELETE it after.
# Leave blank to fall back to a local .env file.
OPENAI_API_KEY = ""
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
elif not os.environ.get("OPENAI_API_KEY"):
    try:
        from dotenv import load_dotenv
        load_dotenv(_root / ".env")
    except ImportError:
        pass
API_KEY = os.environ.get("OPENAI_API_KEY", "")

# ── Model ────────────────────────────────────────────────────────────────
# gpt-4o-mini works on virtually any key; switch to gpt-4.1-nano (cheaper) or any
# chat model your key supports. This pipeline makes many LLM calls — mind the cost.
MODEL = "gpt-4o-mini"

print("✅ notebook_src ready —", _root)
print("🔑 OpenAI key:", "found" if API_KEY else "MISSING — paste it above or create a .env file")
print("🤖 Model:", MODEL)'''))

cells.append(code(
'''# What this hands-on covers, end to end
from notebook_src.visuals import show
from notebook_src.display import render_4_1_roadmap
show(render_4_1_roadmap())'''))

# ─── Part 1 · The Corpus ───────────────────────────────────────────── #
cells.append(sub("##", TEAL, TEALBG, "📄", "Part 1 · The Corpus",
                 "Five same-domain abstracts on pancreatic cancer. One becomes the working "
                 "example we take all the way to a knowledge graph."))
cells.append(code(
'''from notebook_src import pancreatic as P
from notebook_src.display import render_corpus, render_abstract

show(render_corpus(P.abstracts(), working=0))

# The working abstract — shown in the SAME paper-card representation as notebook 4.
working = P.working_abstract()
show(render_abstract(P.to_ex(working), working["title"], working["authors"],
                     working["journal"], working["year"]))'''))

# ─── Part 2 · Chunking ─────────────────────────────────────────────── #
cells.append(sub("##", PUR, PURBG, "✂️", "Part 2 · Chunking the Abstract",
                 "Two ways to break text into knowledge units: atomic PROPOSITIONS, and "
                 "TRIPLES (open-domain vs ontology-based)."))

cells.append(sub("###", PUR, PURBG, "🧩", "Proposition chunking",
                 "Decompose the abstract into atomic, single-fact statements (pronouns kept for now)."))
cells.append(code(
'''from notebook_src.extraction import extract_propositions
from notebook_src.display import render_propositions

text  = P.full_text(working)
props = extract_propositions(text, API_KEY, model=MODEL)
show(render_propositions(props))'''))

cells.append(sub("###", PUR, PURBG, "🗺️", "The schema we're extracting (as a graph)",
                 "Before extracting anything, here is the ontology itself as a knowledge graph — "
                 "the entity TYPES (nodes) and the typical relations we expect to populate. "
                 "Triple extraction fills this schema with real instances."))
cells.append(code(
'''from notebook_src.display import render_kg

# The ontology as a KG: nodes are entity TYPES, edges are the schema-level relations.
show(render_kg(P.schema_triples(), strategy="Ontology Schema", color_by="type",
               group_colours=P.TYPE_COLOURS, height="420px"))'''))

cells.append(sub("###", PUR, PURBG, "📚", "Where does the OBIE schema come from?",
                 "OBIE's categories must be fixed in advance. Ours is a curated slice of MeSH and "
                 "UMLS — standard biomedical vocabularies from the U.S. National Library of Medicine."))
cells.append(code(
'''from notebook_src.display import render_obie_schema_source
show(render_obie_schema_source(P.PANCREATIC_ONTOLOGY))'''))

cells.append(sub("###", PUR, PURBG, "🔗", "Triple chunking — OpenIE vs OBIE",
                 "Open-domain extraction (schema-free) beside ontology-based extraction "
                 "(anchored to the pancreatic-cancer MeSH ontology above)."))
cells.append(code(
'''from notebook_src.extraction import extract_openie, extract_obie
from notebook_src.display import render_triples

contexts, labels = P.sections(working)

# Open-domain: every relationship, entity types guessed against our ontology.
openie = extract_openie(contexts, labels, API_KEY, model=MODEL,
                        ontology_types=P.PANCREATIC_ONTOLOGY)
show(render_triples(openie, strategy="OpenIE"))

# Ontology-based: triples anchored to the pancreatic MeSH concepts.
obie = extract_obie(contexts, labels, P.mesh_headings(), API_KEY, model=MODEL)
show(render_triples(obie, strategy="OBIE"))'''))

cells.append(sub("###", BLUE, BLUEBG, "🔬", "OpenIE vs OBIE — the structural difference",
                 "The same kind of fact, extracted two ways: an open-domain triple carries a GUESSED "
                 "entity type; an ontology-based triple is ANCHORED to a fixed MeSH concept."))
cells.append(code(
'''from notebook_src.display import render_ie_structure_compare

# Pick a representative triple from each (one that actually carries its tag).
openie_ex = next((t for t in openie if t.get("subject_type")), openie[0]) if openie else {}
obie_ex   = next((t for t in obie   if t.get("subject_mesh")), obie[0])   if obie   else {}
show(render_ie_structure_compare(openie_ex, obie_ex))'''))

# ─── Part 3 · Validate ─────────────────────────────────────────────── #
cells.append(sub("##", BLUE, BLUEBG, "🔁", "Part 3 · Validate — Back-translation & Calibration",
                 "Reconstruct the abstract from a representation and measure the round-trip. "
                 "A raw cosine is only meaningful once you calibrate it — across THREE models."))

cells.append(sub("###", BLUE, BLUEBG, "↩️", "Back-translation",
                 "Turn triples back into prose. If the meaning survived, the reconstruction "
                 "should be close to the original."))
cells.append(code(
'''from notebook_src.validation import back_translate, text_cosine, BIOMED_MODEL
from notebook_src.display import render_abstract_comparison

reconstructed = back_translate(openie, API_KEY, model=MODEL)
sim = text_cosine(text, reconstructed, model_name=BIOMED_MODEL)
show(render_abstract_comparison(text, reconstructed, sim, model_name="BioLORD"))'''))

cells.append(sub("###", BLUE, BLUEBG, "📏", "What does a cosine score mean? — three models",
                 "The same STS-B benchmark under a general, a biomedical and a legal model. "
                 "Our 5 abstracts' round-trip score is marked on each scale."))
cells.append(code(
'''import numpy as np
from notebook_src.extraction import extract_propositions
from notebook_src.validation import (CALIBRATION_MODELS, stsb_cosine_by_category,
    plot_calibration, back_translate_statements, text_cosine)

# Round-trip all 5 abstracts (cheap: proposition reconstruction) for the highlight.
roundtrips = []
for a in P.abstracts():
    t  = P.full_text(a)
    ap = props if a is P.abstracts()[0] else extract_propositions(t, API_KEY, model=MODEL)
    roundtrips.append((t, back_translate_statements(ap, API_KEY, model=MODEL)))

# One calibration plot per model (general → biomedical → legal), each highlighting
# the mean cosine of OUR abstracts' round-trip under that model.
cat_by_model, highlights = {}, {}
for label, mname in CALIBRATION_MODELS.items():
    cat = stsb_cosine_by_category(max_pairs=500, model_name=mname)
    hl  = float(np.mean([text_cosine(o, r, model_name=mname) for o, r in roundtrips]))
    plot_calibration(cat, highlight=hl, highlight_label="our abstracts", model_name=label)
    cat_by_model[label], highlights[label] = cat, hl'''))

cells.append(sub("###", BLUE, BLUEBG, "⚖️", "Compare 1 — the three models on one axis",
                 "Same relatedness, different cosine. A domain model with no STS tuning "
                 "(legal) compresses everything high — its cosine is hard to read."))
cells.append(code(
'''from notebook_src.validation import plot_model_comparison
plot_model_comparison(cat_by_model, highlights=highlights)'''))

cells.append(sub("###", BLUE, BLUEBG, "🧪", "Compare 2 — which representation preserved the meaning?",
                 "Back-translate each chunking representation and score its fidelity: "
                 "propositions vs OpenIE triples vs OBIE triples."))
cells.append(code(
'''from notebook_src.validation import representation_fidelity
from notebook_src.display import render_representation_compare

reps = [
    {"name": "Propositions",   "kind": "propositions", "items": props},
    {"name": "OpenIE triples", "kind": "triples",      "items": openie},
    {"name": "OBIE triples",   "kind": "triples",      "items": obie},
]
fidelity = representation_fidelity(text, reps, API_KEY, model_name=BIOMED_MODEL, model=MODEL)
show(render_representation_compare(fidelity))'''))

# ─── Part 4 · Coreference ──────────────────────────────────────────── #
cells.append(sub("##", TEAL, TEALBG, "🔗", "Part 4 · Coreference Resolution",
                 "Our propositions still say 'it' and 'they'. Resolve every reference to the "
                 "explicit entity, so each proposition stands on its own."))
cells.append(code(
'''from notebook_src.extraction import resolve_coreferences
from notebook_src.display import render_coref

resolved = resolve_coreferences(props, API_KEY, model=MODEL, context=text)
show(render_coref(props, resolved))'''))

# ─── Part 5 · Triples from propositions ────────────────────────────── #
cells.append(sub("##", PUR, PURBG, "⚙️", "Part 5 · Triples from the Propositions",
                 "Because each proposition is atomic and self-contained, extraction is "
                 "cleaner. Every triple keeps its source proposition."))
cells.append(code(
'''from notebook_src.extraction import triples_from_propositions
from notebook_src.display import render_triples, render_proposition_schema

prop_triples = triples_from_propositions(resolved, API_KEY, model=MODEL,
                                         ontology_types=P.PANCREATIC_ONTOLOGY)

# The SCHEMA these triples follow: ontological TYPES on the entities, and the
# source PROPOSITION embedded inside the relationship (concepts are added in Part 6).
show(render_proposition_schema(prop_triples[0] if prop_triples else None))

# The triples themselves.
show(render_triples(prop_triples, strategy="OpenIE"))
print("Each triple's provenance is the proposition it came from, e.g.:")
print(" •", prop_triples[0]["sentences"][0] if prop_triples else "(none)")'''))

# ─── Part 6 · Entity mapping ───────────────────────────────────────── #
cells.append(sub("##", AMB, AMBBG, "🧬", "Part 6 · Entity Mapping — Bridging Synonyms",
                 "Ground every entity to a concept. Watch the many surface forms of the disease "
                 "— PDAC, adenocarcinoma, cancer of the pancreas — bridge to ONE concept."))
cells.append(code(
'''from notebook_src.extraction import ground_to_mesh
from notebook_src.graph import canonicalize_triples
from notebook_src.display import render_grounding, render_disambiguation

# (a) Ground each entity to a concept — every surface form of the disease
#     (PDAC, adenocarcinoma, cancer of the pancreas) bridges to one concept.
typed, rows = ground_to_mesh(prop_triples, P.mesh_headings(),
                             m2t=P.mesh_to_type(), allowed_types=P.type_names(),
                             synonyms=P.synonyms())
show(render_grounding(rows))'''))

cells.append(code(
'''# 🔎 The bridge: every surface form of the disease now points at ONE concept.
for r in rows:
    if r["mapped_type"] == "Neoplastic Process":
        print(f'{r["entity"]:32s} -> {r["mesh"]}  ({r["via"]})')

# (b) Merge those surface forms into a single canonical node.
kg_triples, clusters, (n_before, n_after) = canonicalize_triples(typed, threshold=0.9)
show(render_disambiguation(clusters, n_before, n_after))'''))

# ─── Part 7 · Final KG ─────────────────────────────────────────────── #
cells.append(sub("##", TEAL, TEALBG, "🕸️", "Part 7 · The Final Knowledge Graph",
                 "One graph: PROPOSITIONS live inside the edges (hover an edge), CONCEPTS live "
                 "on the entities (hover a node). This is the structure you'll reuse in Hands-on B."))
cells.append(code(
'''from notebook_src.graph import build_graph, graph_stats
from notebook_src.display import render_kg_pair, render_graph_stats, render_proposition_schema

# Reminder of what every edge and node in the final graph carries — now with the
# grounded CONCEPT filled in by Part 6's entity mapping.
show(render_proposition_schema(kg_triples[0] if kg_triples else None))

# Before vs after entity mapping: raw proposition-triples (varied surface forms,
# LLM-guessed types) → grounded to concepts and merged into canonical nodes.
show(render_kg_pair(prop_triples, kg_triples,
                    left_title="Before entity mapping",
                    right_title="After entity mapping (grounded + merged)",
                    color_by="type", group_colours=P.TYPE_COLOURS, height="460px"))

kg = build_graph(kg_triples)
show(render_graph_stats(graph_stats(kg)))'''))

# ─── Part 8 · Bridge ───────────────────────────────────────────────── #
cells.append(sub("##", RED, REDBG, "🔪", "Part 8 · Now Apply It to a Murder",
                 "You just built a proposition-grounded knowledge graph from scientific text. "
                 "In Hands-on B you use the very same logic to solve a crime."))
cells.append(code(
'''from notebook_src.display import render_points_card
show(render_points_card("Bridge", "Same pipeline, new domain",
    "What you built here transfers directly to Hands-on B", [
    "<b>Chunk</b> the source into propositions and triples — text becomes knowledge units.",
    "<b>Validate</b> the extraction — back-translation + a calibrated similarity score.",
    "<b>Resolve coreference</b> so every unit stands alone.",
    "<b>Map entities to concepts</b> — bridge synonyms to one node.",
    "<b>Build the graph</b> — propositions in the edges, concepts on the entities — then "
    "reason over it. In Hands-on B, that reasoning names a murderer.",
], grad="135deg,#7f1d1d,#b91c1c"))'''))

# ─── References ────────────────────────────────────────────────────── #
cells.append(md("""## References

**Chunking & extraction**
- [Chen et al. (2023) — Dense X Retrieval: What Retrieval Granularity Should We Use? (proposition chunking)](https://arxiv.org/abs/2312.06648)
- Banko et al. (2007) — Open Information Extraction from the Web (IJCAI) · Wimalasuriya & Dou (2010) — Ontology-Based Information Extraction: A Survey

**Validation & similarity**
- [Cer et al. (2017) — SemEval-2017 STS Benchmark](https://arxiv.org/abs/1708.00055)
- [Reimers & Gurevych (2019) — Sentence-BERT (EMNLP)](https://arxiv.org/abs/1908.10084) · [Wang et al. (2020) — MiniLM (NeurIPS)](https://arxiv.org/abs/2002.10957)

**Biomedical ontology & embeddings**
- [MeSH — Medical Subject Headings (NLM)](https://www.nlm.nih.gov/mesh/) · [UMLS — Bodenreider (2004), NLM](https://www.nlm.nih.gov/research/umls/)
- [BioLORD — Remy et al. (2023)](https://huggingface.co/FremyCompany/BioLORD-2023-C) · [LEGAL-BERT — Chalkidis et al. (2020)](https://arxiv.org/abs/2010.02559)

**Models & tools**
- [OpenAI API](https://platform.openai.com/docs) · [Hugging Face Datasets](https://huggingface.co/docs/datasets) · [sentence-transformers](https://www.sbert.net) · [NetworkX](https://networkx.org) · [pyvis](https://pyvis.readthedocs.io)

*The five pancreatic-cancer abstracts are hand-authored for teaching from established facts — illustrative, not real papers.*
"""))

# ─── write ─────────────────────────────────────────────────────────── #
existing = json.loads(NB.read_text()) if NB.exists() else {}
META = existing.get("metadata", {}) or {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}
nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": META, "cells": cells}
NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))

import nbformat
nbformat.validate(nbformat.read(str(NB), as_version=4))
print(f"Wrote {NB.name} — {len(cells)} cells")
