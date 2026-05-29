"""pypsychonaut — typed Python client for PsychonautWiki (psychonautwiki.org).

PsychonautWiki is a harm-reduction wiki cataloguing psychoactive substances:
each has routes of administration with dose brackets, a duration time-course,
chemical/psychoactive class, tolerance notes and subjective effects.

This client talks to two surfaces: the wiki's ``Summary_index`` HTML page (the
substance catalogue) and the official **GraphQL API** at
``api.psychonautwiki.org`` (structured dose/duration/effect data).

Quick start::

    import pypsychonaut as pw

    # The catalogue of substances (scraped from the wiki index)
    names = pw.get_substance_list()
    print(len(names), names[:5])

    # Structured data via the GraphQL API
    subs = pw.search_psychonaut_wiki("LSD")
    s = subs[0]
    print(s.name, s.substance_class.psychoactive)   # 'LSD' ['Psychedelic']
    for roa in s.roas:
        print(roa.name, roa.dose.common.to_dict() if roa.dose else None)

    # Slang normalisation before querying
    pw.extract_substance_name("took some acid last night")   # 'LSD'
    pw.search_psychonaut_wiki("ecstasy")                      # resolves to MDMA

    # Serialise
    import json
    print(json.dumps(s.to_dict(), indent=2)[:300])

Build a markdown corpus (one file per substance) with
:mod:`pypsychonaut.dataset` — the retrieval source for a harm-reduction RAG
assistant.
"""
from pypsychonaut.types import (
    Dose,
    Duration,
    Effect,
    Range,
    Roa,
    Substance,
    SubstanceClass,
    Tolerance,
)
from pypsychonaut.slang import DRUG_SLANG
from pypsychonaut.wiki import (
    PsychonautWiki,
    SUBSTANCE_QUERY,
    extract_substance_name,
    get_substance_index,
    get_substance_list,
    search_psychonaut_wiki,
)
from pypsychonaut._transport import Transport
from pypsychonaut.version import __version__

__all__ = [
    "Substance",
    "Roa",
    "Dose",
    "Duration",
    "Range",
    "Effect",
    "SubstanceClass",
    "Tolerance",
    "PsychonautWiki",
    "Transport",
    "DRUG_SLANG",
    "SUBSTANCE_QUERY",
    "get_substance_list",
    "get_substance_index",
    "search_psychonaut_wiki",
    "extract_substance_name",
    "__version__",
]
