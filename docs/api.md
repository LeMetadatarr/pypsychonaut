# API reference

## Functions

| Function | Returns | Source |
|---|---|---|
| `get_substance_list(*, transport=None)` | `List[str]` | `Summary_index` HTML |
| `get_substance_index(*, transport=None)` | nested `dict` | `Summary_index` HTML |
| `extract_substance_name(sentence, *, substance_list=None, transport=None)` | `str | False` | slang lexicon + list |
| `search_psychonaut_wiki(substance, *, resolve_name=True, transport=None)` | `List[Substance]` | GraphQL API |

All take an optional `transport: Transport`. The module-level functions use a
shared, environment-driven default transport when none is given.

## Models (`pypsychonaut.types`)

- **`Substance`** — `name`, `url`, `roas: List[Roa]`, `substance_class:
  SubstanceClass`, `tolerance: Tolerance`, `effects: List[Effect]`. `page_url`
  property; `to_dict()`. Build with `Substance.from_graphql(node)`.
- **`Roa`** — route of administration: `name`, `dose: Dose`, `duration:
  Duration`, `bioavailability: Range`.
- **`Dose`** — `units`, `threshold`, `heavy`, and `light`/`common`/`strong` as
  `Range`.
- **`Duration`** — phases `onset`, `comeup`, `peak`, `offset`, `total`,
  `afterglow`, `duration`, each a `Range`.
- **`Range`** — `{min, max, units}`.
- **`Effect`** — `name`, `url`.
- **`SubstanceClass`** — `chemical: List[str]`, `psychoactive: List[str]`.
- **`Tolerance`** — `full`, `half`, `zero` (free-text).

Every model exposes `to_dict()` for JSON serialisation.

## GraphQL

`pypsychonaut.SUBSTANCE_QUERY` is the readable GraphQL document used by
`search_psychonaut_wiki`; it takes a `$query: String!` variable. Issue arbitrary
queries through a transport with `Transport().graphql(query, variables)`.

## Client

`PsychonautWiki(transport=None, *, flaresolverr_url=None,
flaresolverr_timeout_ms=None, wayback=False, wayback_fallback=None)` mirrors the
functions (`get_substance_list`, `get_substance_index`,
`extract_substance_name`, `search`), caching the substance list. See
[advanced.md](advanced.md) for transport configuration.
