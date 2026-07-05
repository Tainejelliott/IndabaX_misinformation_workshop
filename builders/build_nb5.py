"""
builders/build_nb5.py
Rebuild '5 - Hands-on B.ipynb' with the full murder-mystery KG-RAG flow:
  Setup → The Case Narrative → Design Your Ontology → Extract Triples →
  Build Your Graph → Query the Graph → KG-RAG Agent → Solve the Case

Run: .venv/bin/python builders/build_nb5.py
"""
import json, uuid, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "5 - Hands-on B.ipynb"


def md(s):
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:8],
            "metadata": {}, "source": s}

def code(s):
    return {"cell_type": "code", "id": uuid.uuid4().hex[:8],
            "metadata": {}, "source": s, "outputs": [], "execution_count": None}

def sub(hashes, border, bg, icon, name, desc, indent=0, fs=14):
    return md(
        f"{hashes} {name}\n\n"
        f'<div style="margin-left:{indent}px;border-left:{4 if hashes=="###" else 3}px solid {border};'
        f'background:{bg};border-radius:0 10px 10px 0;padding:13px 18px;margin-top:4px;'
        f'margin-bottom:10px;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">'
        f'<div style="font-size:{fs}px;font-weight:700;color:#0f172a;">{icon} &nbsp;{name}</div>'
        f'<div style="font-size:12px;color:#475569;margin-top:3px;line-height:1.5">{desc}</div>'
        f'</div>'
    )


RED   = "#b91c1c"; REDBG = "#fef2f2"
PUR   = "#7c3aed"; PURBG = "#f5f3ff"
TEAL  = "#0d9488"; TEALBG = "#f0fdfa"
BLUE  = "#1d4ed8"; BLUEBG = "#eff6ff"
SLATE = "#475569"; SLATEBG = "#f8fafc"


existing = json.loads(NB.read_text())
META = existing.get("metadata", {})

# Keep original setup cells 0-3
setup_cells = existing["cells"][:4]

cells = list(setup_cells)   # title, ## Setup md, pip install, sys.path

# ─── 1 · The Case ──────────────────────────────────────────────────── #
cells.append(sub("##", RED, REDBG, "🕵️", "The Case",
                 "A guest is dead at Ashworth Manor — five suspects, one murderer"))

cells.append(sub("###", RED, REDBG, "📰", "The Case Narrative",
                 "Raw text — this is what you will build a knowledge graph from"))
cells.append(code(
"""from notebook_src.visuals import show
from notebook_src.mystery import NARRATIVE
from notebook_src.display import render_narrative

# This ~580-word police inspector's report is your IE input.
# Read it carefully — then design the ontology you would use to extract
# a knowledge graph that captures the key facts.
show(render_narrative(NARRATIVE))"""))

# ─── 2 · Design Your Ontology ──────────────────────────────────────── #
cells.append(sub("##", PUR, PURBG, "🧩", "Design Your Ontology",
                 "Decide what entities and relationships matter — this defines your graph's schema"))

cells.append(sub("###", PUR, PURBG, "📐", "Reference Ontology",
                 "A suggested starting point — modify it in the cell below"))
cells.append(code(
"""from notebook_src.mystery import ENTITY_TYPES, RELATION_TYPES
from notebook_src.display import render_mystery_ontology

# Show the reference ontology before the attendee modifies it
show(render_mystery_ontology(ENTITY_TYPES, RELATION_TYPES))"""))

cells.append(sub("###", PUR, PURBG, "✏️", "Your Ontology",
                 "Edit the lists below — your changes flow into the extraction prompt automatically"))
cells.append(code(
"""# ── EDIT THESE to design your own ontology ──────────────────────────
# Add, remove or rename any type.  The extraction prompt is built from
# exactly these lists — so what you put here shapes the graph you get.

MY_ENTITY_TYPES = [
    "Person",    # suspects, victim, witnesses
    "Place",     # rooms in the manor
    "Object",    # weapons and items
    "Motive",    # reasons to commit murder
    "Time",      # timestamps / durations
]

MY_RELATION_TYPES = [
    "has_motive",         # Person → Motive
    "has_alibi",          # Person → Place   (confirmed elsewhere)
    "was_seen_in",        # Person → Place   (witnessed at a location)
    "owns",               # Person → Object
    "found_in",           # Object → Place
    "victim_of",          # Person → Event
    "partner_of",         # Person → Person  (business relationship)
    "blackmailed_by",     # Person → Person
    "dismissed_by",       # Person → Person
    "witnessed_by",       # Person → Person  (who saw whom)
    "stands_to_inherit",  # Person → estate/Object
]

# Preview your schema
show(render_mystery_ontology(MY_ENTITY_TYPES, MY_RELATION_TYPES))"""))

# ─── 3 · Information Extraction ────────────────────────────────────── #
cells.append(sub("##", TEAL, TEALBG, "⚙️", "Information Extraction",
                 "Run your ontology through OpenAI — the LLM extracts triples that fit your schema"))

cells.append(sub("###", TEAL, TEALBG, "🔬", "Extract Triples",
                 "Each (subject, predicate, object) triple must use your defined types"))
cells.append(code(
"""import os
from notebook_src.extraction import extract_mystery_triples

API_KEY = os.environ.get("OPENAI_API_KEY", "")

# The extraction prompt is automatically built from MY_ENTITY_TYPES
# and MY_RELATION_TYPES — change those above and re-run this cell.
my_triples = extract_mystery_triples(
    NARRATIVE,
    MY_ENTITY_TYPES,
    MY_RELATION_TYPES,
    API_KEY,
)
print(f"Extracted {len(my_triples)} triples")"""))

cells.append(sub("###", TEAL, TEALBG, "📋", "Extracted Triples",
                 "The raw output — every (subject, predicate, object) the LLM found"))
cells.append(code(
"""from notebook_src.display import render_triples

# This table shows what the LLM extracted using your ontology.
# If a type looks wrong — adjust your ontology and re-extract.
show(render_triples(my_triples, strategy="My Ontology"))"""))

# ─── 4 · Build the Graph ───────────────────────────────────────────── #
cells.append(sub("##", BLUE, BLUEBG, "🕸️", "Your Knowledge Graph",
                 "The extracted triples become nodes and edges — coloured by your entity types"))

cells.append(code(
"""from notebook_src.graph import build_graph
from notebook_src.display import render_kg

my_graph = build_graph(my_triples)

# group_colours maps YOUR entity type names to hex colours.
# Add or change colours to match the types you defined above.
MY_COLOURS = {
    "Person":  "#ef4444",   # red
    "Place":   "#3b82f6",   # blue
    "Object":  "#64748b",   # slate
    "Motive":  "#f59e0b",   # amber
    "Time":    "#10b981",   # green
}

show(render_kg(
    my_triples,
    strategy="My Mystery KG",
    color_by="type",
    group_colours=MY_COLOURS,
    height="520px",
))"""))

# ─── 5 · Compare to Reference Graph ───────────────────────────────── #
cells.append(sub("##", SLATE, SLATEBG, "🔍", "How Much Did You Capture?",
                 "Compare your extracted graph to the reference — see what your ontology missed"))

cells.append(code(
"""from notebook_src.mystery import mystery_triples, MYSTERY_COLOURS
from notebook_src.display import render_kg_pair

# The reference graph was hand-authored with the same ontology — it contains
# every solvable fact.  Yours was extracted automatically by the LLM.
# The gap between the two shows what good ontology + extraction design gains you.
ref_triples = mystery_triples()

show(render_kg_pair(
    my_triples,  ref_triples,
    left_title="Your Extracted Graph",
    right_title="Reference Graph (all facts)",
    color_by="type",
    height="440px",
))
print(f"Your graph:  {len(my_triples)} triples, {len(set(t['subject'] for t in my_triples) | set(t['object'] for t in my_triples))} nodes")
print(f"Reference:   {len(ref_triples)} triples, {len(set(t['subject'] for t in ref_triples) | set(t['object'] for t in ref_triples))} nodes")"""))

# ─── 6 · KG-RAG Agent ──────────────────────────────────────────────── #
cells.append(sub("##", PUR, PURBG, "🤖", "KG-RAG Agent",
                 "A language model that answers questions by calling tools to traverse the graph"))

cells.append(md(
"""### About the Agent

<div style="border-left:4px solid #7c3aed;background:#f5f3ff;border-radius:0 10px 10px 0;
padding:12px 16px;margin:8px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:12.5px;color:#475569;line-height:1.7;">
The agent uses <b>OpenAI function calling</b> — it decides which tools to call based on your question,
reads the graph results, and reasons iteratively until it can give a grounded answer.<br><br>
For the demo below we query the <b>reference graph</b> (full coverage) so every answer is supported by the
complete set of facts. You could swap in <code>my_graph</code> and <code>MY_ENTITY_TYPES</code> to test
against your own extracted graph instead.
</div>"""))

cells.append(code(
"""from notebook_src.graph import build_graph, neighbours, farthest_path, graph_stats
from notebook_src.graph_agent import query_graph
from notebook_src.display import render_agent_response, render_graph_stats, render_query_panel

# Build the reference graph (complete, hand-authored facts)
ref_graph = build_graph(ref_triples)
REF_TYPES      = ["Suspect", "Victim", "Room", "Weapon", "Motive"]
REF_RELATIONS  = ["was murdered in", "was found in", "had motive",
                   "was seen in", "owned", "had alibi in"]

show(render_graph_stats(graph_stats(ref_graph)))"""))

cells.append(code(
"""# Who and what connects to the Study?
scene = "the Study"
show(render_query_panel(
    scene,
    neighbours(ref_graph, scene),
    farthest_path(ref_graph, scene),
))"""))

cells.append(code(
"""# Ask the agent a question — watch the tool calls it makes
q1 = "Which suspects had a confirmed alibi at the time of the murder?"
result1 = query_graph(q1, ref_graph, REF_TYPES, REF_RELATIONS, API_KEY)
show(render_agent_response(q1, result1))"""))

cells.append(code(
"""q2 = "Who had both a motive and no alibi?"
result2 = query_graph(q2, ref_graph, REF_TYPES, REF_RELATIONS, API_KEY)
show(render_agent_response(q2, result2))"""))

# ─── 7 · Solve the Case ────────────────────────────────────────────── #
cells.append(sub("##", RED, REDBG, "🔪", "Solve the Case",
                 "Ask the agent directly — let it reason its way to the murderer"))

cells.append(code(
"""q_solve = (
    "Based only on the graph, who is the most likely murderer? "
    "Reason step by step: first establish who the victim is, then check each "
    "suspect for motive — then eliminate anyone with a confirmed alibi. "
    "The person left with motive and no alibi is the culprit."
)
result_solve = query_graph(
    q_solve, ref_graph, REF_TYPES, REF_RELATIONS, API_KEY, max_steps=10
)
show(render_agent_response(q_solve, result_solve))"""))

cells.append(code(
"""# Reveal the solution
from notebook_src.mystery import CASE, is_correct
sol = CASE["solution"]
solved = is_correct(result_solve["answer"])
print(f"{'✅ CASE SOLVED' if solved else '❌ Not quite'}: {sol['culprit']} — {sol['weapon']} — {sol['motive']}")"""))

cells.append(md(
"""### 🎓 What you just built

<div style="border-left:4px solid #7c3aed;background:#f5f3ff;border-radius:0 10px 10px 0;
padding:14px 18px;margin:10px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="font-size:15px;font-weight:700;color:#0f172a;">A complete KG-RAG pipeline from scratch</div>
  <div style="font-size:12.5px;color:#475569;margin-top:6px;line-height:1.7;">
    <b>1. You designed the ontology</b> — chose what entities and relations matter for your task.<br>
    <b>2. You extracted the graph</b> — an LLM turned raw prose into typed triples using your schema.<br>
    <b>3. You queried the graph</b> — traversed relationships that keyword search can't answer.<br>
    <b>4. You ran a graph agent</b> — an LLM used tool calls to reason over your graph iteratively.<br><br>
    Change the ontology → re-extract → get a different graph. That's the core of KG design.
  </div>
</div>"""))

# ─── write ─────────────────────────────────────────────────────────── #
nb = {
    "nbformat": 4,
    "nbformat_minor": META.get("nbformat_minor", 5) or 5,
    "metadata": META,
    "cells": cells,
}
NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))

import nbformat
nbformat.validate(nbformat.read(str(NB), as_version=4))
print(f"Wrote {NB.name} — {len(cells)} cells")
