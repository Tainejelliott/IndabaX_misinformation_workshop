"""
refactor_html_files.py

Moves all inline HTML out of the notebook and visuals.py into
notebook_src/html/*.html files.  Updates the notebook setup cell to
write those files to Colab disk at runtime.

Run with: .venv/bin/python builders/refactor_html_files.py
"""
import json, pathlib, re, textwrap

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"
HTML_DIR = ROOT / "notebook_src" / "html"

nb = json.loads(NB.read_text())


# ── 1. Extract current visuals.py source from setup cell ─────────── #
setup_cell = nb["cells"][4]
assert "Write visuals module" in setup_cell["source"]

# The source is between the outer triple-quotes: src = '''...'''
raw = setup_cell["source"]
vis_src = raw.split("src = '''", 1)[1].rsplit("'''", 1)[0]


# ── 2. Parse concept_* function bodies ────────────────────────────── #
# Each looks like:
#   def concept_XXX(...):
#       ...
#       body = """..."""
#       return _wrap(body)
#
# We pull the body = """...""" string for each function.

CONCEPTS = ["concept_llm", "concept_embeddings", "concept_rag"]

# Execute visuals.py in an isolated namespace (mock IPython so no Colab needed)
import sys, types

_ipython_mock = types.ModuleType("IPython")
_display_mock  = types.ModuleType("IPython.display")
_display_mock.HTML    = lambda x: x
_display_mock.display = lambda x: None
_ipython_mock.display = _display_mock
sys.modules.setdefault("IPython",         _ipython_mock)
sys.modules.setdefault("IPython.display", _display_mock)

globs = {}
exec(vis_src, globs)

concept_html = {}
for name in CONCEPTS:
    concept_html[name] = globs[name]()
    print(f"  rendered {name}: {len(concept_html[name])} chars")


# ── 3. Extract HyDE HTML from cell 65 ─────────────────────────────── #
hyde_cell = nb["cells"][65]
assert "HyDE" in hyde_cell["source"] or "hyde" in hyde_cell["source"].lower()

hyde_raw = hyde_cell["source"]
# Content is between show(''' and ''')
hyde_html = hyde_raw.split("show('''", 1)[1].rsplit("''')", 1)[0]
print(f"  extracted hyde: {len(hyde_html)} chars")


# ── 4. Write HTML files locally ───────────────────────────────────── #
HTML_DIR.mkdir(parents=True, exist_ok=True)

files = {
    "concept_llm.html":        concept_html["concept_llm"],
    "concept_embeddings.html": concept_html["concept_embeddings"],
    "concept_rag.html":        concept_html["concept_rag"],
    "hyde.html":               hyde_html,
}

for fname, content in files.items():
    (HTML_DIR / fname).write_text(content)
    print(f"  wrote notebook_src/html/{fname}")


# ── 5. Build updated visuals.py source ────────────────────────────── #
# The concept_* functions rendered static HTML at build time.
# The new visuals.py simply loads those HTML files from disk.

NEW_VISUALS = (
    '"""\n'
    'notebook_src/visuals.py\n'
    'Colab-safe visual components for the KG-RAG workshop.\n'
    'HTML is stored in notebook_src/html/ — edit files there, not here.\n'
    '"""\n'
    'from __future__ import annotations\n'
    'import pathlib\n'
    '\n'
    '_HERE = pathlib.Path(__file__).parent\n'
    '\n'
    '\n'
    'def load_html(name: str) -> str:\n'
    '    return (_HERE / "html" / name).read_text()\n'
    '\n'
    '\n'
    'def show(html: str) -> None:\n'
    '    from IPython.display import HTML, display\n'
    '    display(HTML(html))\n'
    '\n'
    '\n'
    'def concept_llm():        return load_html("concept_llm.html")\n'
    'def concept_embeddings(): return load_html("concept_embeddings.html")\n'
    'def concept_rag():        return load_html("concept_rag.html")\n'
)


# ── 6. Build the new setup cell source ────────────────────────────── #
# The cell must write visuals.py AND all HTML files to Colab disk.

def py_str(s):
    """Wrap s as a Python triple-quoted raw string literal."""
    # Escape any ''' that appears inside s
    safe = s.replace("'''", "'\\''\\''\\'")
    return "r'''" + safe + "'''"

lines = [
    "# @title Write notebook_src module { display-mode: \"form\" }",
    "import pathlib",
    "pathlib.Path('notebook_src').mkdir(exist_ok=True)",
    "pathlib.Path('notebook_src/__init__.py').touch()",
    "pathlib.Path('notebook_src/html').mkdir(exist_ok=True)",
    "",
    "# ── visuals.py ─────────────────────────────────────────────────",
    f"pathlib.Path('notebook_src/visuals.py').write_text({py_str(NEW_VISUALS)})",
    "",
    "# ── HTML files ─────────────────────────────────────────────────",
]
for fname, content in files.items():
    lines.append(
        f"pathlib.Path('notebook_src/html/{fname}').write_text({py_str(content)})"
    )

lines += [
    "",
    "print('✅ notebook_src ready')",
]

new_setup_src = "\n".join(lines)


# ── 7. Update cells in notebook ───────────────────────────────────── #
setup_cell["source"] = new_setup_src

# Update HyDE cell to use load_html
hyde_cell["source"] = (
    "from notebook_src.visuals import show, load_html\n\n"
    "show(load_html('hyde.html'))"
)


NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"\nDone — {len(nb['cells'])} cells, setup cell {len(new_setup_src)} chars")
