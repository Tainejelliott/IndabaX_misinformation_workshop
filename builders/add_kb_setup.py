"""
add_kb_setup.py
Inserts a ### Setup subsection before Information Extraction in the A.2
Knowledge Base section.  Contains:
  - markdown heading cell
  - code cell: load PubMedQA + render abstract
  - code cell: segment the context into sentences
Run with: .venv/bin/python builders/add_kb_setup.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

# ── cell factories ─────────────────────────────────────────────────── #
_cid = 800
def _id():
    global _cid; _cid += 1
    return f"kbs{_cid:04d}"

def md(src):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": src}

def code(src):
    return {"cell_type": "code", "id": _id(), "metadata": {},
            "source": src, "outputs": [], "execution_count": None}

# ── 1. Heading cell ────────────────────────────────────────────────── #
heading = md(
    "### Setup\n\n"
    '<div style="margin-left:0px;border-left:4px solid #7c3aed;background:#f5f3ff;'
    'border-radius:0 10px 10px 0;padding:13px 18px;margin-top:4px;margin-bottom:10px;'
    "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;\">\n"
    '  <div style="font-size:16px;font-weight:700;color:#0f172a;">'
    '🔬 &nbsp;Setup</div>\n'
    '  <div style="font-size:12px;color:#475569;margin-top:3px;line-height:1.5">'
    'Load a real PubMedQA abstract and inspect its structure before we extract knowledge from it.'
    '</div>\n'
    '</div>'
)

# ── 2. Load + display cell ─────────────────────────────────────────── #
DISPLAY_CODE = '''\
# ── Load PubMedQA and display the first abstract ─────────────────────
from datasets import load_dataset
from notebook_src.visuals import show

ds  = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split="train",
                   trust_remote_code=True)
ex  = ds[0]          # first example

pmid     = ex["pubid"]           # 21645374
question = ex["question"]
contexts = ex["context"]["contexts"]
labels   = ex["context"]["labels"]
meshes   = ex["context"]["meshes"]
answer   = ex["long_answer"]
decision = ex["final_decision"].upper()

# ── Static metadata (fetched from NCBI) ──────────────────────────────
TITLE   = "Do mitochondria play a role in remodelling lace plant leaves during programmed cell death?"
AUTHORS = "Lord CEN, Wertman JN, Lane S, Gunawardena AHLAN"
JOURNAL = "BMC Plant Biology"
YEAR    = "2011"

LABEL_COLOURS = {
    "BACKGROUND": ("#1e40af", "#dbeafe"),
    "METHODS":    ("#065f46", "#d1fae5"),
    "RESULTS":    ("#92400e", "#fef3c7"),
    "CONCLUSIONS":("#4c1d95", "#ede9fe"),
    "OBJECTIVE":  ("#155e75", "#cffafe"),
}

def section_card(label, text):
    col, bg = LABEL_COLOURS.get(label, ("#374151", "#f9fafb"))
    return (
        f\'<div style="margin-bottom:10px;">\' +
        f\'<span style="display:inline-block;background:{col};color:#fff;\' +
        f\'font-size:10px;font-weight:700;letter-spacing:1.5px;padding:2px 8px;\' +
        f\'border-radius:4px;margin-bottom:5px;">{label}</span>\' +
        f\'<div style="font-size:13px;color:#1e293b;line-height:1.7;background:{bg};\' +
        f\'border-radius:6px;padding:10px 14px;">{text}</div></div>\'
    )

mesh_tags = "".join(
    f\'<span style="display:inline-block;background:#f1f5f9;border:1px solid #e2e8f0;\' +
    f\'border-radius:20px;padding:2px 10px;font-size:11px;color:#475569;margin:2px;">\' +
    f\'{m}</span>\'
    for m in meshes
)

decision_col = {"YES":"#059669","NO":"#dc2626","MAYBE":"#d97706"}.get(decision,"#6b7280")

abstract_html = "".join(section_card(l, c) for l, c in zip(labels, contexts))

html = f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;
            border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;margin:8px 0;">

  <!-- Header bar -->
  <div style="background:linear-gradient(135deg,#1e3a8a,#3b82f6);padding:16px 20px;">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
      <span style="background:rgba(255,255,255,.2);color:#fff;font-size:10px;
                   font-weight:700;letter-spacing:1.5px;padding:2px 8px;
                   border-radius:4px;">PubMedQA</span>
      <span style="background:rgba(255,255,255,.2);color:#fff;font-size:10px;
                   font-weight:700;padding:2px 8px;border-radius:4px;">
        PMID {pmid}</span>
      <span style="margin-left:auto;background:{decision_col};color:#fff;
                   font-size:11px;font-weight:700;padding:3px 10px;
                   border-radius:20px;">✓ {decision}</span>
    </div>
    <div style="color:#fff;font-size:15px;font-weight:700;line-height:1.4;
                margin-bottom:6px;">{TITLE}</div>
    <div style="color:rgba(255,255,255,.8);font-size:12px;">{AUTHORS}</div>
    <div style="color:rgba(255,255,255,.65);font-size:11px;margin-top:2px;">
      {JOURNAL} · {YEAR}</div>
  </div>

  <!-- MeSH terms -->
  <div style="padding:10px 16px;background:#f8fafc;border-bottom:1px solid #e2e8f0;">
    <span style="font-size:10px;font-weight:700;color:#94a3b8;
                 letter-spacing:1px;margin-right:6px;">MeSH</span>
    {mesh_tags}
  </div>

  <!-- Research question -->
  <div style="padding:12px 16px;background:#fefce8;border-bottom:1px solid #fef08a;">
    <div style="font-size:10px;font-weight:700;color:#854d0e;
                letter-spacing:1px;margin-bottom:4px;">❓ RESEARCH QUESTION</div>
    <div style="font-size:13px;color:#1c1917;font-weight:500;
                font-style:italic;">{question}</div>
  </div>

  <!-- Abstract sections -->
  <div style="padding:14px 16px;">
    <div style="font-size:10px;font-weight:700;color:#94a3b8;
                letter-spacing:1px;margin-bottom:10px;">📄 ABSTRACT</div>
    {abstract_html}
  </div>

  <!-- Answer -->
  <div style="padding:12px 16px;background:#f0fdf4;border-top:1px solid #bbf7d0;">
    <div style="font-size:10px;font-weight:700;color:#14532d;
                letter-spacing:1px;margin-bottom:4px;">💡 CONCLUSION / ANSWER</div>
    <div style="font-size:13px;color:#1c1917;line-height:1.7;">{answer}</div>
  </div>

</div>
"""

show(html)
print(f"Loaded: PMID {pmid} — {len(contexts)} abstract section(s), "
      f"{sum(len(c) for c in contexts)} chars total")
'''

display_cell = code(DISPLAY_CODE)

# ── 3. Segmentation cell ───────────────────────────────────────────── #
SEG_CODE = '''\
# ── Segment the abstract contexts into sentences ─────────────────────
import re
from notebook_src.visuals import show

def segment(text):
    """Split on sentence boundaries, keeping fragments ≥ 20 chars."""
    raw = re.split(r\'(?<=[.!?])\\s+\', text.strip())
    return [s.strip() for s in raw if len(s.strip()) >= 20]

segments = []
for label, ctx in zip(labels, contexts):
    for sent in segment(ctx):
        segments.append({"label": label, "text": sent})

# ── Visual display ────────────────────────────────────────────────────
LABEL_COLOURS = {
    "BACKGROUND": ("#1e40af", "#dbeafe"),
    "RESULTS":    ("#92400e", "#fef3c7"),
    "METHODS":    ("#065f46", "#d1fae5"),
    "CONCLUSIONS":("#4c1d95", "#ede9fe"),
}

rows = ""
for i, seg in enumerate(segments):
    col, bg = LABEL_COLOURS.get(seg["label"], ("#374151", "#f9fafb"))
    rows += (
        f\'<tr>\' +
        f\'<td style="padding:6px 10px;color:#94a3b8;font-size:11px;\'
        f\'font-weight:600;white-space:nowrap;vertical-align:top;">{i}</td>\' +
        f\'<td style="padding:6px 8px;vertical-align:top;">\' +
        f\'  <span style="display:inline-block;background:{col};color:#fff;\' +
        f\'  font-size:9px;font-weight:700;letter-spacing:1px;padding:1px 6px;\' +
        f\'  border-radius:3px;">{seg["label"]}</span></td>\' +
        f\'<td style="padding:6px 10px;font-size:12px;color:#1e293b;\' +
        f\'  line-height:1.6;background:{bg};border-radius:4px;">\' +
        f\'  {seg["text"]}</td>\' +
        f\'</tr>\'
    )

html = f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">
  <div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:8px;">
    📋 Segmented Abstract — {len(segments)} sentences
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:12px;">
    <thead>
      <tr style="border-bottom:2px solid #e2e8f0;">
        <th style="padding:6px 10px;text-align:left;color:#94a3b8;
                   font-size:10px;letter-spacing:1px;">#</th>
        <th style="padding:6px 8px;text-align:left;color:#94a3b8;
                   font-size:10px;letter-spacing:1px;">SECTION</th>
        <th style="padding:6px 10px;text-align:left;color:#94a3b8;
                   font-size:10px;letter-spacing:1px;">SENTENCE</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</div>
"""
show(html)
print(f"\\n{len(segments)} segments ready in `segments` list")
print("Each segment: {\'label\': ..., \'text\': ...}")
'''

seg_cell = code(SEG_CODE)

# ── Insert before Information Extraction cell ──────────────────────── #
def src(c):
    s = c["source"]
    return "".join(s) if isinstance(s, list) else s

ie_idx = next(
    i for i, c in enumerate(nb["cells"])
    if src(c).startswith("### Information Extraction")
    and c["cell_type"] == "markdown"
)

new_cells = [heading, display_cell, seg_cell]
nb["cells"] = nb["cells"][:ie_idx] + new_cells + nb["cells"][ie_idx:]

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Done — inserted 3 cells before Information Extraction (was idx {ie_idx})")
print(f"Total cells: {len(nb['cells'])}")
