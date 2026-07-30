# Datasets and ML planning

pypsychonaut can produce several datasets from PsychonautWiki. The headline
artefact is a **markdown corpus** (one file per substance, from
`pypsychonaut.dataset.build_corpus`), the retrieval source for a
harm-reduction RAG assistant. The structured GraphQL data and the slang
lexicon also yield clean tabular datasets.

## What this client can produce

### 1. Substance markdown corpus (RAG source)

One markdown file per substance: YAML front-matter (`name`, `url`,
`chemical_class`, `psychoactive_class`, `routes`, `effects`) plus a body with
per-ROA dose/duration tables, tolerance notes, an effects list, and the
source link. `dataset.build_corpus(out_dir, …)` builds it. The build is
resumable and polite.

- **Scale:** a few hundred substances (the whole `Summary_index`).
- **Use:** chunk, embed, and retrieve for a grounded harm-reduction chatbot.
  This corpus is the intended replacement source for the dead
  AskTheCaterpillar Q&A bot, a retrieval-grounded assistant instead of an
  opaque remote API.

### 2. Dose / duration table

**One row per (substance, route, dose-bracket)** from the GraphQL `roas`
field: `substance`, `route`, `units`, `threshold`, `light`/`common`/`strong`
(each `{min, max}`), `heavy`, and the `duration` phases (`onset`, `comeup`,
`peak`, `offset`, `total`, `afterglow`) each as `{min, max, units}`, plus
`bioavailability`.

| Column | Type | Notes |
|---|---|---|
| `substance` | string | join key |
| `route` | string | oral, sublingual, insufflated, … |
| `dose_units` | string | mg, µg, g |
| `common_min` / `common_max` | float | the canonical bracket |
| `total_min` / `total_max` / `total_units` | float / str | trip length |
| `bioavailability_min` / `_max` | float | % |

The table is numeric, well-typed, and immediately loadable as a structured
table.

### 3. Effects taxonomy

**One row per (substance, effect)** edge from the GraphQL `effects` field
(`name`, `url`), plus a node list of distinct effects. This forms a bipartite
substance-to-effect graph and a controlled vocabulary of subjective effects.

### 4. Substance-name and slang lexicon

`pypsychonaut.slang.DRUG_SLANG`, joined with the live
`get_substance_list()`: **one row per (alias, canonical_name)**. This is a
normalisation gazetteer that maps street names to canonical substances.

## Worth publishing on Hugging Face?

| Dataset | Publish? | Why |
|---|---|---|
| Substance markdown corpus | **Yes** | self-contained, citable, the RAG source; small and high-value |
| Dose/duration table | **Yes** | clean numeric table, hard to find structured elsewhere |
| Effects taxonomy | **Yes** | reusable controlled vocabulary and edge list |
| Slang <-> canonical lexicon | **Yes (small)** | a compact, useful NER/normalisation gazetteer |

All datasets derive from PsychonautWiki. Keep its attribution and license
terms with any published artefact, and link back to each substance page (the
corpus already embeds `Source:` URLs).

## ML tasks served

- **Substance NER.** Tag substance mentions in free text. The substance list
  and slang lexicon serve as weak-supervision seeds and an evaluation
  gazetteer.
- **Slang normalisation.** Map street names to canonical substances (`acid ->
  LSD`, `ecstasy -> MDMA`) using a labelled alias-to-canonical pair set.
- **Dose / duration extraction.** Train and evaluate extraction of structured
  dose and duration spans from text against the GraphQL ground truth.
- **Retrieval / RAG.** The markdown corpus grounds a harm-reduction assistant
  (the AskTheCaterpillar successor). Each chunk is attributable to a
  substance page.
- **Effect classification / linking.** Predict or link subjective effects to
  substances using the effects taxonomy.

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

---
[← Advanced](advanced.md) · [Home](../README.md)
