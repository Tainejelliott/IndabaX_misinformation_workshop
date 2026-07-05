"""
clean_kb_setup_cells.py
1. Embeds notebook_src/display.py into the hidden setup cell.
2. Replaces the two verbose KB-setup code cells with clean one-liners.
Run with: .venv/bin/python builders/clean_kb_setup_cells.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

def src(c):
    s = c["source"]
    return "".join(s) if isinstance(s, list) else s


# ── 1. Read display.py from disk ───────────────────────────────────── #
display_py = (ROOT / "notebook_src" / "display.py").read_text()


# ── 2. Inject into the hidden setup cell ──────────────────────────── #
setup_idx = next(
    i for i, c in enumerate(nb["cells"])
    if "Write notebook_src module" in src(c)
)

old_setup = src(nb["cells"][setup_idx])

# Insert display.py write call just before the reload block
display_write = (
    "\n# ── display.py ────────────────────────────────────────────────\n"
    f"pathlib.Path(\"notebook_src/display.py\").write_text('''\n{display_py}\n''')\n"
)

old_setup = old_setup.replace(
    "\n# Reload if already imported",
    display_write + "\n# Reload if already imported"
)

# Also reload display module if already imported
old_setup = old_setup.replace(
    'if "notebook_src.visuals" in _sys.modules:\n'
    '    importlib.reload(_sys.modules["notebook_src.visuals"])',
    'if "notebook_src.visuals" in _sys.modules:\n'
    '    importlib.reload(_sys.modules["notebook_src.visuals"])\n'
    'if "notebook_src.display" in _sys.modules:\n'
    '    importlib.reload(_sys.modules["notebook_src.display"])'
)

nb["cells"][setup_idx]["source"] = old_setup


# ── 3. Replace the two verbose KB-setup code cells ────────────────── #
LOAD_MARKER = "# ── Load PubMedQA and display the first abstract"
SEG_MARKER  = "# ── Segment the abstract contexts into sentences"

CLEAN_LOAD = """\
from datasets import load_dataset
from notebook_src.visuals import show
from notebook_src.display import render_abstract

ds  = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split="train",
                   trust_remote_code=True)
ex  = ds[0]

# Metadata (title / authors fetched from NCBI for PMID 21645374)
TITLE   = "Do mitochondria play a role in remodelling lace plant leaves during programmed cell death?"
AUTHORS = "Lord CEN, Wertman JN, Lane S, Gunawardena AHLAN"
JOURNAL = "BMC Plant Biology"
YEAR    = "2011"

# Expose raw fields for downstream cells
question = ex["question"]
contexts = ex["context"]["contexts"]
labels   = ex["context"]["labels"]

show(render_abstract(ex, TITLE, AUTHORS, JOURNAL, YEAR))
print(f"Loaded PMID {ex['pubid']} — {len(contexts)} section(s), "
      f"{sum(len(c) for c in contexts)} chars")
"""

CLEAN_SEG = """\
import re
from notebook_src.visuals import show
from notebook_src.display import render_segments

def segment(text):
    raw = re.split(r'(?<=[.!?])\\s+', text.strip())
    return [s.strip() for s in raw if len(s.strip()) >= 20]

segments = [
    {"label": label, "text": sent}
    for label, ctx in zip(labels, contexts)
    for sent in segment(ctx)
]

show(render_segments(segments))
print(f"{len(segments)} segments ready in `segments`")
"""

for i, c in enumerate(nb["cells"]):
    s = src(c)
    if s.startswith(LOAD_MARKER):
        nb["cells"][i]["source"] = CLEAN_LOAD
    elif s.startswith(SEG_MARKER):
        nb["cells"][i]["source"] = CLEAN_SEG


# ── 4. Save ────────────────────────────────────────────────────────── #
NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))

import nbformat
nbn = nbformat.read(str(NB), as_version=4)
nbformat.validate(nbn)
print(f"Valid — {len(nbn.cells)} cells")

# Verify cleanliness of the two cells
for c in nbn.cells:
    if "render_abstract" in c.source or "render_segments" in c.source:
        print(f"\n--- {c.source.splitlines()[0]} ---")
        print(c.source)
