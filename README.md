# IndabaX 2026 — Knowledge Graph RAG for Misinformation

A hands-on workshop notebook for the **IndabaX 2026** conference. Attendees go
from raw biomedical text to a typed, queryable knowledge graph, then use it to
reason — finishing by cracking a murder mystery with a KG-RAG detective.

---

## Workshop structure

| Part | Notebook | Description |
|------|----------|-------------|
| 1 | `1 - Introduction.ipynb` | LLMs, embeddings and RAG — the three core concepts |
| 2 | `2 - RAG Components & Misinformation.ipynb` | How RAG guards against misinformation |
| A.1 | `3 - Hands-on A1 (Beginner).ipynb` | Knowledge representation pipeline — concepts |
| A.2 | `4 - Hands-on A2 (Intermediate).ipynb` | Build a real KG from a PubMedQA abstract |
| B | `5 - Hands-on B.ipynb` | Use the graph — murder mystery KG-RAG |
| Combined | `NdabaX 2026 KG-RAG Workshop.ipynb` | **All parts in one notebook** (Colab deliverable) |

The combined notebook is the one attendees open on Google Colab.
Link to Setup and API Key : https://docs.google.com/document/d/1p-yaU-OKJpxpYteMhDVr_6w0oWTC9qwiBs0qFTgPgjQ/edit?usp=sharing

---

## Local setup

### 1. Clone & enter the repo

```bash
git clone https://github.com/Tainejelliott/IndabaX_misinformation_workshop.git
cd IndabaX_misinformation_workshop
```

### 2. Create a Python virtual environment

Requires **Python 3.11+**.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install datasets openai python-dotenv spacy pyvis networkx \
            "sentence-transformers>=3.0" matplotlib scipy
python -m spacy download en_core_web_sm
```

### 4. Add your OpenAI API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
```

This file is gitignored — it never gets committed.

### 5. Run a notebook

Open the individual section you're working on in VS Code or JupyterLab.
Only **Part A.2** and **Part B** call the OpenAI API.

---

## Developing your section (Part 2)

The `2 - RAG Components & Misinformation.ipynb` notebook is your section — it currently has an amber TODO placeholder. Replace it with your content.

**Rules of the repo:**
- All HTML visualisations live in `notebook_src/html/` and are loaded via
  `notebook_src/visuals.load_html(name)`. Never paste raw HTML into a notebook cell.
- All reusable Python helpers go into `notebook_src/` (e.g. add a render function
  to `display.py`). Notebook cells stay thin — one import + one call.
- After editing any `notebook_src/` module, delete `notebook_src/__pycache__/`
  to avoid stale `.pyc` bites.

**Display helpers available to you:**

```python
from notebook_src.visuals import show, load_html
from notebook_src.display import render_points_card, render_rag_components, render_vector_vs_graph
```

`render_points_card(kicker, title, subtitle, points, grad)` — a styled bullet-point card.  
`render_rag_components()` — ready-made card explaining the four RAG guard-rails.  
`show(html_string)` — renders any HTML string safely inside a notebook cell.

---

## Google Colab (attendee delivery)

1. Upload `NdabaX_KG_Workshop.zip` to the Colab session (`Files` panel → drag & drop).
2. In a cell, run:
   ```python
   !unzip -o -q NdabaX_KG_Workshop.zip
   ```
3. Open `NdabaX 2026 KG-RAG Workshop.ipynb` and paste the OpenAI key into the
   **Setup** cell (`OPENAI_API_KEY = "sk-..."`). Delete it after the session.
4. Runtime → Run all.

To rebuild the zip after changes:

```bash
cd "/path/to/collab notebook"
zip -r NdabaX_KG_Workshop.zip \
    "NdabaX 2026 KG-RAG Workshop.ipynb" \
    notebook_src/ \
    --exclude "notebook_src/__pycache__/*" \
    --exclude "*.pyc" \
    --exclude ".env"
```

---

## Project layout

```
.
├── notebook_src/           # Shared Python package (imported by all notebooks)
│   ├── display.py          # All render_*() visual helpers
│   ├── extraction.py       # OBIE + OpenIE triple extraction (OpenAI + BioLORD)
│   ├── graph.py            # Canonicalisation, build_graph, queries, Cypher export
│   ├── mystery.py          # Hands-on B murder mystery case data + retrieval/solve
│   ├── validation.py       # Back-translation, cosine, STS-B calibration
│   ├── visuals.py          # show(), load_html()
│   └── html/               # Static HTML assets (concept cards, HyDE explainer)
├── builders/               # One-off scripts that edit .ipynb JSON programmatically
├── 1 - Introduction.ipynb
├── 2 - RAG Components & Misinformation.ipynb
├── 3 - Hands-on A1 (Beginner).ipynb
├── 4 - Hands-on A2 (Intermediate).ipynb
├── 5 - Hands-on B.ipynb
└── NdabaX 2026 KG-RAG Workshop.ipynb   ← combined Colab deliverable
```

---

## Key technical choices

| Component | Choice | Reason |
|-----------|--------|--------|
| LLM | `gpt-4.1-nano` (OpenAI) | Fast, cheap, structured JSON output via Pydantic |
| OBIE extraction | MeSH-constrained structured JSON | Precision over PubMedQA concepts |
| OpenIE extraction | Schema-free + inline type guessing | High recall, ontology-aware tooltips |
| Entity grounding | BioLORD-2023-C embeddings (cosine ≥ 0.8) | Biomedical ontology alignment |
| Graph rendering | pyvis/vis.js wrapped in `<iframe srcdoc>` | Scripts execute even inside Jupyter cells |
| Validation | all-MiniLM-L6-v2 + STS-B calibration | Gives a cosine score an interpretable meaning |
| Dataset | PubMedQA (`pqa_labeled`, PMID 21645374) | Real biomedical text with MeSH annotations |
