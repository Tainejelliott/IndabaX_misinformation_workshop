


"""
notebook_src/display.py
Rendering functions for workshop data displays.
HTML lives here — not in notebook cells.
"""
from __future__ import annotations
import re
import html as _h


_LABEL_COLOURS = {
    "BACKGROUND": ("#1e40af", "#dbeafe"),
    "METHODS":    ("#065f46", "#d1fae5"),
    "RESULTS":    ("#92400e", "#fef3c7"),
    "CONCLUSIONS":("#4c1d95", "#ede9fe"),
    "OBJECTIVE":  ("#155e75", "#cffafe"),
}


def render_abstract(ex: dict, title: str, authors: str,
                    journal: str, year: str) -> str:
    """Render a PubMedQA example as a styled paper card."""
    pmid     = ex["pubid"]
    question = ex["question"]
    contexts = ex["context"]["contexts"]
    labels   = ex["context"]["labels"]
    meshes   = ex["context"]["meshes"]
    answer   = ex["long_answer"]
    decision = ex["final_decision"].upper()

    decision_col = {"YES": "#059669", "NO": "#dc2626",
                    "MAYBE": "#d97706"}.get(decision, "#6b7280")

    mesh_tags = "".join(
        f'<span style="display:inline-block;background:#f1f5f9;'
        f'border:1px solid #e2e8f0;border-radius:20px;padding:2px 10px;'
        f'font-size:11px;color:#475569;margin:2px;">{m}</span>'
        for m in meshes
    )

    def section_card(label, text):
        col, bg = _LABEL_COLOURS.get(label, ("#374151", "#f9fafb"))
        return (
            f'<div style="margin-bottom:10px;">'
            f'<span style="display:inline-block;background:{col};color:#fff;'
            f'font-size:10px;font-weight:700;letter-spacing:1.5px;'
            f'padding:2px 8px;border-radius:4px;margin-bottom:5px;">{label}</span>'
            f'<div style="font-size:13px;color:#1e293b;line-height:1.7;'
            f'background:{bg};border-radius:6px;padding:10px 14px;">{text}</div></div>'
        )

    abstract_html = "".join(section_card(l, c) for l, c in zip(labels, contexts))

    _ff = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    return (
        f'<div style="font-family:{_ff};border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;margin:8px 0;">'

        # Header
        f'<div style="background:linear-gradient(135deg,#1e3a8a,#3b82f6);padding:16px 20px;">'
        f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px;">'
        f'<span style="background:rgba(255,255,255,.2);color:#fff;font-size:10px;'
        f'font-weight:700;letter-spacing:1.5px;padding:2px 8px;border-radius:4px;">PubMedQA</span>'
        f'<span style="background:rgba(255,255,255,.2);color:#fff;font-size:10px;'
        f'font-weight:700;padding:2px 8px;border-radius:4px;">PMID {pmid}</span>'
        f'<span style="margin-left:auto;background:{decision_col};color:#fff;'
        f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;">✓ {decision}</span>'
        f'</div>'
        f'<div style="color:#fff;font-size:15px;font-weight:700;line-height:1.4;margin-bottom:6px;">{title}</div>'
        f'<div style="color:rgba(255,255,255,.8);font-size:12px;">{authors}</div>'
        f'<div style="color:rgba(255,255,255,.65);font-size:11px;margin-top:2px;">{journal} · {year}</div>'
        f'</div>'

        # MeSH
        f'<div style="padding:10px 16px;background:#f8fafc;border-bottom:1px solid #e2e8f0;">'
        f'<span style="font-size:10px;font-weight:700;color:#94a3b8;letter-spacing:1px;margin-right:6px;">MeSH</span>'
        f'{mesh_tags}</div>'

        # Research question
        f'<div style="padding:12px 16px;background:#fefce8;border-bottom:1px solid #fef08a;">'
        f'<div style="font-size:10px;font-weight:700;color:#854d0e;letter-spacing:1px;margin-bottom:4px;">❓ RESEARCH QUESTION</div>'
        f'<div style="font-size:13px;color:#1c1917;font-weight:500;font-style:italic;">{question}</div>'
        f'</div>'

        # Abstract
        f'<div style="padding:14px 16px;">'
        f'<div style="font-size:10px;font-weight:700;color:#94a3b8;letter-spacing:1px;margin-bottom:10px;">📄 ABSTRACT</div>'
        f'{abstract_html}</div>'

        # Answer
        f'<div style="padding:12px 16px;background:#f0fdf4;border-top:1px solid #bbf7d0;">'
        f'<div style="font-size:10px;font-weight:700;color:#14532d;letter-spacing:1px;margin-bottom:4px;">💡 CONCLUSION / ANSWER</div>'
        f'<div style="font-size:13px;color:#1c1917;line-height:1.7;">{answer}</div>'
        f'</div>'

        f'</div>'
    )


def render_ie_intro() -> str:
    """Brief explainer: what is Information Extraction?"""
    _ff = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    rows = "".join(
        f'<div style="display:flex;gap:10px;align-items:flex-start;'
        f'padding:10px 0;border-bottom:1px solid #f1f5f9;">'
        f'<span style="font-size:18px;line-height:1;">{icon}</span>'
        f'<div><div style="font-size:13px;font-weight:700;color:#0f172a;">{term}</div>'
        f'<div style="font-size:12px;color:#475569;line-height:1.6;margin-top:2px;">{desc}</div></div>'
        f'</div>'
        for icon, term, desc in [
            ("🔍", "Entities",
             "Named things in text — people, organisations, biological processes, diseases, "
             "chemicals, locations. The <em>nodes</em> of your future knowledge graph."),
            ("🔗", "Relations",
             "Verbs or predicates that connect two entities — <em>inhibits</em>, "
             "<em>causes</em>, <em>is-a</em>, <em>part-of</em>. The <em>edges</em> of your graph."),
            ("📐", "Triples (Subject → Predicate → Object)",
             "The atomic unit of a knowledge graph. e.g. "
             "<code>Mitochondria → play role in → programmed cell death</code>. "
             "IE turns unstructured sentences into these structured facts."),
        ]
    )
    return (
        f'<div style="font-family:{_ff};border:1px solid #e2e8f0;border-radius:10px;'
        f'overflow:hidden;margin:8px 0;">'
        f'<div style="background:linear-gradient(135deg,#1e40af,#3b82f6);'
        f'padding:14px 18px;">'
        f'<div style="color:rgba(255,255,255,.75);font-size:10px;font-weight:700;'
        f'letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">Concept</div>'
        f'<div style="color:#fff;font-size:16px;font-weight:700;">Information Extraction</div>'
        f'<div style="color:rgba(255,255,255,.85);font-size:12px;margin-top:3px;">'
        f'Turning unstructured text into structured, queryable facts</div>'
        f'</div>'
        f'<div style="padding:14px 18px;background:#fff;">{rows}</div>'
        f'<div style="padding:10px 18px;background:#eff6ff;border-top:1px solid #dbeafe;">'
        f'<span style="font-size:11px;color:#1e40af;font-weight:600;">Goal for this section: </span>'
        f'<span style="font-size:11px;color:#1e40af;">'
        f'extract triples from the PubMedQA abstract using two complementary strategies — '
        f'schema-guided (OBIE) and schema-free (OpenIE).</span>'
        f'</div>'
        f'</div>'
    )


def render_obie_intro() -> str:
    """Brief explainer: Ontology-Based Information Extraction."""
    _ff = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    steps = [
        ("1", "Define ontology", "A fixed schema of allowed entity types and relation types "
         "(e.g. MeSH: <em>Disease</em>, <em>Gene</em>, <em>Drug</em>, "
         "<em>treats</em>, <em>inhibits</em>)."),
        ("2", "Entity recognition", "Scan the text and tag only tokens that match "
         "ontology entity types — everything else is ignored."),
        ("3", "Relation classification", "For each pair of tagged entities, "
         "predict which ontology relation (if any) connects them."),
        ("4", "Triple output", "Emit only triples whose predicate exists in the schema. "
         "Result: high-precision, schema-consistent facts ready for graph ingestion."),
    ]
    step_html = "".join(
        f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;">'
        f'<span style="flex-shrink:0;width:22px;height:22px;border-radius:50%;'
        f'background:#7c3aed;color:#fff;font-size:11px;font-weight:700;'
        f'display:flex;align-items:center;justify-content:center;">{n}</span>'
        f'<div><span style="font-size:12px;font-weight:700;color:#0f172a;">{title} — </span>'
        f'<span style="font-size:12px;color:#475569;line-height:1.6;">{desc}</span></div>'
        f'</div>'
        for n, title, desc in steps
    )
    return (
        f'<div style="font-family:{_ff};border:1px solid #ddd6fe;border-radius:10px;'
        f'overflow:hidden;margin:8px 0;">'
        f'<div style="background:linear-gradient(135deg,#5b21b6,#7c3aed);padding:14px 18px;">'
        f'<div style="color:rgba(255,255,255,.75);font-size:10px;font-weight:700;'
        f'letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">Strategy A</div>'
        f'<div style="color:#fff;font-size:16px;font-weight:700;">'
        f'Ontology-Based IE (OBIE)</div>'
        f'<div style="color:rgba(255,255,255,.85);font-size:12px;margin-top:3px;">'
        f'Schema-constrained extraction — high precision, closed world</div>'
        f'</div>'
        f'<div style="padding:14px 18px;background:#fff;">{step_html}</div>'
        f'<div style="display:flex;gap:0;border-top:1px solid #ddd6fe;">'
        f'<div style="flex:1;padding:10px 14px;background:#f5f3ff;'
        f'border-right:1px solid #ddd6fe;">'
        f'<div style="font-size:10px;font-weight:700;color:#6d28d9;margin-bottom:3px;">✅ Strengths</div>'
        f'<div style="font-size:11px;color:#4c1d95;line-height:1.7;">'
        f'Consistent schema · Easy to validate · Graph-ready output</div></div>'
        f'<div style="flex:1;padding:10px 14px;background:#faf5ff;">'
        f'<div style="font-size:10px;font-weight:700;color:#6d28d9;margin-bottom:3px;">⚠️ Limits</div>'
        f'<div style="font-size:11px;color:#4c1d95;line-height:1.7;">'
        f'Misses facts outside the ontology · Requires upfront schema design</div></div>'
        f'</div>'
        f'</div>'
    )


def render_openie_intro() -> str:
    """Brief explainer: Open-Domain Information Extraction."""
    _ff = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    steps = [
        ("1", "Parse sentence", "Dependency-parse or chunk the sentence to find "
         "subject–verb–object patterns — no predefined types needed."),
        ("2", "Extract argument spans", "Pull out the subject noun phrase, "
         "the relation verb phrase, and the object noun phrase directly from syntax."),
        ("3", "Normalise", "Lemmatise verbs, resolve basic coreference "
         "(e.g. <em>it</em> → <em>lace plant</em>) and remove stop words."),
        ("4", "Triple output", "Emit the raw (S, P, O) triple. "
         "Result: high-recall, schema-free facts that may need post-processing."),
    ]
    step_html = "".join(
        f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;">'
        f'<span style="flex-shrink:0;width:22px;height:22px;border-radius:50%;'
        f'background:#0d9488;color:#fff;font-size:11px;font-weight:700;'
        f'display:flex;align-items:center;justify-content:center;">{n}</span>'
        f'<div><span style="font-size:12px;font-weight:700;color:#0f172a;">{title} — </span>'
        f'<span style="font-size:12px;color:#475569;line-height:1.6;">{desc}</span></div>'
        f'</div>'
        for n, title, desc in steps
    )
    return (
        f'<div style="font-family:{_ff};border:1px solid #99f6e4;border-radius:10px;'
        f'overflow:hidden;margin:8px 0;">'
        f'<div style="background:linear-gradient(135deg,#0f766e,#0d9488);padding:14px 18px;">'
        f'<div style="color:rgba(255,255,255,.75);font-size:10px;font-weight:700;'
        f'letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">Strategy B</div>'
        f'<div style="color:#fff;font-size:16px;font-weight:700;">'
        f'Open-Domain IE (OpenIE)</div>'
        f'<div style="color:rgba(255,255,255,.85);font-size:12px;margin-top:3px;">'
        f'Schema-free extraction — high recall, open world</div>'
        f'</div>'
        f'<div style="padding:14px 18px;background:#fff;">{step_html}</div>'
        f'<div style="display:flex;gap:0;border-top:1px solid #99f6e4;">'
        f'<div style="flex:1;padding:10px 14px;background:#f0fdfa;'
        f'border-right:1px solid #99f6e4;">'
        f'<div style="font-size:10px;font-weight:700;color:#0f766e;margin-bottom:3px;">✅ Strengths</div>'
        f'<div style="font-size:11px;color:#134e4a;line-height:1.7;">'
        f'No schema needed · Discovers unexpected relations · High recall</div></div>'
        f'<div style="flex:1;padding:10px 14px;background:#f0fdfa;">'
        f'<div style="font-size:10px;font-weight:700;color:#0f766e;margin-bottom:3px;">⚠️ Limits</div>'
        f'<div style="font-size:11px;color:#134e4a;line-height:1.7;">'
        f'Noisy output · Inconsistent predicates · Harder to load into typed graph</div></div>'
        f'</div>'
        f'</div>'
    )


def render_kg(triples: list[dict], strategy: str = "OBIE",
              height: str = "540px", color_by: str | None = None,
              group_colours: dict | None = None) -> str:
    """
    Render extracted KG triples as an interactive knowledge graph, styled after
    professional graph explorers (Neo4j Bloom / Linkurious):
      • force-directed (ForceAtlas2) organic layout
      • nodes coloured by group, sized by degree centrality
      • click a node to focus its neighbourhood (dims everything else)
      • hover for entity / relation detail; scroll to zoom, drag to pan

    Args:
        color_by: "mesh"    → colour nodes by the MeSH concept they map to
                  "section" → colour nodes by abstract section
                  None      → auto ("mesh" for OBIE, "section" otherwise)
    """
    import re, tempfile, pathlib, html as _html
    from pyvis.network import Network

    is_obie  = strategy.upper() == "OBIE"
    accent   = "#7c3aed" if is_obie else "#0d9488"
    hdr_grad = "135deg,#5b21b6,#7c3aed" if is_obie else "135deg,#0f766e,#0d9488"
    _ff      = "Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"

    if color_by is None:
        color_by = "mesh" if is_obie else "section"

    # Fixed colours for abstract sections (keeps OpenIE / section view stable)
    SECTION_COLOURS = {
        "BACKGROUND":  "#6366f1",   # indigo
        "RESULTS":     "#f59e0b",   # amber
        "METHODS":     "#10b981",   # emerald
        "CONCLUSIONS": "#8b5cf6",   # violet
        "OBJECTIVE":   "#06b6d4",   # cyan
    }
    # Generic categorical palette for MeSH concepts (assigned in encounter order)
    GROUP_PALETTE = [
        "#6366f1", "#f59e0b", "#10b981", "#8b5cf6", "#06b6d4",
        "#ec4899", "#f97316", "#0ea5e9", "#a855f7", "#84cc16",
    ]
    OTHER_COL = "#94a3b8"           # slate — un-grouped / no match

    def _darken(hex_col: str) -> str:
        """Return a slightly darker shade for the node border ring."""
        h = hex_col.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        f = 0.72
        return f"#{int(r*f):02x}{int(g*f):02x}{int(b*f):02x}"

    # ── empty-state guard ───────────────────────────────────────────── #
    if not triples:
        return (
            f'<div style="font-family:{_ff};border:1px dashed #cbd5e1;'
            f'border-radius:10px;padding:28px;text-align:center;color:#94a3b8;'
            f'background:#f8fafc;margin:8px 0;">No triples of these types.</div>'
        )

    # ── which triple fields hold the grouping key? ──────────────────── #
    if color_by == "mesh":
        key_s, key_o = "subject_mesh", "object_mesh"
    elif color_by == "type":
        key_s, key_o = "subject_type", "object_type"
    else:  # section — same group for both endpoints of a triple
        key_s = key_o = None

    def _grp(triple: dict, key: str | None) -> str:
        val = (triple.get(key, "") if key else triple.get("section", "")) or ""
        return val.strip()

    # ── node degree + group membership ──────────────────────────────── #
    node_group: dict[str, str] = {}
    node_count: dict[str, int] = {}
    for t in triples:
        for entity, key in ((t["subject"], key_s), (t["object"], key_o)):
            node_count[entity] = node_count.get(entity, 0) + 1
            grp = _grp(t, key)
            if grp and not node_group.get(entity):   # prefer first non-empty
                node_group[entity] = grp
            node_group.setdefault(entity, grp)

    max_count = max(node_count.values(), default=1)

    # If MeSH colouring was requested but nothing mapped, fall back to sections
    if color_by == "mesh" and not any(node_group.values()):
        color_by = "section"
        node_group = {}
        for t in triples:
            for entity in (t["subject"], t["object"]):
                node_group.setdefault(entity, (t.get("section", "") or "").strip())

    # ── assign a colour to every group ──────────────────────────────── #
    # Fixed map for ontology types → both graphs in a pair stay comparable.
    ONTOLOGY_TYPE_COLOURS = {
        "Organism":             "#10b981",   # emerald
        "Anatomical Structure": "#f59e0b",   # amber
        "Cell Component":       "#6366f1",   # indigo
        "Biological Process":   "#8b5cf6",   # violet
    }

    groups_present: list[str] = []
    for g in node_group.values():
        # "Other" / empty are always the grey catch-all, never a palette colour
        if g and g != "Other" and g not in groups_present:
            groups_present.append(g)
    if color_by in ("mesh", "type"):
        groups_present.sort()   # deterministic legend order

    group_colour: dict[str, str] = {}
    for i, g in enumerate(groups_present):
        if group_colours and g in group_colours:      # caller-supplied palette
            group_colour[g] = group_colours[g]
        elif color_by == "section":
            group_colour[g] = SECTION_COLOURS.get(g, GROUP_PALETTE[i % len(GROUP_PALETTE)])
        elif color_by == "type":
            group_colour[g] = ONTOLOGY_TYPE_COLOURS.get(g, GROUP_PALETTE[i % len(GROUP_PALETTE)])
        else:
            group_colour[g] = GROUP_PALETTE[i % len(GROUP_PALETTE)]

    def _colour_for(entity: str) -> str:
        return group_colour.get(node_group.get(entity, ""), OTHER_COL)

    group_label = {"mesh": "MeSH concept", "type": "ontology type"}.get(color_by, "Section")

    # ── build pyvis network ─────────────────────────────────────────── #
    net = Network(
        height=height,
        width="100%",
        directed=True,
        bgcolor="#f8fafc",
        font_color="#1e293b",
        cdn_resources="in_line",
        neighborhood_highlight=True,   # click-to-focus, Bloom-style
    )

    # per-entity metadata for richer tooltips (type guess, MeSH match, score)
    node_meta: dict[str, dict] = {}
    for t in triples:
        for role, ent in (("subject", t["subject"]), ("object", t["object"])):
            meta = node_meta.setdefault(ent, {})
            for field, key in (("guess", f"{role}_type_guess"),
                               ("mesh",  f"{role}_mesh"),
                               ("score", f"{role}_score")):
                v = t.get(key)
                if v not in (None, "") and field not in meta:
                    meta[field] = v

    for entity, count in node_count.items():
        # sqrt scaling → gentler size spread, avoids one giant hub
        size  = 13 + 30 * ((count / max_count) ** 0.5)
        grp   = node_group.get(entity, "") or "—"
        color = _colour_for(entity)
        meta  = node_meta.get(entity, {})

        tip = [f"<b>{entity}</b>", f"{group_label}: {grp}"]
        if meta.get("guess") and meta["guess"] != grp:
            tip.append(f"LLM guessed: {meta['guess']}")
        if meta.get("mesh"):
            sc = meta.get("score")
            sc = f" ({float(sc):.2f})" if isinstance(sc, (int, float)) else ""
            tip.append(f"≈ MeSH: {meta['mesh']}{sc}")
        tip.append(f"Connections: {count}")

        net.add_node(
            entity,
            label=entity,
            size=size,
            color={
                "background": color,
                "border": _darken(color),
                "highlight": {"background": color, "border": accent},
                "hover":     {"background": color, "border": accent},
            },
            title="<br>".join(tip),
            borderWidth=2,
            borderWidthSelected=4,
        )

    for t in triples:
        conf = t.get("confidence", 0.8)
        etip = [f"<b>{t['predicate']}</b>"]
        if t.get("predicate_type"):
            etip.append(f"Relationship type: {t['predicate_type']}")
        etip.append(f"Confidence: {conf:.0%}")
        etip.append(f"<i>“{t.get('sentence', '')[:90]}…”</i>")
        net.add_edge(
            t["subject"],
            t["object"],
            label=t["predicate"],
            width=1.2 + conf * 2.8,               # thicker = higher confidence
            title="<br>".join(etip),
        )

    # ── global vis.js options (ForceAtlas2 + polished node/edge styling) ─ #
    options = """
    {
      "nodes": {
        "shape": "dot",
        "borderWidth": 2,
        "borderWidthSelected": 4,
        "shadow": { "enabled": true, "size": 12, "x": 2, "y": 3,
                    "color": "rgba(15,23,42,0.20)" },
        "font": { "size": 14, "face": "%(ff)s", "color": "#1e293b",
                  "strokeWidth": 5, "strokeColor": "#f8fafc" }
      },
      "edges": {
        "arrows": { "to": { "enabled": true, "scaleFactor": 0.55, "type": "arrow" } },
        "color": { "color": "rgba(100,116,139,0.5)", "highlight": "%(accent)s",
                   "hover": "%(accent)s", "inherit": false },
        "font": { "size": 11, "face": "%(ff)s", "color": "#64748b",
                  "strokeWidth": 5, "strokeColor": "#f8fafc", "align": "middle" },
        "smooth": { "enabled": true, "type": "dynamic", "roundness": 0.5 },
        "hoverWidth": 1.4,
        "selectionWidth": 1.6
      },
      "physics": {
        "enabled": true,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": { "gravitationalConstant": -60, "centralGravity": 0.012,
                              "springLength": 130, "springConstant": 0.08,
                              "damping": 0.55, "avoidOverlap": 0.7 },
        "maxVelocity": 40,
        "minVelocity": 0.6,
        "stabilization": { "enabled": true, "iterations": 240,
                           "updateInterval": 25, "fit": true }
      },
      "interaction": {
        "hover": true,
        "hoverConnectedEdges": true,
        "tooltipDelay": 120,
        "navigationButtons": false,
        "keyboard": false,
        "multiselect": false,
        "zoomView": true,
        "dragView": true
      }
    }
    """ % {"accent": accent, "ff": _ff}
    net.set_options(options)

    # ── render pyvis to a full HTML document ──────────────────────────── #
    import uuid
    uid = "kg_" + uuid.uuid4().hex[:8]   # unique per render (defensive)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        tmp = pathlib.Path(f.name)
    net.save_graph(str(tmp))
    full_html = tmp.read_text()
    tmp.unlink(missing_ok=True)

    # Give the canvas a unique id (div id / CSS selector / JS getElementById)
    for old, new in (
        ('"mynetwork"', f'"{uid}"'),
        ("'mynetwork'", f"'{uid}'"),
        ("#mynetwork",  f"#{uid}"),
    ):
        full_html = full_html.replace(old, new)

    # ── legend badges (one per group, counting NODES) ─────────────────── #
    group_node_count: dict[str, int] = {}
    for entity in node_count:
        g = node_group.get(entity, "") or "Other"
        group_node_count[g] = group_node_count.get(g, 0) + 1

    # order: known groups first (legend order), then any "Other" bucket last
    ordered_groups = [g for g in groups_present if g in group_node_count]
    if "Other" in group_node_count:
        ordered_groups.append("Other")

    badges = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;'
        f'background:rgba(255,255,255,.15);border-radius:20px;padding:3px 10px;'
        f'font-size:11px;color:rgba(255,255,255,.9);margin:2px;">'
        f'<span style="width:9px;height:9px;border-radius:50%;'
        f'background:{group_colour.get(g, OTHER_COL)};'
        f'border:1px solid rgba(255,255,255,.4);display:inline-block;"></span>'
        f'{g}: {group_node_count[g]} node{"s" if group_node_count[g] != 1 else ""}</span>'
        for g in ordered_groups
    )

    header_bar = (
        f'<div style="font-family:{_ff};background:linear-gradient({hdr_grad});'
        f'padding:14px 18px;">'
        f'<div style="color:rgba(255,255,255,.75);font-size:10px;font-weight:700;'
        f'letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">'
        f'Knowledge Graph · coloured by {group_label}</div>'
        f'<div style="color:#fff;font-size:16px;font-weight:700;">'
        f'{strategy} — {len(triples)} triple{"s" if len(triples) != 1 else ""} · '
        f'{len(node_count)} node{"s" if len(node_count) != 1 else ""}</div>'
        f'<div style="margin-top:8px;">{badges}</div>'
        f'</div>'
    )
    footer_bar = (
        f'<div style="font-family:{_ff};padding:9px 18px;background:#fff;'
        f'border-top:1px solid #e2e8f0;">'
        f'<span style="font-size:11px;color:#94a3b8;">'
        f'Node size = degree · Edge thickness = confidence · '
        f'<b style="color:#64748b;">Click a node</b> to focus its neighbourhood · '
        f'Scroll to zoom · Drag to pan</span>'
        f'</div>'
    )

    # Inject header/footer into the document body + kill default body margin
    full_html = full_html.replace(
        "</head>", "<style>html,body{margin:0;padding:0;}</style></head>", 1)
    full_html = full_html.replace("<body>", f"<body>{header_bar}", 1)
    full_html = full_html.replace("</body>", f"{footer_bar}</body>", 1)

    # ── wrap in an iframe via srcdoc ──────────────────────────────────── #
    # display(HTML(...)) injects via innerHTML, and inline <script> tags do
    # NOT execute when inserted that way — so vis.js never runs and the canvas
    # stays blank.  An iframe's srcdoc is parsed as its own document, so its
    # scripts DO execute regardless of how the iframe was inserted.  This is
    # exactly how pyvis's own .show() renders in notebooks, and it is Colab-safe
    # and fully self-contained (vis.js is inlined, no CDN needed).
    m = re.search(r"(\d+)", height)
    graph_px = int(m.group(1)) if m else 520
    frame_px = graph_px + 160   # room for header + footer

    srcdoc = _html.escape(full_html, quote=True)
    return (
        f'<iframe srcdoc="{srcdoc}" '
        f'style="width:100%;height:{frame_px}px;border:1px solid #e2e8f0;'
        f'border-radius:10px;box-sizing:border-box;background:#f8fafc;" '
        f'frameborder="0" scrolling="no"></iframe>'
    )


def render_kg_pair(left_triples: list[dict], right_triples: list[dict], *,
                   left_title: str = "OBIE", right_title: str = "OpenIE",
                   color_by: str = "type", height: str = "400px") -> str:
    """
    Render two knowledge graphs side by side for direct comparison.
    Both use the same `color_by` scheme so identical groups share a colour
    (essential when comparing OBIE vs a type-filtered OpenIE graph).
    """
    _ff  = "Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    left  = render_kg(left_triples,  strategy=left_title,  height=height, color_by=color_by)
    right = render_kg(right_triples, strategy=right_title, height=height, color_by=color_by)
    return (
        f'<div style="font-family:{_ff};display:flex;gap:12px;align-items:stretch;'
        f'flex-wrap:wrap;margin:8px 0;">'
        f'<div style="flex:1 1 320px;min-width:300px;">{left}</div>'
        f'<div style="flex:1 1 320px;min-width:300px;">{right}</div>'
        f'</div>'
    )


def render_ontology(types: list[dict]) -> str:
    """
    Explain the ontological types behind OBIE — each grounded in a UMLS
    Semantic Type and cross-referenced to the MeSH descriptor(s) that
    instantiate it in this abstract.
    """
    _ff = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    TYPE_COLOURS = {
        "Organism":             "#10b981",
        "Anatomical Structure": "#f59e0b",
        "Cell Component":       "#6366f1",
        "Biological Process":   "#8b5cf6",
    }

    rows = ""
    for t in types:
        col   = TYPE_COLOURS.get(t["type"], "#64748b")
        meshes = "".join(
            f'<span style="display:inline-block;background:#f1f5f9;border:1px solid #e2e8f0;'
            f'border-radius:20px;padding:1px 9px;font-size:11px;color:#475569;'
            f'margin:2px 3px 0 0;">{m}</span>'
            for m in t["mesh"]
        )
        rows += (
            f'<div style="display:flex;gap:12px;align-items:flex-start;'
            f'padding:12px 0;border-bottom:1px solid #f1f5f9;">'
            # colour chip + type name
            f'<div style="flex-shrink:0;width:150px;">'
            f'<span style="display:inline-flex;align-items:center;gap:7px;">'
            f'<span style="width:12px;height:12px;border-radius:50%;background:{col};'
            f'border:2px solid #fff;box-shadow:0 0 0 1px {col};display:inline-block;"></span>'
            f'<span style="font-size:13px;font-weight:700;color:#0f172a;">{t["type"]}</span>'
            f'</span>'
            f'<div style="font-size:10px;color:#94a3b8;font-weight:700;letter-spacing:.5px;'
            f'margin-top:3px;margin-left:19px;">UMLS {t["umls"]}</div>'
            f'</div>'
            # reason + mesh
            f'<div style="flex:1;">'
            f'<div style="font-size:12px;color:#475569;line-height:1.6;">{t["reason"]}</div>'
            f'<div style="margin-top:5px;">'
            f'<span style="font-size:10px;color:#94a3b8;font-weight:700;'
            f'letter-spacing:.5px;margin-right:4px;">MeSH</span>{meshes}</div>'
            f'</div>'
            f'</div>'
        )

    return (
        f'<div style="font-family:{_ff};border:1px solid #ddd6fe;border-radius:10px;'
        f'overflow:hidden;margin:8px 0;">'
        f'<div style="background:linear-gradient(135deg,#5b21b6,#7c3aed);padding:14px 18px;">'
        f'<div style="color:rgba(255,255,255,.75);font-size:10px;font-weight:700;'
        f'letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">Ontology</div>'
        f'<div style="color:#fff;font-size:16px;font-weight:700;">'
        f'Ontological types for this abstract</div>'
        f'<div style="color:rgba(255,255,255,.85);font-size:12px;margin-top:3px;">'
        f'The 5 MeSH descriptors collapse into {len(types)} UMLS semantic types — '
        f'the schema OBIE extracts against</div>'
        f'</div>'
        f'<div style="padding:6px 18px 12px;background:#fff;">{rows}</div>'
        f'<div style="padding:10px 18px;background:#f5f3ff;border-top:1px solid #ddd6fe;">'
        f'<span style="font-size:11px;color:#4c1d95;">'
        f'<b>Key idea:</b> if we tag every entity with its ontological type — even the '
        f'schema-free OpenIE ones — we can filter OpenIE down to just these types and '
        f'recover the same scope as OBIE.</span>'
        f'</div>'
        f'</div>'
    )


def render_grounding(rows: list[dict], threshold: float = 0.8,
                     model_name: str = "BioLORD-2023-C") -> str:
    """
    Show how a biomedical embedding model grounds each OpenIE entity to the MeSH
    ontology: nearest MeSH heading, cosine similarity, and the ontological type
    adopted when similarity clears the threshold.
    """
    _ff = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    TYPE_COLOURS = {
        "Organism": "#10b981", "Anatomical Structure": "#f59e0b",
        "Cell Component": "#6366f1", "Biological Process": "#8b5cf6",
    }

    def _bar(score: float, passed: bool) -> str:
        pct = max(0, min(100, int(score * 100)))
        col = "#10b981" if passed else "#cbd5e1"
        return (
            f'<div style="display:flex;align-items:center;gap:6px;">'
            f'<div style="flex:1;height:6px;background:#f1f5f9;border-radius:3px;'
            f'overflow:hidden;min-width:60px;">'
            f'<div style="width:{pct}%;height:100%;background:{col};"></div></div>'
            f'<span style="font-size:11px;color:#475569;font-variant-numeric:tabular-nums;">'
            f'{score:.2f}</span></div>'
        )

    body = ""
    for r in rows:
        passed = r["via"].startswith("embedding") or r["via"] == "exact MeSH tag"
        mtype  = r["mapped_type"]
        chip_col = TYPE_COLOURS.get(mtype, "#94a3b8")
        type_chip = (
            f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:11px;'
            f'color:#334155;"><span style="width:9px;height:9px;border-radius:50%;'
            f'background:{chip_col};display:inline-block;"></span>{mtype}</span>'
            if mtype != "Other" else
            f'<span style="font-size:11px;color:#94a3b8;">Other (dropped)</span>'
        )
        body += (
            f'<tr style="border-bottom:1px solid #f1f5f9;'
            f'{"background:#f0fdf4;" if passed and mtype!="Other" else ""}">'
            f'<td style="padding:6px 10px;font-size:12px;color:#0f172a;">{r["entity"]}</td>'
            f'<td style="padding:6px 10px;font-size:11px;color:#94a3b8;">{r["guess"] or "—"}</td>'
            f'<td style="padding:6px 10px;font-size:12px;color:#475569;">{r["mesh"] or "—"}</td>'
            f'<td style="padding:6px 10px;width:130px;">{_bar(r["score"], passed)}</td>'
            f'<td style="padding:6px 10px;">{type_chip}</td>'
            f'</tr>'
        )

    mapped = sum(1 for r in rows if r["mapped_type"] != "Other")
    return (
        f'<div style="font-family:{_ff};border:1px solid #99f6e4;border-radius:10px;'
        f'overflow:hidden;margin:8px 0;">'
        f'<div style="background:linear-gradient(135deg,#0f766e,#0d9488);padding:14px 18px;">'
        f'<div style="color:rgba(255,255,255,.75);font-size:10px;font-weight:700;'
        f'letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">'
        f'Embedding grounding · {model_name}</div>'
        f'<div style="color:#fff;font-size:16px;font-weight:700;">'
        f'Aligning OpenIE entities to the MeSH ontology</div>'
        f'<div style="color:rgba(255,255,255,.85);font-size:12px;margin-top:3px;">'
        f'cosine ≥ {threshold:g} ⇒ same concept ⇒ adopt that heading\'s type · '
        f'{mapped}/{len(rows)} entities mapped</div>'
        f'</div>'
        f'<div style="max-height:320px;overflow:auto;background:#fff;">'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<thead><tr style="position:sticky;top:0;background:#f8fafc;">'
        f'<th style="text-align:left;padding:8px 10px;font-size:10px;color:#94a3b8;'
        f'letter-spacing:1px;">ENTITY</th>'
        f'<th style="text-align:left;padding:8px 10px;font-size:10px;color:#94a3b8;'
        f'letter-spacing:1px;">LLM GUESS</th>'
        f'<th style="text-align:left;padding:8px 10px;font-size:10px;color:#94a3b8;'
        f'letter-spacing:1px;">NEAREST MeSH</th>'
        f'<th style="text-align:left;padding:8px 10px;font-size:10px;color:#94a3b8;'
        f'letter-spacing:1px;">SIMILARITY</th>'
        f'<th style="text-align:left;padding:8px 10px;font-size:10px;color:#94a3b8;'
        f'letter-spacing:1px;">→ ONTOLOGY TYPE</th>'
        f'</tr></thead><tbody>{body}</tbody></table></div>'
        f'</div>'
    )


def render_abstract_comparison(original: str, reconstructed: str,
                               similarity: float,
                               model_name: str = "all-MiniLM-L6-v2") -> str:
    """
    Show the original abstract next to the abstract reconstructed from triples
    (back-translation), with a cosine-similarity badge between them.
    """
    _ff = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    if similarity >= 0.8:
        sim_col, verdict = "#059669", "high fidelity"
    elif similarity >= 0.6:
        sim_col, verdict = "#d97706", "partial fidelity"
    else:
        sim_col, verdict = "#dc2626", "low fidelity"

    def _panel(title, text, accent, bg):
        return (
            f'<div style="flex:1 1 300px;min-width:280px;border:1px solid #e2e8f0;'
            f'border-radius:10px;overflow:hidden;">'
            f'<div style="background:{accent};padding:8px 14px;color:#fff;'
            f'font-size:11px;font-weight:700;letter-spacing:1px;">{title}</div>'
            f'<div style="padding:12px 14px;font-size:12.5px;line-height:1.65;'
            f'color:#1e293b;background:{bg};max-height:280px;overflow:auto;">{text}</div>'
            f'</div>'
        )

    return (
        f'<div style="font-family:{_ff};margin:8px 0;">'
        # similarity banner
        f'<div style="display:flex;align-items:center;gap:12px;background:#f8fafc;'
        f'border:1px solid #e2e8f0;border-radius:10px;padding:10px 16px;margin-bottom:10px;">'
        f'<div style="font-size:11px;color:#64748b;">Back-translation cosine similarity '
        f'<span style="color:#94a3b8;">({model_name})</span></div>'
        f'<div style="margin-left:auto;display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:22px;font-weight:800;color:{sim_col};'
        f'font-variant-numeric:tabular-nums;">{similarity:.2f}</span>'
        f'<span style="background:{sim_col};color:#fff;font-size:10px;font-weight:700;'
        f'padding:2px 9px;border-radius:20px;text-transform:uppercase;">{verdict}</span>'
        f'</div></div>'
        # two panels
        f'<div style="display:flex;gap:12px;flex-wrap:wrap;align-items:stretch;">'
        f'{_panel("📄 ORIGINAL ABSTRACT", original, "#1e3a8a", "#fff")}'
        f'{_panel("🔁 RECONSTRUCTED FROM OPENIE TRIPLES", reconstructed, "#0f766e", "#f0fdfa")}'
        f'</div>'
        f'</div>'
    )


_FF = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
_TYPE_COLOURS = {
    "Organism": "#10b981", "Anatomical Structure": "#f59e0b",
    "Cell Component": "#6366f1", "Biological Process": "#8b5cf6",
}


def _card(header_grad: str, kicker: str, title: str, subtitle: str, body: str,
          footer: str = "") -> str:
    foot = (f'<div style="padding:10px 18px;background:#f8fafc;'
            f'border-top:1px solid #e2e8f0;font-size:11px;color:#64748b;">{footer}</div>'
            if footer else "")
    return (
        f'<div style="font-family:{_FF};border:1px solid #e2e8f0;border-radius:10px;'
        f'overflow:hidden;margin:8px 0;">'
        f'<div style="background:linear-gradient({header_grad});padding:14px 18px;">'
        f'<div style="color:rgba(255,255,255,.75);font-size:10px;font-weight:700;'
        f'letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">{kicker}</div>'
        f'<div style="color:#fff;font-size:16px;font-weight:700;">{title}</div>'
        f'<div style="color:rgba(255,255,255,.85);font-size:12px;margin-top:3px;">{subtitle}</div>'
        f'</div><div style="padding:14px 18px;background:#fff;">{body}</div>{foot}</div>'
    )


def render_kr_intro() -> str:
    """Framing card: from a bag of triples to a formal property graph."""
    levers = [
        ("🔗", "Disambiguation",
         "Many surface forms name the <em>same</em> entity — merge them into one canonical node."),
        ("➡️", "Directionality",
         "Edges are directed; <em>causes</em> ≠ <em>caused by</em>. Some relations are symmetric."),
        ("⏱️", "Temporality",
         "Facts can be scoped to a stage or time window (early vs late PCD)."),
        ("🏷️", "Properties & provenance",
         "Every node & edge carries metadata: type, confidence, source sentence, section."),
    ]
    rows = "".join(
        f'<div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;'
        f'border-bottom:1px solid #f1f5f9;">'
        f'<span style="font-size:17px;line-height:1.2;">{ic}</span>'
        f'<div><span style="font-size:13px;font-weight:700;color:#0f172a;">{t}</span>'
        f'<div style="font-size:12px;color:#475569;line-height:1.6;margin-top:1px;">{d}</div></div></div>'
        for ic, t, d in levers
    )
    body = (
        '<div style="font-size:12.5px;color:#475569;line-height:1.7;margin-bottom:8px;">'
        'Extraction gave us a <b>bag of triples</b>. A knowledge graph is a '
        '<b>property graph</b>: typed nodes and directed, labelled edges, each carrying '
        'properties. Turning noisy triples into a clean, queryable graph rests on four '
        'design levers:</div>' + rows
    )
    return _card("135deg,#5b21b6,#7c3aed", "Knowledge Representation",
                 "From triples to a property graph",
                 "The design levers that make a graph queryable & trustworthy", body)


def render_disambiguation(clusters: list[dict], n_before: int, n_after: int,
                          threshold: float = 0.9) -> str:
    """Show entity-merge clusters produced by canonicalisation."""
    reduction = n_before - n_after
    pct = int(100 * reduction / n_before) if n_before else 0
    if clusters:
        rows = "".join(
            f'<tr style="border-bottom:1px solid #f1f5f9;">'
            f'<td style="padding:7px 10px;font-size:12.5px;font-weight:700;color:#0f172a;'
            f'white-space:nowrap;">{_h.escape(c["canonical"])}</td>'
            f'<td style="padding:7px 10px;">' +
            "".join(
                f'<span style="display:inline-block;background:#f1f5f9;border:1px solid #e2e8f0;'
                f'border-radius:20px;padding:1px 9px;font-size:11px;color:#475569;margin:2px 3px 0 0;">'
                f'{_h.escape(m)}</span>'
                for m in c["members"] if m != c["canonical"]
            ) +
            f'</td>'
            f'<td style="padding:7px 10px;font-size:12px;color:#64748b;text-align:right;">'
            f'{c["size"]}&nbsp;forms</td></tr>'
            for c in clusters
        )
        table = (
            '<table style="width:100%;border-collapse:collapse;">'
            '<thead><tr style="background:#f8fafc;">'
            '<th style="text-align:left;padding:7px 10px;font-size:10px;color:#94a3b8;letter-spacing:1px;">CANONICAL NODE</th>'
            '<th style="text-align:left;padding:7px 10px;font-size:10px;color:#94a3b8;letter-spacing:1px;">MERGED SURFACE FORMS</th>'
            '<th style="text-align:right;padding:7px 10px;font-size:10px;color:#94a3b8;letter-spacing:1px;"></th>'
            f'</tr></thead><tbody>{rows}</tbody></table>'
        )
    else:
        table = ('<div style="font-size:12px;color:#94a3b8;padding:8px 0;">'
                 'No duplicate surface forms merged at this threshold.</div>')

    body = (
        f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">'
        f'<div style="font-size:26px;font-weight:800;color:#0f172a;">{n_before}'
        f'<span style="color:#cbd5e1;font-weight:400;"> → </span>{n_after}</div>'
        f'<div style="font-size:12px;color:#475569;">unique entities after merging '
        f'<b style="color:#0d9488;">(−{reduction}, {pct}% fewer)</b><br>'
        f'<span style="color:#94a3b8;">lexical + embedding similarity ≥ {threshold:g}</span></div>'
        f'</div>{table}'
    )
    return _card("135deg,#0f766e,#0d9488", "Entity Disambiguation",
                 "Merging duplicate entities into canonical nodes",
                 "A graph with duplicate nodes is fragmented and un-queryable", body)


def render_graph_design() -> str:
    """Explain the four property-graph design facets."""
    facets = [
        ("Properties", "#6366f1",
         "Attributes attached to nodes (type, mention count, MeSH id) and edges "
         "(confidence, relationship type). They make the graph <em>self-describing</em>."),
        ("Directionality", "#8b5cf6",
         "Edges point A→B with meaning. <em>mitochondria → play role in → PCD</em> is not "
         "the same as the reverse. Symmetric relations (is-associated-with) are flagged."),
        ("Temporal", "#0ea5e9",
         "Some facts hold only within a window — early vs late PCD, developmental stages. "
         "Edges can carry a temporal scope."),
        ("Metadata / provenance", "#0d9488",
         "Every edge remembers <em>where it came from</em>: the source sentence, section and "
         "extraction confidence — essential for trust and debugging."),
    ]
    cards = "".join(
        f'<div style="flex:1 1 220px;min-width:200px;border:1px solid #e2e8f0;'
        f'border-left:4px solid {col};border-radius:6px;padding:10px 12px;">'
        f'<div style="font-size:12.5px;font-weight:700;color:#0f172a;margin-bottom:2px;">{name}</div>'
        f'<div style="font-size:11.5px;color:#475569;line-height:1.55;">{desc}</div></div>'
        for name, col, desc in facets
    )
    body = (f'<div style="display:flex;gap:10px;flex-wrap:wrap;">{cards}</div>')
    return _card("135deg,#5b21b6,#7c3aed", "Graph Design",
                 "What turns a triple store into a good knowledge graph",
                 "Four structural decisions applied to every node and edge", body)


def render_edge_anatomy(edge: dict) -> str:
    """Show a single relationship as a full property bag."""
    s, p, o = edge["subject"], edge["predicate"], edge["object"]
    prov = edge.get("provenance") or ([edge["sentence"]] if edge.get("sentence") else [])
    prov_txt = _h.escape(prov[0][:140] + "…") if prov else "—"
    props = [
        ("relationship type", edge.get("predicate_type") or "—"),
        ("confidence", f'{float(edge.get("confidence", 0)):.0%}'),
        ("directionality", "symmetric ↔" if edge.get("symmetric") else "directed →"),
        ("temporal scope", edge.get("temporal") or "—"),
        ("source section", edge.get("section") or "—"),
        ("provenance mentions", str(edge.get("provenance_count", len(prov)))),
    ]
    prop_rows = "".join(
        f'<tr><td style="padding:4px 10px;font-size:11px;color:#94a3b8;'
        f'white-space:nowrap;">{k}</td>'
        f'<td style="padding:4px 10px;font-size:12px;color:#1e293b;font-weight:600;">{_h.escape(str(v))}</td></tr>'
        for k, v in props
    )
    triple_viz = (
        f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;'
        f'justify-content:center;background:#f8fafc;border-radius:8px;padding:14px;margin-bottom:12px;">'
        f'<span style="background:#6366f1;color:#fff;font-size:12px;font-weight:700;'
        f'padding:6px 12px;border-radius:20px;">{_h.escape(s)}</span>'
        f'<span style="font-size:11px;color:#64748b;">— {_h.escape(p)} →</span>'
        f'<span style="background:#8b5cf6;color:#fff;font-size:12px;font-weight:700;'
        f'padding:6px 12px;border-radius:20px;">{_h.escape(o)}</span></div>'
    )
    body = (
        triple_viz +
        f'<table style="width:100%;border-collapse:collapse;">{prop_rows}</table>'
        f'<div style="margin-top:10px;padding:8px 10px;background:#f0fdfa;border-radius:6px;'
        f'font-size:11.5px;color:#134e4a;line-height:1.5;"><b>Provenance:</b> '
        f'<i>“{prov_txt}”</i></div>'
    )
    return _card("135deg,#3730a3,#4f46e5", "Anatomy of an edge",
                 "One relationship, fully described",
                 "Properties · directionality · temporal scope · provenance", body)


def render_graph_stats(stats: dict) -> str:
    """A compact statistics dashboard for the consolidated graph."""
    def stat(label, value, col="#0f172a"):
        return (f'<div style="flex:1 1 90px;text-align:center;padding:8px 4px;">'
                f'<div style="font-size:22px;font-weight:800;color:{col};">{value}</div>'
                f'<div style="font-size:10px;color:#94a3b8;letter-spacing:.5px;'
                f'text-transform:uppercase;">{label}</div></div>')
    kpis = (
        f'<div style="display:flex;flex-wrap:wrap;gap:6px;background:#f8fafc;'
        f'border-radius:8px;padding:6px;margin-bottom:12px;">'
        f'{stat("nodes", stats["nodes"])}{stat("edges", stats["edges"])}'
        f'{stat("density", f"{stats['density']:.2f}")}'
        f'{stat("symmetric", stats["symmetric_edges"], "#8b5cf6")}'
        f'{stat("temporal", stats["temporal_edges"], "#0ea5e9")}</div>'
    )
    type_chips = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;background:#f1f5f9;'
        f'border-radius:20px;padding:2px 10px;font-size:11px;color:#475569;margin:2px;">'
        f'<span style="width:9px;height:9px;border-radius:50%;'
        f'background:{_TYPE_COLOURS.get(t, "#94a3b8")};display:inline-block;"></span>'
        f'{t}: {n}</span>'
        for t, n in stats["types"].items()
    )
    max_deg = stats["top"][0][1] if stats["top"] else 1
    hubs = "".join(
        f'<div style="display:flex;align-items:center;gap:8px;margin:3px 0;">'
        f'<span style="width:150px;font-size:12px;color:#1e293b;overflow:hidden;'
        f'text-overflow:ellipsis;white-space:nowrap;">{_h.escape(name)}</span>'
        f'<div style="flex:1;height:8px;background:#f1f5f9;border-radius:4px;overflow:hidden;">'
        f'<div style="width:{int(100*deg/max_deg)}%;height:100%;background:#7c3aed;"></div></div>'
        f'<span style="font-size:11px;color:#64748b;width:20px;text-align:right;">{deg}</span></div>'
        for name, deg in stats["top"]
    )
    body = (
        kpis +
        f'<div style="font-size:10px;color:#94a3b8;letter-spacing:1px;margin-bottom:4px;">NODE TYPES</div>'
        f'<div style="margin-bottom:12px;">{type_chips}</div>'
        f'<div style="font-size:10px;color:#94a3b8;letter-spacing:1px;margin-bottom:6px;">'
        f'MOST-CONNECTED ENTITIES (hubs)</div>{hubs}'
    )
    return _card("135deg,#334155,#475569", "Graph statistics",
                 "The consolidated knowledge graph at a glance",
                 "Hubs are the entities the abstract is really 'about'", body)


def render_query_panel(node: str, neighbour_rows: list[dict],
                       path_hops: list[tuple]) -> str:
    """Show a couple of graph queries: neighbours of a node and a multi-hop path."""
    nb = "".join(
        f'<div style="display:flex;align-items:center;gap:8px;padding:3px 0;font-size:12px;">'
        f'<span style="font-size:13px;color:{"#0d9488" if r["dir"]=="out" else "#7c3aed"};">'
        f'{"→" if r["dir"]=="out" else "←"}</span>'
        f'<span style="color:#64748b;font-style:italic;">{_h.escape(r["predicate"])}</span>'
        f'<span style="color:#0f172a;font-weight:600;">{_h.escape(r["other"])}</span></div>'
        for r in neighbour_rows[:8]
    ) or '<div style="font-size:12px;color:#94a3b8;">no neighbours</div>'

    if path_hops:
        chain = ""
        chain += (f'<span style="background:#6366f1;color:#fff;font-size:11px;font-weight:700;'
                  f'padding:4px 10px;border-radius:16px;">{_h.escape(path_hops[0][0])}</span>')
        for a, pred, b in path_hops:
            chain += (f'<span style="font-size:10px;color:#94a3b8;white-space:nowrap;"> ─{_h.escape(pred)}→ </span>'
                      f'<span style="background:#8b5cf6;color:#fff;font-size:11px;font-weight:700;'
                      f'padding:4px 10px;border-radius:16px;">{_h.escape(b)}</span>')
        path_html = (f'<div style="display:flex;align-items:center;gap:4px;flex-wrap:wrap;'
                     f'line-height:2.1;">{chain}</div>')
    else:
        path_html = '<div style="font-size:12px;color:#94a3b8;">no connecting path found</div>'

    body = (
        f'<div style="font-size:11px;color:#94a3b8;letter-spacing:1px;margin-bottom:4px;">'
        f'NEIGHBOURS OF <b style="color:#0f172a;">{_h.escape(node)}</b></div>'
        f'<div style="margin-bottom:14px;">{nb}</div>'
        f'<div style="font-size:11px;color:#94a3b8;letter-spacing:1px;margin-bottom:6px;">'
        f'MULTI-HOP PATH  <span style="color:#cbd5e1;">(reasoning flat text can\'t do)</span></div>'
        f'{path_html}'
    )
    return _card("135deg,#0369a1,#0ea5e9", "Querying the graph",
                 "Why we built it: traverse relationships",
                 "Neighbourhoods and multi-hop connections become one-line queries", body)


def render_code_block(code: str, title: str = "Neo4j Cypher",
                      subtitle: str = "The same graph, ready to persist & query") -> str:
    """Dark monospace card for exported code (e.g. Cypher)."""
    esc = _h.escape(code)
    esc = esc.replace("CREATE", '<span style="color:#c792ea;">CREATE</span>')
    esc = re.sub(r'(//[^\n]*)', r'<span style="color:#5c6370;">\1</span>', esc)
    body = (
        f'<pre style="margin:0;background:#0f172a;color:#e2e8f0;border-radius:8px;'
        f'padding:14px 16px;font-size:11.5px;line-height:1.6;overflow:auto;max-height:340px;'
        f'font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;">{esc}</pre>'
    )
    return _card("135deg,#064e3b,#059669", "Export", title, subtitle, body)


def render_takeaways() -> str:
    """Closing summary of the A.2 knowledge-graph journey."""
    steps = [
        ("1", "Extract", "OBIE (ontology-guided) vs OpenIE (schema-free) triples from the abstract."),
        ("2", "Type & ground", "LLM guesses + BioLORD embeddings map entities to MeSH ontology types."),
        ("3", "Validate", "Back-translation + STS-B calibration measure how faithful the triples are."),
        ("4", "Disambiguate", "Merge duplicate surface forms into canonical nodes."),
        ("5", "Design & build", "Directed, typed, temporally-scoped edges with provenance metadata."),
        ("6", "Query & export", "Traverse multi-hop relationships; persist as Neo4j Cypher."),
    ]
    rows = "".join(
        f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:8px;">'
        f'<span style="flex-shrink:0;width:22px;height:22px;border-radius:50%;background:#7c3aed;'
        f'color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;'
        f'justify-content:center;">{n}</span>'
        f'<div><span style="font-size:12.5px;font-weight:700;color:#0f172a;">{t} — </span>'
        f'<span style="font-size:12.5px;color:#475569;line-height:1.6;">{d}</span></div></div>'
        for n, t, d in steps
    )
    body = (
        '<div style="font-size:12.5px;color:#475569;line-height:1.7;margin-bottom:10px;">'
        'You took an unstructured biomedical abstract all the way to a clean, typed, '
        'queryable knowledge graph — the full <b>KG generation pipeline</b>:</div>' + rows +
        '<div style="margin-top:10px;padding:9px 12px;background:#f5f3ff;border-radius:6px;'
        'font-size:11.5px;color:#4c1d95;line-height:1.6;"><b>The pay-off:</b> the graph makes '
        'relationships <em>explicit and traversable</em> — the foundation a KG-RAG system '
        'retrieves over to reason across facts and resist misinformation.</div>'
    )
    return _card("135deg,#5b21b6,#7c3aed", "Wrap-up", "What you built in Hands-on A.2",
                 "From raw text to a queryable knowledge graph", body)


# ══════════════════════════════════════════════════════════════════════ #
#  Hands-on B — murder-mystery KG-RAG                                       #
# ══════════════════════════════════════════════════════════════════════ #

def render_case_file(case: dict) -> str:
    facts = (
        '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;">'
        + "".join(
            f'<div style="flex:1 1 110px;background:#f8fafc;border-radius:8px;'
            f'padding:10px 12px;text-align:center;">'
            f'<div style="font-size:10px;color:#94a3b8;text-transform:uppercase;'
            f'letter-spacing:.5px;">{k}</div>'
            f'<div style="font-size:13px;font-weight:700;color:#0f172a;margin-top:2px;">{_h.escape(v)}</div></div>'
            for k, v in [("Victim", case["victim"]), ("Scene", case["scene"]),
                         ("Time", case["time"]), ("Weapon", "❓ unknown")])
        + '</div>'
    )
    suspects = "".join(
        f'<div style="flex:1 1 180px;min-width:165px;border:1px solid #e2e8f0;'
        f'border-left:4px solid #ef4444;border-radius:6px;padding:10px 12px;">'
        f'<div style="font-size:13px;font-weight:700;color:#0f172a;">{s["emoji"]} {_h.escape(s["name"])}</div>'
        f'<div style="font-size:10px;color:#94a3b8;text-transform:uppercase;'
        f'letter-spacing:.5px;margin-bottom:5px;">{_h.escape(s["role"])}</div>'
        f'<div style="font-size:11px;color:#334155;line-height:1.5;">'
        f'<b style="color:#b91c1c;">Motive:</b> {_h.escape(s["motive"])}</div>'
        f'<div style="font-size:11px;color:#334155;line-height:1.5;margin-top:3px;">'
        f'<b style="color:#0d9488;">Alibi:</b> {_h.escape(s["alibi"])}</div></div>'
        for s in case["suspects"]
    )
    body = (
        facts +
        '<div style="font-size:11px;color:#94a3b8;letter-spacing:1px;margin-bottom:8px;">THE FIVE SUSPECTS</div>'
        f'<div style="display:flex;gap:10px;flex-wrap:wrap;">{suspects}</div>'
    )
    return _card("135deg,#7f1d1d,#b91c1c", "Case File", case["title"],
                 "A guest was murdered — one of five suspects did it. The graph knows who.", body)


def render_retrieval(question: str, results: list[dict]) -> str:
    rows = "".join(
        f'<div style="display:flex;align-items:center;gap:10px;padding:5px 0;'
        f'border-bottom:1px solid #f1f5f9;">'
        f'<div style="width:54px;flex-shrink:0;">'
        f'<div style="height:6px;background:#f1f5f9;border-radius:3px;overflow:hidden;">'
        f'<div style="width:{int(max(0, min(1, r["score"]))*100)}%;height:100%;background:#3b82f6;"></div></div>'
        f'<div style="font-size:10px;color:#64748b;text-align:center;margin-top:1px;">{r["score"]:.2f}</div></div>'
        f'<div style="font-size:12px;color:#1e293b;line-height:1.5;">{_h.escape(r["clue"])}</div></div>'
        for r in results
    )
    body = (
        f'<div style="background:#eff6ff;border-radius:8px;padding:10px 14px;margin-bottom:12px;">'
        f'<span style="font-size:10px;color:#1e40af;font-weight:700;letter-spacing:1px;">QUESTION</span>'
        f'<div style="font-size:13px;color:#1e3a8a;font-weight:600;margin-top:2px;">{_h.escape(question)}</div></div>'
        f'<div style="font-size:10px;color:#94a3b8;letter-spacing:1px;margin-bottom:4px;">'
        f'TOP RETRIEVED FACTS (cosine similarity)</div>{rows}'
    )
    return _card("135deg,#1e3a8a,#3b82f6", "Retrieval", "Semantic search over the case facts",
                 "The retriever pulls only the facts relevant to the question", body)


def render_prompt_compare(question: str, ungrounded: str, grounded: str) -> str:
    def panel(title, text, accent, bg, tag):
        return (
            f'<div style="flex:1 1 300px;min-width:265px;border:1px solid #e2e8f0;'
            f'border-radius:10px;overflow:hidden;">'
            f'<div style="background:{accent};padding:8px 14px;color:#fff;font-size:11px;'
            f'font-weight:700;letter-spacing:.5px;">{title}'
            f'<span style="float:right;background:rgba(255,255,255,.22);padding:1px 8px;'
            f'border-radius:20px;font-size:10px;">{tag}</span></div>'
            f'<div style="padding:12px 14px;font-size:12px;line-height:1.6;color:#1e293b;'
            f'background:{bg};max-height:260px;overflow:auto;">{_h.escape(text)}</div></div>'
        )
    body = (
        f'<div style="background:#f8fafc;border-radius:8px;padding:10px 14px;margin-bottom:12px;">'
        f'<span style="font-size:10px;color:#64748b;font-weight:700;letter-spacing:1px;">QUESTION</span>'
        f'<div style="font-size:13px;color:#0f172a;font-weight:600;margin-top:2px;">{_h.escape(question)}</div></div>'
        f'<div style="display:flex;gap:12px;flex-wrap:wrap;align-items:stretch;">'
        f'{panel("🙈 Ungrounded (no graph)", ungrounded, "#b91c1c", "#fef2f2", "may hallucinate")}'
        f'{panel("📎 Grounded (KG-RAG)", grounded, "#0f766e", "#f0fdfa", "cites facts")}'
        f'</div>'
    )
    return _card("135deg,#5b21b6,#7c3aed", "Prompt Engineering",
                 "Same question, with and without the graph",
                 "Grounding the prompt in retrieved facts is what stops the model inventing an answer", body)


def render_reasoning(result: dict, correct: bool) -> str:
    steps = "".join(
        f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:7px;">'
        f'<span style="flex-shrink:0;width:20px;height:20px;border-radius:50%;background:#7c3aed;'
        f'color:#fff;font-size:10px;font-weight:700;display:flex;align-items:center;'
        f'justify-content:center;">{i+1}</span>'
        f'<div style="font-size:12px;color:#334155;line-height:1.55;">{_h.escape(s)}</div></div>'
        for i, s in enumerate(result["reasoning"])
    ) or '<div style="font-size:12px;color:#94a3b8;">(no reasoning returned)</div>'
    vcol = "#059669" if correct else "#dc2626"
    vbg, vbd = ("#f0fdf4", "#bbf7d0") if correct else ("#fef2f2", "#fecaca")
    verdict = (
        f'<div style="margin-top:12px;padding:14px 16px;background:{vbg};'
        f'border:1px solid {vbd};border-radius:8px;">'
        f'<div style="font-size:10px;color:{vcol};font-weight:700;letter-spacing:1px;">'
        f'{"✓ CASE SOLVED" if correct else "✗ VERDICT"}</div>'
        f'<div style="font-size:17px;font-weight:800;color:#0f172a;margin-top:3px;">'
        f'🔪 {_h.escape(result["culprit"] or "—")}</div>'
        f'<div style="font-size:12px;color:#475569;margin-top:3px;">'
        f'weapon: <b>{_h.escape(result["weapon"] or "—")}</b> · '
        f'motive: <b>{_h.escape(result["motive"] or "—")}</b></div></div>'
    )
    body = (
        '<div style="font-size:10px;color:#94a3b8;letter-spacing:1px;margin-bottom:8px;">'
        'CHAIN OF THOUGHT — grounded in the case facts</div>' + steps + verdict
    )
    return _card("135deg,#3730a3,#4f46e5", "Chain-of-Thought Reasoning",
                 "Solving the case, one deduction at a time",
                 "The model reasons over the facts — eliminating alibis to find the culprit", body)


# ══════════════════════════════════════════════════════════════════════ #
#  Concept cards (RAG components, A.1 pipeline)                             #
# ══════════════════════════════════════════════════════════════════════ #

def render_rag_components() -> str:
    comps = [
        ("🔎", "Retriever", "Finds the few facts relevant to a query from the knowledge "
         "base (vector or graph search).",
         "Grounds answers in real, citable sources instead of the model's fuzzy memory."),
        ("➕", "Augmentation", "Injects the retrieved facts into the prompt as context "
         "the model must use.",
         "Keeps answers current — the KB updates without retraining the model."),
        ("🧠", "Generator (LLM)", "Writes the answer, constrained to the supplied context.",
         "Reasons over given facts rather than inventing them — far less hallucination."),
        ("📎", "Citations / provenance", "Every claim traces back to a source fact.",
         "Lets users verify — the antidote to confident-but-wrong answers."),
    ]
    rows = "".join(
        f'<div style="display:flex;gap:12px;align-items:flex-start;padding:9px 0;'
        f'border-bottom:1px solid #f1f5f9;"><span style="font-size:18px;">{ic}</span>'
        f'<div style="flex:1;"><div style="font-size:13px;font-weight:700;color:#0f172a;">{t}</div>'
        f'<div style="font-size:12px;color:#475569;line-height:1.55;">{d}</div>'
        f'<div style="font-size:11px;color:#c2410c;line-height:1.5;margin-top:2px;">'
        f'<b>vs misinformation:</b> {m}</div></div></div>'
        for ic, t, d, m in comps
    )
    return _card("135deg,#c2410c,#f97316", "RAG Components",
                 "How retrieval-augmented generation resists misinformation",
                 "Each component is a guard-rail between a question and a confidently-wrong answer", rows)


def render_points_card(kicker: str, title: str, subtitle: str, points: list[str],
                       grad: str = "135deg,#1e40af,#3b82f6") -> str:
    rows = "".join(
        f'<div style="display:flex;gap:10px;align-items:flex-start;padding:6px 0;'
        f'border-bottom:1px solid #f1f5f9;"><span style="color:#3b82f6;font-weight:700;">▸</span>'
        f'<div style="font-size:12.5px;color:#475569;line-height:1.6;">{p}</div></div>'
        for p in points
    )
    return _card(grad, kicker, title, subtitle, rows)


def render_vector_vs_graph() -> str:
    def col(title, colour, rows):
        items = "".join(
            f'<div style="font-size:12px;color:#334155;line-height:1.6;padding:3px 0;">{r}</div>'
            for r in rows)
        return (f'<div style="flex:1 1 260px;min-width:235px;border:1px solid #e2e8f0;'
                f'border-top:4px solid {colour};border-radius:8px;padding:12px 14px;">'
                f'<div style="font-size:14px;font-weight:700;color:{colour};margin-bottom:6px;">{title}</div>{items}</div>')
    v = col("🔵 Vector database", "#3b82f6", [
        "Stores text as embeddings; finds items by <b>semantic similarity</b>.",
        "Great for fuzzy retrieval — “find facts <em>like</em> this question”.",
        "No explicit relationships — can't traverse or reason over links.",
        "e.g. FAISS, Chroma, Pinecone."])
    g = col("🟣 Graph database", "#7c3aed", [
        "Stores entities as nodes and <b>explicit relationships</b> as edges.",
        "Great for structure — “who connects to whom, and how”.",
        "Enables multi-hop reasoning and provenance you can follow.",
        "e.g. Neo4j, Memgraph."])
    body = (
        f'<div style="display:flex;gap:12px;flex-wrap:wrap;">{v}{g}</div>'
        f'<div style="margin-top:10px;padding:9px 12px;background:#f5f3ff;border-radius:6px;'
        f'font-size:11.5px;color:#4c1d95;line-height:1.6;"><b>KG-RAG uses both:</b> vector '
        f'search to <em>find</em> the right facts, the graph to <em>reason</em> across them.</div>'
    )
    return _card("135deg,#334155,#475569", "Vector DB vs Graph DB",
                 "Two ways to store knowledge for retrieval",
                 "They solve different halves of the problem", body)


def render_triples(triples: list[dict], strategy: str = "OBIE") -> str:
    """Render extracted KG triples as a styled table with confidence bars."""
    _ff = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"

    is_obie   = strategy.upper() == "OBIE"
    hdr_grad  = "135deg,#5b21b6,#7c3aed" if is_obie else "135deg,#0f766e,#0d9488"
    conf_col  = "#7c3aed" if is_obie else "#0d9488"
    badge_bg  = "#f5f3ff" if is_obie else "#f0fdfa"
    badge_col = "#4c1d95" if is_obie else "#134e4a"

    section_counts: dict[str, int] = {}
    for t in triples:
        section_counts[t.get("section", "—")] = section_counts.get(t.get("section", "—"), 0) + 1

    section_badges = "".join(
        f'<span style="display:inline-block;background:{badge_bg};color:{badge_col};'
        f'border:1px solid;border-radius:20px;padding:2px 10px;font-size:11px;margin:2px;">'
        f'{sec}: {cnt} triple{"s" if cnt != 1 else ""}</span>'
        for sec, cnt in section_counts.items()
    )

    rows = ""
    for t in triples:
        conf   = t.get("confidence", 0.8)
        bar_w  = int(conf * 100)
        snippet = t.get("sentence", "")[:80] + ("…" if len(t.get("sentence","")) > 80 else "")
        rows += (
            f'<tr style="border-bottom:1px solid #f1f5f9;vertical-align:top;">'
            f'<td style="padding:8px 10px;font-size:12px;font-weight:600;color:#0f172a;">'
            f'{t["subject"]}</td>'
            f'<td style="padding:8px 6px;text-align:center;">'
            f'<span style="background:{conf_col};color:#fff;font-size:10px;font-weight:700;'
            f'padding:2px 8px;border-radius:20px;white-space:nowrap;">{t["predicate"]}</span></td>'
            f'<td style="padding:8px 10px;font-size:12px;font-weight:600;color:#0f172a;">'
            f'{t["object"]}</td>'
            f'<td style="padding:8px 10px;min-width:80px;">'
            f'<div style="background:#f1f5f9;border-radius:4px;height:6px;margin-bottom:2px;">'
            f'<div style="width:{bar_w}%;background:{conf_col};border-radius:4px;height:6px;"></div></div>'
            f'<span style="font-size:10px;color:#94a3b8;">{conf:.0%}</span></td>'
            f'<td style="padding:8px 10px;font-size:11px;color:#94a3b8;font-style:italic;">'
            f'{snippet}</td>'
            f'</tr>'
        )

    empty = (
        f'<tr><td colspan="5" style="padding:16px;text-align:center;'
        f'color:#94a3b8;font-size:13px;">No triples extracted.</td></tr>'
    ) if not triples else ""

    return (
        f'<div style="font-family:{_ff};border:1px solid #e2e8f0;border-radius:10px;'
        f'overflow:hidden;margin:8px 0;">'
        f'<div style="background:linear-gradient({hdr_grad});padding:14px 18px;">'
        f'<div style="color:rgba(255,255,255,.75);font-size:10px;font-weight:700;'
        f'letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">'
        f'Extraction Results</div>'
        f'<div style="color:#fff;font-size:16px;font-weight:700;">'
        f'{strategy} — {len(triples)} triple{"s" if len(triples) != 1 else ""} extracted</div>'
        f'<div style="margin-top:8px;">{section_badges}</div>'
        f'</div>'
        f'<div style="overflow-x:auto;">'
        f'<table style="width:100%;border-collapse:collapse;font-size:12px;">'
        f'<thead><tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0;">'
        f'<th style="padding:8px 10px;text-align:left;color:#64748b;font-size:10px;'
        f'letter-spacing:1px;font-weight:700;">SUBJECT</th>'
        f'<th style="padding:8px 6px;text-align:center;color:#64748b;font-size:10px;'
        f'letter-spacing:1px;font-weight:700;">PREDICATE</th>'
        f'<th style="padding:8px 10px;text-align:left;color:#64748b;font-size:10px;'
        f'letter-spacing:1px;font-weight:700;">OBJECT</th>'
        f'<th style="padding:8px 10px;text-align:left;color:#64748b;font-size:10px;'
        f'letter-spacing:1px;font-weight:700;">CONF</th>'
        f'<th style="padding:8px 10px;text-align:left;color:#64748b;font-size:10px;'
        f'letter-spacing:1px;font-weight:700;">SOURCE SENTENCE</th>'
        f'</tr></thead>'
        f'<tbody>{rows}{empty}</tbody>'
        f'</table></div>'
        f'</div>'
    )


def render_segments(segments: list[dict]) -> str:
    """Render a list of {label, text} sentence dicts as a labelled table."""
    rows = ""
    for i, seg in enumerate(segments):
        col, bg = _LABEL_COLOURS.get(seg["label"], ("#374151", "#f9fafb"))
        rows += (
            f'<tr>'
            f'<td style="padding:6px 10px;color:#94a3b8;font-size:11px;'
            f'font-weight:600;white-space:nowrap;vertical-align:top;">{i}</td>'
            f'<td style="padding:6px 8px;vertical-align:top;">'
            f'<span style="display:inline-block;background:{col};color:#fff;'
            f'font-size:9px;font-weight:700;letter-spacing:1px;padding:1px 6px;'
            f'border-radius:3px;">{seg["label"]}</span></td>'
            f'<td style="padding:6px 10px;font-size:12px;color:#1e293b;'
            f'line-height:1.6;background:{bg};border-radius:4px;">{seg["text"]}</td>'
            f'</tr>'
        )

    _ff = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    return (
        f'<div style="font-family:{_ff};">'
        f'<div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:8px;">'
        f'📋 Segmented Abstract — {len(segments)} sentences</div>'
        f'<table style="width:100%;border-collapse:collapse;font-size:12px;">'
        f'<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        f'<th style="padding:6px 10px;text-align:left;color:#94a3b8;font-size:10px;letter-spacing:1px;">#</th>'
        f'<th style="padding:6px 8px;text-align:left;color:#94a3b8;font-size:10px;letter-spacing:1px;">SECTION</th>'
        f'<th style="padding:6px 10px;text-align:left;color:#94a3b8;font-size:10px;letter-spacing:1px;">SENTENCE</th>'
        f'</tr></thead>'
        f'<tbody>{rows}</tbody>'
        f'</table></div>'
    )



