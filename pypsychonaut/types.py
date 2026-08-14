from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

BASE = "https://psychonautwiki.org"


def _maybe(node: Optional[dict], key: str) -> Any:
    return node.get(key) if isinstance(node, dict) else None


@dataclass
class Range:
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
    name: str
    url: Optional[str] = None
    substances: List[str] = field(default_factory=list)

    @classmethod
    def from_graphql(cls, node: dict) -> "Effect":
        substances = []
        subs = node.get("substances")
        if isinstance(subs, list):
            substances = [s.get("name", "") if isinstance(s, dict) else str(s) for s in subs]
        return cls(name=node.get("name") or "", url=node.get("url"), substances=substances)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"name": self.name, "url": self.url}
        if self.substances:
            d["substances"] = self.substances
        return d


@dataclass
class SubstanceClass:
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
class SubstanceImage:
    thumb: Optional[str] = None
    image: Optional[str] = None

    @classmethod
    def from_graphql(cls, node: dict) -> "SubstanceImage":
        return cls(thumb=node.get("thumb"), image=node.get("image"))

    def to_dict(self) -> Dict[str, Any]:
        return {"thumb": self.thumb, "image": self.image}


@dataclass
class SubstanceInteraction:
    name: str
    url: Optional[str] = None
    addiction_potential: Optional[str] = None
    toxicity: Optional[List[str]] = None
    summary: Optional[str] = None

    @classmethod
    def from_graphql(cls, node: dict) -> "SubstanceInteraction":
        return cls(
            name=node.get("name") or "",
            url=node.get("url"),
            addiction_potential=node.get("addictionPotential"),
            toxicity=[str(s) for s in (node.get("toxicity") or [])] if node.get("toxicity") else None,
            summary=node.get("summary"),
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"name": self.name}
        if self.url:
            d["url"] = self.url
        if self.addiction_potential:
            d["addiction_potential"] = self.addiction_potential
        if self.toxicity:
            d["toxicity"] = self.toxicity
        if self.summary:
            d["summary"] = self.summary
        return d


@dataclass
class ReagentColor:
    id: Optional[int] = None
    name: Optional[str] = None
    hex: Optional[str] = None
    simple: Optional[bool] = None
    simple_color_id: Optional[int] = None

    @classmethod
    def from_graphql(cls, node: dict) -> "ReagentColor":
        return cls(
            id=node.get("id"),
            name=node.get("name"),
            hex=node.get("hex"),
            simple=node.get("simple"),
            simple_color_id=node.get("simpleColorId"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass
class Reagent:
    id: Optional[int] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    short_name: Optional[str] = None
    white_first_color: Optional[bool] = None

    @classmethod
    def from_graphql(cls, node: dict) -> "Reagent":
        return cls(
            id=node.get("id"),
            name=node.get("name"),
            full_name=node.get("fullName"),
            short_name=node.get("shortName"),
            white_first_color=node.get("whiteFirstColor"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass
class ReagentTestResult:
    reagent: Optional[Reagent] = None
    start_colors: List[ReagentColor] = field(default_factory=list)
    end_colors: List[ReagentColor] = field(default_factory=list)
    is_positive: Optional[bool] = None
    description: Optional[str] = None

    @classmethod
    def from_graphql(cls, node: dict) -> "ReagentTestResult":
        return cls(
            reagent=Reagent.from_graphql(node.get("reagent") or {}),
            start_colors=[ReagentColor.from_graphql(c) for c in (node.get("startColors") or [])],
            end_colors=[ReagentColor.from_graphql(c) for c in (node.get("endColors") or [])],
            is_positive=node.get("isPositive"),
            description=node.get("description"),
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.reagent:
            d["reagent"] = self.reagent.to_dict()
        if self.start_colors:
            d["start_colors"] = [c.to_dict() for c in self.start_colors]
        if self.end_colors:
            d["end_colors"] = [c.to_dict() for c in self.end_colors]
        if self.is_positive is not None:
            d["is_positive"] = self.is_positive
        if self.description:
            d["description"] = self.description
        return d


@dataclass
class SubstanceReagents:
    substance_name: Optional[str] = None
    raw_name: Optional[str] = None
    results: List[ReagentTestResult] = field(default_factory=list)

    @classmethod
    def from_graphql(cls, node: Optional[dict]) -> Optional["SubstanceReagents"]:
        if not isinstance(node, dict):
            return None
        return cls(
            substance_name=node.get("substanceName"),
            raw_name=node.get("rawName"),
            results=[ReagentTestResult.from_graphql(r) for r in (node.get("results") or [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.substance_name:
            d["substance_name"] = self.substance_name
        if self.raw_name:
            d["raw_name"] = self.raw_name
        if self.results:
            d["results"] = [r.to_dict() for r in self.results]
        return d


@dataclass
class ErowidMeta:
    erowid_id: Optional[str] = None
    gender: Optional[str] = None
    published: Optional[str] = None
    year: Optional[int] = None
    age: Optional[int] = None
    views: Optional[int] = None

    @classmethod
    def from_graphql(cls, node: Optional[dict]) -> Optional["ErowidMeta"]:
        if not isinstance(node, dict):
            return None
        return cls(
            erowid_id=node.get("erowidId"),
            gender=node.get("gender"),
            published=node.get("published"),
            year=node.get("year"),
            age=node.get("age"),
            views=node.get("views"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass
class ErowidSubstanceInfo:
    amount: Optional[str] = None
    method: Optional[str] = None
    substance: Optional[str] = None
    form: Optional[str] = None

    @classmethod
    def from_graphql(cls, node: Optional[dict]) -> Optional["ErowidSubstanceInfo"]:
        if not isinstance(node, dict) or not node:
            return None
        return cls(
            amount=node.get("amount"),
            method=node.get("method"),
            substance=node.get("substance"),
            form=node.get("form"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass
class ErowidExperience:
    title: Optional[str] = None
    author: Optional[str] = None
    substance: Optional[str] = None
    body: Optional[str] = None
    meta: Optional[ErowidMeta] = None
    substance_info: List[ErowidSubstanceInfo] = field(default_factory=list)
    erowid_notes: List[str] = field(default_factory=list)
    pull_quotes: List[str] = field(default_factory=list)

    @classmethod
    def from_graphql(cls, node: dict) -> "ErowidExperience":
        infos = []
        raw = node.get("substanceInfo")
        if isinstance(raw, list):
            infos = [ErowidSubstanceInfo.from_graphql(i) for i in raw if isinstance(i, dict)]
        return cls(
            title=node.get("title"),
            author=node.get("author"),
            substance=node.get("substance"),
            body=node.get("body"),
            meta=ErowidMeta.from_graphql(node.get("meta")),
            substance_info=infos,
            erowid_notes=[str(s) for s in (node.get("erowidNotes") or [])],
            pull_quotes=[str(s) for s in (node.get("pullQuotes") or [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.title:
            d["title"] = self.title
        if self.author:
            d["author"] = self.author
        if self.substance:
            d["substance"] = self.substance
        if self.body:
            d["body"] = self.body
        if self.meta:
            d["meta"] = self.meta.to_dict()
        if self.substance_info:
            d["substance_info"] = [s.to_dict() for s in self.substance_info]
        if self.erowid_notes:
            d["erowid_notes"] = self.erowid_notes
        if self.pull_quotes:
            d["pull_quotes"] = self.pull_quotes
        return d


@dataclass
class RoaTypes:
    oral: Optional[Roa] = None
    sublingual: Optional[Roa] = None
    buccal: Optional[Roa] = None
    insufflated: Optional[Roa] = None
    rectal: Optional[Roa] = None
    transdermal: Optional[Roa] = None
    subcutaneous: Optional[Roa] = None
    intramuscular: Optional[Roa] = None
    intravenous: Optional[Roa] = None
    smoked: Optional[Roa] = None

    _ROUTES = ("oral", "sublingual", "buccal", "insufflated", "rectal",
               "transdermal", "subcutaneous", "intramuscular", "intravenous", "smoked")

    @classmethod
    def from_graphql(cls, node: Optional[dict]) -> Optional["RoaTypes"]:
        if not isinstance(node, dict):
            return None
        return cls(**{r: Roa.from_graphql(node.get(r) or {}) if node.get(r) else None
                      for r in cls._ROUTES})

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        for r in self._ROUTES:
            val = getattr(self, r)
            if val is not None:
                d[r] = val.to_dict()
        return d


@dataclass
class Substance:
    name: str
    url: Optional[str] = None
    roas: List[Roa] = field(default_factory=list)
    roa_typed: Optional[RoaTypes] = None
    substance_class: Optional[SubstanceClass] = None
    tolerance: Optional[Tolerance] = None
    effects: List[Effect] = field(default_factory=list)
    featured: bool = False
    addiction_potential: Optional[str] = None
    toxicity: Optional[List[str]] = None
    cross_tolerances: Optional[List[str]] = None
    common_names: Optional[List[str]] = None
    systematic_name: Optional[str] = None
    summary: Optional[str] = None
    images: List[SubstanceImage] = field(default_factory=list)
    uncertain_interactions: List[SubstanceInteraction] = field(default_factory=list)
    unsafe_interactions: List[SubstanceInteraction] = field(default_factory=list)
    dangerous_interactions: List[SubstanceInteraction] = field(default_factory=list)
    reagents: Optional[SubstanceReagents] = None

    @classmethod
    def from_graphql(cls, node: dict) -> "Substance":
        images = [SubstanceImage.from_graphql(i) for i in (node.get("images") or [])]
        return cls(
            name=node.get("name") or "",
            url=node.get("url"),
            roas=[Roa.from_graphql(r) for r in (node.get("roas") or [])],
            roa_typed=RoaTypes.from_graphql(node.get("roa")),
            substance_class=SubstanceClass.from_graphql(node.get("class")),
            tolerance=Tolerance.from_graphql(node.get("tolerance")),
            effects=[Effect.from_graphql(e) for e in (node.get("effects") or [])],
            featured=bool(node.get("featured")),
            addiction_potential=node.get("addictionPotential"),
            toxicity=[str(s) for s in (node.get("toxicity") or [])] if node.get("toxicity") else None,
            cross_tolerances=[str(s) for s in (node.get("crossTolerances") or [])] if node.get("crossTolerances") else None,
            common_names=[str(s) for s in (node.get("commonNames") or [])] if node.get("commonNames") else None,
            systematic_name=node.get("systematicName"),
            summary=node.get("summary"),
            images=images,
            uncertain_interactions=[SubstanceInteraction.from_graphql(i) for i in (node.get("uncertainInteractions") or [])],
            unsafe_interactions=[SubstanceInteraction.from_graphql(i) for i in (node.get("unsafeInteractions") or [])],
            dangerous_interactions=[SubstanceInteraction.from_graphql(i) for i in (node.get("dangerousInteractions") or [])],
            reagents=SubstanceReagents.from_graphql(node.get("reagents")),
        )

    @property
    def page_url(self) -> str:
        return self.url or f"{BASE}/wiki/{self.name}"

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "name": self.name,
            "url": self.page_url,
            "class": self.substance_class.to_dict() if self.substance_class else None,
            "tolerance": self.tolerance.to_dict() if self.tolerance else None,
            "roas": [r.to_dict() for r in self.roas],
            "effects": [e.to_dict() for e in self.effects],
        }
        if self.roa_typed:
            d["roa_typed"] = self.roa_typed.to_dict()
        if self.featured:
            d["featured"] = True
        if self.addiction_potential:
            d["addiction_potential"] = self.addiction_potential
        if self.toxicity:
            d["toxicity"] = self.toxicity
        if self.cross_tolerances:
            d["cross_tolerances"] = self.cross_tolerances
        if self.common_names:
            d["common_names"] = self.common_names
        if self.systematic_name:
            d["systematic_name"] = self.systematic_name
        if self.summary:
            d["summary"] = self.summary
        if self.images:
            d["images"] = [i.to_dict() for i in self.images]
        if self.uncertain_interactions:
            d["uncertain_interactions"] = [i.to_dict() for i in self.uncertain_interactions]
        if self.unsafe_interactions:
            d["unsafe_interactions"] = [i.to_dict() for i in self.unsafe_interactions]
        if self.dangerous_interactions:
            d["dangerous_interactions"] = [i.to_dict() for i in self.dangerous_interactions]
        if self.reagents:
            d["reagents"] = self.reagents.to_dict()
        return d


__all__ = [
    "Range", "Dose", "Duration", "Roa", "RoaTypes",
    "Effect", "SubstanceClass", "Tolerance",
    "SubstanceImage", "SubstanceInteraction",
    "ReagentColor", "Reagent", "ReagentTestResult", "SubstanceReagents",
    "ErowidMeta", "ErowidSubstanceInfo", "ErowidExperience",
    "Substance",
]
