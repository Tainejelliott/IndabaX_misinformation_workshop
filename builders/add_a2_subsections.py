"""
add_a2_subsections.py
Adds subsections to the Knowledge Base (A.2) section.
Run with: .venv/bin/python builders/add_a2_subsections.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

_cid = 500
def _id():
    global _cid; _cid += 1
    return f"a2s{_cid:04d}"

def md(src):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": src}

def code(src, tags=None):
    meta = {"tags": tags} if tags else {}
    return {"cell_type": "code", "id": _id(), "metadata": meta,
            "source": src, "outputs": [], "execution_count": None}

def subsection(icon, title, subtitle, colour="#7c3aed"):
    return md(
        f"### {title}\n\n"
        f'<div style="border-left:4px solid {colour};background:#f5f3ff;'
        f'border-radius:0 10px 10px 0;padding:14px 20px;margin:4px 0 10px 0;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">\n'
        f'  <div style="font-size:16px;font-weight:700;color:#0f172a;">'
        f'{icon} &nbsp;{title}</div>\n'
        f'  <div style="font-size:12px;color:#475569;margin-top:3px;">{subtitle}</div>\n'
        f'</div>'
    )

def placeholder(label):
    return code(f"# {label}\n")


SUBSECTIONS = [
    ("🔬", "Information Extraction",
     "Identifying and pulling structured facts — entities, relations and claims — from raw text"),
    ("🗺️", "Ontology",
     "Defining the vocabulary of the knowledge base: node types, edge types and their semantics"),
    ("🌐", "Open-domain",
     "Handling knowledge that spans multiple domains without a fixed, closed schema"),
    ("🧠", "Knowledge Representation",
     "Choosing how to encode facts so they are queryable, traversable and maintainable"),
    ("📊", "Graph Design",
     "Structural decisions that determine how well the graph supports retrieval and reasoning"),
    ("🔩", "Properties, Directionality, Temporal, Disambiguation & Metadata",
     "Properties: attributes on nodes/edges · Directionality: A→B semantics · "
     "Temporal: validity windows · Disambiguation: resolving ambiguous surface forms · "
     "Metadata: provenance, confidence, source reliability"),
]

# Find A.2 header index — insert immediately after it
a2_idx = next(
    i for i, c in enumerate(nb["cells"])
    if c["source"].startswith("## Knowledge Base")
)

new_cells = []
for icon, title, subtitle in SUBSECTIONS:
    new_cells.append(subsection(icon, title, subtitle))
    new_cells.append(placeholder(title))

nb["cells"] = (
    nb["cells"][:a2_idx + 1] +
    new_cells +
    nb["cells"][a2_idx + 1:]
)

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Done — {len(nb['cells'])} cells total")
