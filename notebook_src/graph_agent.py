"""
notebook_src/graph_agent.py
An OpenAI function-calling agent that answers natural-language questions
about a NetworkX graph, using a caller-supplied ontology schema as context.

The agent iterates tool calls (get_entities_by_type, get_neighbours,
get_relationship, find_path) until it can write a grounded final answer.
"""
from __future__ import annotations
import json


# ── tool definitions ──────────────────────────────────────────────── #

def _make_tools(entity_types: list[str], relation_types: list[str]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_entities_by_type",
                "description": "List every entity of a given type in the knowledge graph.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_type": {
                            "type": "string",
                            "enum": entity_types,
                            "description": "The ontology entity type to filter by",
                        }
                    },
                    "required": ["entity_type"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_neighbours",
                "description": (
                    "Get all direct relationships of a named entity — "
                    "both outgoing (entity → X) and incoming (X → entity)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity": {"type": "string", "description": "Entity name (exact or partial)"}
                    },
                    "required": ["entity"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_relationship",
                "description": "Find all triples that use a specific relation type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relation_type": {
                            "type": "string",
                            "enum": relation_types,
                            "description": "The relation type to search for",
                        }
                    },
                    "required": ["relation_type"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "find_path",
                "description": "Find the shortest connection between two entities in the graph.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "description": "Starting entity name"},
                        "target": {"type": "string", "description": "Destination entity name"},
                    },
                    "required": ["source", "target"],
                },
            },
        },
    ]


# ── tool execution ────────────────────────────────────────────────── #

def _fuzzy_match(name: str, nodes: list[str]) -> str | None:
    """Return best matching node: exact → case-insensitive → substring."""
    nl = name.lower()
    exact = next((n for n in nodes if n == name), None)
    if exact:
        return exact
    ci = next((n for n in nodes if n.lower() == nl), None)
    if ci:
        return ci
    return next((n for n in nodes if nl in n.lower() or n.lower() in nl), None)


def _execute(G, tool_name: str, args: dict) -> object:
    import networkx as nx

    nodes = list(G.nodes())

    if tool_name == "get_entities_by_type":
        etype = args["entity_type"]
        return [n for n, d in G.nodes(data=True) if d.get("type") == etype]

    if tool_name == "get_neighbours":
        match = _fuzzy_match(args["entity"], nodes)
        if match is None:
            return {"error": f"'{args['entity']}' not found. Known: {nodes[:15]}"}
        rows = []
        for _, o, d in G.out_edges(match, data=True):
            rows.append({"subject": match, "relation": d["predicate"], "object": o})
        for s, _, d in G.in_edges(match, data=True):
            rows.append({"subject": s, "relation": d["predicate"], "object": match})
        return rows or {"note": f"'{match}' has no edges in this graph."}

    if tool_name == "get_relationship":
        rel = args["relation_type"].lower()
        return [
            {"subject": s, "predicate": d["predicate"], "object": o}
            for s, o, d in G.edges(data=True)
            if d.get("predicate", "").lower() == rel
        ]

    if tool_name == "find_path":
        src = _fuzzy_match(args["source"], nodes)
        tgt = _fuzzy_match(args["target"], nodes)
        if src is None:
            return {"error": f"Source '{args['source']}' not found."}
        if tgt is None:
            return {"error": f"Target '{args['target']}' not found."}
        UG = nx.Graph(G)
        try:
            path = nx.shortest_path(UG, src, tgt)
            return {"path": path, "hops": len(path) - 1}
        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            return {"error": str(e)}

    return {"error": f"Unknown tool: {tool_name}"}


# ── main agent loop ───────────────────────────────────────────────── #

def query_graph(
    question: str,
    G,
    entity_types: list[str],
    relation_types: list[str],
    api_key: str,
    model: str = "gpt-4.1-nano",
    max_steps: int = 8,
) -> dict:
    """
    Answer a natural-language question by letting an agent traverse the graph.

    Returns:
        {
          "answer": str,          # final grounded answer
          "steps": [              # each tool call the agent made
            {"tool": ..., "args": ..., "result": ...}, ...
          ]
        }
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    tools = _make_tools(entity_types, relation_types)
    sample_nodes = list(G.nodes())[:20]

    system = (
        "You are a detective's assistant with access to a knowledge graph "
        "built from a case file. Use the tools to query the graph and "
        "build up a grounded answer.\n\n"
        f"Ontology:\n"
        f"  Entity types: {', '.join(entity_types)}\n"
        f"  Relation types: {', '.join(relation_types)}\n\n"
        f"Sample entities in the graph: {', '.join(sample_nodes)}\n\n"
        "Reason step by step. When you have enough evidence, write a clear "
        "final answer that cites the specific graph facts you found."
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": question},
    ]
    steps: list[dict] = []

    for _ in range(max_steps):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return {"answer": (msg.content or "").strip(), "steps": steps}

        tool_results = []
        for tc in msg.tool_calls:
            args   = json.loads(tc.function.arguments)
            result = _execute(G, tc.function.name, args)
            steps.append({"tool": tc.function.name, "args": args, "result": result})
            tool_results.append({
                "role":         "tool",
                "tool_call_id": tc.id,
                "content":      json.dumps(result),
            })
        messages.extend(tool_results)

    # max steps reached — force a closing answer
    messages.append({"role": "user",
                     "content": "Based on what you found so far, give your final answer."})
    final = client.chat.completions.create(model=model, messages=messages)
    return {
        "answer": (final.choices[0].message.content or "").strip(),
        "steps":  steps,
    }
