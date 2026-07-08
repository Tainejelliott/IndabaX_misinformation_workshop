"""
builders/add_a2_roadmap.py
Insert an opening roadmap card into '4 - Hands-on A2 (Intermediate).ipynb',
mirroring how Hands-on B opens with render_mystery_roadmap(). The roadmap is a
pure-display cell (no API), so its output is pre-rendered here to keep A.2's
"reference notebook with outputs" intact. Idempotent — safe to re-run.

Run: .venv/bin/python builders/add_a2_roadmap.py
"""
import json, uuid, sys, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "4 - Hands-on A2 (Intermediate).ipynb"
sys.path.insert(0, str(ROOT))
from notebook_src.display import render_a2_roadmap

nb    = json.loads(NB.read_text())
cells = nb["cells"]

def src_of(c):
    return "".join(c["source"]) if isinstance(c["source"], list) else c["source"]

body = {
    "cell_type": "code",
    "metadata": {},
    "execution_count": None,
    "source": [
        "# What this hands-on covers, end to end\n",
        "from notebook_src.visuals import show\n",
        "from notebook_src.display import render_a2_roadmap\n",
        "show(render_a2_roadmap())",
    ],
    "outputs": [{
        "output_type": "display_data",
        "data": {
            "text/html": [render_a2_roadmap()],
            "text/plain": ["<IPython.core.display.HTML object>"],
        },
        "metadata": {},
    }],
}

existing = next((i for i, c in enumerate(cells) if "render_a2_roadmap" in src_of(c)), None)
if existing is not None:
    cells[existing] = {**cells[existing], **body}     # refresh source + output, keep id
    msg = f"Refreshed roadmap at cell index {existing}"
else:
    # Insert right after the setup form cell (it puts notebook_src on sys.path).
    setup_idx = next((i for i, c in enumerate(cells)
                      if c["cell_type"] == "code" and "@title Setup" in src_of(c)), None)
    insert_at = (setup_idx + 1) if setup_idx is not None else 2
    cells.insert(insert_at, {"id": uuid.uuid4().hex[:8], **body})
    msg = f"Inserted roadmap at cell index {insert_at}"

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
import nbformat
nbformat.validate(nbformat.read(str(NB), as_version=4))
print(f"{msg} — {len(cells)} cells total")
