# Source Corpus Overview

This file documents what's in `index/faiss.index` and `index/chunks.pkl` —
useful as a quick reference during the interview if asked "what does your
corpus actually cover?"

Built from the 12 files in `source_docs/`, each a manually curated,
paraphrased summary of official/reputable sources (not scraped — see
README.md "Why not scrape?"). Each doc is tagged with its source URL(s),
which is what powers the citation links shown under each answer in the app.

## Topics covered (3 categories, 12 docs)

**Highly Skilled Migrant Permit** (2 docs)
- `highly_skilled_migrant_overview.txt` — sponsor system, permit basics
  — ind.nl
- `highly_skilled_migrant_requirements.txt` — salary thresholds, MVV entry
  visa — business.gov.nl

**BSN (Citizen Service Number)** (2 docs)
- `bsn_registration_process.txt` — how/where to register, required documents
  — netherlandsworldwide.nl, living-in-holland.nl
- `bsn_what_and_where.txt` — what it's used for, finding an existing BSN
  — netherlandsworldwide.nl, wise.com

**30% Ruling (Expat Tax Scheme)** (2 docs)
- `thirty_percent_ruling_eligibility.txt` — who qualifies, salary
  thresholds, the 150km rule — iamsterdam.com, business.gov.nl
- `thirty_percent_ruling_application.txt` — how to apply, processing time,
  what happens if you change employers — octagonpeople.com, business.gov.nl

**Health Insurance** (2 docs)
- `health_insurance_requirement.txt` — the 4-month mandatory deadline,
  basic package rules — government.nl, iamexpat.nl
- `health_insurance_switching_subsidy.txt` — annual switching window,
  zorgtoeslag subsidy — expatfocus.com, feather-insurance.com

**DigiD** (2 docs)
- `digid_application.txt` — what it's for, standard domestic application
  — digid.nl, iamexpat.nl
- `digid_from_abroad.txt` — applying before arrival, collection codes,
  video-call verification — netherlandsworldwide.nl, denhaag.nl

**Banking & Address Registration** (2 docs)
- `opening_dutch_bank_account.txt` — BSN vs. no-BSN account options
  — abnamro.nl, dutchreview.com
- `address_change_reporting.txt` — reporting a move within NL, deadlines,
  fines — government.nl, iamexpat.nl

## Regenerating this index

This file is documentation only — it isn't read by the app. If `source_docs/`
changes, rebuild the actual index with:

```bash
python src/ingest.py
```

which overwrites `index/faiss.index` and `index/chunks.pkl`. Update this
file's topic list by hand afterward if docs were added, removed, or renamed.
