# NL Expat Guide 🇳🇱

A retrieval-augmented Q&A assistant for common Netherlands immigration questions
(highly skilled migrant permits, BSN registration, the 30% ruling). It answers
in plain language, cites its sources, and always points the user to the IND or
Belastingdienst for anything binding.

**Why this exists:** immigration information in the Netherlands is scattered
across IND, gemeente, and Belastingdienst pages written in dense official
language. This project explores whether a small, carefully-scoped RAG system
can make that information easier to navigate — without pretending to replace
official guidance.

## How it works

```
question ──▶ embed (MiniLM) ──▶ FAISS similarity search ──▶ top-k chunks
                                                                  │
                                                                  ▼
                                              LLM (Groq, context-only prompt)
                                                                  │
                                                                  ▼
                                              answer + source links + IND/
                                              Belastingdienst reminder
```

1. **Source curation** (`source_docs/`): a small set of manually written,
   paraphrased summaries of official/reputable pages (IND, business.gov.nl,
   I amsterdam, NetherlandsWorldwide), each tagged with its source URL.
   Content is *not* scraped — see "Why not scrape?" below.
2. **Ingestion** (`src/ingest.py`): splits each doc into ~350-word overlapping
   chunks, embeds them locally with `sentence-transformers` (MiniLM), and
   stores the vectors in a FAISS index.
3. **Retrieval + generation** (`src/rag.py`): embeds the user's question,
   retrieves the top-4 most similar chunks, and passes them to an LLM with a
   system prompt that restricts it to answering only from that context.
4. **UI** (`src/app.py`): a Streamlit app for asking questions and viewing
   cited sources.

Everything runs on free tiers: local embeddings (no API cost), FAISS (local,
no subscription), Groq's free-tier API for generation, Streamlit Community
Cloud for hosting.

## Setup

```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_free_key   # https://console.groq.com
python src/ingest.py                # builds the FAISS index from source_docs/
streamlit run src/app.py
```

Without a `GROQ_API_KEY`, the app still runs and shows the raw retrieved
context instead of a generated answer — useful for demonstrating retrieval
and generation as separate, independently-testable steps.

## Why not scrape the source websites?

For a small, legally-sensitive corpus like this, manually curating ~15-20
pages was faster than building a compliant scraper, and it sidesteps open
questions around government site terms of service and the EU database right.
It also produces a better product: source accuracy and provenance matter more
here than raw volume, since bad information about immigration has real
consequences for someone.

## Design tradeoffs (and what I'd revisit at scale)

- **Chunk size (350 words, 50-word overlap):** smaller chunks retrieve more
  precisely but lose surrounding context; larger chunks keep context but
  dilute relevance scores. This was tuned by eye for explanatory prose, not
  systematically evaluated — with more time I'd build a small labelled
  eval set (question → correct source) and grid-search chunk size/overlap
  against retrieval accuracy.
- **FAISS `IndexFlatIP` (exact search):** fine up to roughly 100k–1M vectors,
  after which exact search gets slow. At real scale (the full IND + gemeente
  site corpus) I'd move to an approximate index (HNSW or IVF) and accept a
  small recall tradeoff for speed, or move to a managed vector DB if this
  needed to be a multi-tenant service.
- **Local embedding model (MiniLM, 384-dim):** fast and free, but lower
  quality than larger hosted embedding models. Good enough for a focused
  3-topic demo; I'd re-evaluate against a larger model if the corpus grew to
  cover all IND permit types.
- **Answer-only-from-context prompting:** the main hallucination guardrail.
  It's not foolproof — the model can still misread a chunk — so a production
  version would need an evaluation set of known Q&A pairs plus a way to flag
  low-confidence answers (e.g. low retrieval similarity score) for a "I'm not
  sure, check the IND directly" response instead of a confident-sounding guess.
- **Source freshness:** immigration and tax rules change (the 2026/2027 30%
  ruling rate change is a good example). Right now the corpus is static. At
  scale this needs a re-scraping/re-ingestion schedule, versioning so old
  answers can be distinguished from current ones, and ideally a "last updated"
  timestamp shown to the user per source.
- **No conversation memory:** each question is answered independently. This
  keeps the system simple and easy to reason about, at the cost of not
  handling follow-up questions like "what about for my partner?" naturally.

## Limitations

This is a demo, not a legal or tax tool. It answers only from the small set of
sources in `source_docs/`, doesn't handle every visa category or edge case,
and rules like salary thresholds and the 30% ruling percentage change over
time. Always verify anything binding with the IND or Belastingdienst directly.

## Project structure

```
source_docs/    curated, cited source text
src/ingest.py   chunking + embedding + FAISS index build
src/rag.py      retrieval + generation pipeline
src/app.py      Streamlit UI
requirements.txt
```
