"""
notebook_src/validation.py
Validation utilities for the KG-RAG workshop.

  - back_translate            : reconstruct an abstract from triples (round-trip test)
  - text_cosine               : cosine similarity between two texts
  - stsb_cosine_by_category   : run the model on STS-B, grouped by gold relatedness
  - plot_calibration          : density + box-and-whisker per STS category, so a raw
                                cosine value can be read as a relatedness level.

HTML rendering (the side-by-side abstracts) lives in display.render_abstract_comparison.
"""
from __future__ import annotations

# General-purpose STS embedding model. all-MiniLM-L6-v2 is fine-tuned on 1B+
# sentence pairs (incl. NLI / STS) and STS-B is its native benchmark, so its
# cosine scores are meaningfully calibrated to STS relatedness levels — the same
# model is used for the abstract comparison AND the STS-B calibration below.
VALIDATION_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_MODELS: dict = {}

STS_LABELS = {
    0: "0 · unrelated",
    1: "1 · same topic",
    2: "2 · shares details",
    3: "3 · roughly equiv.",
    4: "4 · mostly equiv.",
    5: "5 · equivalent",
}


def _model(name: str = VALIDATION_EMBED_MODEL):
    if name not in _MODELS:
        from sentence_transformers import SentenceTransformer
        _MODELS[name] = SentenceTransformer(name)
    return _MODELS[name]


# ── back-translation (triples → abstract) ─────────────────────────────── #

def back_translate(triples: list[dict], api_key: str,
                   model: str = "gpt-4.1-nano") -> str:
    """
    Reconstruct a prose abstract from a set of KG triples — the round-trip test:
    if the triples captured the abstract's meaning, the reconstruction should be
    semantically close to the original.
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    lines = "\n".join(
        f"({t['subject']}) --[{t['predicate']}]--> ({t['object']})" for t in triples
    )
    system = (
        "You reconstruct a scientific abstract from a knowledge graph. You are given "
        "(subject, predicate, object) triples that were extracted from a biomedical "
        "abstract. Write ONE flowing abstract in scientific prose that expresses only "
        "the facts contained in the triples — do NOT introduce new findings, numbers "
        "or entities that are not present in the triples. Be concise and coherent."
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Triples:\n{lines}\n\nReconstructed abstract:"},
        ],
    )
    return (resp.choices[0].message.content or "").strip()


# ── embedding similarity ──────────────────────────────────────────────── #

def text_cosine(text_a: str, text_b: str,
                model_name: str = VALIDATION_EMBED_MODEL) -> float:
    """Cosine similarity between two texts under the validation embedding model."""
    from sentence_transformers import util
    m = _model(model_name)
    emb = m.encode([text_a, text_b], normalize_embeddings=True)
    return float(util.cos_sim(emb[0], emb[1]))


# ── STS-B calibration ─────────────────────────────────────────────────── #

def stsb_cosine_by_category(split: str = "test", max_pairs: int | None = None,
                            model_name: str = VALIDATION_EMBED_MODEL) -> dict:
    """
    Run the embedding model over the STS Benchmark and group the resulting cosine
    similarities by their integer gold relatedness label (0-5).

    Returns {category: numpy array of cosine similarities}.
    """
    import numpy as np
    from datasets import load_dataset

    ds = load_dataset("mteb/stsbenchmark-sts", split=split)
    if max_pairs:
        ds = ds.select(range(min(max_pairs, len(ds))))

    m  = _model(model_name)
    e1 = m.encode(list(ds["sentence1"]), normalize_embeddings=True,
                  batch_size=64, show_progress_bar=False)
    e2 = m.encode(list(ds["sentence2"]), normalize_embeddings=True,
                  batch_size=64, show_progress_bar=False)
    cos = np.sum(np.asarray(e1) * np.asarray(e2), axis=1)

    cats: dict[int, list] = {}
    for c, s in zip(cos, ds["score"]):
        cats.setdefault(int(round(float(s))), []).append(float(c))
    return {k: np.array(cats[k]) for k in sorted(cats)}


def plot_calibration(cat_cos: dict, highlight: float | None = None,
                     highlight_label: str = "our abstracts",
                     model_name: str = "all-MiniLM-L6-v2"):
    """
    Draw a density (KDE) curve per STS category with box-and-whiskers below,
    sharing a cosine-similarity x-axis. Optionally mark a cosine value (e.g. the
    back-translation similarity) so it can be read against the relatedness levels.

    Returns (nearest_category, label) for the highlighted value, else None.
    """
    import io
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.stats import gaussian_kde
    from IPython.display import Image, display

    cats   = sorted(cat_cos)
    cmap   = plt.cm.RdYlGn
    colors = {c: cmap(i / (len(cats) - 1 or 1)) for i, c in enumerate(cats)}

    fig, (ax_d, ax_b) = plt.subplots(
        2, 1, figsize=(8, 5.2), sharex=True,
        gridspec_kw={"height_ratios": [3, 2], "hspace": 0.1},
    )

    xs = np.linspace(-0.15, 1.0, 300)
    for c in cats:
        data = cat_cos[c]
        if len(data) > 1 and data.std() > 1e-3:
            ys = gaussian_kde(data)(xs)
            ax_d.plot(xs, ys, color=colors[c], lw=1.8, label=STS_LABELS.get(c, str(c)))
            ax_d.fill_between(xs, ys, color=colors[c], alpha=0.16)
    ax_d.set_ylabel("density")
    ax_d.set_yticks([])
    ax_d.legend(title="STS-B gold label", fontsize=8, title_fontsize=8,
                loc="upper left", frameon=False)
    ax_d.set_title(f"What does a cosine score mean?   ({model_name} on STS-B)",
                   fontsize=12, fontweight="bold", loc="left")

    positions = list(range(len(cats)))
    bp = ax_b.boxplot([cat_cos[c] for c in cats], vert=False, positions=positions,
                      widths=0.6, patch_artist=True, showfliers=False)
    for patch, c in zip(bp["boxes"], cats):
        patch.set_facecolor(colors[c]); patch.set_alpha(0.55)
        patch.set_edgecolor("#334155")
    for med in bp["medians"]:
        med.set_color("#0f172a"); med.set_linewidth(1.4)
    ax_b.set_yticks(positions)
    ax_b.set_yticklabels([STS_LABELS.get(c, str(c)) for c in cats], fontsize=8)
    ax_b.set_xlabel("cosine similarity")
    ax_b.set_xlim(-0.15, 1.0)

    result = None
    if highlight is not None:
        for ax in (ax_d, ax_b):
            ax.axvline(highlight, color="#7c3aed", lw=2, ls="--")
        ax_d.annotate(f"{highlight_label}: {highlight:.2f}",
                      xy=(highlight, ax_d.get_ylim()[1] * 0.92),
                      xytext=(6, 0), textcoords="offset points",
                      color="#7c3aed", fontsize=9, fontweight="bold")
        med = {c: float(np.median(cat_cos[c])) for c in cats}
        nearest = min(cats, key=lambda c: abs(med[c] - highlight))
        result = (nearest, STS_LABELS.get(nearest, str(nearest)))

    for ax in (ax_d, ax_b):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    display(Image(data=buf.getvalue()))
    return result
