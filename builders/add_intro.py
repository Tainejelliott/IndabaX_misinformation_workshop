"""
add_intro.py  —  appends the Intro section to KG_RAG_Workshop.ipynb.
Run with: .venv/bin/python builders/add_intro.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent   # project root, one level up from builders/
NB   = ROOT / "KG_RAG_Workshop.ipynb"
SRC  = ROOT / "notebook_src"

visuals_src = (SRC / "visuals.py").read_text()

nb = json.loads(NB.read_text())

_cid = 100
def _id():
    global _cid; _cid += 1
    return f"intro{_cid:04d}"

def md(src):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": src}

def code(src, tags=None):
    meta = {"tags": tags} if tags else {}
    return {"cell_type": "code", "id": _id(), "metadata": meta,
            "source": src, "outputs": [], "execution_count": None}

def section_card(step, title, subtitle, colour):
    return f"""<div style="
  background: linear-gradient(135deg, {colour[0]} 0%, {colour[1]} 100%);
  border-radius: 12px; padding: 20px 28px; margin: 4px 0 12px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <div style="color:rgba(255,255,255,0.7);font-size:11px;font-weight:600;
              letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">
    📖 &nbsp;{step}
  </div>
  <div style="color:#fff;font-size:22px;font-weight:700;margin-bottom:4px;">{title}</div>
  <div style="color:rgba(255,255,255,0.75);font-size:13px;">{subtitle}</div>
</div>"""

def subsection_card(icon, title, subtitle, colour):
    return f"""<div style="
  border-left: 4px solid {colour}; background: #f8fafc;
  border-radius: 0 10px 10px 0; padding: 14px 20px; margin: 4px 0 10px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <div style="font-size:16px;font-weight:700;color:#0f172a;">{icon} &nbsp;{title}</div>
  <div style="font-size:12px;color:#475569;margin-top:3px;">{subtitle}</div>
</div>"""


new_cells = []

# ── hidden: write visuals.py to Colab disk ────────────────────────────
new_cells.append(code(
    "# @title Write visuals module { display-mode: \"form\" }\n"
    "import pathlib\n"
    "pathlib.Path('notebook_src').mkdir(exist_ok=True)\n"
    "pathlib.Path('notebook_src/__init__.py').touch()\n"
    "src = '''" + visuals_src.replace("\\", "\\\\").replace("'''", "\\'\\'\\'") + "'''\n"
    "pathlib.Path('notebook_src/visuals.py').write_text(src)\n"
    "print('✅ visuals module ready')",
    tags=["hide-input"]
))

# ── Intro section header ──────────────────────────────────────────────
new_cells.append(md(
    "## Intro\n\n" +
    section_card(
        "Section 1", "Introduction & Overview",
        "LLMs · Embeddings · RAG — the three ideas this workshop builds on",
        ("#0d9488", "#0891b2")   # teal → cyan
    )
))

# ── 1.1 What are LLMs ────────────────────────────────────────────────
new_cells.append(md(
    "### What are LLMs?\n\n" +
    subsection_card("🤖", "What are LLMs?",
                    "Large Language Models — next-token prediction at scale",
                    "#6366f1")
))
new_cells.append(code(
    "from notebook_src.visuals import show, concept_llm\n"
    "show(concept_llm())"
))

# ── 1.2 What are Embeddings ───────────────────────────────────────────
new_cells.append(md(
    "### What are Embeddings?\n\n" +
    subsection_card("📐", "What are Embeddings?",
                    "Dense vectors that encode meaning — the engine behind semantic search",
                    "#0d9488")
))
new_cells.append(code(
    "from notebook_src.visuals import show, concept_embeddings\n"
    "show(concept_embeddings())"
))

# ── 1.3 What is RAG ───────────────────────────────────────────────────
new_cells.append(md(
    "### What is RAG?\n\n" +
    subsection_card("🔗", "What is RAG?",
                    "Retrieval-Augmented Generation — grounding an LLM in a knowledge base",
                    "#8b5cf6")
))
new_cells.append(code(
    "from notebook_src.visuals import show, concept_rag\n"
    "show(concept_rag())"
))

nb["cells"].extend(new_cells)
NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Done — {len(nb['cells'])} cells total")
