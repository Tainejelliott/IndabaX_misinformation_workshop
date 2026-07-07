
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

def llm_prediction_pipeline():       return load_html("llm_prediction_pipeline.html")
def rag_pipeline_overview():         return load_html("rag_pipeline_overview.html")

def embedding_space_explorer():      return load_html("embedding_space_explorer.html")
def embeddings_llm_relationship():   return load_html("embeddings_llm_relationship.html")
def knowledge_graph_deep_dive():     return load_html("knowledge_graph_deep_dive.html")
def semantic_search_depth_explorer(): return load_html("semantic_search_depth_explorer.html")

def information_extraction_methods(): return load_html("information_extraction_methods.html")

def knowledge_representation_spectrum(): return load_html("knowledge_representation_spectrum.html")

def information_retrieval_methods(): return load_html("information_retrieval_methods.html")

def augmented_generation_methods(): return load_html("augmented_generation_methods.html")

def generation_reasoning_strategies(): return load_html("generation_reasoning_strategies.html")
