"""
notebook_src/graph.py
Turn extracted triples into a clean, queryable property graph.

  - canonicalize_triples : merge duplicate entity surface forms (lexical + embedding)
  - build_graph          : assemble a networkx MultiDiGraph with node/edge properties
  - graph_stats          : summary statistics
  - central_entities / neighbours / connecting_path : simple graph queries
  - to_cypher            : export the property graph as Neo4j Cypher
"""
from __future__ import annotations
import re

# Relations that are conceptually symmetric (A rel B ⇔ B rel A). Everything else
# is treated as directed.
SYMMETRIC_PREDICATES = {
    "is associated with", "associated with", "is similar to", "similar to",
    "correlates with", "co-occurs with", "interacts with", "is related to",
    "related to", "is linked to", "linked to", "is comparable to", "resembles",
    "coincides with", "is coincident with",
}

_ARTICLES = ("the ", "a ", "an ", "these ", "those ", "this ", "that ",
             "its ", "their ", "our ")

_TEMPORAL_WORDS = {"early", "late", "mature", "stage", "stages", "phase", "phases",
                   "during", "developmental", "initial", "subsequent", "window",
                   "npcd", "epcd", "lpcd", "prior", "before", "after"}

# Meaning-bearing modifiers: two entities that differ only by one of these are
# NOT the same node (e.g. "early stages of PCD" vs "late stages of PCD").
_CONTRASTIVE = {
    "early", "late", "initial", "final", "mature", "young", "old",
    "non", "not", "without", "npcd", "epcd", "lpcd",
    "high", "low", "increased", "decreased", "elevated", "reduced",
    "before", "after", "pre", "post", "first", "second", "third",
}


def _blocks_merge(a: str, b: str) -> bool:
    """True if `a` and `b` differ by a contrastive modifier → must stay distinct."""
    diff = set(a.split()) ^ set(b.split())
    return bool(diff & _CONTRASTIVE)


def _norm(s: str) -> str:
    """Lightweight lexical normalisation for merging trivial surface variants."""
    s = (s or "").strip().lower()
    changed = True
    while changed:                      # strip stacked leading articles
        changed = False
        for art in _ARTICLES:
            if s.startswith(art):
                s = s[len(art):]; changed = True
    s = re.sub(r"\s+", " ", s).strip(" .,:;")
    return s


def _temporal_tag(text: str) -> str | None:
    # match whole words only — "late" must not fire inside "regulated"
    seen: list[str] = []
    for w in re.findall(r"[a-z]+", (text or "").lower()):
        if w in _TEMPORAL_WORDS and w not in seen:
            seen.append(w)
    return ", ".join(seen[:3]) or None


def canonicalize_triples(triples: list[dict], threshold: float = 0.9,
                         model_name: str | None = None):
    """
    Collapse different surface forms of the same entity into one canonical node.
    Two-stage: (1) cheap lexical normalisation (case / articles / whitespace),
    then (2) biomedical-embedding clustering of the remaining forms — two forms
    with cosine >= `threshold` are treated as the same entity.

    Returns (canonical_triples, clusters, (n_before, n_after)) where `clusters`
    lists only the entities that were actually merged (for display).
    """
    from sentence_transformers import util
    from notebook_src.extraction import _get_embedder, BIOMED_EMBED_MODEL
    model_name = model_name or BIOMED_EMBED_MODEL

    counts: dict[str, int] = {}
    for t in triples:
        for e in (t["subject"], t["object"]):
            counts[e] = counts.get(e, 0) + 1
    entities = sorted(counts)
    if not entities:
        return list(triples), [], (0, 0)

    # (1) lexical grouping
    norm_groups: dict[str, list[str]] = {}
    for e in entities:
        norm_groups.setdefault(_norm(e), []).append(e)
    reps = list(norm_groups)

    # (2) cluster the normalised reps with union-find over three signals:
    #     embedding similarity, and acronym ⇄ expansion links.
    model = _get_embedder(model_name)
    emb = model.encode(reps, normalize_embeddings=True)
    sim = util.cos_sim(emb, emb)
    n = len(reps)

    parent = list(range(n))
    def _find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def _union(a, b):
        ra, rb = _find(a), _find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    # (2a) embedding similarity, blocked by contrastive modifiers
    for i in range(n):
        for j in range(i + 1, n):
            if float(sim[i][j]) >= threshold and not _blocks_merge(reps[i], reps[j]):
                _union(i, j)

    # (2b) acronym ⇄ expansion  ("pcd" ⇄ "programmed cell death")
    acr_idx: dict[str, int] = {}
    for idx, r in enumerate(reps):
        toks = [t for t in r.split() if t[:1].isalpha()]
        if len(toks) >= 2:
            acr = "".join(t[0] for t in toks)
            if 2 <= len(acr) <= 6:
                acr_idx.setdefault(acr, idx)
    for idx, r in enumerate(reps):
        if " " not in r and 2 <= len(r) <= 6 and r in acr_idx:
            _union(idx, acr_idx[r])

    groups_map: dict[int, list[int]] = {}
    for idx in range(n):
        groups_map.setdefault(_find(idx), []).append(idx)
    groups = list(groups_map.values())

    # canonical label per cluster = most-mentioned original surface form
    mapping: dict[str, str] = {}
    clusters = []
    for members in groups:
        surfaces = []
        for idx in members:
            surfaces += norm_groups[reps[idx]]
        surfaces = sorted(set(surfaces), key=lambda s: (-counts[s], len(s)))
        canonical = surfaces[0]
        for s in surfaces:
            mapping[s] = canonical
        if len(surfaces) > 1:
            clusters.append({
                "canonical": canonical,
                "members": surfaces,
                "size": len(surfaces),
                "mentions": sum(counts[s] for s in surfaces),
            })

    # rewrite triples to canonical entities, merging duplicate (s, p, o)
    merged: dict[tuple, dict] = {}
    for t in triples:
        s = mapping.get(t["subject"], t["subject"])
        o = mapping.get(t["object"], t["object"])
        key = (s, t["predicate"].lower().strip(), o)
        if key not in merged:
            d = dict(t); d["subject"] = s; d["object"] = o
            d["sentences"] = [t["sentence"]] if t.get("sentence") else []
            d["provenance_count"] = 1
            merged[key] = d
        else:
            d = merged[key]
            d["confidence"] = max(d.get("confidence", 0.0), t.get("confidence", 0.0))
            if t.get("sentence") and t["sentence"] not in d["sentences"]:
                d["sentences"].append(t["sentence"])
            d["provenance_count"] += 1

    clusters.sort(key=lambda c: -c["mentions"])
    n_after = len(set(mapping.values()))
    return list(merged.values()), clusters, (len(entities), n_after)


def build_graph(triples: list[dict]):
    """Assemble a networkx MultiDiGraph with rich node & edge properties."""
    import networkx as nx
    G = nx.MultiDiGraph()
    for t in triples:
        for ent, tkey, mkey in ((t["subject"], "subject_type", "subject_mesh"),
                                (t["object"],  "object_type",  "object_mesh")):
            if not G.has_node(ent):
                G.add_node(ent, type=t.get(tkey, "") or "Other",
                           mesh=t.get(mkey, ""), section=t.get("section", ""),
                           mentions=0)
            G.nodes[ent]["mentions"] += 1
        pred = t["predicate"]
        prov = t.get("sentences") or ([t["sentence"]] if t.get("sentence") else [])
        G.add_edge(
            t["subject"], t["object"], key=pred,
            predicate=pred,
            predicate_type=t.get("predicate_type", ""),
            confidence=round(float(t.get("confidence", 0.0)), 2),
            symmetric=pred.lower().strip() in SYMMETRIC_PREDICATES,
            temporal=_temporal_tag(" ".join(prov)),
            section=t.get("section", ""),
            provenance=prov,
        )
    return G


def graph_stats(G) -> dict:
    import networkx as nx
    n, m = G.number_of_nodes(), G.number_of_edges()
    types: dict[str, int] = {}
    for _, d in G.nodes(data=True):
        types[d.get("type", "Other")] = types.get(d.get("type", "Other"), 0) + 1
    sym = sum(1 for *_, d in G.edges(data=True) if d.get("symmetric"))
    temporal = sum(1 for *_, d in G.edges(data=True) if d.get("temporal"))
    density = nx.density(nx.DiGraph(G)) if n > 1 else 0.0
    return {
        "nodes": n, "edges": m, "density": density,
        "types": dict(sorted(types.items(), key=lambda kv: -kv[1])),
        "symmetric_edges": sym, "temporal_edges": temporal,
        "top": central_entities(G, 6),
    }


def central_entities(G, k: int = 6):
    """Top-k entities by total degree (hub-ness)."""
    deg = dict(G.degree())
    return sorted(deg.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


def neighbours(G, node) -> list[dict]:
    rows = []
    for _, o, d in G.out_edges(node, data=True):
        rows.append({"other": o, "predicate": d["predicate"], "dir": "out"})
    for s, _, d in G.in_edges(node, data=True):
        rows.append({"other": s, "predicate": d["predicate"], "dir": "in"})
    return rows


def farthest_path(G, source) -> list[tuple]:
    """
    Longest reachable chain from `source` (ignoring edge direction), annotated
    with predicates — a guaranteed multi-hop path within source's component.
    """
    import networkx as nx
    UG = nx.Graph()
    for s, o, d in G.edges(data=True):
        if not UG.has_edge(s, o):
            UG.add_edge(s, o, predicate=d["predicate"])
    if source not in UG:
        return []
    lengths = nx.single_source_shortest_path_length(UG, source)
    if len(lengths) < 2:
        return []
    target = max(lengths, key=lengths.get)
    nodes = nx.shortest_path(UG, source, target)
    return [(a, UG[a][b]["predicate"], b) for a, b in zip(nodes, nodes[1:])]


def _cypher_str(s: str) -> str:
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"


def to_cypher(G, max_edges: int | None = None) -> str:
    """Serialise the property graph as Neo4j Cypher CREATE statements."""
    lines, var = [], {}
    for i, (node, d) in enumerate(G.nodes(data=True)):
        v = f"n{i}"; var[node] = v
        label = (d.get("type") or "Entity").replace(" ", "") or "Entity"
        props = f"name: {_cypher_str(node)}, mentions: {d.get('mentions', 1)}"
        if d.get("mesh"):
            props += f", mesh: {_cypher_str(d['mesh'])}"
        lines.append(f"CREATE ({v}:{label} {{{props}}})")
    lines.append("")
    for k, (s, o, d) in enumerate(G.edges(data=True)):
        if max_edges is not None and k >= max_edges:
            lines.append(f"// … {G.number_of_edges() - max_edges} more relationships")
            break
        rel = re.sub(r"[^A-Za-z0-9]+", "_", d["predicate"].strip()).upper().strip("_") or "REL"
        lines.append(
            f"CREATE ({var[s]})-[:{rel} {{confidence: {d.get('confidence', 0.0)}}}]->({var[o]})"
        )
    return "\n".join(lines)
