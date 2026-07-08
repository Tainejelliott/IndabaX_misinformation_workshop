# Hands-on B — Standalone bundle (Google Colab)

This folder runs **`5 - Hands-on B.ipynb`** on its own. It contains only the
`notebook_src` modules this notebook actually needs.

## Run it on Google Colab

1. Upload this whole **`part 5`** folder to Colab
   (Files panel → ⬆ upload, or drag the folder in). The notebook and the
   `notebook_src/` folder must sit next to each other.
2. Open **`5 - Hands-on B.ipynb`**.
3. In the **Setup** cell, paste your OpenAI API key between the quotes:

   ```python
   OPENAI_API_KEY = "sk-...your key here..."
   ```

4. **Runtime → Run all.**
   The first cell installs the Python packages; the rest runs the murder-mystery
   KG-RAG pipeline end to end.

> The model is set by `MODEL = "gpt-4o-mini"` in the Setup cell — change it to any
> chat model your key can access (e.g. `gpt-4.1-nano`).
>
> ⚠️ Delete your API key from the notebook when you're finished.

## What's included

```
part 5/
  5 - Hands-on B.ipynb        the notebook
  notebook_src/               only the modules this notebook imports:
    visuals.py  display.py  mystery.py  extraction.py
    graph.py    graph_agent.py  validation.py  __init__.py
```
