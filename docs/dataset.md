# Datasets and ML planning

pypsychonaut can produce several datasets from PsychonautWiki. The headline
artefact is a **markdown corpus** (one file per substance, from
`pypsychonaut.dataset.build_corpus`) — the retrieval source for a harm-reduction
RAG assistant. Alongside it, the GraphQL API yields structured substance data,
reagent test results, and full-wiki page text.

The **batch scrapers** live in `ml/psychonautics-dataset/` and are driven by the
global `tools/dataset_queue.sh`.

## What this client can produce

### 1. Expanded substance records (GraphQL)

All 18 Substance fields from the GraphQL API: dosing per RoA (list and typed),
tolerance, effects, chemical/psychoactive class, addiction potential, toxicity,
cross-tolerances, common names, systematic name, summary, images, interactions
(uncertain/unsafe/dangerous), and reagent test results.

**Script:** `scrape_psychonaut.py` → `psychonautwiki.jsonl`
**Rows:** ~317 substances, one JSON object per row.

### 2. LLM-enriched substance records

Same structured data merged with 21 prose fields extracted from the page text by
a local Gemma LLM: summary, common names, chemistry formula, mechanism of action,
metabolism, half-life, toxicity, addiction potential, legal status, history, etc.

**Script:** `scrape_psychonaut_full.py` → `psychonautwiki_substances.jsonl`
**Rows:** ~317 substances, with `structured` and `llm_enriched` keys.
Add `--page-text` to include the raw rendered HTML text.

### 3. Substance markdown corpus (RAG source)

One markdown file per substance: YAML front-matter (`name`, `url`,
`chemical_class`, `psychoactive_class`, `routes`, `effects`) plus a body with
per-ROA dose/duration tables, tolerance notes, an effects list and the source
link. Built by `dataset.build_corpus(out_dir, …)`, resumable and polite. This
corpus is the intended replacement source for the dead AskTheCaterpillar Q&A bot
— a retrieval-grounded assistant instead of an opaque remote API.

### 4. Full-wiki page text

Every wiki page discovered via the sitemap (18k+ pages): substances, effects,
trip reports, categories, article stubs. Each record is `{title, url, content,
char_count}` with the rendered text.

**Script:** `scrape_psychonaut_pages.py` → `psychonautwiki_pages.jsonl`
**Rows:** ~18,669 pages (the full sitemap).

### 5. Reagent test data

Two files: the reagent master list (15 reagents with names, short names,
white-first-color) plus reagent colors (27 named colors), and per-substance
reagent test results (which reagent changes what color for each substance).

**Script:** `scrape_psychonaut_reagents.py` → `psychonautwiki_reagents.jsonl`
(static) + `psychonautwiki_reagents_results.jsonl` (per-substance).

### 6. Dose / duration table

One row per (substance, route, dose-bracket) from the GraphQL `roas`:
`substance`, `route`, `units`, `threshold`, `light/common/strong {min,max}`,
`heavy`, and the `duration` phases (`onset`, `comeup`, `peak`, `offset`,
`total`, `afterglow`) each as `{min, max, units}`, plus `bioavailability`.

### 7. Effects taxonomy

One row per (substance, effect) edge from `effects` (`name`, `url`,
`substances`). A controlled vocabulary of subjective effects.

### 8. Substance-name + slang lexicon

`pypsychonaut.slang.DRUG_SLANG` joined with the live `get_substance_list()`:
one row per (alias, canonical_name). A normalisation gazetteer mapping street
names to canonical substances.

## Worth publishing on Hugging Face?

| Dataset | Publish? | Why |
|---|---|---|
| Expanded substance records | **Yes** | self-contained, citable, all PW fields |
| LLM-enriched substance records | **Yes** | prose fields fill gaps the API misses |
| Substance markdown corpus | **Yes** | self-contained, the RAG source |
| Full-wiki page text | **Yes** | comprehensive knowledge base |
| Reagent test data | **Yes** | hard to find structured elsewhere |
| Dose/duration table | **Yes** | clean numeric table |
| Effects taxonomy | **Yes** | reusable controlled vocabulary + edge list |
| Slang ↔ canonical lexicon | **Yes (small)** | NER/normalisation gazetteer |

All datasets derive from PsychonautWiki. Keep its attribution and license
terms with any published artefact, and link back to each substance page (the
corpus already embeds `Source:` URLs).

## ML tasks served

- **Substance NER** — tag substance mentions in free text; the substance list +
  slang lexicon are weak-supervision seeds and an evaluation gazetteer.
- **Slang normalisation** — map street names to canonical substances
  (`acid → LSD`, `ecstasy → MDMA`); a labelled alias→canonical pair set.
- **Dose / duration extraction** — train/evaluate extracting structured dose and
  duration spans from text against the GraphQL ground truth.
- **Retrieval / RAG** — the markdown corpus and full-wiki page text grounds a
  harm-reduction assistant (the AskTheCaterpillar successor); each chunk is
  attributable to a substance page.
- **Effect classification / linking** — predict or link subjective effects to
  substances from the effects taxonomy.
- **Reagent test classification** — predict reagent test outcomes from
  substance structure; build a reagent test recommendation system.

## Recipe

```python
from pypsychonaut import dataset

# validate on a small, polite sample first
print(dataset.build_corpus("corpus", limit=5, delay=1.0))

# full run (treat as a homelab job: raise delay, drop the limit)
# dataset.build_corpus("corpus", delay=2.0)
```

The dump reuses one `Transport`, sleeps `delay` seconds between substances,
and skips files already written. You can kill and resume it freely.

See `examples/04_build_corpus.py` for a runnable version.

## Batch scrapers (queue-driven)

All scrapers are registered in `tools/dataset_queue.sh` under the `pw-*` labels
and run under `tools/cap` (4G RAM, 250% CPU, 24h timeout, 6 concurrent slots).
Each is resumable — kill and re-run safely.
