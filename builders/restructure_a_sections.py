"""
restructure_a_sections.py
Rebuilds the A.1 and A.2 subsection hierarchy with correct nesting.
Replaces the existing flat subsections entirely.
Run with: .venv/bin/python builders/restructure_a_sections.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

# ── cell factories ─────────────────────────────────────────────────── #
_cid = 600
def _id():
    global _cid; _cid += 1
    return f"rst{_cid:04d}"

def md(src):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": src}

def code(src, tags=None):
    meta = {"tags": tags} if tags else {}
    return {"cell_type": "code", "id": _id(), "metadata": meta,
            "source": src, "outputs": [], "execution_count": None}

def sub(depth, heading_char_count, icon, title, subtitle, base_colour, bg_colour):
    """
    depth 1 → ###   indent 0px
    depth 2 → ####  indent 24px
    depth 3 → ##### indent 48px
    """
    hashes  = "#" * heading_char_count
    indent  = (depth - 1) * 24
    border  = 4 if depth == 1 else 3
    return md(
        f"{hashes} {title}\n\n"
        f'<div style="margin-left:{indent}px;border-left:{border}px solid {base_colour};'
        f'background:{bg_colour};border-radius:0 10px 10px 0;padding:13px 18px;'
        f'margin-top:4px;margin-bottom:10px;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">\n'
        f'  <div style="font-size:{"16" if depth==1 else "14"}px;font-weight:700;'
        f'color:#0f172a;">{icon} &nbsp;{title}</div>\n'
        f'  <div style="font-size:12px;color:#475569;margin-top:3px;'
        f'line-height:1.5">{subtitle}</div>\n'
        f'</div>'
    )

def empty(label):
    return code(f"# {label}\n")


# ── A.1 palette ───────────────────────────────────────────────────── #
A1 = dict(
    l1=("#2563eb", "#eff6ff"),   # blue tint
    l2=("#1d4ed8", "#f0f4ff"),   # slightly deeper blue
    l3=("#1e40af", "#f5f8ff"),   # deepest blue
)

# ── A.2 palette ───────────────────────────────────────────────────── #
A2 = dict(
    l1=("#7c3aed", "#f5f3ff"),   # violet tint
    l2=("#6d28d9", "#f3f0ff"),
    l3=("#5b21b6", "#f0ecff"),
)

def s1(icon, title, subtitle, pal):
    return [sub(1, 3, icon, title, subtitle, *pal["l1"]), empty(title)]

def s2(icon, title, subtitle, pal):
    return [sub(2, 4, icon, title, subtitle, *pal["l2"]), empty(title)]

def s3(icon, title, subtitle, pal):
    return [sub(3, 5, icon, title, subtitle, *pal["l3"]), empty(title)]


# ══════════════════════════════════════════════════════════════════════ #
# A.1 — Knowledge Representation subsections                            #
# ══════════════════════════════════════════════════════════════════════ #
a1_cells = [
    *s1("📂", "Data Source",
        "Identifying, collecting and citing raw information sources",
        A1),

    *s1("🔎", "Data / Information Analysis",
        "Exploring structure, quality, coverage and biases of the raw data",
        A1),

    *s1("⚙️", "Data Processing",
        "Cleaning, normalising and transforming raw data into a consistent format",
        A1),

    *s2("🧹", "Data Pre-processing",
        "Fine-grained preparation within processing — tokenisation, entity resolution, deduplication",
        A1),

    *s2("🗂️", "Dataset Creation",
        "Assembling the final labelled dataset ready for ingestion",
        A1),

    *s3("⚖️", "Vector DB vs Graph DB",
        "Comparing storage paradigms for the created dataset — "
        "similarity search vs structured graph traversal",
        A1),

    *s1("📏", "Task Evaluation Set",
        "Designing held-out questions to measure retrieval and answer quality",
        A1),

    *s1("🏗️", "Knowledge Base Creation",
        "Embedding, indexing and graph construction — turning the dataset into a queryable KB",
        A1),
]

# ══════════════════════════════════════════════════════════════════════ #
# A.2 — Knowledge Base subsections                                      #
# ══════════════════════════════════════════════════════════════════════ #
a2_cells = [
    *s1("🔬", "Information Extraction",
        "Identifying and pulling structured facts — entities, relations and claims — from text",
        A2),

    *s2("🗺️", "Ontology-based Information Extraction (OBIE)",
        "Using a predefined ontology to guide extraction — high precision, closed schema",
        A2),

    *s2("🌐", "Open-Domain Information Extraction (OpenIE)",
        "Schema-free extraction across any domain — higher recall, noisier output",
        A2),

    *s1("📐", "Ontology",
        "Defining the vocabulary of the KB: node types, edge types and their semantics",
        A2),

    *s1("🧠", "Knowledge Representation",
        "Choosing how to encode facts so they are queryable, traversable and maintainable",
        A2),

    *s2("📊", "Graph Design",
        "Structural decisions that determine how well the graph supports retrieval and reasoning",
        A2),

    *s3("🔩", "Properties, Directionality, Temporal, Disambiguation & Metadata",
        "Properties: attributes on nodes/edges · "
        "Directionality: what A→B means semantically · "
        "Temporal: validity windows · "
        "Disambiguation: resolving ambiguous surface forms · "
        "Metadata: provenance, confidence, source reliability",
        A2),
]


# ══════════════════════════════════════════════════════════════════════ #
# Rebuild notebook: keep everything outside A.1/A.2 content             #
# ══════════════════════════════════════════════════════════════════════ #
def first_idx(cells, prefix):
    return next(i for i, c in enumerate(cells) if c["source"].startswith(prefix))

a1_idx = first_idx(nb["cells"], "## Knowledge Representation")
a2_idx = first_idx(nb["cells"], "## Knowledge Base")

# Cells before A.1 content, the two section headers, and anything after A.2 content
before      = nb["cells"][:a1_idx + 1]          # up to and including A.1 header
a2_header   = [nb["cells"][a2_idx]]              # just the A.2 header cell

# Everything after A.2 header — skip old subsection cells, keep only
# future top-level (##) sections that may be added later.
raw_after   = nb["cells"][a2_idx + 1:]
after       = [c for c in raw_after
               if c["source"].startswith("## ")
               and not c["source"].startswith("## Knowledge Base")]

nb["cells"] = before + a1_cells + a2_header + a2_cells + after

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Done — {len(nb['cells'])} cells total")
