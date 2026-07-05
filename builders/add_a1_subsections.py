"""
add_a1_subsections.py
Adds subsections to the Knowledge Representation (A.1) section.
Run with: .venv/bin/python builders/add_a1_subsections.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

_cid = 400
def _id():
    global _cid; _cid += 1
    return f"a1s{_cid:04d}"

def md(src):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": src}

def code(src, tags=None):
    meta = {"tags": tags} if tags else {}
    return {"cell_type": "code", "id": _id(), "metadata": meta,
            "source": src, "outputs": [], "execution_count": None}

def subsection(icon, title, subtitle, colour="#2563eb"):
    """### heading + styled left-border card."""
    return md(
        f"### {title}\n\n"
        f'<div style="border-left:4px solid {colour};background:#eff6ff;'
        f'border-radius:0 10px 10px 0;padding:14px 20px;margin:4px 0 10px 0;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">\n'
        f'  <div style="font-size:16px;font-weight:700;color:#0f172a;">'
        f'{icon} &nbsp;{title}</div>\n'
        f'  <div style="font-size:12px;color:#475569;margin-top:3px;">{subtitle}</div>\n'
        f'</div>'
    )

def placeholder(label):
    """Empty code cell ready for content."""
    return code(f"# {label}\n")


SUBSECTIONS = [
    ("📂", "Data Source",
     "Where the data comes from — identifying, collecting and citing raw information sources"),
    ("🔎", "Data / Information Analysis",
     "Exploring and understanding the structure, quality and coverage of the raw data"),
    ("⚙️", "Data Processing",
     "Cleaning, normalising and transforming raw data into a consistent, usable format"),
    ("🧹", "Data Pre-processing",
     "Fine-grained preparation — tokenisation, entity resolution, deduplication"),
    ("🗂️", "Dataset Creation",
     "Assembling the final labelled dataset ready for ingestion into the knowledge base"),
    ("⚖️", "Vector DB vs Graph DB",
     "Comparing storage paradigms — when to use similarity search vs structured traversal"),
    ("📏", "Task Evaluation Set",
     "Designing the held-out questions used to measure retrieval and answer quality"),
    ("🏗️", "Knowledge Base Creation",
     "Building and populating the knowledge base — embedding, indexing and graph construction"),
]

# Find the index of the A.1 header cell so we insert immediately after it
a1_idx = next(
    i for i, c in enumerate(nb["cells"])
    if c["source"].startswith("## Knowledge Representation")
)

new_cells = []
for icon, title, subtitle in SUBSECTIONS:
    new_cells.append(subsection(icon, title, subtitle))
    new_cells.append(placeholder(title))

# Insert after the A.1 header (not at the end, so A.2 stays below)
nb["cells"] = (
    nb["cells"][:a1_idx + 1] +
    new_cells +
    nb["cells"][a1_idx + 1:]
)

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Done — {len(nb['cells'])} cells total")
