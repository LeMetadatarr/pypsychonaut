# Quickstart

```bash
pip install pypsychonaut
pip install pypsychonaut[stealth]   # adds curl-cffi, recommended (Cloudflare)
pip install pypsychonaut[test]      # adds pytest
```

## The substance catalogue (wiki HTML)

```python
import pypsychonaut as pw

names = pw.get_substance_list()        # flat list from Summary_index
index = pw.get_substance_index()       # nested category -> substance -> url
```

## Structured data (GraphQL API)

```python
subs = pw.search_psychonaut_wiki("LSD")
s = subs[0]
print(s.substance_class.psychoactive)   # ['Psychedelic']
for roa in s.roas:
    print(roa.name, roa.dose.common.to_dict() if roa.dose else None)
```

## Slang normalisation

```python
pw.extract_substance_name("took some acid last night")   # 'LSD'
pw.search_psychonaut_wiki("ecstasy")                      # resolves to MDMA
```

`search_psychonaut_wiki` runs the query through `extract_substance_name`
first. Pass `resolve_name=False` to skip this step and query verbatim.

## High-level client

```python
client = pw.PsychonautWiki()           # caches the substance list
client.search("molly")                 # MDMA
```

## Transport

PsychonautWiki's wiki pages can sit behind Cloudflare, but the GraphQL API does not.
Both route through `unblock_requests.CloudflareSession`.
Configure transport with kwargs or `PYPSYCHONAUT_*` env vars.
See [advanced.md](advanced.md).

## Build a corpus

```python
from pypsychonaut import dataset
dataset.build_corpus("corpus", limit=5, delay=1.0)   # one markdown file per substance
```

See [dataset.md](dataset.md).

---
[Home](../README.md) · [API reference →](api.md)
