---
name: pypsychonaut
description: look up PsychonautWiki substance data (dose, duration, effects) for accessible voice-first harm-reduction info on behalf of users who cannot navigate the website
---
# pypsychonaut — PsychonautWiki for agents

## When to use

Use this skill when a user asks a harm-reduction question about a psychoactive substance — dose ranges, duration, effects, drug class, or tolerance — and cannot or does not want to browse the website. Typical callers: blind users relying on a screen reader or voice assistant, users in a voice-only session, or automated pipelines building a harm-reduction RAG corpus.

Answer factually and without judgment. Harm-reduction framing means giving accurate information so people can make safer choices, not encouraging use.

## Install

```bash
pip install pypsychonaut
```

## Core operations

### `get_substance_list() -> List[str]`

Returns the flat list of all substance names from the PsychonautWiki Summary_index page (scraped HTML, no key required).

```python
import pypsychonaut as pw

names = pw.get_substance_list()
print(len(names), names[:5])
# 400+ ['1P-LSD', '2C-B', '2C-E', '4-AcO-DMT', 'Alcohol']
```

**Returns:** `List[str]` — canonical substance names as PsychonautWiki spells them.

---

### `get_substance_index() -> Dict[str, Any]`

Returns the same catalogue structured as a nested `{category: {substance: url}}` dict — useful for browsing by drug class or presenting a menu.

```python
import pypsychonaut as pw

index = pw.get_substance_index()
for category, entries in list(index.items())[:2]:
    print(category, list(entries.keys())[:3])
```

**Returns:** `Dict[str, Any]` — category → substance → wiki URL.

---

### `search_psychonaut_wiki(substance: str, *, resolve_name: bool = True) -> List[Substance]`

Queries the PsychonautWiki GraphQL API (`api.psychonautwiki.org`) for structured data on a substance. When `resolve_name=True` (default), free-text and slang are normalised first (e.g. `"ecstasy"` → `"MDMA"`).

```python
import pypsychonaut as pw

results = pw.search_psychonaut_wiki("LSD")
s = results[0]
print(s.name, s.substance_class.psychoactive)   # 'LSD' ['Psychedelic']
for roa in s.roas:
    if roa.dose:
        d = roa.dose
        print(roa.name, f"common {d.common.min}–{d.common.max} {d.units}")
```

**Returns:** `List[Substance]` — each item exposes:

| Field | Type | Content |
|---|---|---|
| `name` | `str` | canonical substance name |
| `url` | `str` | PsychonautWiki page URL |
| `substance_class` | `SubstanceClass` | `.chemical` and `.psychoactive` lists |
| `roas` | `List[Roa]` | routes of administration (see below) |
| `tolerance` | `Tolerance` | `.full`, `.half`, `.zero` (time strings) |
| `effects` | `List[Effect]` | subjective effect names + wiki URLs |

Each `Roa` carries:

| Field | Type | Content |
|---|---|---|
| `name` | `str` | route name (`"Oral"`, `"Smoked"`, `"Insufflated"`, …) |
| `dose` | `Dose` | `.threshold`, `.light`, `.common`, `.strong`, `.heavy`, `.units` |
| `duration` | `Duration` | `.onset`, `.comeup`, `.peak`, `.offset`, `.afterglow`, `.total` (each a `Range` with `.min`, `.max`, `.units`) |

---

### `extract_substance_name(sentence: str) -> str | False`

Resolves a free-text phrase to a canonical substance name using a built-in slang lexicon plus the live substance list. Returns the canonical name or `False` when nothing matches.

```python
import pypsychonaut as pw

pw.extract_substance_name("took some acid last night")  # 'LSD'
pw.extract_substance_name("molly makes me happy")       # 'MDMA'
pw.extract_substance_name("cup of coffee")              # False
```

**Use before `search_psychonaut_wiki`** when input comes from free speech or casual text.

---

### High-level client: `PsychonautWiki`

Caches the substance list across calls — preferred for multi-query sessions.

```python
import pypsychonaut as pw

client = pw.PsychonautWiki()
subs = client.search("ecstasy")   # slang → MDMA
print(subs[0].name)               # 'MDMA'
```

## Access notes

The GraphQL endpoint at `api.psychonautwiki.org` is public — no API key, no auth header. The HTML scraper fetches `psychonautwiki.org/wiki/Summary_index`. Both surfaces are free and openly licensed under harm-reduction terms.

## Speaking the results (accessibility)

When relaying data to a blind or voice-only user:

- **Dose:** read the common range first, then the strong range, then note the units. Example: "A common oral dose of MDMA is 75 to 125 milligrams; a strong dose is 125 to 180 milligrams."
- **Duration:** read total duration, then onset and peak. Example: "Effects last 3 to 5 hours in total, with onset in 30 to 60 minutes and peak at 1.5 to 2.5 hours."
- **Effects:** list the first 5 subjective effects by name. Keep it factual; avoid editorialising.
- **Tone:** answer "what is a common dose of X?" directly with the numbers. Use non-judgmental, factual language throughout — this is harm-reduction, not endorsement.
