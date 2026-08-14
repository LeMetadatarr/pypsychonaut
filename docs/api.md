# API reference

## Functions

| Function | Returns | Source |
|---|---|---|
| `get_substance_list(*, transport=None)` | `List[str]` | `Summary_index` HTML |
| `get_substance_index(*, transport=None)` | nested `dict` | `Summary_index` HTML |
| `extract_substance_name(sentence, *, substance_list=None, transport=None)` | `str \| False` | slang lexicon + list |
| `search_psychonaut_wiki(substance, *, resolve_name=True, transport=None)` | `List[Substance]` | GraphQL API |
| `query_effects(substance, *, transport=None)` | `List[Effect]` | GraphQL `effectsBySubstance` |
| `query_erowid_experiences(substance, *, limit=100, transport=None)` | `List[ErowidExperience]` | GraphQL `erowid` |
| `query_reagents(*, transport=None)` | `List[Reagent]` | GraphQL `reagents` |
| `query_reagent_colors(*, transport=None)` | `List[ReagentColor]` | GraphQL `reagentColors` |
| `query_reagent_results(substance, *, transport=None)` | `List[dict]` | GraphQL `reagentResults` |
| `list_wiki_pages(timeout=30.0)` | `List[str]` | sitemap (requires `sitemapper`) |
| `fetch_page_text(title, *, transport=None)` | `str` | MediaWiki `action=parse` |

Each function takes an optional `transport: Transport`. The module-level
functions use a shared, environment-driven default transport when the caller
gives none.

## Models (`pypsychonaut.types`)

### Core substance models

- **`Substance`** — the top-level record. Fields:

  | Field | Type | GraphQL source |
  |---|---|---|
  | `name` | `str` | `name` |
  | `url` | `Optional[str]` | `url` |
  | `featured` | `bool` | `featured` |
  | `common_names` | `Optional[List[str]]` | `commonNames` |
  | `systematic_name` | `Optional[str]` | `systematicName` |
  | `substance_class` | `Optional[SubstanceClass]` | `class` |
  | `tolerance` | `Optional[Tolerance]` | `tolerance` |
  | `roas` | `List[Roa]` | `roas` (list form) |
  | `roa_typed` | `Optional[RoaTypes]` | `roa` (typed per-route) |
  | `effects` | `List[Effect]` | `effects` |
  | `addiction_potential` | `Optional[str]` | `addictionPotential` |
  | `toxicity` | `Optional[List[str]]` | `toxicity` |
  | `cross_tolerances` | `Optional[List[str]]` | `crossTolerances` |
  | `summary` | `Optional[str]` | `summary` |
  | `images` | `List[SubstanceImage]` | `images` |
  | `uncertain_interactions` | `List[SubstanceInteraction]` | `uncertainInteractions` |
  | `unsafe_interactions` | `List[SubstanceInteraction]` | `unsafeInteractions` |
  | `dangerous_interactions` | `List[SubstanceInteraction]` | `dangerousInteractions` |
  | `reagents` | `Optional[SubstanceReagents]` | `reagents` |

  `page_url` property; `to_dict()` for JSON. Build with `Substance.from_graphql(node)`.

- **`SubstanceClass`** — `chemical: List[str]`, `psychoactive: List[str]`.
- **`Tolerance`** — `full`, `half`, `zero` (free-text).
- **`SubstanceImage`** — `thumb`, `image` (URLs).
- **`SubstanceInteraction`** — `name`, `url`, `addiction_potential`, `toxicity`, `summary`.

### Route-of-administration models

- **`Roa`** — `name`, `dose: Dose`, `duration: Duration`, `bioavailability: Range`.
- **`RoaTypes`** — typed per-route: `oral`, `sublingual`, `buccal`, `insufflated`,
  `rectal`, `transdermal`, `subcutaneous`, `intramuscular`, `intravenous`, `smoked`,
  each `Optional[Roa]`.
- **`Dose`** — `units` (str), `threshold`, `heavy` (float), and `light`/`common`/`strong` as `Range`.
- **`Duration`** — phases `onset`, `comeup`, `peak`, `offset`, `total`, `afterglow`, `duration`, each a `Range`.
- **`Range`** — `{min, max, units}`.

### Effect model

- **`Effect`** — `name`, `url`, `substances: List[str]`.

### Reagent test models

- **`Reagent`** — `id`, `name`, `full_name`, `short_name`, `white_first_color`.
- **`ReagentColor`** — `id`, `name`, `hex`, `simple`, `simple_color_id`.
- **`ReagentTestResult`** — `reagent: Reagent`, `start_colors`, `end_colors`, `is_positive`, `description`.
- **`SubstanceReagents`** — `substance_name`, `raw_name`, `results: List[ReagentTestResult]`.

### Erowid models

- **`ErowidExperience`** — `title`, `author`, `substance`, `body`, `meta: ErowidMeta`,
  `substance_info`, `erowid_notes`, `pull_quotes`.
- **`ErowidMeta`** — `erowid_id`, `gender`, `published`, `year`, `age`, `views`.
- **`ErowidSubstanceInfo`** — `amount`, `method`, `substance`, `form`.

Every model has a `to_dict()` method for JSON serialisation.

## GraphQL

`pypsychonaut.SUBSTANCE_QUERY` is the expanded GraphQL document that fetches all
Substance fields; it takes a `$query: String!` variable. Additional queries are
available for effects, Erowid experiences, reagents, and reagent colors. Issue
arbitrary queries through a transport with `Transport().graphql(query, variables)`.

## Client

`PsychonautWiki(transport=None, *, flaresolverr_url=None,
flaresolverr_timeout_ms=None, wayback=False, wayback_fallback=None)` mirrors the
module-level functions (`get_substance_list`, `get_substance_index`,
`extract_substance_name`, `search`, `query_effects`, `query_erowid`,
`query_reagents`, `query_reagent_colors`, `query_reagent_results`,
`list_wiki_pages`, `fetch_page_text`), caching the substance list. See
[advanced.md](advanced.md) for transport configuration.

## Page text

`fetch_page_text(title, *, transport=None)` fetches the rendered text of any
PsychonautWiki page via the MediaWiki `action=parse` API. The HTML is cleaned
(scripts, styles, superscripts stripped). Returns the plain text or `""` on
failure. Useful for building a full-wiki corpus for RAG.

---
[← Quickstart](quickstart.md) · [Home](../README.md) · [Advanced →](advanced.md)
