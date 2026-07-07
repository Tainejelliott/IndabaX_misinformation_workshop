# Plan: Guided Python RAG Demo (ChromaDB) for `1 - Introduction.ipynb`

## Objective

Close Part 1 with a hands-on payoff: a minimal, **runs-top-to-bottom-in-Colab** Python
walkthrough that builds a working RAG pipeline over a plaintext document using ChromaDB
as the vector datastore. Every step should map back to a visual the attendee just
explored (chunking → *Information Extraction* visual, embeddings → *Embedding Space
Explorer*, retrieval → *Information Retrieval* visual, prompt assembly → *Augmented
Generation* U-curve/prompting tabs).

## Placement

Appended as a new top-level section at the end of the notebook, after "Additional
Generation Methodologies":

```
## Hands-On: A Minimal RAG Pipeline in ~40 Lines
```

## Design constraints

- **CPU-only, no GPU required.** Use ChromaDB's default embedding function
  (`all-MiniLM-L6-v2` via ONNX runtime) — no torch download, fast cold start on Colab.
- **No API key required for the core loop.** Retrieval + grounded-prompt assembly work
  fully offline. The final LLM call is an *optional* cell gated on `OPENAI_API_KEY`
  (matches `.env.example`); if absent, the cell prints the assembled prompt and tells
  the attendee what the LLM would receive.
- **Self-contained data.** A cell writes a small plaintext corpus to `data/myths.txt`
  rather than depending on a repo file — nothing to download, nothing to break.
- **Corpus theme:** short myth-busting passages consistent with the workshop's existing
  examples (Great Wall visibility, 10%-of-brain, goldfish memory, blood colour, sugar
  hyperactivity — all already cited in REFERENCES.md). ~10 paragraphs, one topic each,
  so paragraph-chunking gives clean chunks and queries have obvious right answers.
- **Style:** match existing notebook voice — every code cell preceded by a 1–3 sentence
  markdown cell saying what it does and which visual it echoes. Code kept plain
  (no classes, no helper modules), commented sparingly, ≤ ~15 lines per cell.

## Cell-by-cell breakdown (md = markdown, py = code)

1. **md — section intro.** What we're building (index → retrieve → assemble → generate),
   the 5 steps, and a note that this is dense-vector RAG only — Part 2 adds the
   knowledge graph.
2. **py — install.** `%pip install -q chromadb` (pin a known-good major version).
   Comment noting Colab may take ~30s and no runtime restart is needed.
3. **md + py — create the corpus.** Write `data/myths.txt` (~10 myth-busting
   paragraphs separated by blank lines) via a `pathlib` write; print a preview.
4. **md + py — chunk it.** Split on blank lines (paragraph = chunk). Print chunk count
   and one sample chunk. Markdown ties back to the *Chunking demo* tab (sentence-aware
   beats fixed-size; here paragraphs are already semantically clean units).
5. **md + py — index into ChromaDB.** `chromadb.Client()` (in-memory),
   `create_collection("myths")`, `collection.add(documents=chunks, ids=[...],
   metadatas=[{"source": "myths.txt", "para": i}])`. Markdown notes the default
   embedding model and that ids + metadata are what later make answers *citable*
   (provenance — echoes the extraction-pitfalls tab).
6. **md + py — query it.** `collection.query(query_texts=["Can you see the Great Wall
   of China from space?"], n_results=3)`; print each hit with its distance and
   paragraph number. Markdown points out the query shares almost no keywords with the
   matching passage — this is the *semantic vs keyword* point from the retrieval visual.
   Include a second query in the same cell with a deliberately out-of-corpus question
   to show weak/distant matches (sets up the "insufficient evidence" behaviour).
7. **md + py — assemble the grounded prompt.** Build the exact string: system prompt
   (grounded + cited + abstain-if-absent, copied from the *Prompting Strategies* tab),
   numbered context chunks placed best-first (mention U-curve ordering matters once
   k grows), then the question. Print it.
8. **md + py — optional LLM call.** If `OPENAI_API_KEY` is set (env var or `.env`),
   call the chat completions API with the assembled prompt and print the answer;
   otherwise print a friendly note + the prompt so the exercise still completes.
   Wrapped in try/except so a bad key can't break the run-all.
9. **md — wrap-up.** Recap the 5 steps against the earlier visuals; tease Part 2
   (the same pipeline's failure cases and why a knowledge graph fixes them).

## Verification plan (before committing)

1. `jupyter nbconvert --to notebook --execute` locally (or manual run) with **no**
   `OPENAI_API_KEY` set — all cells must succeed and the optional cell must degrade
   gracefully.
2. Confirm fresh-environment behaviour: `pip install chromadb` in a clean venv,
   first `collection.add()` downloads the ONNX MiniLM model (~80 MB) — acceptable
   once-off cost on Colab; note it in the install cell's markdown.
3. Check query results actually rank the intended paragraph first for each demo query;
   adjust corpus wording if not.
4. Re-run the full notebook top-to-bottom to make sure nothing above broke.

## Out of scope (deliberately)

- Persistent Chroma storage, HNSW tuning, metadata filtering — noted in wrap-up as
  "where to go next", not demonstrated.
- Re-ranking / hybrid search — covered conceptually by the visuals; adding code here
  would double the section's length for marginal teaching value.
- Any non-OpenAI LLM fallback (keeps the optional cell tiny; `.env.example` already
  standardises on OpenAI).
