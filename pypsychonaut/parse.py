"""Offline HTML parsers for PsychonautWiki's ``Summary_index`` page.

The index is a set of category panels (``div.panel.radius``), each listing its
substances as ``li.featured.list-item`` entries with anchor links. These
parsers are independent of how the HTML was fetched (see :mod:`_transport`).
"""
from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup

BASE = "https://psychonautwiki.org"


def _clean(name: str) -> str:
    return (name.replace("/Summary", "")
                .replace("(page does not exist)", "")
                .strip())


def parse_substance_list(html: str) -> List[str]:
    """Return a flat list of substance names from a ``Summary_index`` page."""
    soup = BeautifulSoup(html, "html.parser")
    panels = soup.find_all("div", {"class": "panel radius"})
    substances: List[str] = []
    for panel in panels:
        for item in panel.find_all("li", {"class": "featured list-item"}):
            subcat = item.find("span", {"class": "mw-headline"})
            i = 0
            if subcat is not None:
                subcat = subcat.getText()
            anchors = item.find_all("a")
            if subcat is not None and anchors and anchors[0].getText() == subcat:
                i = 1
            for anchor in anchors[i:]:
                substances.append(_clean(anchor.getText()))
    return substances


def parse_substance_index(html: str) -> Dict[str, Any]:
    """Return the nested category → (subcategory) → substance → url index."""
    soup = BeautifulSoup(html, "html.parser")
    panels = soup.find_all("div", {"class": "panel radius"})
    index: Dict[str, Any] = {}
    for panel in panels:
        category = panel.find("span", {"class": "mw-headline"})
        if category is None:
            continue
        name = category.get("id") or category.getText()
        link = category.find("a")
        cat_url = f"{BASE}{link['href']}" if link and link.get("href") else None
        bucket = index.setdefault(name, {"url": cat_url})

        for item in panel.find_all("li", {"class": "featured list-item"}):
            subcat = item.find("span", {"class": "mw-headline"})
            i = 0
            target: Dict[str, Any] = bucket
            if subcat is not None:
                subcat_name = subcat.getText()
                target = bucket.setdefault(subcat_name, {})
            anchors = item.find_all("a")
            if subcat is not None and anchors and anchors[0].getText() == subcat.getText():
                i = 1
                href = anchors[0].get("href")
                target["url"] = f"{BASE}{href}" if href else None
            for anchor in anchors[i:]:
                href = anchor.get("href")
                target[_clean(anchor.getText())] = f"{BASE}{href}" if href else None
    return index
