"""Typed dataclass models for pypsychonaut.

These mirror the PsychonautWiki GraphQL schema (``api.psychonautwiki.org``).
A :class:`Substance` is the top-level record; it carries its routes of
administration (:class:`Roa`), each with a :class:`Dose` and a
:class:`Duration`, plus its chemical/psychoactive class, tolerance notes and
subjective :class:`Effect` list.

Shared interface on the headline models:

- ``url`` — the canonical PsychonautWiki page;
- ``to_dict()`` — a JSON-serialisable plain ``dict``;
- ``Substance.from_graphql()`` / ``Roa.from_graphql()`` etc. — build a model
  from the raw GraphQL JSON node.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

BASE = "https://psychonautwiki.org"


def _maybe(node: Optional[dict], key: str) -> Any:
    return node.get(key) if isinstance(node, dict) else None


@dataclass
class Range:
    """A numeric ``{min, max}`` pair (dose bracket or duration span)."""

    min: Optional[float] = None
    max: Optional[float] = None
    units: Optional[str] = None

    @classmethod
    def from_graphql(cls, node: Optional[dict]) -> Optional["Range"]:
        if not isinstance(node, dict):
            return None
        return cls(min=node.get("min"), max=node.get("max"), units=node.get("units"))

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass
class Dose:
    """Dose brackets for a single route of administration.

    ``threshold`` and ``heavy`` are scalars in ``units``; ``light`` / ``common``
    / ``strong`` are :class:`Range` brackets.
    """

    units: Optional[str] = None
    threshold: Optional[float] = None
    heavy: Optional[float] = None
    light: Optional[Range] = None
    common: Optional[Range] = None
    strong: Optional[Range] = None

    @classmethod
    def from_graphql(cls, node: Optional[dict]) -> Optional["Dose"]:
        if not isinstance(node, dict):
            return None
        return cls(
            units=node.get("units"),
            threshold=node.get("threshold"),
            heavy=node.get("heavy"),
            light=Range.from_graphql(node.get("light")),
            common=Range.from_graphql(node.get("common")),
            strong=Range.from_graphql(node.get("strong")),
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.units is not None:
            d["units"] = self.units
        if self.threshold is not None:
            d["threshold"] = self.threshold
        for name in ("light", "common", "strong"):
            r = getattr(self, name)
            if r is not None:
                d[name] = r.to_dict()
        if self.heavy is not None:
            d["heavy"] = self.heavy
        return d


@dataclass
class Duration:
    """Time course of a route of administration, each phase a :class:`Range`."""

    onset: Optional[Range] = None
    comeup: Optional[Range] = None
    peak: Optional[Range] = None
    offset: Optional[Range] = None
    total: Optional[Range] = None
    afterglow: Optional[Range] = None
    duration: Optional[Range] = None

    _PHASES = ("onset", "comeup", "peak", "offset", "total", "afterglow", "duration")

    @classmethod
    def from_graphql(cls, node: Optional[dict]) -> Optional["Duration"]:
        if not isinstance(node, dict):
            return None
        return cls(**{p: Range.from_graphql(node.get(p)) for p in cls._PHASES})

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        for p in self._PHASES:
            r = getattr(self, p)
            if r is not None:
                d[p] = r.to_dict()
        return d


@dataclass
class Roa:
    """A route of administration (oral, sublingual, insufflated, …)."""

    name: str
    dose: Optional[Dose] = None
    duration: Optional[Duration] = None
    bioavailability: Optional[Range] = None

    @classmethod
    def from_graphql(cls, node: dict) -> "Roa":
        return cls(
            name=node.get("name") or "",
            dose=Dose.from_graphql(node.get("dose")),
            duration=Duration.from_graphql(node.get("duration")),
            bioavailability=Range.from_graphql(node.get("bioavailability")),
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"name": self.name}
        if self.dose is not None:
            d["dose"] = self.dose.to_dict()
        if self.duration is not None:
            d["duration"] = self.duration.to_dict()
        if self.bioavailability is not None:
            d["bioavailability"] = self.bioavailability.to_dict()
        return d


@dataclass
class Effect:
    """A subjective effect linked from a substance page."""

    name: str
    url: Optional[str] = None

    @classmethod
    def from_graphql(cls, node: dict) -> "Effect":
        return cls(name=node.get("name") or "", url=node.get("url"))

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "url": self.url}


@dataclass
class SubstanceClass:
    """Chemical and psychoactive class membership."""

    chemical: List[str] = field(default_factory=list)
    psychoactive: List[str] = field(default_factory=list)

    @classmethod
    def from_graphql(cls, node: Optional[dict]) -> Optional["SubstanceClass"]:
        if not isinstance(node, dict):
            return None
        return cls(
            chemical=list(node.get("chemical") or []),
            psychoactive=list(node.get("psychoactive") or []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"chemical": self.chemical, "psychoactive": self.psychoactive}


@dataclass
class Tolerance:
    """Free-text tolerance notes (full / half-life / baseline reset)."""

    full: Optional[str] = None
    half: Optional[str] = None
    zero: Optional[str] = None

    @classmethod
    def from_graphql(cls, node: Optional[dict]) -> Optional["Tolerance"]:
        if not isinstance(node, dict):
            return None
        return cls(full=node.get("full"), half=node.get("half"), zero=node.get("zero"))

    def to_dict(self) -> Dict[str, Any]:
        return {"full": self.full, "half": self.half, "zero": self.zero}


@dataclass
class Substance:
    """A PsychonautWiki substance record from the GraphQL API.

    Obtain via :func:`pypsychonaut.search_psychonaut_wiki`.

    Example::

        import pypsychonaut as pw
        subs = pw.search_psychonaut_wiki("LSD")
        s = subs[0]
        print(s.name, [r.name for r in s.roas])
        print(s.substance_class.psychoactive)   # ['Psychedelic']
    """

    name: str
    url: Optional[str] = None
    roas: List[Roa] = field(default_factory=list)
    substance_class: Optional[SubstanceClass] = None
    tolerance: Optional[Tolerance] = None
    effects: List[Effect] = field(default_factory=list)

    @classmethod
    def from_graphql(cls, node: dict) -> "Substance":
        return cls(
            name=node.get("name") or "",
            url=node.get("url"),
            roas=[Roa.from_graphql(r) for r in (node.get("roas") or [])],
            substance_class=SubstanceClass.from_graphql(node.get("class")),
            tolerance=Tolerance.from_graphql(node.get("tolerance")),
            effects=[Effect.from_graphql(e) for e in (node.get("effects") or [])],
        )

    @property
    def page_url(self) -> str:
        return self.url or f"{BASE}/wiki/{self.name}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "url": self.page_url,
            "class": self.substance_class.to_dict() if self.substance_class else None,
            "tolerance": self.tolerance.to_dict() if self.tolerance else None,
            "roas": [r.to_dict() for r in self.roas],
            "effects": [e.to_dict() for e in self.effects],
        }


__all__ = [
    "Range",
    "Dose",
    "Duration",
    "Roa",
    "Effect",
    "SubstanceClass",
    "Tolerance",
    "Substance",
]
