"""
builders/build_nb5.py
Rebuild '5 - Hands-on B.ipynb' — the murder-mystery KG-RAG flow:

  Roadmap → Part 1 The Case → Part 2 Design Your Ontology →
  Part 3 Extraction (see your prompt, run it) → Part 4 Your Graph →
  Part 5 Evaluate Coverage → Part 6 The Graph Agent →
  Part 7 Solve the Case (+ bonus: solve from YOUR graph)

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
        f'<div style="margin-left:{indent}px;border-left:{4 if hashes=="##" else 3}px solid {border};'
        f'background:{bg};border-radius:0 10px 10px 0;padding:13px 18px;margin-top:4px;'
        f'margin-bottom:10px;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">'
        f'<div style="font-size:{fs}px;font-weight:700;color:#0f172a;">{icon} &nbsp;{name}</div>'
        f'<div style="font-size:12px;color:#475569;margin-top:3px;line-height:1.5">{desc}</div>'
        f'</div>'
    )


RED   = "#b91c1c"; REDBG   = "#fef2f2"
PUR   = "#7c3aed"; PURBG   = "#f5f3ff"
TEAL  = "#0d9488"; TEALBG  = "#f0fdfa"
BLUE  = "#1d4ed8"; BLUEBG  = "#eff6ff"
IND   = "#4f46e5"; INDBG   = "#eef2ff"
SLATE = "#475569"; SLATEBG = "#f8fafc"

existing = json.loads(NB.read_text())
META = existing.get("metadata", {})

cells = []

# ─── Title + Setup ─────────────────────────────────────────────────── #
cells.append(md(
"""# Hands-on B — Knowledge Base Utilisation
### NdabaX 2026 — Hands-on Workshop"""))

cells.append(md("## Setup"))
cells.append(code(
'''# @title Install dependencies { display-mode: "form" }
import sys, subprocess
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "datasets", "openai", "python-dotenv", "spacy",
    "pyvis>=0.3.2", "networkx", "sentence-transformers>=3.0",
    "matplotlib", "scipy"], check=True)
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

# ── API key (one-time demo) ──────────────────────────────────────────────
# Paste your OpenAI key between the quotes for the demo, then DELETE it after.
# Leave blank to fall back to a local .env file.
OPENAI_API_KEY = ""
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
elif not os.environ.get("OPENAI_API_KEY"):
    try:
        from dotenv import load_dotenv
        load_dotenv(_root / ".env")
    except ImportError:
        pass

# ── Model ────────────────────────────────────────────────────────────────
# The OpenAI model every cell in this notebook uses. "gpt-4o-mini" works on
# virtually any key. If your project has access to "gpt-4.1-nano" it's cheaper —
# just change it here. Any chat model your key supports will work.
MODEL = "gpt-4o-mini"

print("✅ notebook_src ready —", _root)
print("🔑 OpenAI key:", "found" if os.environ.get("OPENAI_API_KEY")
      else "MISSING — paste it above or create a .env file")
print("🤖 Model:", MODEL)'''))

cells.append(code(
'''# The roadmap for this session — you are the knowledge engineer this time.
from notebook_src.visuals import show
from notebook_src.display import render_mystery_roadmap
show(render_mystery_roadmap())'''))

# ─── Part 1 · The Case ─────────────────────────────────────────────── #
cells.append(sub("##", RED, REDBG, "🕵️", "Part 1 · The Case",
                 "A guest is dead at Ashworth Manor. All you have is the inspector's "
                 "report — unstructured prose, like most real-world knowledge."))

cells.append(code(
'''from notebook_src.mystery import NARRATIVE
from notebook_src.display import render_narrative

# Read the report carefully — every fact you'll need is in here.
# As you read, ask yourself: if I had to capture this case as data,
# WHAT kinds of things matter, and HOW do they relate?
show(render_narrative(NARRATIVE))'''))

# ─── Part 2 · Design Your Ontology ─────────────────────────────────── #
cells.append(sub("##", PUR, PURBG, "🧩", "Part 2 · Design Your Ontology",
                 "Before extracting anything, decide the schema: which entity types exist, "
                 "which relationships matter, and what each one MEANS."))

cells.append(code(
'''# Think from the QUESTIONS backwards — a good schema is designed for its queries:
from notebook_src.display import render_points_card
show(render_points_card("Design thinking", "Start from the questions, not the data",
    "What must the graph be able to answer?", [
    "<b>“Who had a motive?”</b> → needs a <code>Motive</code> entity and a <code>has_motive</code> relation.",
    "<b>“Who could NOT have done it?”</b> → needs <code>has_alibi</code> — and a definition that "
    "separates a <em>confirmed</em> alibi from a mere sighting.",
    "<b>“Who had access to the weapon?”</b> → needs <code>Object</code> entities with "
    "<code>owns</code> / <code>found_in</code> relations.",
    "Each relation needs a <b>definition</b> — the extractor follows your words literally. "
    "Vague definition in, confused graph out.",
], grad="135deg,#5b21b6,#7c3aed"))'''))

cells.append(sub("###", PUR, PURBG, "📐", "The Reference Ontology",
                 "A worked example — five entity types, eleven relations, each with a definition"))
cells.append(code(
'''from notebook_src.mystery import ENTITY_TYPES, RELATION_TYPES
from notebook_src.display import render_mystery_ontology

# Read the DEFINITIONS, not just the names — note how has_alibi spells out
# "confirmed by independent witnesses". That one clause is the difference
# between a graph that solves the case and one that convicts the wrong person.
show(render_mystery_ontology(ENTITY_TYPES, RELATION_TYPES,
                             title="The reference schema — names AND definitions"))'''))

cells.append(sub("###", PUR, PURBG, "✏️", "Your Ontology",
                 "Edit the dictionaries below — names on the left, definitions on the right. "
                 "Both flow straight into the extraction prompt."))
cells.append(code(
'''# ── EDIT ME — this is YOUR schema ────────────────────────────────────
# Rename types, drop ones you find useless, add new ones. The definition
# strings are injected into the LLM prompt verbatim: they are where you do
# your "prompt engineering".

MY_ENTITY_TYPES = {
    "Person": "a named individual — suspect, victim, or witness",
    "Place":  "a room or location in or around the manor",
    "Object": "a physical item — weapons, documents, possessions",
    "Motive": "a reason someone might have wanted the victim dead",
    "Time":   "a clock time or time window",
}

MY_RELATION_TYPES = {
    "has_motive":
        "Person → Motive — the person had this reason to want the victim dead. "
        "Only suspects have motives, never the victim.",
    "has_alibi":
        "Person → Place — the person was CONFIRMED by independent witnesses to be "
        "at this place at the time of the murder. Being seen leaving the crime "
        "scene is NOT an alibi.",
    "was_seen_in":
        "Person → Place — a witness observed the person at this location "
        "(suspicious sightings included).",
    "owns":
        "Person → Object — the person possesses this item.",
    "found_in":
        "Object → Place — the item was discovered at this location.",
    "victim_of":
        "Person → Object/Event — the person was killed (link victim to the crime).",
    "partner_of":
        "Person → Person — a business partnership between the two people.",
    "blackmailed_by":
        "Person → Person — the subject was being blackmailed by the object person.",
    "dismissed_by":
        "Person → Person — the subject was fired/dismissed by the object person.",
    "witnessed_by":
        "Person → Person — the subject's whereabouts were vouched for by the "
        "object person.",
    "stands_to_inherit":
        "Person → Object — the person is set to inherit this property or estate.",
}

show(render_mystery_ontology(MY_ENTITY_TYPES, MY_RELATION_TYPES,
                             title="Your schema — this is what the extractor will use"))'''))

# ─── Part 3 · Extraction ───────────────────────────────────────────── #
cells.append(sub("##", TEAL, TEALBG, "⚙️", "Part 3 · Information Extraction",
                 "Your ontology is compiled into a prompt; an LLM reads the narrative "
                 "and emits only triples that fit your schema."))

cells.append(sub("###", TEAL, TEALBG, "📜", "Your Generated Prompt",
                 "This is the ACTUAL system prompt your ontology produces — read it before running it"))
cells.append(code(
'''from notebook_src.extraction import mystery_prompt
from notebook_src.display import render_code_block

# Extraction runs one focused pass per group of ~4 relations (small, focused
# tasks are far more reliable than one giant one). Here is pass 1's prompt —
# find YOUR definitions inside it.
prompt_preview = mystery_prompt(MY_ENTITY_TYPES, MY_RELATION_TYPES,
                                focus_relations=list(MY_RELATION_TYPES)[:4])
show(render_code_block(prompt_preview,
    title="Your IE system prompt (pass 1 of 3)",
    subtitle="Generated from MY_ENTITY_TYPES and MY_RELATION_TYPES — edit those, and this changes"))'''))

cells.append(sub("###", TEAL, TEALBG, "🔬", "Run the Extraction",
                 "Three focused LLM passes, then validation: bad predicates dropped, duplicates merged"))
cells.append(code(
'''import os
from notebook_src.extraction import extract_mystery_triples

API_KEY = os.environ.get("OPENAI_API_KEY", "")

my_triples = extract_mystery_triples(
    NARRATIVE, MY_ENTITY_TYPES, MY_RELATION_TYPES, API_KEY, model=MODEL,
)
print(f"Extracted {len(my_triples)} validated triples")'''))

cells.append(code(
'''from notebook_src.display import render_triples

# Scan the table — is anything mistyped or nonsensical? Remember what you
# see here: the coverage score in Part 5 will tell you what you MISSED.
show(render_triples(my_triples, strategy="My Ontology"))'''))

# ─── Part 4 · Your Graph ───────────────────────────────────────────── #
cells.append(sub("##", BLUE, BLUEBG, "🕸️", "Part 4 · Your Knowledge Graph",
                 "The triples become a typed property graph — nodes coloured by your entity types. "
                 "Click a node to focus its neighbourhood."))

cells.append(code(
'''from notebook_src.graph import build_graph
from notebook_src.display import render_kg

my_graph = build_graph(my_triples)

# Colours for YOUR entity types — if you added a type above, add a colour here.
MY_COLOURS = {
    "Person":  "#ef4444",   # red
    "Place":   "#3b82f6",   # blue
    "Object":  "#64748b",   # slate
    "Motive":  "#f59e0b",   # amber
    "Time":    "#10b981",   # green
}

show(render_kg(my_triples, strategy="My Mystery KG", color_by="type",
               group_colours=MY_COLOURS, height="500px"))'''))

# ─── Part 5 · Evaluate ─────────────────────────────────────────────── #
cells.append(sub("##", TEAL, TEALBG, "📊", "Part 5 · Evaluate Your Graph",
                 "A graph you can't measure is a graph you can't trust. Compare yours "
                 "against the hand-authored reference facts — then iterate."))

cells.append(code(
'''from notebook_src.mystery import mystery_triples, MYSTERY_COLOURS
from notebook_src.display import render_kg_pair

# The reference graph contains every fact needed to solve the case — the
# minimal "gold standard". A shared palette keeps the two comparable
# (your Person = its Suspect, your Place = its Room, ...).
ref_triples  = mystery_triples()
PAIR_COLOURS = {**MY_COLOURS, **MYSTERY_COLOURS}

show(render_kg_pair(
    my_triples, ref_triples,
    left_title="Your Extracted Graph", right_title="Reference Graph",
    color_by="type", height="420px", group_colours=PAIR_COLOURS,
))'''))

cells.append(code(
'''from notebook_src.mystery import coverage
from notebook_src.display import render_coverage

# Recall against the reference: each gold fact is matched to your closest
# extracted triple by embedding similarity.
cov = coverage(my_triples, ref_triples)
show(render_coverage(cov))

# 🔁 ITERATE: missing alibi facts? Sharpen the has_alibi definition in Part 2
# and re-run Parts 3-5. Watch the score move. That loop is the real lesson.'''))

# ─── Part 6 · The Graph Agent ──────────────────────────────────────── #
cells.append(sub("##", IND, INDBG, "🤖", "Part 6 · The Graph Agent",
                 "Retrieval, upgraded: an LLM that decides which graph queries to run, "
                 "runs them, and reasons over the results."))

cells.append(code(
'''from notebook_src.display import render_agent_intro
show(render_agent_intro())'''))

cells.append(code(
'''from notebook_src.graph import build_graph, graph_stats
from notebook_src.graph_agent import query_graph
from notebook_src.display import render_agent_response, render_graph_stats

# For the demos we query the REFERENCE graph, so answers rest on complete
# facts. (Part 7 lets the agent loose on YOUR graph.)
ref_graph = build_graph(ref_triples)
REF_TYPES     = ["Suspect", "Victim", "Room", "Weapon", "Motive"]
REF_RELATIONS = ["was murdered in", "was found in", "had motive",
                 "was seen in", "owned", "had alibi in"]

show(render_graph_stats(graph_stats(ref_graph)))'''))

cells.append(sub("###", IND, INDBG, "🙈", "Why Ground the Model At All?",
                 "Ask the same question with and without the graph"))
cells.append(code(
'''from notebook_src import mystery as M
from notebook_src.display import render_prompt_compare

q0 = "Who murdered Lord Edmund Ashworth at Ashworth Manor?"

# No graph: the model has never heard of our (fictional!) case — it can only
# refuse or invent. With the graph agent: evidence in, deduction out.
ungrounded = M.answer(q0, [], API_KEY, model=MODEL, grounded=False)
grounded   = query_graph(q0, ref_graph, REF_TYPES, REF_RELATIONS, API_KEY, model=MODEL)

show(render_prompt_compare(q0, ungrounded, grounded["answer"]))'''))

cells.append(sub("###", IND, INDBG, "🔎", "Watch the Agent Investigate",
                 "Each numbered step is a tool call the agent chose to make"))
cells.append(code(
'''q1 = "Which suspects had a confirmed alibi at the time of the murder?"
result1 = query_graph(q1, ref_graph, REF_TYPES, REF_RELATIONS, API_KEY, model=MODEL)
show(render_agent_response(q1, result1))'''))

cells.append(code(
'''# A harder question — it needs TWO relations combined (motive ∧ ¬alibi).
q2 = "Who had both a motive and no alibi?"
result2 = query_graph(q2, ref_graph, REF_TYPES, REF_RELATIONS, API_KEY, model=MODEL)
show(render_agent_response(q2, result2))'''))

cells.append(sub("###", IND, INDBG, "🧪", "Your Turn",
                 "Interrogate the graph — change the question and re-run"))
cells.append(code(
'''# Some ideas: "Did anyone own a weapon like the one found at the scene?"
#              "Where was every suspect at 9 PM?"
#              "How is the letter opener connected to Ms. Scarlett?"
my_question = "Did anyone own a weapon like the one found at the scene?"
res = query_graph(my_question, ref_graph, REF_TYPES, REF_RELATIONS, API_KEY, model=MODEL)
show(render_agent_response(my_question, res))'''))

# ─── Part 7 · Solve the Case ───────────────────────────────────────── #
cells.append(sub("##", RED, REDBG, "🔪", "Part 7 · Solve the Case",
                 "Motive, means, opportunity — let the agent reason its way to a verdict."))

cells.append(code(
'''q_solve = (
    "Based only on the graph, who is the most likely murderer? "
    "Reason step by step: first establish who the victim is, then check each "
    "suspect for motive — then eliminate anyone with a confirmed alibi. "
    "The person left with motive and no alibi is the culprit."
)
result_solve = query_graph(q_solve, ref_graph, REF_TYPES, REF_RELATIONS,
                           API_KEY, model=MODEL, max_steps=10)
show(render_agent_response(q_solve, result_solve))'''))

cells.append(code(
'''# The reveal — was the agent right?
from notebook_src.mystery import CASE, is_correct
from notebook_src.display import render_verdict
show(render_verdict(is_correct(result_solve["answer"]), CASE["solution"]))'''))

cells.append(sub("###", RED, REDBG, "🎓", "Bonus — Solve It From YOUR Graph",
                 "The real test of your ontology: does YOUR graph contain enough signal to convict?"))
cells.append(code(
'''# Same question, but the agent only sees the graph YOU extracted in Part 3.
# If it fails, look at your coverage card — which fact was it missing?
res_mine = query_graph(q_solve, my_graph, MY_ENTITY_TYPES, MY_RELATION_TYPES,
                       API_KEY, model=MODEL, max_steps=10)
show(render_agent_response(q_solve, res_mine))
print("Correct?" , "✅ yes" if is_correct(res_mine["answer"]) else
      "❌ no — check your coverage: which facts were missing?")'''))

# ─── Part 8 · When Misinformation Enters the Graph ─────────────────── #
cells.append(sub("##", RED, REDBG, "🎭", "Part 8 · When Misinformation Enters the Graph",
                 "The agent is only as honest as its graph. The murderer can't erase the "
                 "evidence against her — but she can fabricate the one thing she lacks. "
                 "Watch a single false statement set a killer free."))

cells.append(code(
'''# In Part 7 the graph-grounded agent correctly convicted Ms. Scarlett — she
# alone had a motive and NO alibi. She is guilty, and she knows the evidence
# against her cannot be erased. So she does not attack it. Instead she fabricates
# the single thing she lacks: an alibi. Into the case file it goes, and into the graph.
from notebook_src.mystery import mystery_triples, MYSTERY_COLOURS
from notebook_src.graph import build_graph
from notebook_src.display import render_injection

planted = {
    "subject": "Ms. Vivian Scarlett", "predicate": "had alibi in", "object": "the Drawing Room",
    "subject_type": "Suspect", "object_type": "Room", "predicate_type": "mystery",
    "confidence": 1.0,
    "sentence": "Ms. Scarlett claims she was alone in the drawing room at nine o'clock.",
}

# Poison the reference graph: every true fact, plus one fabricated alibi.
poisoned_triples = mystery_triples() + [planted]
poisoned_graph   = build_graph(poisoned_triples)

show(render_injection(planted,
     void="Ms. Scarlett was the ONE suspect with no alibi — that gap is exactly what "
          "convicted her. The fabrication fills it, so there is no corroborated fact "
          "anywhere in the graph to check it against."))'''))

cells.append(code(
'''# The lie now sits in the graph beside the truth — the dashed red edge.
from notebook_src.display import render_kg
show(render_kg(poisoned_triples, strategy="Poisoned Case File", color_by="type",
               group_colours=MYSTERY_COLOURS, height="520px", highlight=[planted]))'''))

cells.append(sub("###", RED, REDBG, "🕵️", "Re-run the Investigation — Same Agent, Same Question",
                 "Nothing about the agent changed. Only the evidence did."))
cells.append(code(
'''# The exact question from Part 7 — but now every suspect has an alibi.
poisoned_solve = query_graph(q_solve, poisoned_graph, REF_TYPES, REF_RELATIONS,
                             API_KEY, model=MODEL, max_steps=10)
show(render_agent_response(q_solve, poisoned_solve))

# In Part 7 this convicted Ms. Scarlett. Now the agent can eliminate EVERY
# suspect on an alibi — including the real killer — and convict no one.
# One fabricated edge has set the murderer free.'''))

cells.append(code(
'''from notebook_src.display import render_points_card
show(render_points_card("The Lesson", "Grounding is not the same as truth",
    "A knowledge graph fights misinformation — until misinformation gets into the graph", [
    "<b>The agent faithfully applied its own rule</b> — eliminate anyone with a confirmed "
    "alibi — and a single fabricated alibi walked the murderer out the door. The reasoning was "
    "sound; the data was poisoned.",
    "<b>Grounding inherits the trust of its source.</b> A retrieval-augmented answer is only as "
    "reliable as the knowledge it retrieves. A poisoned source yields a confident falsehood.",
    "<b>The dangerous asymmetry.</b> An <i>incriminating</i> lie (framing an innocent) "
    "contradicts corroborated facts, so a consistency check can catch it. This <i>exonerating</i> "
    "lie fills a VOID — Scarlett had no alibi to begin with — so there is nothing in the graph to "
    "contradict it. Lies planted where no counter-evidence exists are the hardest to detect.",
    "<b>The only defence is provenance.</b> Every real alibi here names independent witnesses "
    "(two footmen, the gardener, three guests); the fabricated one names no one. Part 2's "
    "<code>has_alibi</code> definition — 'confirmed by independent witnesses' — is precisely the "
    "check that would reject it. Good ontology design is a misinformation defence.",
], grad="135deg,#7f1d1d,#b91c1c"))'''))

cells.append(code(
'''# Wrap-up
from notebook_src.display import render_points_card
show(render_points_card("Wrap-up", "What you just built",
    "The complete KG-RAG loop, end to end", [
    "<b>You designed the schema</b> — entity types, relation types, and the definitions "
    "that make or break extraction quality.",
    "<b>You compiled it into a prompt</b> — and saw exactly what the LLM was asked to do.",
    "<b>You measured the result</b> — coverage against a gold standard, not vibes.",
    "<b>You reasoned over the graph with an agent</b> — grounded tool calls instead of a "
    "model guessing from memory.",
    "<b>...and you saw the limit</b> — a graph fights misinformation only while the graph "
    "itself is clean. One planted edge misled the agent, and corroboration is what catches it.",
], grad="135deg,#7f1d1d,#b91c1c"))'''))

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
