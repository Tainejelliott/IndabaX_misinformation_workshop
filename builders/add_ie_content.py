"""
add_ie_content.py
1. Removes the segmentation cell from KB Setup.
2. Replaces the IE / OBIE / OpenIE placeholder code cells with:
   - show(render_*_intro()) call
   - TODO triple-extraction code cell beneath each
Run with: .venv/bin/python builders/add_ie_content.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

def src(c):
    s = c["source"]
    return "".join(s) if isinstance(s, list) else s

def code(cid, source):
    return {"cell_type": "code", "id": cid, "metadata": {},
            "source": source, "outputs": [], "execution_count": None}


# ── 1. Remove segmentation cell ───────────────────────────────────── #
nb["cells"] = [
    c for c in nb["cells"]
    if "render_segments" not in src(c) and "segment(ctx)" not in src(c)
]
print(f"After removing seg cell: {len(nb['cells'])} cells")


# ── 2. Replace IE placeholder ──────────────────────────────────────── #
for i, c in enumerate(nb["cells"]):
    if src(c).strip() == "# Information Extraction":
        nb["cells"][i]["source"] = (
            "from notebook_src.visuals import show\n"
            "from notebook_src.display import render_ie_intro\n\n"
            "show(render_ie_intro())"
        )
        print("  updated: Information Extraction intro cell")
        break


# ── 3. Replace OBIE placeholder + insert TODO ──────────────────────── #
for i, c in enumerate(nb["cells"]):
    if src(c).strip() == "# Ontology-based Information Extraction (OBIE)":
        nb["cells"][i]["source"] = (
            "from notebook_src.visuals import show\n"
            "from notebook_src.display import render_obie_intro\n\n"
            "show(render_obie_intro())"
        )
        TODO_OBIE = code("obie_todo", """\
# TODO — OBIE triple extraction
# Extract knowledge graph triples from `contexts` using the MeSH ontology as schema.
#
# Approach:
#   1. Use MeSH terms (already in `ex["context"]["meshes"]`) as the allowed entity types
#   2. Run a biomedical NER model (e.g. SciSpacy en_core_sci_sm) to tag entities
#   3. For each sentence, classify relations between entity pairs using the ontology schema
#   4. Emit (subject, predicate, object) triples that conform to the MeSH hierarchy
#   5. Combine OBIE triples with OpenIE triples (below) for a unified graph
#
# from notebook_src.extraction import extract_obie
# obie_triples = extract_obie(contexts, labels, ontology=ex["context"]["meshes"])
# show(render_triples(obie_triples, strategy="OBIE"))
""")
        nb["cells"].insert(i + 1, TODO_OBIE)
        print("  updated: OBIE intro cell + inserted TODO")
        break


# ── 4. Replace OpenIE placeholder + insert TODO ────────────────────── #
# Re-scan after insert
for i, c in enumerate(nb["cells"]):
    if src(c).strip() == "# Open-Domain Information Extraction (OpenIE)":
        nb["cells"][i]["source"] = (
            "from notebook_src.visuals import show\n"
            "from notebook_src.display import render_openie_intro\n\n"
            "show(render_openie_intro())"
        )
        TODO_OPENIE = code("openie_todo", """\
# TODO — OpenIE triple extraction
# Extract knowledge graph triples from `contexts` without a predefined schema.
#
# Approach:
#   1. Dependency-parse each sentence (e.g. spaCy or Stanford OpenIE)
#   2. Pull subject–verb–object spans directly from the parse tree
#   3. Normalise: lemmatise predicates, resolve basic coreference
#   4. Filter low-confidence or overly short triples
#   5. Compare coverage vs OBIE triples — what did each strategy find/miss?
#
# from notebook_src.extraction import extract_openie
# openie_triples = extract_openie(contexts, labels)
# show(render_triples(openie_triples, strategy="OpenIE"))
""")
        nb["cells"].insert(i + 1, TODO_OPENIE)
        print("  updated: OpenIE intro cell + inserted TODO")
        break


# ── 5. Save + validate ─────────────────────────────────────────────── #
NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))

import nbformat
nbn = nbformat.read(str(NB), as_version=4)
nbformat.validate(nbn)
print(f"\nValid — {len(nbn.cells)} cells total")

# Show A.2 region
in_a2 = False
for c in nbn.cells:
    s = c.source
    if "## Knowledge Base" in s and "Utilization" not in s: in_a2 = True
    if "## Knowledge Base Utilization" in s: break
    if not in_a2: continue
    if c.cell_type == "code":
        print("  [code]", s.splitlines()[0][:70])
    else:
        print("  [md]  ", s.splitlines()[0][:70])
