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
<img width="773" height="755" alt="image" src="https://github.com/user-attachments/assets/53daa194-354e-415c-9c09-3fb179dc63d2" />

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
export GROQ_API_KEY=your_free_key (placeholder)   # https://console.groq.com
python src/ingest.py                # builds the FAISS index from source_docs/
streamlit run src/app.py            # provides UI and runs the application
```

Without a `GROQ_API_KEY`, the app still runs and shows the raw retrieved
context instead of a generated answer — useful for demonstrating retrieval
and generation as separate, independently-testable steps.

## Why not scrape the source websites?

I manually curated 12 pages rather than scraping IND and government websites. For a small, legally-sensitive corpus, that was faster than building an automated scraper. It's also arguably a better product since the source text is specific to immigration content, valuing quality over quantity.

## Design tradeoffs (and what I'd revisit at scale)

- **Chunk size (350 words, 50-word overlap):** I converted each source into one vector to embed them. The documents were small enough that they didn't need to be further chunked, and I used these directly to make the vectors. I had 12 vectors with one "chunk” each for 12 documents. Each document has two url sources that get preserved.
- **FAISS `IndexFlatIP` (exact search):** I'm using FAISS with an exact search index. It checks similarity against every vector directly, which is fine up to roughly 100,000 to a million vectors, and gives perfect recall. This makes my current version easy to scale from 12 to a couple hundred thousand vectors. Beyond that, we'd have to look at other ways to implement the recall.
- **Local embedding model (MiniLM, 384-dim):** fast and free, but lower
  quality than larger hosted embedding models. Good enough for a focused
  3-topic demo; I'd re-evaluate against a larger model if the corpus grew to
  cover all IND permit types.
- **Answer-only-from-context prompting:** The main safeguard against wrong answers is the prompt itself. The model is instructed to answer only from retrieved context and say so plainly if it can't. Initial tests showed that prompts designed to override the instructions could cause the model to deviate from its intended behaviour. However, this issue was addressed and resolved in later versions.
- **Source freshness:** immigration and tax rules change (the 2026/2027 30%
  ruling rate change is a good example). Right now the corpus is static. At
  scale this needs a re-scraping/re-ingestion schedule, versioning so old
  answers can be distinguished from current ones, and ideally a "last updated"
  timestamp shown to the user per source.
- **Single-Turn Model** each question is answered independently. This
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
