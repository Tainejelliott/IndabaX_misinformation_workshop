"""
add_rag_components.py
Appends "Breakdown of RAG Components & Misinformation" subsection to the notebook.
Run with: .venv/bin/python builders/add_rag_components.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

_cid = 200
def _id():
    global _cid; _cid += 1
    return f"ragc{_cid:04d}"

def md(src):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": src}

def code(src, tags=None):
    meta = {"tags": tags} if tags else {}
    return {"cell_type": "code", "id": _id(), "metadata": meta,
            "source": src, "outputs": [], "execution_count": None}


# ── subsection header card (amber — signals incomplete) ───────────────
header = md(
    "### Breakdown of RAG Components & Misinformation\n\n"
    '<div style="\n'
    '  border-left: 4px solid #d97706; background: #fffbeb;\n'
    '  border-radius: 0 10px 10px 0; padding: 14px 20px; margin: 4px 0 10px 0;\n'
    '  font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;\n'
    '">\n'
    '  <div style="font-size:16px;font-weight:700;color:#0f172a;">\n'
    '    🔎 &nbsp;Breakdown of RAG Components &amp; Misinformation\n'
    '  </div>\n'
    '  <div style="font-size:12px;color:#475569;margin-top:3px;">\n'
    '    How each component of the RAG pipeline directly addresses challenges in\n'
    '    misinformation detection and fact verification\n'
    '  </div>\n'
    '</div>'
)

# ── TODO placeholder ──────────────────────────────────────────────────
todo = md(
    '<div style="\n'
    '  background: #fff7ed;\n'
    '  border: 2px dashed #f97316;\n'
    '  border-radius: 12px;\n'
    '  padding: 24px 28px;\n'
    '  margin: 8px 0;\n'
    '  font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;\n'
    '">\n'
    '  <div style="font-size:13px;font-weight:700;color:#c2410c;\n'
    '              letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;">\n'
    '    🚧 &nbsp;Section to be completed\n'
    '  </div>\n'
    '  <div style="font-size:14px;color:#7c2d12;margin-bottom:12px;">\n'
    '    This section is reserved for a discussion of how each RAG component\n'
    '    (retrieval, augmentation, generation, citations, KB design)\n'
    '    maps to a specific misinformation challenge.\n'
    '  </div>\n'
    '  <div style="font-size:12px;color:#9a3412;background:#fed7aa;\n'
    '              border-radius:6px;padding:8px 12px;display:inline-block;">\n'
    '    ✏️  Assigned to: <strong>[partner name]</strong> &nbsp;·&nbsp;\n'
    '    Add your content in the code cell below\n'
    '  </div>\n'
    '</div>'
)

# ── empty placeholder code cell ───────────────────────────────────────
placeholder = code(
    "# TODO — add the RAG components vs misinformation visual/content here.\n"
    "# Suggested approach:\n"
    "#   from notebook_src.visuals import show\n"
    "#   show(concept_rag_vs_misinfo())   # implement in notebook_src/visuals.py\n"
    "#\n"
    "# Or add a markdown table / HTML card explaining each component's role."
)

nb["cells"].extend([header, todo, placeholder])
NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Done — {len(nb['cells'])} cells total")
