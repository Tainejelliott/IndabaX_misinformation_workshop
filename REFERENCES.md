# References for Workshop Visuals

This file catalogs the real-world sources behind the techniques, models, benchmarks, and
factual claims used across the interactive HTML visuals in `notebook_src/html/`. Every
link below was checked against a live web search before being added.

**Scope note — what is *not* in this file:** most visuals also contain invented
illustrative material built for teaching purposes only — fictional people ("Dr. Amara
Nwosu"), fictional organisations ("GreenFund Foundation"), and hand-picked numeric
examples (cosine-similarity scores, BM25/dense score comparisons, RRF rank tables,
model-comparison chip ratings). None of that is a real study or measurement, so none of
it is cited here — inventing a citation for it would itself be a small act of the
misinformation this workshop is about. Where a table below cites a real technique (e.g.
BM25, RRF) applied to one of those invented examples, the citation is for the technique
only, not for the example's specific numbers.

Legend for **Type**: `paper` = peer-reviewed / arXiv paper, `webpage` = official
documentation or reference site, `article` = journalism / popular-science piece.

---

## `concept_llm.html` — "What is an LLM?"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | Attention Is All You Need | Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin (2017) | [arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762) | The Transformer/attention mechanism underlying "LLM assigns a probability to every possible next token" |
| article | No, You Can't See the Great Wall of China from Space | Scientific American | [scientificamerican.com/article/no-you-cant-see-the-great-wall-of-space](https://www.scientificamerican.com/article/no-you-cant-see-the-great-wall-of-china-from-space/) | The example hallucination in the key-insight box ("The Great Wall is visible from space") |
| webpage | Great Wall (image caption) | NASA | [nasa.gov/image-article/great-wall](https://www.nasa.gov/image-article/great-wall/) | Corroborates the Great Wall visibility myth is false |

## `concept_embeddings.html` — "What are Embeddings?"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | Efficient Estimation of Word Representations in Vector Space | Mikolov, Chen, Corrado, Dean (2013) | [arxiv.org/abs/1301.3781](https://arxiv.org/abs/1301.3781) | Foundational claim that "semantically similar texts produce geometrically nearby vectors" |
| article | Do goldfish really have a 3-second memory? | Live Science | [livescience.com/goldfish-memory.html](https://www.livescience.com/goldfish-memory.html) | Context note: the example sentence "Goldfish have a three-second memory" is itself a well-known myth (real retention is documented at 5+ months) — used here only as neutral example text to encode, not asserted as true |

## `concept_rag.html` — "What is RAG?"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | Lewis, Perez, Piktus, Petroni, Karpukhin, Goyal, Küttler, Lewis, Yih, Rocktäschel, Riedel, Kiela (2020), NeurIPS | [arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401) | The Question→Retrieve→Augment→Generate→Answer pipeline and the "reduces hallucination" claim |

## `llm_prediction_pipeline.html` — "The Prediction Pipeline"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | Attention Is All You Need | Vaswani et al. (2017) | [arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762) | The two "Attention" chambers in the animated pipeline diagram |

## `rag_pipeline_overview.html` — "The RAG Pipeline"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | Lewis et al. (2020) | [arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401) | Overall offline-indexing / online-query two-phase RAG architecture |

## `embedding_space_explorer.html` — "Exploring Embedding Space"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | Efficient Estimation of Word Representations in Vector Space | Mikolov, Chen, Corrado, Dean (2013) | [arxiv.org/abs/1301.3781](https://arxiv.org/abs/1301.3781) | Word2Vec model itself; embedding-space clustering tab |
| paper | Linguistic Regularities in Continuous Space Word Representations | Mikolov, Yih, Zweig (2013), NAACL-HLT | [aclanthology.org/N13-1090](https://aclanthology.org/N13-1090/) | "Vector arithmetic" tab: king − man + woman ≈ queen, Paris − France + Germany ≈ Berlin |
| paper | Deep contextualized word representations (ELMo) | Peters, Neumann, Iyyer, Gardner, Clark, Lee, Zettlemoyer (2018), NAACL | [arxiv.org/abs/1802.05365](https://arxiv.org/abs/1802.05365) | "Dynamic Vectors" tab: same word gets a different vector depending on context |
| paper | BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding | Devlin, Chang, Lee, Toutanova (2018) | [arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805) | "Dynamic Vectors" tab: contextual (vs. static) embeddings; the "bank" polysemy illustration is standard in this literature |

## `embeddings_llm_relationship.html` — "How Embeddings Power the RAG Pipeline"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | Learning Transferable Visual Models From Natural Language Supervision (CLIP) | Radford, Kim, Hallacy, et al. (2021) | [arxiv.org/abs/2103.00020](https://arxiv.org/abs/2103.00020) | "What breaks cross-model" tab: CLIP as an example of explicit image↔text space alignment |
| paper | Language-agnostic BERT Sentence Embedding (LaBSE) | Feng, Yang, Cer, Arivazhagan, Wang (2020) | [arxiv.org/abs/2007.01852](https://arxiv.org/abs/2007.01852) | Same tab: LaBSE as an example of cross-lingual embedding alignment |
| paper | BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding | Devlin et al. (2018) | [arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805) | mBERT mention alongside LaBSE for cross-lingual alignment |

## `knowledge_graph_deep_dive.html` — "Knowledge Graphs & Data Stores"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | Efficient Estimation of Word Representations in Vector Space | Mikolov et al. (2013) | [arxiv.org/abs/1301.3781](https://arxiv.org/abs/1301.3781) | "Shallow" tier (Word2Vec) in the embedding-depth table |
| paper | GloVe: Global Vectors for Word Representation | Pennington, Socher, Manning (2014), EMNLP | [nlp.stanford.edu/projects/glove](https://nlp.stanford.edu/projects/glove/) | "Shallow" tier (GloVe) in the embedding-depth table |
| paper | MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers | Wang, Wei, Dong, Bao, Yang, Zhou (2020) | [arxiv.org/abs/2002.10957](https://arxiv.org/abs/2002.10957) | "Medium" tier (MiniLM) in the embedding-depth table |
| paper | Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks | Reimers, Gurevych (2019), EMNLP-IJCNLP | [arxiv.org/abs/1908.10084](https://arxiv.org/abs/1908.10084) | "Medium" tier (all-mpnet family lineage) in the embedding-depth table |
| paper | Text Embeddings by Weakly-Supervised Contrastive Pre-training (E5) | Wang, Yang, Huang, Jiao, Yang, Jiang, Majumder, Wei (2022) | [arxiv.org/abs/2212.03533](https://arxiv.org/abs/2212.03533) | "Deep / large" tier (E5-large) in the embedding-depth table |
| webpage | Neo4j Graph Database | Neo4j, Inc. | [neo4j.com](https://neo4j.com/) | "Knowledge graph store" examples throughout |

## `semantic_search_depth_explorer.html` — "Search Quality & Model Depth"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models | Thakur, Reimers, Rücklé, Srivastava, Gurevych (2021), NeurIPS Datasets & Benchmarks | [arxiv.org/abs/2104.08663](https://arxiv.org/abs/2104.08663) | "Near-perfect on standard synonym benchmarks (BEIR, MTEB)" claim |
| paper | MTEB: Massive Text Embedding Benchmark | Muennighoff, Tazi, Magne, Reimers (2022), EACL 2023 | [arxiv.org/abs/2210.07316](https://arxiv.org/abs/2210.07316) | Same claim |
| paper | MiniLM: Deep Self-Attention Distillation... | Wang et al. (2020) | [arxiv.org/abs/2002.10957](https://arxiv.org/abs/2002.10957) | "Medium (MiniLM 22M)" model-depth tier |
| paper | Text Embeddings by Weakly-Supervised Contrastive Pre-training (E5) | Wang et al. (2022) | [arxiv.org/abs/2212.03533](https://arxiv.org/abs/2212.03533) | "Deep (E5-large 335M)" tier; E5-mistral 8192-token context window mention |

## `information_extraction_methods.html` — "Turning Raw Sources Into a RAG Datastore"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | GLiNER: Generalist Model for Named Entity Recognition using Bidirectional Transformer | Zaratiana, Tomeh, Holat, Charnois (2023/2024), NAACL | [arxiv.org/abs/2311.08526](https://arxiv.org/abs/2311.08526) | "Transformer NER" and LLM/generalist NER row in the method-comparison grid |
| webpage | spaCy: Industrial-Strength NLP | Explosion (Honnibal, Montani) | [spacy.io](https://spacy.io/) | "Statistical NER (CRF, spaCy)" row in the method-comparison grid |

## `knowledge_representation_spectrum.html` — "From Prose to Predicates"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | WordNet: A Lexical Database for English | Miller (1995), Communications of the ACM | [dl.acm.org/doi/10.1145/219717.219748](https://dl.acm.org/doi/10.1145/219717.219748) | "Symbolic / ontological" ideology card, example list |
| paper | DBpedia: A Nucleus for a Web of Open Data | Auer, Bizer, Kobilarov, Lehmann, Cyganiak, Ives (2007), ISWC | [dl.acm.org/doi/10.1007/978-3-540-76298-0_52](https://dl.acm.org/doi/10.1007/978-3-540-76298-0_52) | Same card |
| paper | CYC: A Large-Scale Investment in Knowledge Infrastructure | Lenat (1995), Communications of the ACM | [dl.acm.org/doi/10.1145/219717.219745](https://dl.acm.org/doi/10.1145/219717.219745) | Same card |
| webpage | SNOMED CT | SNOMED International | [snomed.org/what-is-snomed-ct](https://www.snomed.org/what-is-snomed-ct) | "In The Wild" tab: medical ontology example; symbolic ideology card |
| paper | Efficient Estimation of Word Representations in Vector Space | Mikolov et al. (2013) | [arxiv.org/abs/1301.3781](https://arxiv.org/abs/1301.3781) | "Statistical / distributional" ideology card |
| paper | BERT: Pre-training of Deep Bidirectional Transformers... | Devlin et al. (2018) | [arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805) | Same card |
| paper | From Local to Global: A Graph RAG Approach to Query-Focused Summarization | Edge, Trinh, Cheng, Bradley, Chao, Mody, Truitt, Metropolitansky, Ness, Larson (2024), Microsoft Research | [arxiv.org/abs/2404.16130](https://arxiv.org/abs/2404.16130) | "Neuro-symbolic / hybrid" ideology card |
| paper | Wikidata: A Free Collaborative Knowledgebase | Vrandečić, Krötzsch (2014), Communications of the ACM | [dl.acm.org/doi/10.1145/2629489](https://dl.acm.org/doi/10.1145/2629489) | "In The Wild" tab: Wikidata example |

## `information_retrieval_methods.html` — "Getting the Right Chunk"

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | The Probabilistic Relevance Framework: BM25 and Beyond | Robertson, Zaragoza (2009), Foundations and Trends in Information Retrieval | [scirp.org (full ref)](https://www.scirp.org/reference/referencespapers?referenceid=3896864) | "Sparse vs Dense" tab: BM25 sparse retrieval concept |
| paper | Reciprocal Rank Fusion outperforms Condorcet and Individual Rank Learning Methods | Cormack, Clarke, Buettcher (2009), SIGIR | [cormack.uwaterloo.ca/cormacksigir09-rrf.pdf](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf) | "Hybrid & Fusion" tab: the exact RRF formula `1/(k+rank)`, k=60, used in the live calculation |
| paper | Passage Re-ranking with BERT | Nogueira, Cho (2019) | [arxiv.org/abs/1901.04085](https://arxiv.org/abs/1901.04085) | "Re-ranking" tab: cross-encoder two-stage retrieval concept |
| paper | Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE) | Gao, Ma, Lin, Callan (2022) | [arxiv.org/abs/2212.10496](https://arxiv.org/abs/2212.10496) | "Query Transformation" tab: HyDE and the Reverse-HyDE variant |
| paper | From Local to Global: A Graph RAG Approach to Query-Focused Summarization | Edge et al. (2024), Microsoft Research | [arxiv.org/abs/2404.16130](https://arxiv.org/abs/2404.16130) | "Graph Traversal" tab: multi-hop KG-grounded retrieval framing |

## `hyde.html` (unused asset — kept as source material; not currently linked from the notebook)

| Type | Title | Author(s) | Link | Used for |
|---|---|---|---|---|
| paper | Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE) | Gao, Ma, Lin, Callan (2022) | [arxiv.org/abs/2212.10496](https://arxiv.org/abs/2212.10496) | HyDE / Reverse-HyDE explanation and diagrams |
| article | No, You Can't See the Great Wall of China from Space | Scientific American | [scientificamerican.com/article/no-you-cant-see-the-great-wall-of-space](https://www.scientificamerican.com/article/no-you-cant-see-the-great-wall-of-china-from-space/) | "Standard RAG fails here" example query |
| article / book chapter | Whence cometh the myth that we only use 10% of our brains? | Beyerstein, B.L. (1999), in *Mind Myths* (S. Della Sala, ed.), Wiley | [Wikipedia summary + citation](https://en.wikipedia.org/wiki/Ten-percent-of-the-brain_myth) | HyDE worked example #1 |
| article | Is blood blue? | Medical News Today | [medicalnewstoday.com/articles/321442](https://www.medicalnewstoday.com/articles/321442) | Reverse-HyDE worked example #2 |

---

## How this was compiled

Every citation above was checked with a live web search at the time of writing (not
pulled purely from model memory) specifically to avoid the failure mode this workshop
warns about — a confident-sounding but wrong reference. If you spot one that's stale or
mis-linked, treat it the same way the workshop teaches: verify against the primary
source before trusting it.
