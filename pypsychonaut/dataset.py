"""Markdown corpus dumper for PsychonautWiki substances.

Crawls the substance catalogue and writes **one markdown file per substance**
into an output folder. Each file has YAML front-matter (name, class, common
names, per-ROA dose/duration/bioavailability pulled from the GraphQL API) and a
markdown body (effects list, page link). The corpus is the retrieval source for
a future harm-reduction RAG assistant.

The dump is **resumable** (skips files already written) and **polite** (one
shared :class:`Transport`, a configurable delay between substances). The full
catalogue is a few hundred substances — feasible, but treat a full run as a
homelab job; validate locally on a small sample.

See ``docs/dataset.md`` for the dataset/ML rationale.
"""
from __future__ import annotations

import os
import re
import time
from typing import Any, Dict, Iterable, List, Optional

from pypsychonaut._transport import Transport, default_transport
from pypsychonaut.types import Range, Roa, Substance
from pypsychonaut.wiki import get_substance_list, search_psychonaut_wiki


def _slug(name: str) -> str:
    """Filesystem-safe slug for a substance file name."""
    s = re.sub(r"[^\w\-]+", "_", name.strip().lower())
    return re.sub(r"_+", "_", s).strip("_") or "substance"


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return '""'
    text = str(value)
    if re.search(r'[:#\[\]{}\"\']', text) or text != text.strip():
        return '"' + text.replace('"', '\\"') + '"'
    return text


def _yaml_list(values: Iterable[str]) -> str:
    items = [v for v in values if v]
    if not items:
        return "[]"
    return "[" + ", ".join(_yaml_scalar(v) for v in items) + "]"


def _range_str(r: Optional[Range]) -> Optional[str]:
    if r is None or (r.min is None and r.max is None):
        return None
    if r.min is not None and r.max is not None:
        body = f"{r.min}-{r.max}"
    else:
        body = str(r.min if r.min is not None else r.max)
    return f"{body} {r.units}".strip() if r.units else body


def _roa_block(roa: Roa) -> List[str]:
    """Markdown lines describing one route of administration."""
    lines = [f"### {roa.name or 'unknown'}", ""]
    if roa.dose:
        d = roa.dose
        u = d.units or ""
        rows = []
        if d.threshold is not None:
            rows.append(("Threshold", f"{d.threshold} {u}".strip()))
        for label, rng in (("Light", d.light), ("Common", d.common), ("Strong", d.strong)):
            s = _range_str(rng)
            if s:
                rows.append((label, f"{s} {u}".strip() if u and not (rng and rng.units) else s))
        if d.heavy is not None:
            rows.append(("Heavy", f"{d.heavy} {u}".strip()))
        if rows:
            lines.append("**Dose**")
            lines.append("")
            lines.append("| Bracket | Amount |")
            lines.append("|---|---|")
            lines += [f"| {k} | {v} |" for k, v in rows]
            lines.append("")
    if roa.duration:
        phases = []
        for p in ("onset", "comeup", "peak", "offset", "total", "afterglow"):
            s = _range_str(getattr(roa.duration, p))
            if s:
                phases.append((p.capitalize(), s))
        if phases:
            lines.append("**Duration**")
            lines.append("")
            lines.append("| Phase | Time |")
            lines.append("|---|---|")
            lines += [f"| {k} | {v} |" for k, v in phases]
            lines.append("")
    bio = _range_str(roa.bioavailability)
    if bio:
        lines.append(f"**Bioavailability:** {bio}")
        lines.append("")
    return lines


def substance_to_markdown(sub: Substance) -> str:
    """Render a :class:`Substance` to a markdown document (front-matter + body)."""
    cls = sub.substance_class
    fm: List[str] = ["---"]
    fm.append(f"name: {_yaml_scalar(sub.name)}")
    fm.append(f"url: {_yaml_scalar(sub.page_url)}")
    fm.append(f"chemical_class: {_yaml_list(cls.chemical if cls else [])}")
    fm.append(f"psychoactive_class: {_yaml_list(cls.psychoactive if cls else [])}")
    fm.append(f"routes: {_yaml_list(r.name for r in sub.roas)}")
    fm.append(f"effects: {_yaml_list(e.name for e in sub.effects)}")
    fm.append("---")

    body: List[str] = ["", f"# {sub.name}", ""]
    if cls and (cls.chemical or cls.psychoactive):
        if cls.chemical:
            body.append(f"**Chemical class:** {', '.join(cls.chemical)}")
        if cls.psychoactive:
            body.append(f"**Psychoactive class:** {', '.join(cls.psychoactive)}")
        body.append("")

    if sub.roas:
        body.append("## Routes of administration")
        body.append("")
        for roa in sub.roas:
            body += _roa_block(roa)

    if sub.tolerance and any((sub.tolerance.full, sub.tolerance.half, sub.tolerance.zero)):
        body.append("## Tolerance")
        body.append("")
        for label, val in (("Full", sub.tolerance.full), ("Half", sub.tolerance.half),
                           ("Baseline", sub.tolerance.zero)):
            if val:
                body.append(f"- **{label}:** {val}")
        body.append("")

    if sub.effects:
        body.append("## Effects")
        body.append("")
        for e in sub.effects:
            body.append(f"- [{e.name}]({e.url})" if e.url else f"- {e.name}")
        body.append("")

    body.append(f"Source: <{sub.page_url}>")
    body.append("")
    return "\n".join(fm + body)


def dump_substance(name: str, out_dir: str, *,
                   transport: Optional[Transport] = None,
                   overwrite: bool = False) -> Optional[str]:
    """Fetch one substance and write its markdown file. Returns the path, or
    ``None`` when the GraphQL API has no record for *name* (resumable: an
    existing file is left untouched unless *overwrite*)."""
    path = os.path.join(out_dir, _slug(name) + ".md")
    if os.path.exists(path) and not overwrite:
        return path
    subs = search_psychonaut_wiki(name, resolve_name=False, transport=transport)
    if not subs:
        return None
    os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(substance_to_markdown(subs[0]))
    return path


def build_corpus(out_dir: str, *,
                 names: Optional[Iterable[str]] = None,
                 limit: Optional[int] = None,
                 delay: float = 1.0,
                 overwrite: bool = False,
                 transport: Optional[Transport] = None) -> Dict[str, Any]:
    """Crawl PsychonautWiki and write one markdown file per substance.

    Args:
        out_dir:   output folder (created if missing).
        names:     substances to dump; defaults to the full ``Summary_index``.
        limit:     stop after this many substances (for sampling).
        delay:     seconds to sleep between live GraphQL calls (politeness).
        overwrite: re-fetch substances that already have a file.
        transport: shared :class:`Transport`; one is created if omitted.

    Returns a summary dict: ``{written, skipped, missing, total}``.

    Example::

        from pypsychonaut import dataset
        # validate on a small sample first
        dataset.build_corpus("corpus", limit=5, delay=1.0)
    """
    t = transport or default_transport()
    if names is None:
        names = get_substance_list(transport=t)
    names = list(names)
    if limit is not None:
        names = names[:limit]

    os.makedirs(out_dir, exist_ok=True)
    written = skipped = missing = 0
    for i, name in enumerate(names):
        path = os.path.join(out_dir, _slug(name) + ".md")
        if os.path.exists(path) and not overwrite:
            skipped += 1
            continue
        try:
            result = dump_substance(name, out_dir, transport=t, overwrite=overwrite)
        except Exception:
            result = None
        if result is None:
            missing += 1
        else:
            written += 1
        if delay and i < len(names) - 1:
            time.sleep(delay)
    return {"written": written, "skipped": skipped, "missing": missing,
            "total": len(names)}
