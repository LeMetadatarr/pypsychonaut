"""Offline parser tests against a real Summary_index fixture (no network)."""
import os

from pypsychonaut.parse import parse_substance_index, parse_substance_list

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return fh.read()


def test_parse_substance_list():
    names = parse_substance_list(_read("summary_index.html"))
    assert len(names) > 50
    assert "LSD" in names
    assert "DMT" in names
    # cleaned: no "/Summary" suffix survives
    assert not any("/Summary" in n for n in names)


def test_parse_substance_index_nested():
    index = parse_substance_index(_read("summary_index.html"))
    assert "Psychedelics" in index
    # categories carry a url key and substance → url mappings
    psychedelics = index["Psychedelics"]
    assert "url" in psychedelics
    # somewhere in the tree LSD maps to a psychonautwiki url
    flat = []

    def walk(d):
        for k, v in d.items():
            if isinstance(v, dict):
                walk(v)
            elif isinstance(v, str):
                flat.append((k, v))

    walk(index)
    urls = dict(flat)
    assert any(k == "LSD" for k, _ in flat)
    assert all(u is None or u.startswith("https://psychonautwiki.org") for u in urls.values())


def test_empty_index():
    assert parse_substance_list("<html><body>nothing</body></html>") == []
    assert parse_substance_index("<html><body>nothing</body></html>") == {}
