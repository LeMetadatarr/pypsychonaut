# pypsychonaut

Typed Python client for [PsychonautWiki](https://psychonautwiki.org) — a
harm-reduction wiki cataloguing psychoactive substances, their routes of
administration, dose brackets, duration time-courses, classes, tolerance and
subjective effects.

It talks to two surfaces behind clean dataclasses:

- the wiki's **`Summary_index`** HTML page — the substance catalogue;
- the official **GraphQL API** (`api.psychonautwiki.org`) — structured
  dose/duration/effect data.

It also ships a **slang lexicon** (street name → canonical substance) and a
**markdown corpus dumper** that writes one file per substance — the retrieval
source for a harm-reduction RAG assistant.

## Install

```bash
pip install pypsychonaut
pip install pypsychonaut[stealth]   # adds curl-cffi — recommended (see below)
pip install pypsychonaut[test]      # adds pytest
```

> **Cloudflare:** the wiki HTML pages can sit behind a Cloudflare bot check. The
> client defaults to `curl_cffi` Chrome TLS impersonation (the `stealth` extra),
> with FlareSolverr and Internet-Archive fallbacks available — all via
> `unblock_requests`. The GraphQL API is a clean JSON endpoint and needs no
> bypass. See [docs/advanced.md](docs/advanced.md).

## 30-second tour

```python
import pypsychonaut as pw

# The substance catalogue (scraped from the wiki index)
names = pw.get_substance_list()
print(len(names), names[:5])

# Structured data from the GraphQL API
s = pw.search_psychonaut_wiki("LSD")[0]
print(s.substance_class.psychoactive)              # ['Psychedelic']
for roa in s.roas:
    print(roa.name, roa.dose.common.to_dict() if roa.dose else None)

# Slang normalisation before querying
pw.extract_substance_name("took some acid last night")   # 'LSD'
pw.search_psychonaut_wiki("ecstasy")                      # resolves to MDMA
```

## What you can fetch

| Function | Returns | Source |
|---|---|---|
| `get_substance_list()` | `List[str]` | `Summary_index` HTML |
| `get_substance_index()` | nested `dict` | `Summary_index` HTML |
| `search_psychonaut_wiki("LSD")` | `List[Substance]` | GraphQL API |
| `extract_substance_name(text)` | `str` / `False` | slang lexicon + list |

A `Substance` carries `roas: List[Roa]` (each with `Dose`, `Duration`,
bioavailability), `substance_class`, `tolerance` and `effects`.

## Markdown corpus

```python
from pypsychonaut import dataset
dataset.build_corpus("corpus", limit=5, delay=1.0)   # one .md per substance
```

Resumable and polite — front-matter (class, common names, ROAs) plus a body
(dose/duration tables, effects). The intended retrieval source for a
harm-reduction RAG assistant. See [docs/dataset.md](docs/dataset.md).

## Documentation

- [docs/quickstart.md](docs/quickstart.md) — the essentials
- [docs/api.md](docs/api.md) — every function and model field
- [docs/advanced.md](docs/advanced.md) — transport / Cloudflare / GraphQL
- [docs/dataset.md](docs/dataset.md) — datasets this client produces and the ML
  tasks they serve

Runnable, numbered scripts live in [examples/](examples/).

## Testing

```bash
pytest                  # offline unit + fixture tests (no network)
pytest -m live          # smoke tests against the live GraphQL API
```

Live tests are deselected by default and require a network connection.
