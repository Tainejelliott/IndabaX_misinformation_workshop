
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
    import warnings
    from IPython.display import HTML, display
    # Our interactive graphs embed an <iframe srcdoc="…"> on purpose; silence
    # IPython's "Consider using IPython.display.IFrame instead" suggestion.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*IFrame.*")
        display(HTML(html))


def concept_llm():        return load_html("concept_llm.html")
def concept_embeddings(): return load_html("concept_embeddings.html")
def concept_rag():        return load_html("concept_rag.html")
