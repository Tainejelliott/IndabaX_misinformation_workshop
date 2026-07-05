"""
add_hands_on_b.py
Adds the Knowledge Base Utilization (Hands-on B) section.
Run with: .venv/bin/python builders/add_hands_on_b.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent.parent
NB   = ROOT / "KG_RAG_Workshop.ipynb"

nb = json.loads(NB.read_text())

_cid = 700
def _id():
    global _cid; _cid += 1
    return f"hob{_cid:04d}"

def md(src):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": src}

def code(src, tags=None):
    meta = {"tags": tags} if tags else {}
    return {"cell_type": "code", "id": _id(), "metadata": meta,
            "source": src, "outputs": [], "execution_count": None}

# ── heading + styled card factory ─────────────────────────────────── #
PAL = dict(
    l1=("#059669", "#f0fdf4"),   # emerald
    l2=("#047857", "#ecfdf5"),
    l3=("#065f46", "#f0fffe"),
)

def sub(depth, icon, title, subtitle):
    hashes = "#" * (depth + 2)          # depth 1→###, 2→####, 3→#####
    indent = (depth - 1) * 24
    border = 4 if depth == 1 else 3
    size   = "16" if depth == 1 else "14"
    col, bg = PAL[f"l{depth}"]
    return md(
        f"{hashes} {title}\n\n"
        f'<div style="margin-left:{indent}px;border-left:{border}px solid {col};'
        f'background:{bg};border-radius:0 10px 10px 0;padding:13px 18px;'
        f'margin-top:4px;margin-bottom:10px;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">\n'
        f'  <div style="font-size:{size}px;font-weight:700;color:#0f172a;">'
        f'{icon} &nbsp;{title}</div>\n'
        f'  <div style="font-size:12px;color:#475569;margin-top:3px;line-height:1.5">'
        f'{subtitle}</div>\n'
        f'</div>'
    )

def s1(icon, title, subtitle): return [sub(1, icon, title, subtitle), code(f"# {title}\n")]
def s2(icon, title, subtitle): return [sub(2, icon, title, subtitle), code(f"# {title}\n")]
def s3(icon, title, subtitle): return [sub(3, icon, title, subtitle), code(f"# {title}\n")]


# ── section header ─────────────────────────────────────────────────── #
section_header = md(
    "## Knowledge Base Utilization\n\n"
    '<div style="background:linear-gradient(135deg,#059669 0%,#10b981 100%);'
    'border-radius:12px;padding:20px 28px;margin:4px 0 12px 0;'
    'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">\n'
    '  <div style="color:rgba(255,255,255,0.7);font-size:11px;font-weight:600;'
    'letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">\n'
    '    🧪 &nbsp;Hands-on B\n'
    '  </div>\n'
    '  <div style="color:#fff;font-size:22px;font-weight:700;margin-bottom:4px;">'
    'Knowledge Base Utilization</div>\n'
    '  <div style="color:rgba(255,255,255,0.85);font-size:13px;">'
    'Using embeddings · Prompt engineering · Evaluation — '
    'validation, retrieval recall, and complex multi-step searches'
    '</div>\n'
    '</div>'
)

# ── subsections ────────────────────────────────────────────────────── #
cells = [section_header]

cells += s1("🔢", "Using Embeddings",
            "Encoding knowledge-base content as dense vectors to enable semantic retrieval")

cells += s1("✍️", "Prompt Engineering",
            "Designing prompts that ground the LLM in retrieved context and minimise hallucination")

# Evaluation (###)
cells += [sub(1, "📊", "Evaluation",
              "Measuring quality at every stage — representation, retrieval and reasoning")]
cells += [code("# Evaluation — parent section\n")]

# ── Validation of IE/Representation (####) ──
cells += [sub(2, "✅", "Validation of Information Extraction / Representation",
              "Checking that extracted facts are accurate and that the KB structure is sound")]
cells += [code("# Validation of Information Extraction / Representation\n")]

cells += s3("📦", "Embedding your data",
            "Encoding claims and entities as vectors; inspecting the embedding space for quality")

cells += s3("🔍", "Semantic Search",
            "Querying the KB by meaning rather than keywords; evaluating top-k relevance")

cells += s3("🕸️", "Information Connectedness",
            "Measuring how well related facts are linked — graph path analysis and reachability")

# ── Evaluation of Information Retrieval (####) ──
cells += [sub(2, "📐", "Evaluation of Information Retrieval (Recall)",
              "Quantifying how much relevant information the retrieval step actually surfaces")]
cells += [code("# Evaluation of Information Retrieval (Recall)\n")]

cells += s3("🔄", "HyDE / Reverse-HyDE",
            "Hypothetical Document Embeddings — embed a generated answer instead of the question "
            "to close the query-document gap and boost recall")

# ── Complex Searches (####) ──
cells += [sub(2, "🧩", "Complex Searches",
              "Multi-step retrieval strategies for queries that require reasoning across multiple facts")]
cells += [code("# Complex Searches\n")]

cells += s3("🔗", "Multiple Information Retrieval Steps",
            "Iterative retrieval — each step uses previous results to guide the next query")

cells += s3("🌿", "Chain / Tree of Thoughts",
            "Chain-of-Thought: sequential reasoning steps · "
            "Tree-of-Thought: parallel reasoning branches synthesised into a final answer")

nb["cells"].extend(cells)
NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Done — {len(nb['cells'])} cells total")
