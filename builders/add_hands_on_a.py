"""
add_hands_on_a.py
Appends Hands-on A.1 and A.2 sections to KG_RAG_Workshop.ipynb.
Run with: .venv/bin/python builders/add_hands_on_a.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

_cid = 300
def _id():
    global _cid; _cid += 1
    return f"hoa{_cid:04d}"

def md(src):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": src}

def section_card(step, title, subtitle, grad_start, grad_end):
    return (
        f"## {title}\n\n"
        f'<div style="\n'
        f'  background: linear-gradient(135deg, {grad_start} 0%, {grad_end} 100%);\n'
        f'  border-radius: 12px; padding: 20px 28px; margin: 4px 0 12px 0;\n'
        f'  font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;\n'
        f'">\n'
        f'  <div style="color:rgba(255,255,255,0.7);font-size:11px;font-weight:600;\n'
        f'              letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">\n'
        f'    🧪 &nbsp;{step}\n'
        f'  </div>\n'
        f'  <div style="color:#fff;font-size:22px;font-weight:700;margin-bottom:4px;">\n'
        f'    {title}\n'
        f'  </div>\n'
        f'  <div style="color:rgba(255,255,255,0.85);font-size:13px;">\n'
        f'    {subtitle}\n'
        f'  </div>\n'
        f'</div>'
    )


# ── A.1 Knowledge Representation ──────────────────────────────────────
a1_header = md(section_card(
    step="Hands-on A.1 · Beginner",
    title="Knowledge Representation",
    subtitle="Data source · Analysis · Processing · Dataset creation · Vector DB vs Graph DB · KB creation · Task evaluation set",
    grad_start="#2563eb",
    grad_end="#0ea5e9",
))

# ── A.2 Knowledge Base ────────────────────────────────────────────────
a2_header = md(section_card(
    step="Hands-on A.2 · Intermediate",
    title="Knowledge Base",
    subtitle="Information extraction · Ontology · Open-domain · Knowledge representation · Graph design",
    grad_start="#7c3aed",
    grad_end="#a855f7",
))

nb["cells"].extend([a1_header, a2_header])
NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Done — {len(nb['cells'])} cells total")
