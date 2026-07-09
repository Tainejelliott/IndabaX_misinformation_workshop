# IndabaX 2026 — Knowledge Graph RAG for Misinformation

A hands-on workshop for the **IndabaX 2026** conference. Attendees start from
first principles (LLMs, embeddings, RAG), build a real knowledge graph from
biomedical text, design their own extraction ontology, and finish reasoning
over a knowledge graph with an LLM agent — including seeing what happens when
misinformation is injected into it.

---

## Workshop structure

| # | Notebook | What it covers |
|---|----------|-----------------|
| 1 | `1 - Introduction (Interactive).ipynb` | LLMs, embeddings, knowledge bases, extraction, retrieval, and augmented generation — each concept immediately followed by real, runnable code (not just a slide). Builds a minimal RAG pipeline twice on a small myth-busting corpus: once over a vector store (ChromaDB), once over a knowledge graph, specifically to show a question the vector store structurally can't answer but the graph can. |
| 2 | `2 - Case Study: PubMed Q&A.ipynb` | *("Case Study — Proposition Pipeline")* — a research-style KG pipeline over a real PubMedQA abstract: proposition chunking, OpenIE vs. ontology-based (OBIE) triple extraction, round-trip back-translation validation, coreference resolution, entity mapping across synonyms, and assembling the final knowledge graph — then a preview of applying the same pipeline to a murder-mystery case. |
| 3 | `3 - Hands-on Ontology.ipynb` | *("Hands-on B — Knowledge Base Utilisation")* — attendees design their **own** extraction ontology for a case file, run extraction against it, build and evaluate their graph, then watch (and drive) an OpenAI function-calling agent investigate and solve the case by querying the graph — finishing with a misinformation-injection exercise to see how a corrupted graph changes the agent's conclusion. |

Each notebook is self-contained and can be run independently; `notebook_src/`
is the shared Python package all three import from.

Step-by-step setup and API key walkthrough (Google Doc): https://docs.google.com/document/d/1p-yaU-OKJpxpYteMhDVr_6w0oWTC9qwiBs0qFTgPgjQ/edit?usp=sharing

---

## Local setup

### 1. Clone & enter the repo

```bash
git clone https://github.com/Tainejelliott/IndabaX_misinformation_workshop.git
cd IndabaX_misinformation_workshop
```

### 2. Create a Python virtual environment

Requires **Python 3.10+**.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -U datasets openai python-dotenv spacy \
    "sentence-transformers>=3.0" chromadb==1.5.9 \
    networkx "pyvis>=0.3.2" matplotlib scipy Pillow
python -m spacy download en_core_web_sm
```

`-U` matters for `Pillow` and `datasets` specifically — stale versions of
either are a common source of a misleading "sentence_transformers is not
installed" error the first time an embedding model loads (see the Setup cell
comment in Notebook 1 for the full explanation).

### 4. Add your OpenAI API key

Copy `.env.example` to `.env` and fill in your key:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-...
```

This file is gitignored — it never gets committed. Every notebook falls back
to printing the prompt it *would* have sent if no key is set, so all three
still run end to end without one.

### 5. Run a notebook

Open any of the three notebooks in VS Code or JupyterLab and run top to
bottom. Notebook 1 has a light dense-vector RAG demo before its knowledge-graph
half; Notebooks 2 and 3 call the OpenAI API more heavily (triple extraction,
validation, and the graph agent).

---

## Google Colab

Each notebook's **Setup** section locates `notebook_src/` automatically,
whether it's sitting next to the notebook already or one level down (e.g.
after a `git clone`). Two ways to get it into a Colab session:

- **Git clone (Notebook 1 has a ready-made cell for this):**
  ```python
  !git clone https://github.com/Tainejelliott/IndabaX_misinformation_workshop.git
  import os; os.chdir("IndabaX_misinformation_workshop")
  ```
- **Google Drive:** upload/sync the repo folder to your Drive, mount it, and
  `os.chdir` into it — see the (commented-out) Drive cells near the top of
  each notebook.

Then paste your key into the **Setup** cell's `OPENAI_API_KEY = "sk-..."`
field (delete it again after the session) or rely on a `.env` file, and
Runtime → Run all.

---

## Visual library website

All sixteen interactive visuals in `notebook_src/html/` are also browsable as
a standalone website — useful for skimming the whole workshop without
opening any notebook, or for presenting a visual full-screen.

```bash
cd website
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000/**. It's a small Flask app (`website/app.py`)
with one route per visual (`/visual/<slug>`), grouped and linked from an index
page; each route just reads the matching file straight out of
`notebook_src/html/` and drops it into a shared header/sidebar layout, so the
site always reflects whatever's currently in that folder.

---

## Project layout

```
.
├── notebook_src/                # Shared Python package (imported by all notebooks)
│   ├── visuals.py                # show(), load_html() — renders the interactive HTML visuals
│   ├── display.py                # All render_*() visual/card helpers
│   ├── extraction.py             # OBIE + OpenIE triple extraction (OpenAI + BioLORD grounding)
│   ├── graph.py                  # Canonicalisation, build_graph, graph queries, Cypher export
│   ├── graph_agent.py            # OpenAI function-calling agent that queries a graph
│   ├── validation.py             # Back-translation, cosine similarity, STS-B calibration
│   ├── mystery.py                # Hands-on B murder-mystery case data
│   ├── pancreatic.py             # Case Study pancreatic-cancer teaching corpus + ontology
│   └── html/                     # Static HTML assets for every interactive visual
├── website/                      # Flask app that browses notebook_src/html/ as one site
│   ├── app.py
│   ├── templates/
│   └── static/style.css
├── builders/                     # One-off scripts that edit .ipynb JSON programmatically
├── 1 - Introduction (Interactive).ipynb
├── 2 - Case Study: PubMed Q&A.ipynb
├── 3 - Hands-on Ontology.ipynb
├── REFERENCES.md                 # Citations for every factual claim/technique used in the visuals
├── .env.example                  # Copy to .env and fill in your OpenAI key
└── README.md
```

### Rules of the repo

- All HTML visualisations live in `notebook_src/html/` and are loaded via
  `notebook_src/visuals.load_html(name)`. Never paste raw HTML into a notebook
  cell.
- Reusable Python helpers go into `notebook_src/` — notebook cells stay thin:
  one import, one call.
- After editing any `notebook_src/` module, delete
  `notebook_src/__pycache__/` if you hit stale-`.pyc` behaviour.
- Every factual/technical claim inside a visual should have a citation in
  `REFERENCES.md`, checked against a live source rather than pulled from
  memory — the workshop is about misinformation, so its own material holds to
  that bar too.

---

## Key technical choices

| Component | Choice | Reason |
|-----------|--------|--------|
| LLM | `gpt-4.1-nano` / `gpt-4o-mini` (OpenAI) | Fast, cheap, structured JSON output via Pydantic |
| Vector store (Notebook 1) | ChromaDB, in-memory client | Minimal setup for a first RAG pipeline; swappable embedding model (small/medium/large/custom) |
| OBIE extraction | Ontology-constrained structured JSON | Precision over a defined schema (MeSH for PubMedQA) |
| OpenIE extraction | Schema-free + inline type guessing | High recall; entities/relations named however the text implies |
| Entity grounding | BioLORD-2023-C embeddings (cosine ≥ 0.8) | Biomedical ontology alignment for synonym bridging |
| Graph rendering | pyvis/vis.js wrapped in `<iframe srcdoc>` | Scripts execute even when injected via `display(HTML(...))` in Jupyter |
| Validation | Back-translation + STS-B calibration | Gives a raw cosine score an interpretable meaning |
| Graph agent | OpenAI function calling over graph-query tools | Grounds multi-hop reasoning in explicit tool calls, not free-form recall |
| Dataset (Notebook 2) | PubMedQA (`pqa_labeled`) | Real biomedical text with MeSH annotations |
