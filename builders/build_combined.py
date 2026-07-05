"""
builders/build_combined.py
Assemble ONE combined workshop notebook from the shared modules + the finished
A.2 cells, filling in RAG Components, A.1 and the Hands-on B murder mystery.
Run:  .venv/bin/python builders/build_combined.py
"""
import json, uuid, pathlib

ROOT = pathlib.Path(__file__).parent.parent
OUT  = ROOT / "NdabaX 2026 KG-RAG Workshop.ipynb"


def src(c):
    s = c["source"]; return "".join(s) if isinstance(s, list) else s

def md(s):   return {"cell_type": "markdown", "id": uuid.uuid4().hex[:8], "metadata": {}, "source": s}
def code(s): return {"cell_type": "code", "id": uuid.uuid4().hex[:8], "metadata": {},
                     "source": s, "outputs": [], "execution_count": None}

def fresh(cell):
    import copy
    c = copy.deepcopy(cell); c["id"] = uuid.uuid4().hex[:8]
    if c["cell_type"] == "code":
        c["outputs"] = []; c["execution_count"] = None
    return c


def banner(title, subtitle, grad):
    return md(
f"""## {title}

<div style="background:linear-gradient({grad});border-radius:12px;padding:18px 22px;margin:10px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="color:#fff;font-size:20px;font-weight:800;">{title}</div>
  <div style="color:rgba(255,255,255,.85);font-size:13px;margin-top:3px;">{subtitle}</div>
</div>""")


def sub(hashes, indent, border, bg, icon, name, desc, fs=14):
    return md(
f"""{hashes} {name}

<div style="margin-left:{indent}px;border-left:{4 if hashes=='###' else 3}px solid {border};background:{bg};border-radius:0 10px 10px 0;padding:13px 18px;margin-top:4px;margin-bottom:10px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="font-size:{fs}px;font-weight:700;color:#0f172a;">{icon} &nbsp;{name}</div>
  <div style="font-size:12px;color:#475569;margin-top:3px;line-height:1.5">{desc}</div>
</div>""")


# ── load source notebooks for intro + A.2 cells ───────────────────────── #
nb1 = json.loads((ROOT / "1 - Introduction.ipynb").read_text())
nb4 = json.loads((ROOT / "4 - Hands-on A2 (Intermediate).ipynb").read_text())
META = nb4.get("metadata", {})

cells = []

# ── title + setup ─────────────────────────────────────────────────────── #
cells.append(md(
"""# 🧠 Knowledge Graph RAG for Misinformation
### NdabaX 2026 — Hands-on Workshop

Welcome! Over the next hour you'll go from raw text to a **typed, queryable
knowledge graph**, then use it to reason — finishing by cracking a murder mystery
with a KG-RAG detective. Run every cell top-to-bottom.

**Roadmap:** Introduction → RAG & Misinformation → **A.1** Knowledge Representation →
**A.2** Build a Knowledge Base → **B** Use the Graph (murder mystery)."""))

cells.append(md("## Setup"))
cells.append(code(
'''# @title Install dependencies { display-mode: "form" }
import sys, subprocess
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "datasets", "openai", "python-dotenv", "spacy", "pyvis>=0.3.2", "networkx",
    "sentence-transformers>=3.0", "matplotlib", "scipy"], check=True)
subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm", "-q"], check=True)
print("✅ packages ready")'''))
cells.append(code(
'''# @title Setup { display-mode: "form" }
import sys, os, pathlib

# Locate notebook_src/ whether it sits in the current folder (local, or after
# unzipping into /content) or one level down (e.g. after `git clone`).
_root = pathlib.Path.cwd()
if not (_root / "notebook_src").exists():
    for _p in sorted(_root.glob("*/notebook_src")):
        _root = _p.parent
        break
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# ── API key ──────────────────────────────────────────────────────────────
# Paste your OpenAI key between the quotes for the demo, then DELETE it after.
# Leave blank to fall back to a local .env file.
OPENAI_API_KEY = ""
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

print("✅ notebook_src ready —", _root)'''))

# ── Part 1 · Introduction (concept cards from nb1) ────────────────────── #
cells.append(banner("Part 1 · Introduction",
                    "The three ideas behind KG-RAG: LLMs, embeddings and retrieval",
                    "135deg,#1e3a8a,#3b82f6"))
for c in nb1["cells"][3:9]:      # ### LLMs / Embeddings / RAG + their code
    cells.append(fresh(c))

# ── Part 2 · RAG Components & Misinformation ──────────────────────────── #
cells.append(banner("Part 2 · RAG Components & Misinformation",
                    "How retrieval-augmented generation keeps answers honest",
                    "135deg,#c2410c,#f97316"))
cells.append(code(
'''from notebook_src.visuals import show
from notebook_src.display import render_rag_components

# A large language model alone answers from fuzzy memory — and will confidently
# invent facts. RAG bolts on a retriever + a knowledge base so answers stay
# grounded, current and citable. Each component is a guard-rail.
show(render_rag_components())'''))

# ── Part 3 · Hands-on A.1 (Beginner) ──────────────────────────────────── #
cells.append(banner("Hands-on A.1 · Knowledge Representation (Beginner)",
                    "The pipeline from raw data to a knowledge base — the concepts",
                    "135deg,#1e40af,#2563eb"))
A1 = "#2563eb"; A1BG = "#eff6ff"
cells.append(sub("###", 0, A1, A1BG, "📂", "Data Source",
                 "Identifying, collecting and citing raw information sources"))
cells.append(code(
'''from notebook_src.visuals import show
from notebook_src.display import render_points_card
show(render_points_card("A.1 · Step 1", "Data Source",
    "Where does the knowledge come from?", [
    "Facts live as <b>text</b>: papers, reports, databases, transcripts, web pages.",
    "Prefer <b>authoritative, citable</b> sources — provenance is what makes a KB trustworthy.",
    "Our running example (A.2) uses <b>PubMedQA</b>: real biomedical abstracts with expert Q&A labels.",
]))'''))
cells.append(sub("###", 0, A1, A1BG, "🔬", "Data / Information Analysis",
                 "Understanding what is actually in the data before extracting"))
cells.append(code(
'''from notebook_src.display import render_points_card
show(render_points_card("A.1 · Step 2", "Data / Information Analysis",
    "Know your data before you mine it", [
    "What entities and relationships actually appear? What questions should the KB answer?",
    "Assess <b>quality, coverage and ambiguity</b> — messy input yields a messy graph.",
    "Decide <b>scope</b>: which facts matter, which are noise.",
]))'''))
cells.append(sub("###", 0, A1, A1BG, "⚙️", "Data Processing",
                 "Turning raw documents into clean, machine-readable units"))
cells.append(code(
'''from notebook_src.display import render_points_card
show(render_points_card("A.1 · Step 3", "Data Processing",
    "From messy documents to clean units", [
    "Normalise, segment and structure the text so it can be extracted from reliably.",
    "Two sub-steps follow: <b>pre-processing</b> and <b>dataset creation</b>.",
]))'''))
cells.append(sub("####", 24, "#3b82f6", "#f0f7ff", "🧹", "Data Pre-processing",
                 "Sentence splitting, normalisation, coreference & abbreviation resolution"))
cells.append(code(
'''from notebook_src.display import render_points_card
show(render_points_card("A.1 · Step 3a", "Data Pre-processing",
    "Clean the raw text", [
    "Sentence splitting, tokenisation, normalising case & whitespace.",
    "Coreference & abbreviation resolution — “it”, “PCD” → the entity they name.",
    "You'll see this pay off in A.2's <b>entity disambiguation</b> step.",
], grad="135deg,#2563eb,#3b82f6"))'''))
cells.append(sub("####", 24, "#3b82f6", "#f0f7ff", "🗂️", "Dataset Creation",
                 "Assembling the exact corpus you will extract from"))
cells.append(code(
'''from notebook_src.display import render_points_card
show(render_points_card("A.1 · Step 3b", "Dataset Creation",
    "Assemble the working corpus", [
    "Select the precise passages the KB will be built from.",
    "Pick the store that fits your access pattern → <b>Vector DB vs Graph DB</b> (next).",
], grad="135deg,#2563eb,#3b82f6"))'''))
cells.append(sub("#####", 48, "#1d4ed8", "#eaf2ff", "🔵🟣", "Vector DB vs Graph DB",
                 "Two stores for two jobs — similarity search vs relationship traversal"))
cells.append(code(
'''from notebook_src.display import render_vector_vs_graph
show(render_vector_vs_graph())'''))
cells.append(sub("###", 0, A1, A1BG, "🎯", "Task Evaluation Set",
                 "Held-out questions that measure whether the KB actually works"))
cells.append(code(
'''from notebook_src.display import render_points_card
show(render_points_card("A.1 · Step 4", "Task Evaluation Set",
    "How will you know the KB is any good?", [
    "Hold out <b>question–answer pairs</b> the KB should be able to answer.",
    "Measure retrieval quality (recall@k) and answer <b>faithfulness</b> objectively.",
    "In A.2 we even calibrate <b>what a similarity score means</b> using the STS-B benchmark.",
]))'''))
cells.append(sub("###", 0, A1, A1BG, "🏗️", "Knowledge Base Creation",
                 "The end-to-end pipeline — which Hands-on A.2 runs for real"))
cells.append(code(
'''from notebook_src.display import render_points_card
show(render_points_card("A.1 · Step 5", "Knowledge Base Creation",
    "Putting it together", [
    "Pipeline: <b>extract</b> triples → <b>type &amp; ground</b> to an ontology → <b>disambiguate</b> → <b>build</b> the graph.",
    "That is exactly what <b>Hands-on A.2</b> does next, on a real abstract.",
    "Result: a typed, queryable knowledge graph — ready for RAG in Hands-on B.",
]))'''))

# ── Part 4 · Hands-on A.2 (Intermediate) — copy finished cells ────────── #
cells.append(banner("Hands-on A.2 · Knowledge Base (Intermediate)",
                    "Build a real knowledge graph from a biomedical abstract, end to end",
                    "135deg,#5b21b6,#7c3aed"))
for c in nb4["cells"][4:]:       # ### Setup ... Key Takeaways (skip title/install/setup/## KB)
    cells.append(fresh(c))

# ── Part 5 · Hands-on B — murder mystery KG-RAG ───────────────────────── #
cells.append(banner("Hands-on B · Use the Graph — A Murder Mystery",
                    "Retrieval, prompt engineering and chain-of-thought to crack a case",
                    "135deg,#7f1d1d,#b91c1c"))
RED = "#b91c1c"; REDBG = "#fef2f2"

cells.append(sub("###", 0, RED, REDBG, "🕵️", "The Case",
                 "A guest is dead. Five suspects, one culprit — the graph holds the answer"))
cells.append(code(
'''from notebook_src.visuals import show
from notebook_src import mystery as M
from notebook_src.display import render_case_file
show(render_case_file(M.CASE))'''))

cells.append(sub("###", 0, RED, REDBG, "🕸️", "The Mystery Knowledge Graph",
                 "Suspects, rooms, weapons and motives as a typed property graph"))
cells.append(code(
'''from notebook_src.graph import build_graph
from notebook_src.display import render_kg

case_triples = M.mystery_triples()
mystery_kg   = build_graph(case_triples)

# Suspects (red) linked to rooms (blue), the weapon (grey) and motives (amber).
show(render_kg(case_triples, strategy="Mystery KG", color_by="type",
               group_colours=M.MYSTERY_COLOURS, height="500px"))'''))

cells.append(sub("###", 0, RED, REDBG, "🔗", "Querying the Graph",
                 "Traverse the graph to see who connects to the scene of the crime"))
cells.append(code(
'''from notebook_src.graph import neighbours, farthest_path
from notebook_src.display import render_query_panel

# Who and what is connected to the Study — the scene of the crime?
scene = "the Study"
show(render_query_panel(scene, neighbours(mystery_kg, scene),
                        farthest_path(mystery_kg, scene)))'''))

cells.append(sub("###", 0, RED, REDBG, "🔎", "Retrieval with Embeddings",
                 "Semantic search finds the handful of facts relevant to a question"))
cells.append(code(
'''from notebook_src.display import render_retrieval

question = "Where was Ms. Vivian Scarlett and did she have an alibi?"
hits = M.retrieve(question, k=4)
show(render_retrieval(question, hits))'''))

cells.append(sub("###", 0, RED, REDBG, "✍️", "Prompt Engineering — Grounded vs Ungrounded",
                 "The same question, answered with and without the retrieved facts"))
cells.append(code(
'''import os
from notebook_src.display import render_prompt_compare
API_KEY = os.environ.get("OPENAI_API_KEY", "")

q = "What was Ms. Vivian Scarlett's motive, and did she have an alibi?"
context = [h["clue"] for h in M.retrieve("Vivian Scarlett motive alibi partnership Study", 6)]

ungrounded = M.answer(q, [],      API_KEY, grounded=False)   # no graph -> guesses
grounded   = M.answer(q, context, API_KEY, grounded=True)    # KG-RAG -> cites facts
show(render_prompt_compare(q, ungrounded, grounded))'''))

cells.append(sub("###", 0, RED, REDBG, "🧩", "Chain-of-Thought — Solving the Case",
                 "Reasoning step-by-step over the facts to unmask the murderer"))
cells.append(code(
'''from notebook_src.display import render_reasoning
API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Give the model ALL the facts and let it reason: eliminate alibis, find the one
# suspect with motive, means and opportunity.
solution = M.solve(API_KEY)
show(render_reasoning(solution, M.is_correct(solution["culprit"])))
print("Ground truth:", M.CASE["solution"]["culprit"])'''))

cells.append(md(
"""### 🎓 Workshop Wrap-up

<div style="border-left:4px solid #7c3aed;background:#f5f3ff;border-radius:0 10px 10px 0;padding:14px 18px;margin:10px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="font-size:16px;font-weight:700;color:#0f172a;">🎓 &nbsp;You built a KG-RAG system end to end</div>
  <div style="font-size:12.5px;color:#475569;margin-top:4px;line-height:1.6">
  <b>A.2</b> — extracted, typed, grounded, disambiguated and queried a knowledge graph from raw text.<br>
  <b>B</b> — retrieved facts by meaning, grounded a prompt to stop hallucination, and reasoned step-by-step to solve a case.<br>
  That is the core of using knowledge graphs to make LLMs trustworthy and resistant to misinformation.
  </div>
</div>"""))

# ── write ─────────────────────────────────────────────────────────────── #
nb = {"nbformat": 4, "nbformat_minor": META.get("nbformat_minor", 5) or 5,
      "metadata": META, "cells": cells}
OUT.write_text(json.dumps(nb, indent=1, ensure_ascii=False))

import nbformat
nbformat.validate(nbformat.read(str(OUT), as_version=4))
print(f"Wrote {OUT.name} — {len(cells)} cells")
