"""
notebook_src/pancreatic.py
A small pancreatic-cancer corpus + ontology for Hands-on A.2 v4.1 (the
proposition-pipeline notebook).

The five abstracts are HAND-AUTHORED for teaching from well-established,
textbook-accurate facts about pancreatic cancer — they are NOT real papers and
carry no PMIDs. They are written at the depth of a real research abstract
(~180-220 words, rich in entities, mechanisms and methods) and deliberately refer
to the same disease with many different surface forms (pancreatic ductal
adenocarcinoma, PDAC, pancreatic cancer, cancer of the pancreas, adenocarcinoma,
pancreatic tumour) so the entity-mapping step can show them all bridging to one
concept. Pronouns are kept in so coreference resolution has something to resolve.

The ontology mirrors the shape of extraction.ONTOLOGY_TYPES (type / umls / reason
/ mesh) so it can be passed straight into extract_openie(ontology_types=...),
extract_obie(ontology_terms=...) and ground_to_mesh(...).
"""
from __future__ import annotations

# ── The corpus: 5 same-domain abstracts ──────────────────────────────── #
ABSTRACTS = [
    {
        "title":   "Molecular pathogenesis of pancreatic ductal adenocarcinoma",
        "authors": "(illustrative teaching abstract)",
        "journal": "NdabaX Workshop Corpus",
        "year":    "—",
        "sections": [
            {"label": "BACKGROUND",
             "text": "Pancreatic ductal adenocarcinoma (PDAC) is the most common malignancy "
                     "of the pancreas and among the most lethal of human cancers, with a "
                     "five-year survival of roughly ten percent. The tumour arises from the "
                     "ductal epithelium and evolves through a series of non-invasive precursor "
                     "lesions called pancreatic intraepithelial neoplasia (PanIN). As these "
                     "lesions progress, they accumulate an expanding set of genetic alterations "
                     "that culminate in invasive disease."},
            {"label": "RESULTS",
             "text": "Activating point mutations in the KRAS oncogene are detectable in about "
                     "ninety percent of cases and represent the earliest, near-universal driver "
                     "event; they lock the RAS-MAPK pathway into constitutive signalling and "
                     "sustain tumour-cell proliferation. Progression is then driven by "
                     "inactivation of the tumour-suppressor genes CDKN2A, TP53 and SMAD4, each "
                     "lost in a large fraction of tumours. Immunohistochemical loss of SMAD4 in "
                     "particular correlates with a widely metastatic pattern of spread. "
                     "Surrounding the malignant cells is a dense desmoplastic stroma of "
                     "cancer-associated fibroblasts and extracellular matrix that characterises "
                     "pancreatic cancer and shapes its aggressive behaviour."},
            {"label": "CONCLUSIONS",
             "text": "PDAC therefore follows a stereotyped genetic trajectory — KRAS activation "
                     "followed by loss of CDKN2A, TP53 and SMAD4 — embedded within a distinctive "
                     "fibrotic microenvironment."},
        ],
    },
    {
        "title":   "Late diagnosis and biomarkers in cancer of the pancreas",
        "authors": "(illustrative teaching abstract)",
        "journal": "NdabaX Workshop Corpus",
        "year":    "—",
        "sections": [
            {"label": "BACKGROUND",
             "text": "Cancer of the pancreas is usually detected at an advanced stage, because "
                     "early tumours of the exocrine pancreas grow silently and produce "
                     "non-specific symptoms such as weight loss and painless jaundice. The great "
                     "majority of these tumours are adenocarcinomas arising in the head of the "
                     "gland."},
            {"label": "RESULTS",
             "text": "Contrast-enhanced computed tomography defines the local extent of the "
                     "tumour and its relationship to the mesenteric vessels, while endoscopic "
                     "ultrasound with fine-needle aspiration provides tissue for histological "
                     "confirmation. The carbohydrate antigen CA19-9 is the most widely used serum "
                     "biomarker: it helps monitor response to treatment and detect recurrence, "
                     "but its limited sensitivity and specificity make it unsuitable for "
                     "screening. In a large proportion of patients the pancreatic adenocarcinoma "
                     "has already metastasised to the liver or peritoneum at presentation, which "
                     "precludes curative resection."},
            {"label": "CONCLUSIONS",
             "text": "Late presentation and the absence of a reliable early biomarker remain "
                     "central obstacles to improving outcomes in pancreatic cancer."},
        ],
    },
    {
        "title":   "Chemotherapy and drug resistance in pancreatic adenocarcinoma",
        "authors": "(illustrative teaching abstract)",
        "journal": "NdabaX Workshop Corpus",
        "year":    "—",
        "sections": [
            {"label": "BACKGROUND",
             "text": "Because most patients present with unresectable or metastatic disease, "
                     "systemic chemotherapy is the mainstay of treatment for advanced pancreatic "
                     "adenocarcinoma. For many years gemcitabine given as a single agent was the "
                     "reference regimen, but it produced only modest gains in survival."},
            {"label": "RESULTS",
             "text": "Two combination regimens have since improved outcomes for patients well "
                     "enough to tolerate them: FOLFIRINOX, which couples fluorouracil, irinotecan "
                     "and oxaliplatin, and gemcitabine combined with nab-paclitaxel. Both extend "
                     "median survival by several months compared with gemcitabine alone, though "
                     "at the cost of greater toxicity. Responses are often short-lived, however, "
                     "because the tumour's dense desmoplastic stroma raises interstitial pressure "
                     "and forms a physical barrier that limits delivery of these drugs to the "
                     "malignant cells. Cancer-associated fibroblasts within the stroma further "
                     "support tumour-cell survival and contribute to the chemoresistance that "
                     "characterises pancreatic cancer."},
            {"label": "CONCLUSIONS",
             "text": "Overcoming the stromal barrier is thus a central goal in the treatment of "
                     "pancreatic ductal adenocarcinoma."},
        ],
    },
    {
        "title":   "The genomic landscape and microenvironment of PDAC",
        "authors": "(illustrative teaching abstract)",
        "journal": "NdabaX Workshop Corpus",
        "year":    "—",
        "sections": [
            {"label": "BACKGROUND",
             "text": "Large-scale sequencing studies have defined the genomic landscape of "
                     "pancreatic ductal adenocarcinoma (PDAC) and shown that it is dominated by a "
                     "small number of recurrently mutated genes. KRAS, TP53, CDKN2A and SMAD4 — "
                     "the four canonical drivers — are altered in the majority of tumours, "
                     "whereas most other mutations occur at low frequency across many genes."},
            {"label": "RESULTS",
             "text": "Beyond these drivers, PDAC is distinguished by an extensive tumour "
                     "microenvironment. Cancer-associated fibroblasts deposit a collagen-rich "
                     "extracellular matrix, and together they form the desmoplastic stroma that "
                     "can make up the bulk of the tumour mass. This microenvironment is "
                     "profoundly immunosuppressive: it excludes cytotoxic T cells and recruits "
                     "regulatory immune populations, so the pancreatic cancer evades immune "
                     "attack and responds poorly to immune-checkpoint blockade. The same stromal "
                     "signalling promotes cancer-cell proliferation, invasion and metastasis to "
                     "the liver."},
            {"label": "CONCLUSIONS",
             "text": "The interplay between a conserved set of driver mutations and a hostile "
                     "microenvironment underlies the aggressive biology of pancreatic "
                     "adenocarcinoma."},
        ],
    },
    {
        "title":   "Surgical resection and relapse in pancreatic cancer",
        "authors": "(illustrative teaching abstract)",
        "journal": "NdabaX Workshop Corpus",
        "year":    "—",
        "sections": [
            {"label": "BACKGROUND",
             "text": "Complete surgical resection offers the only realistic prospect of cure for "
                     "pancreatic cancer, yet fewer than one in five patients have disease that is "
                     "anatomically resectable at diagnosis. Tumours in the head of the pancreas "
                     "are removed by pancreaticoduodenectomy, the Whipple procedure, which "
                     "resects the pancreatic head together with the duodenum, distal bile duct "
                     "and adjacent lymph nodes."},
            {"label": "RESULTS",
             "text": "Even when the pancreatic tumour is excised with clear margins, most "
                     "patients relapse within two years, because occult micrometastases are "
                     "already present at the time of operation. Adjuvant chemotherapy given after "
                     "surgery reduces this risk and modestly prolongs survival, and it is now "
                     "standard practice for patients who recover sufficiently. Recurrence appears "
                     "most often in the liver or as local disease at the resection bed, "
                     "reflecting the early metastatic tendency of cancer of the pancreas."},
            {"label": "CONCLUSIONS",
             "text": "Surgery is therefore necessary but rarely sufficient for cure in pancreatic "
                     "ductal adenocarcinoma, underscoring the importance of effective systemic "
                     "therapy."},
        ],
    },
]


# ── The ontology (same shape as extraction.ONTOLOGY_TYPES) ────────────── #
# Every pancreatic-cancer surface form is meant to ground to the SINGLE
# neoplasm concept below — that is the synonym-bridging the entity-mapping
# step demonstrates.
PANCREATIC_ONTOLOGY = [
    {
        "type": "Neoplastic Process", "umls": "T191",
        "reason": "The malignancy under study — the tumour, its precursor lesions and "
                  "histological subtypes. Every surface form (PDAC, adenocarcinoma, "
                  "cancer of the pancreas) denotes this one concept.",
        "mesh": ["Pancreatic Neoplasms", "Pancreatic Intraepithelial Neoplasia"],
    },
    {
        "type": "Anatomical Structure", "umls": "T017",
        "reason": "Organs, tissues and structures where the disease arises or spreads.",
        "mesh": ["Pancreas", "Liver", "Peritoneum", "Duodenum", "Bile Ducts",
                 "Lymph Nodes", "Extracellular Matrix"],
    },
    {
        "type": "Gene or Protein", "umls": "T028",
        "reason": "Driver genes and signalling proteins implicated in tumour biology.",
        "mesh": ["KRAS gene", "TP53 gene", "CDKN2A gene", "SMAD4 gene"],
    },
    {
        "type": "Pharmacologic Substance", "umls": "T121",
        "reason": "Chemotherapy agents and regimens used in treatment.",
        "mesh": ["Gemcitabine", "FOLFIRINOX", "Paclitaxel", "Fluorouracil",
                 "Irinotecan", "Oxaliplatin"],
    },
    {
        "type": "Biological Process", "umls": "T038",
        "reason": "Dynamic disease processes — spread, growth, invasion.",
        "mesh": ["Neoplasm Metastasis", "Cell Proliferation", "Neoplasm Invasiveness"],
    },
    {
        "type": "Cell", "umls": "T025",
        "reason": "Cell populations that make up the tumour and its microenvironment.",
        "mesh": ["Cancer-Associated Fibroblasts", "T-Lymphocytes"],
    },
    {
        "type": "Biomarker", "umls": "T201",
        "reason": "Measurable indicators used for diagnosis or monitoring.",
        "mesh": ["CA-19-9 Antigen"],
    },
]


# Known surface forms for a concept — the synonym dictionary that entity linking
# uses BEFORE falling back to embeddings (embeddings alone score "PDAC" vs
# "Pancreatic Neoplasms" far too low to bridge).
SYNONYMS = {
    "Pancreatic Neoplasms": [
        "pancreatic ductal adenocarcinoma", "pancreatic adenocarcinoma",
        "adenocarcinoma of the pancreas", "cancer of the pancreas",
        "pancreatic cancer", "pancreatic tumour", "pancreatic tumor",
        "pancreatic tumours", "pancreatic tumors", "adenocarcinoma", "pdac",
    ],
    "Pancreatic Intraepithelial Neoplasia": ["pancreatic intraepithelial neoplasia", "panin"],
    "KRAS gene":   ["kras"],
    "TP53 gene":   ["tp53", "p53"],
    "CDKN2A gene": ["cdkn2a", "p16"],
    "SMAD4 gene":  ["smad4"],
    "Paclitaxel":  ["nab-paclitaxel", "nab paclitaxel", "paclitaxel"],
    "FOLFIRINOX":  ["folfirinox"],
    "Cancer-Associated Fibroblasts": ["cancer-associated fibroblasts", "cancer associated fibroblasts"],
    "T-Lymphocytes": ["cytotoxic t cells", "t lymphocytes", "t cells", "t-cells"],
}


# A stable colour per ontology type — used for the schema graph AND the instance
# graphs so the two are visually comparable.
TYPE_COLOURS = {
    "Neoplastic Process":      "#ef4444",   # red
    "Anatomical Structure":    "#3b82f6",   # blue
    "Gene or Protein":         "#8b5cf6",   # violet
    "Pharmacologic Substance": "#10b981",   # green
    "Biological Process":      "#f59e0b",   # amber
    "Cell":                    "#ec4899",   # pink
    "Biomarker":               "#06b6d4",   # cyan
}

# Type-level schema: the typical (subject type → relation → object type) patterns
# the extractor is expected to populate. Rendered as the "ontology schema" graph.
SCHEMA_RELATIONS = [
    ("Gene or Protein",         "drives",          "Neoplastic Process"),
    ("Neoplastic Process",      "arises in",       "Anatomical Structure"),
    ("Neoplastic Process",      "metastasises to", "Anatomical Structure"),
    ("Neoplastic Process",      "undergoes",       "Biological Process"),
    ("Pharmacologic Substance", "treats",          "Neoplastic Process"),
    ("Cell",                    "shapes",          "Neoplastic Process"),
    ("Biomarker",               "monitors",        "Neoplastic Process"),
]


def schema_triples() -> list[dict]:
    """Type-level triples for rendering the ontology itself as a knowledge graph."""
    return [
        {"subject": s, "subject_type": s, "predicate": p, "predicate_type": "schema",
         "object": o, "object_type": o, "confidence": 1.0,
         "sentence": f"{s} {p} {o}", "section": "SCHEMA"}
        for s, p, o in SCHEMA_RELATIONS
    ]


# ── Accessors (mirrors the small helpers in mystery.py / extraction.py) ── #

def abstracts() -> list[dict]:
    return [dict(a) for a in ABSTRACTS]


def working_abstract() -> dict:
    """The single abstract used for the chunking / coref / KG walk-through."""
    return dict(ABSTRACTS[0])


def sections(abstract: dict) -> tuple[list[str], list[str]]:
    """Return (contexts, labels) — the shape extract_obie / extract_openie want."""
    return ([s["text"] for s in abstract["sections"]],
            [s["label"] for s in abstract["sections"]])


def full_text(abstract: dict) -> str:
    return " ".join(s["text"] for s in abstract["sections"])


def synonyms() -> dict[str, list[str]]:
    return {k: list(v) for k, v in SYNONYMS.items()}


def mesh_headings() -> list[str]:
    """Flat list of every MeSH heading — the ontology_terms for OBIE / grounding."""
    return [m for t in PANCREATIC_ONTOLOGY for m in t["mesh"]]


def mesh_to_type() -> dict[str, str]:
    """Map each MeSH heading to the ontological type it instantiates."""
    return {m: t["type"] for t in PANCREATIC_ONTOLOGY for m in t["mesh"]}


def type_names() -> list[str]:
    return [t["type"] for t in PANCREATIC_ONTOLOGY]


# ── paper-card view (renders identically to notebook 4's render_abstract) ── #
SOURCE = "NdabaX corpus"

# Per-abstract metadata for the rich paper card: a focus question, a one-line
# conclusion, and the MeSH concepts the abstract touches (parallel to ABSTRACTS).
_META = [
    {"question": "What defines pancreatic ductal adenocarcinoma, and which mutations drive its progression?",
     "answer":   "PDAC develops from PanIN precursor lesions in the ductal epithelium; early KRAS activation, "
                 "then loss of CDKN2A, TP53 and SMAD4, drives progression to invasive, metastatic disease "
                 "within a dense desmoplastic stroma.",
     "meshes":   ["Pancreatic Neoplasms", "Pancreatic Intraepithelial Neoplasia", "Pancreas",
                  "KRAS gene", "TP53 gene", "CDKN2A gene", "SMAD4 gene", "Cancer-Associated Fibroblasts"]},
    {"question": "Why is cancer of the pancreas diagnosed late, and what biomarker monitors it?",
     "answer":   "Pancreatic adenocarcinoma is usually found late; CA19-9 helps monitor disease but lacks "
                 "early sensitivity, and metastasis to the liver or peritoneum at diagnosis often precludes "
                 "curative surgery.",
     "meshes":   ["Pancreatic Neoplasms", "Pancreas", "CA-19-9 Antigen", "Neoplasm Metastasis",
                  "Liver", "Peritoneum"]},
    {"question": "What chemotherapy is used for advanced pancreatic adenocarcinoma, and why does resistance arise?",
     "answer":   "FOLFIRINOX and gemcitabine plus nab-paclitaxel extend survival over gemcitabine alone, but "
                 "the dense stroma and cancer-associated fibroblasts limit drug delivery and drive "
                 "chemoresistance.",
     "meshes":   ["Pancreatic Neoplasms", "Gemcitabine", "FOLFIRINOX", "Paclitaxel", "Fluorouracil",
                  "Irinotecan", "Oxaliplatin", "Cancer-Associated Fibroblasts"]},
    {"question": "What are the driver genes and microenvironment of PDAC?",
     "answer":   "Four driver genes dominate PDAC; cancer-associated fibroblasts and an immunosuppressive "
                 "stroma exclude T cells and promote proliferation, invasion and metastasis while blunting "
                 "immunotherapy.",
     "meshes":   ["Pancreatic Neoplasms", "KRAS gene", "TP53 gene", "CDKN2A gene", "SMAD4 gene",
                  "Cancer-Associated Fibroblasts", "T-Lymphocytes", "Neoplasm Metastasis", "Liver"]},
    {"question": "How curable is pancreatic cancer by surgery, and why do patients relapse?",
     "answer":   "Fewer than one in five patients are resectable; even after a Whipple resection, occult "
                 "micrometastasis causes relapse in the liver or resection bed, and adjuvant chemotherapy "
                 "helps only modestly.",
     "meshes":   ["Pancreatic Neoplasms", "Pancreas", "Duodenum", "Bile Ducts", "Lymph Nodes",
                  "Neoplasm Metastasis", "Liver"]},
]


def to_ex(abstract: dict) -> dict:
    """Shape an abstract into the (optional-field) dict render_abstract consumes."""
    meta = next((m for m, a in zip(_META, ABSTRACTS)
                 if a["title"] == abstract["title"]), {})
    ctx, lab = sections(abstract)
    return {
        "pubid": "", "source": SOURCE,
        "question": meta.get("question", ""),
        "long_answer": meta.get("answer", ""),
        "final_decision": "",
        "context": {"contexts": ctx, "labels": lab, "meshes": meta.get("meshes", [])},
    }
