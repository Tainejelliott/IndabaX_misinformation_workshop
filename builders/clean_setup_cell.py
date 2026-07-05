"""
clean_setup_cell.py
Replaces the bloated setup cell with a slim version that writes only
visuals.py. The HTML files in notebook_src/html/ come from disk (cloned
repo) — they are NOT embedded in the notebook.

Run with: .venv/bin/python builders/clean_setup_cell.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

VISUALS_PY = '''\
"""
notebook_src/visuals.py
Visual helper for the KG-RAG workshop.
HTML assets live in notebook_src/html/ — edit them there.
"""
from __future__ import annotations
import pathlib

_HERE = pathlib.Path(__file__).parent


def load_html(name: str) -> str:
    return (_HERE / "html" / name).read_text()


def show(html: str) -> None:
    from IPython.display import HTML, display
    display(HTML(html))


def concept_llm():        return load_html("concept_llm.html")
def concept_embeddings(): return load_html("concept_embeddings.html")
def concept_rag():        return load_html("concept_rag.html")
'''

NEW_SETUP = (
    '# @title Write notebook_src module { display-mode: "form" }\n'
    'import pathlib, sys\n'
    '\n'
    '# Make notebook_src importable from the repo root\n'
    'sys.path.insert(0, str(pathlib.Path.cwd()))\n'
    '\n'
    'pathlib.Path("notebook_src").mkdir(exist_ok=True)\n'
    'pathlib.Path("notebook_src/__init__.py").touch()\n'
    'pathlib.Path("notebook_src/html").mkdir(exist_ok=True)\n'
    '\n'
    'pathlib.Path("notebook_src/visuals.py").write_text(\n'
    + "'''\n"
    + VISUALS_PY
    + "'''\n"
    + ')\n'
    '\n'
    'print("\\u2705 notebook_src ready")\n'
)

# Find and replace the setup cell
idx = next(
    i for i, c in enumerate(nb["cells"])
    if "Write" in c.get("source", "") and "visuals" in c.get("source", "")
)
nb["cells"][idx]["source"] = NEW_SETUP

NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Setup cell {idx} rewritten — {len(NEW_SETUP)} chars (was {len(nb['cells'][idx]['source'])} ... wait that's the new one)")

# Verify
import nbformat
nbn = nbformat.read(str(NB), as_version=4)
nbformat.validate(nbn)
print(f"Valid — {len(nbn.cells)} cells")
print("\nSetup cell source:")
print(nbn.cells[idx].source)
