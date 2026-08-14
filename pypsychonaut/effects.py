"""PsychonautWiki subjective effects catalog scraper.

Crawls the Subjective Effect Index page to discover all effect pages, then
fetches each effect's wiki page to extract:
  - Full description text
  - Categories (sensory/visual/cognitive/auditory/etc)
  - Variations / subtypes listed on the page
  - Substances that produce this effect
  - Sections: image examples, see also, references
  - Page URL and wikitext

Schema per row (JSONL):
  name, url, slug, categories[], description, variations[],
  substances[], sections{heading: text}, wikitext

Usage:
    python -m pypsychonaut.effects [--out PATH] [--delay SECS]
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set
from urllib.parse import unquote, urlencode

import time as _time

from pypsychonaut._transport import Transport, default_transport

EFFECT_INDEX_URL = "/wiki/Subjective_effect_index"
MW_API = "https://psychonautwiki.org/w/api.php"
BASE = "https://psychonautwiki.org"

# Skip meta/navigation pages
_SKIP_PREFIXES = ("File:", "Template:", "Help:", "Special:", "Talk:", "User:")
_SKIP_TITLES = {"Guidelines", "Replication_index", "Experience_index",
                "Psychoactive_substance_index", "Psychonautics", "Meditation",
                "Sensory_deprivation", "Lucid_dreaming", "Hallucinogens"}

_UA = "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
_last_request: float = 0.0
_min_delay: float = 1.5


def _throttle(delay: float = 0.0) -> None:
    global _last_request
    d = max(_min_delay, delay)
    elapsed = _time.time() - _last_request
    if elapsed < d:
        _time.sleep(d - elapsed)
    _last_request = _time.time()


def _get_html(path: str, transport: Transport) -> str:
    url = path if path.startswith("http") else f"{BASE}{path}"
    _throttle()
    return transport.get_html(url)


def _mw_api(transport: Transport, **params) -> dict:
    params.setdefault("format", "json")
    _throttle()
    r = transport.session.get(MW_API, params=params, timeout=30, headers={"User-Agent": _UA})
    r.raise_for_status()
    return r.json()


def _discover_effect_slugs(transport: Transport) -> List[str]:
    """Return unique wiki slugs from the Subjective Effect Index."""
    from bs4 import BeautifulSoup
    html = _get_html(EFFECT_INDEX_URL, transport)
    soup = BeautifulSoup(html, "html.parser")
    slugs: List[str] = []
    seen: Set[str] = set()
    for a in soup.select("a[href^='/wiki/']"):
        href = a.get("href", "")
        slug = href[len("/wiki/"):]
        if not slug or slug in seen:
            continue
        if any(slug.startswith(p) for p in _SKIP_PREFIXES):
            continue
        if slug in _SKIP_TITLES or "#" in slug:
            continue
        seen.add(slug)
        slugs.append(slug)
    return slugs


def _parse_effect_page(slug: str, transport: Transport) -> Optional[dict]:
    """Fetch and parse a single effect wiki page."""
    from bs4 import BeautifulSoup

    title = unquote(slug).replace("_", " ")
    # Get wikitext
    try:
        data = _mw_api(transport, action="parse", page=slug, prop="wikitext|categories")
        wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
        cats_raw = data.get("parse", {}).get("categories", [])
        categories = [c.get("*", "") for c in cats_raw if c.get("*")]
    except Exception:
        wikitext = ""
        categories = []

    # Get rendered HTML for structured extraction
    try:
        html = _get_html(f"/wiki/{slug}", transport)
    except Exception:
        return None

    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("#mw-content-text")
    if not content:
        return None

    # Page categories from sidebar
    cat_sidebar = [a.get_text(strip=True) for a in soup.select("#catlinks a")
                   if a.get_text(strip=True) not in ("Categories", "Effect")]

    # Description: first substantial paragraph(s)
    desc_parts = []
    for p in content.select("p"):
        text = p.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        if len(text) > 50:
            desc_parts.append(text)
        if len(" ".join(desc_parts)) > 800:
            break
    description = " ".join(desc_parts)

    # Substances section: find heading "Psychoactive substances" then links
    substances: List[str] = []
    for h in content.select("h2, h3"):
        heading_text = h.get_text(strip=True).lower()
        if "substance" in heading_text or "psychoactive" in heading_text:
            # Collect links until next heading
            node = h.find_next_sibling()
            while node and node.name not in ("h2", "h3"):
                if hasattr(node, "select"):
                    for a in node.select("a[href^='/wiki/']"):
                        sub = unquote(a.get("href", "")[len("/wiki/"):]).replace("_", " ")
                        if sub and sub not in substances:
                            substances.append(sub)
                node = node.find_next_sibling()
            break

    # All sections: heading → text
    sections: Dict[str, str] = {}
    for h in content.select("h2, h3"):
        heading = h.get_text(strip=True)
        if heading in ("Contents", "References"):
            continue
        text_parts = []
        node = h.find_next_sibling()
        while node and node.name not in ("h2", "h3"):
            if hasattr(node, "get_text"):
                t = node.get_text(" ", strip=True)
                if t:
                    text_parts.append(t)
            node = node.find_next_sibling()
        if text_parts:
            sections[heading] = re.sub(r"\s+", " ", " ".join(text_parts))[:2000]

    # Variations: bullet list items under Variations heading, or first ul
    variations: List[str] = []
    for h in content.select("h2, h3"):
        if "variation" in h.get_text(strip=True).lower():
            node = h.find_next_sibling()
            while node and node.name not in ("h2", "h3"):
                if node.name == "ul":
                    for li in node.select("li"):
                        v = li.get_text(" ", strip=True)
                        if v:
                            variations.append(v[:200])
                node = node.find_next_sibling()
            break

    return {
        "slug": slug,
        "name": title,
        "url": f"{BASE}/wiki/{slug}",
        "categories": list(dict.fromkeys(cat_sidebar + categories)),
        "description": description,
        "variations": variations,
        "substances": substances,
        "sections": sections,
        "wikitext": wikitext,
    }


def iter_effects(*, seen: Optional[Set[str]] = None,
                 transport: Optional[Transport] = None) -> Iterator[dict]:
    """Yield one dict per effect page from PsychonautWiki."""
    t = transport or default_transport()
    if seen is None:
        seen = set()

    slugs = _discover_effect_slugs(t)
    print(f"[pw_effects] discovered {len(slugs)} effect slugs")

    for slug in slugs:
        if slug in seen:
            continue
        seen.add(slug)
        row = _parse_effect_page(slug, t)
        if row:
            yield row


def export_jsonl(path: str, *, delay: float = 1.5,
                 transport: Optional[Transport] = None) -> int:
    global _min_delay
    _min_delay = delay
    from pathlib import Path as _P
    t = transport or Transport()
    out = _P(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    seen: Set[str] = set()
    if out.exists():
        with open(out) as f:
            for line in f:
                try:
                    seen.add(json.loads(line)["slug"])
                except Exception:
                    pass
        print(f"[pw_effects] {len(seen)} already saved")

    count = 0
    with open(out, "a", encoding="utf-8") as fh:
        for row in iter_effects(seen=seen, transport=t):
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            count += 1
            print(f"[pw_effects] [{count}] {row['name']}")
    return count


def main(argv=None):
    ap = argparse.ArgumentParser(description="PsychonautWiki subjective effects crawler")
    ap.add_argument("--out", default=str(Path.home() / ".cache/metadatarr/scrapers/psychonaut_effects.jsonl"))
    ap.add_argument("--delay", type=float, default=1.5)
    args = ap.parse_args(argv)
    export_jsonl(args.out, delay=args.delay)


if __name__ == "__main__":
    main()
