"""
website/app.py
A small Flask app that combines every interactive HTML visual from
notebook_src/html/ into one navigable website.

Each visual is a self-contained HTML fragment (inline <style>/<script>, no
external assets) designed to be dropped into a page body — exactly what this
app does, one visual per route, wrapped in a shared header/sidebar layout.

Run with:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000/
"""
from pathlib import Path

from flask import Flask, abort, render_template

HTML_DIR = Path(__file__).resolve().parent.parent / "notebook_src" / "html"

# Every visual, grouped to match the order concepts appear in the workshop.
SECTIONS = [
    {
        "name": "Foundations",
        "visuals": [
            {"slug": "what-is-rag", "file": "concept_rag.html",
             "title": "What is RAG?",
             "blurb": "The Retrieve → Augment → Generate loop, as a static concept card."},
            {"slug": "rag-pipeline", "file": "rag_pipeline_overview.html",
             "title": "The RAG Pipeline",
             "blurb": "Animated walkthrough of the offline indexing and online query phases."},
            {"slug": "what-is-an-llm", "file": "concept_llm.html",
             "title": "What is an LLM?",
             "blurb": "Next-token prediction, as a static concept card."},
            {"slug": "llm-prediction-pipeline", "file": "llm_prediction_pipeline.html",
             "title": "The Prediction Pipeline",
             "blurb": "Animated token-by-token generation loop."},
            {"slug": "what-are-embeddings", "file": "concept_embeddings.html",
             "title": "What are Embeddings?",
             "blurb": "Semantic similarity as geometry, as a static concept card."},
            {"slug": "embedding-space-explorer", "file": "embedding_space_explorer.html",
             "title": "Exploring Embedding Space",
             "blurb": "Clustering, vector arithmetic, cosine similarity, and contextual (dynamic) vectors."},
            {"slug": "embeddings-llm-relationship", "file": "embeddings_llm_relationship.html",
             "title": "How Embeddings Power the RAG Pipeline",
             "blurb": "Where embeddings sit in the pipeline, cross-model spaces, and what breaks."},
            {"slug": "knowledge-bases", "file": "knowledge_graph_deep_dive.html",
             "title": "Four Ways to Store What You Know",
             "blurb": "Graph, vector, relational, and document stores, side by side."},
            {"slug": "knowledge-representation-spectrum", "file": "knowledge_representation_spectrum.html",
             "title": "From Prose to Predicates",
             "blurb": "The spectrum from free text to formal triples, and how to choose a representation."},
        ],
    },
    {
        "name": "Extraction & Validation",
        "visuals": [
            {"slug": "information-extraction", "file": "information_extraction_methods.html",
             "title": "Turning Raw Sources Into a RAG Datastore",
             "blurb": "Extraction pipeline, chunking, ontology vs. open extraction, disambiguation, and common pitfalls."},
            {"slug": "extraction-validation", "file": "extraction_validation_methods.html",
             "title": "Validating & Verifying Extracted Information",
             "blurb": "Schema checks, source grounding, round-trip validation, cross-run consistency, and contradiction detection."},
        ],
    },
    {
        "name": "Retrieval",
        "visuals": [
            {"slug": "information-retrieval", "file": "information_retrieval_methods.html",
             "title": "Getting the Right Chunk",
             "blurb": "Sparse vs. dense retrieval, hybrid fusion, graph traversal, re-ranking, and query transformation."},
            {"slug": "semantic-search-depth", "file": "semantic_search_depth_explorer.html",
             "title": "Search Quality & Model Depth",
             "blurb": "How embedding model depth trades off against retrieval quality."},
            {"slug": "hyde", "file": "hyde.html",
             "title": "HyDE: Hypothetical Document Embeddings",
             "blurb": "Query transformation via a hypothetical answer, and its reverse variant."},
        ],
    },
    {
        "name": "Generation",
        "visuals": [
            {"slug": "augmented-generation", "file": "augmented_generation_methods.html",
             "title": "From Retrieved Chunks to a Trustworthy Answer",
             "blurb": "The U-curve, grounding & citation, conflicting evidence, faithfulness checks, and prompting strategies."},
            {"slug": "generation-reasoning-strategies", "file": "generation_reasoning_strategies.html",
             "title": "Beyond a Single Pass: Reasoning & Re-Ranking Strategies",
             "blurb": "Re-ranking revisited, Chain/Tree of Thought, Self-Consistency, Chain-of-Verification, and ReAct."},
        ],
    },
]

# Flat list (in section order) for slug lookup and prev/next navigation.
_ALL = [v for section in SECTIONS for v in section["visuals"]]
_BY_SLUG = {v["slug"]: v for v in _ALL}
_SECTION_OF = {v["slug"]: s["name"] for s in SECTIONS for v in s["visuals"]}

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", sections=SECTIONS, current_slug=None)


@app.route("/visual/<slug>")
def visual(slug):
    v = _BY_SLUG.get(slug)
    if v is None:
        abort(404)

    content = (HTML_DIR / v["file"]).read_text()
    idx = _ALL.index(v)
    prev_v = _ALL[idx - 1] if idx > 0 else None
    next_v = _ALL[idx + 1] if idx < len(_ALL) - 1 else None

    return render_template(
        "visual.html",
        sections=SECTIONS,
        current_slug=slug,
        visual=v,
        content=content,
        section_name=_SECTION_OF[slug],
        prev_v=prev_v,
        next_v=next_v,
    )


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html", sections=SECTIONS, current_slug=None), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
