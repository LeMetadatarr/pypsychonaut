"""PsychonautWiki experience report crawler.

Two complementary strategies:
  1. GraphQL `erowid` query — per-substance, structured (title/author/body/meta/dose).
     Iterates all substances from the substance index and paginates reports.
  2. HTML scrape of /wiki/Experience_index — PW-native trip reports (separate from Erowid).
     Fetches each Experience: page and parses the structured HTML.

Both write to the same JSONL with a `source` field ("graphql_erowid" / "pw_experience").

Schema per row:
  source, title, author, substance, substances[],
  dose_info[]{amount, method, substance, form},
  body, year, gender, age, views, erowid_id,
  url, tags[]

Usage:
    python -m pypsychonaut.experiences [--out PATH] [--strategy {both,graphql,html}]
                                       [--delay SECS] [--limit N]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set
from urllib.parse import unquote

import time as _time

from pypsychonaut._transport import Transport, default_transport

BASE = "https://psychonautwiki.org"

_UA = "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
_last_request: float = 0.0
_min_delay: float = 1.5


def _throttle() -> None:
    global _last_request
    elapsed = _time.time() - _last_request
    if elapsed < _min_delay:
        _time.sleep(_min_delay - elapsed)
    _last_request = _time.time()
EXPERIENCE_INDEX = "/wiki/Experience_index"


def _gql_experiences_for_substance(substance: str, t: Transport,
                                    limit: int = 200, offset: int = 0) -> List[dict]:
    QUERY = """
    query Erowid($substance: String!, $limit: Int, $offset: Int) {
      erowid(substance: $substance, limit: $limit, offset: $offset) {
        title author substance body
        meta { erowidId gender published year age views }
        erowidNotes pullQuotes
        substanceInfo { amount method substance form }
      }
    }
    """
    try:
        data = t.graphql(QUERY, {"substance": substance, "limit": limit, "offset": offset})
        return data.get("erowid") or []
    except Exception:
        return []


def _row_from_gql(node: dict, substance: str) -> dict:
    meta = node.get("meta") or {}
    infos = node.get("substanceInfo") or []
    return {
        "source": "graphql_erowid",
        "title": node.get("title", ""),
        "author": node.get("author", ""),
        "substance": substance,
        "substances": [substance],
        "dose_info": [
            {"amount": d.get("amount"), "method": d.get("method"),
             "substance": d.get("substance"), "form": d.get("form")}
            for d in infos if isinstance(d, dict)
        ],
        "body": node.get("body", ""),
        "year": meta.get("year"),
        "gender": meta.get("gender"),
        "age": meta.get("age"),
        "views": meta.get("views"),
        "erowid_id": meta.get("erowidId"),
        "erowid_notes": node.get("erowidNotes") or [],
        "pull_quotes": node.get("pullQuotes") or [],
        "url": f"https://erowid.org/experiences/exp.php?ID={meta.get('erowidId', '')}",
    }


def _get_substance_list(t: Transport) -> List[str]:
    from pypsychonaut.wiki import get_substance_list
    return get_substance_list(transport=t)


def iter_graphql_experiences(*, seen_ids: Optional[Set[str]] = None,
                              transport: Optional[Transport] = None,
                              limit: int = 0) -> Iterator[dict]:
    """Yield Erowid experience reports per substance via GraphQL."""
    t = transport or default_transport()
    if seen_ids is None:
        seen_ids = set()

    substances = _get_substance_list(t)
    print(f"[pw_exp_gql] {len(substances)} substances to query")
    total = 0

    for substance in substances:
        page_size = 200
        offset = 0
        while True:
            reports = _gql_experiences_for_substance(substance, t, limit=page_size, offset=offset)
            if not reports:
                break
            for node in reports:
                eid = (node.get("meta") or {}).get("erowidId", "")
                key = f"erowid:{eid}" if eid else f"gql:{substance}:{offset}"
                if key in seen_ids:
                    continue
                seen_ids.add(key)
                row = _row_from_gql(node, substance)
                yield row
                total += 1
                if limit and total >= limit:
                    return
            if len(reports) < page_size:
                break
            offset += page_size
        print(f"[pw_exp_gql] substance={substance} done (total={total})")


# ── HTML trip reports ──────────────────────────────────────────────────────

def _discover_experience_urls(t: Transport) -> List[str]:
    """Return all /wiki/Experience:... URLs from the Experience Index."""
    from bs4 import BeautifulSoup
    _throttle()
    html = t.get_html(f"{BASE}{EXPERIENCE_INDEX}")
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    seen: Set[str] = set()
    for a in soup.select("a[href^='/wiki/Experience:']"):
        href = a.get("href", "")
        if href and href not in seen:
            seen.add(href)
            urls.append(href)
    return urls


def _parse_experience_page(path: str, t: Transport) -> Optional[dict]:
    """Fetch and parse one PW-native experience report."""
    from bs4 import BeautifulSoup
    try:
        _throttle()
        html = t.get_html(f"{BASE}{path}")
    except Exception:
        return None
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("#mw-content-text")
    if not content:
        return None

    title = unquote(path.split("/wiki/Experience:")[-1]).replace("_", " ")
    url = f"{BASE}{path}"

    # Extract metadata from infobox or first paragraphs
    substances: List[str] = []
    dose_info: List[dict] = []
    year = None
    gender = None

    # PW experience pages often have an infobox table
    for table in content.select("table"):
        for row in table.select("tr"):
            cells = [td.get_text(strip=True) for td in row.select("td, th")]
            if len(cells) >= 2:
                key = cells[0].lower()
                val = cells[1] if len(cells) > 1 else ""
                if "substance" in key or "drug" in key:
                    substances.append(val)
                elif "dose" in key or "amount" in key:
                    dose_info.append({"amount": val, "method": cells[2] if len(cells) > 2 else ""})
                elif "year" in key or "date" in key:
                    m = re.search(r"20\d\d|19\d\d", val)
                    if m:
                        year = int(m.group())
                elif "gender" in key or "sex" in key:
                    gender = val

    # All substances linked in the page
    for a in content.select("a[href^='/wiki/']"):
        sub = unquote(a.get("href", "")[len("/wiki/"):]).replace("_", " ")
        if sub and sub not in substances and len(sub) < 60:
            substances.append(sub)

    # Body text: all paragraphs
    body_parts = []
    for p in content.select("p"):
        text = re.sub(r"\s+", " ", p.get_text(" ", strip=True))
        if len(text) > 20:
            body_parts.append(text)
    body = "\n\n".join(body_parts)

    # Tags from categories
    tags = [a.get_text(strip=True) for a in soup.select("#catlinks a")
            if a.get_text(strip=True) not in ("Categories",)]

    return {
        "source": "pw_experience",
        "title": title,
        "author": "",
        "substance": substances[0] if substances else "",
        "substances": substances[:20],
        "dose_info": dose_info,
        "body": body,
        "year": year,
        "gender": gender,
        "age": None,
        "views": None,
        "erowid_id": None,
        "erowid_notes": [],
        "pull_quotes": [],
        "url": url,
        "tags": tags,
    }


def iter_html_experiences(*, seen_urls: Optional[Set[str]] = None,
                           transport: Optional[Transport] = None,
                           limit: int = 0) -> Iterator[dict]:
    """Yield PW-native experience reports via HTML scrape."""
    t = transport or default_transport()
    if seen_urls is None:
        seen_urls = set()

    urls = _discover_experience_urls(t)
    print(f"[pw_exp_html] {len(urls)} experience pages discovered")
    total = 0

    for path in urls:
        if path in seen_urls:
            continue
        seen_urls.add(path)
        row = _parse_experience_page(path, t)
        if row:
            yield row
            total += 1
            if limit and total >= limit:
                break


def export_jsonl(path: str, *, strategy: str = "both", delay: float = 1.5,
                 limit: int = 0) -> int:
    global _min_delay
    _min_delay = delay
    t = Transport()
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    seen_erowid_ids: Set[str] = set()
    seen_urls: Set[str] = set()
    if out.exists():
        with open(out) as f:
            for line in f:
                try:
                    row = json.loads(line)
                    if row.get("erowid_id"):
                        seen_erowid_ids.add(f"erowid:{row['erowid_id']}")
                    if row.get("url"):
                        seen_urls.add(row["url"].replace(BASE, "").replace("https://erowid.org", ""))
                except Exception:
                    pass
        print(f"[pw_exp] {len(seen_erowid_ids)} erowid + {len(seen_urls)} pw already saved")

    count = 0
    with open(out, "a", encoding="utf-8") as fh:
        def _write(row):
            nonlocal count
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            count += 1

        if strategy in ("both", "graphql"):
            for row in iter_graphql_experiences(seen_ids=seen_erowid_ids, transport=t, limit=limit):
                _write(row)
        if strategy in ("both", "html"):
            for row in iter_html_experiences(seen_urls=seen_urls, transport=t, limit=limit):
                _write(row)

    return count


def main(argv=None):
    ap = argparse.ArgumentParser(description="PsychonautWiki experience reports crawler")
    ap.add_argument("--out", default=str(Path.home() / ".cache/metadatarr/scrapers/psychonaut_experiences.jsonl"))
    ap.add_argument("--strategy", choices=["both", "graphql", "html"], default="both")
    ap.add_argument("--delay", type=float, default=1.5)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)
    n = export_jsonl(args.out, strategy=args.strategy, delay=args.delay, limit=args.limit)
    print(f"[pw_exp] done — {n} rows written")


if __name__ == "__main__":
    main()
