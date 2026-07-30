"""Markdown corpus rendering + resumable dump (offline via fixture)."""
import json
import os

from pypsychonaut import dataset
from pypsychonaut.types import Substance

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _substance():
    with open(os.path.join(FIX, "substance_lsd.json"), encoding="utf-8") as fh:
        node = json.load(fh)["data"]["substances"][0]
    return Substance.from_graphql(node)


def test_slug():
    assert dataset._slug("LSD") == "lsd"
    assert dataset._slug("2C-B") == "2c-b"
    assert dataset._slug("Psilocybin mushrooms") == "psilocybin_mushrooms"


def test_substance_to_markdown_frontmatter_and_body():
    md = dataset.substance_to_markdown(_substance())
    assert md.startswith("---\n")
    assert "name: LSD" in md
    assert "psychoactive_class: [Psychedelic]" in md
    assert "routes: [sublingual]" in md
    # body has the ROA dose table and effects + source link
    assert "## Routes of administration" in md
    assert "### sublingual" in md
    assert "| Common |" in md
    assert "## Effects" in md
    assert "Source: <https://psychonautwiki.org/wiki/LSD>" in md


def test_dump_substance_resumable(tmp_path, monkeypatch):
    sub = _substance()

    calls = {"n": 0}

    def fake_search(name, *, resolve_name=True, transport=None):
        calls["n"] += 1
        return [sub]

    monkeypatch.setattr(dataset, "search_psychonaut_wiki", fake_search)

    path = dataset.dump_substance("LSD", str(tmp_path))
    assert path and os.path.exists(path)
    assert calls["n"] == 1

    # second call skips (resumable) — no extra fetch
    again = dataset.dump_substance("LSD", str(tmp_path))
    assert again == path
    assert calls["n"] == 1


def test_build_corpus_sample(tmp_path, monkeypatch):
    sub = _substance()
    monkeypatch.setattr(dataset, "search_psychonaut_wiki",
                        lambda name, **k: [sub])
    summary = dataset.build_corpus(str(tmp_path),
                                   names=["LSD", "MDMA", "Ketamine"],
                                   delay=0)
    assert summary == {"written": 3, "skipped": 0, "missing": 0, "total": 3}
    assert len(list(tmp_path.glob("*.md"))) == 3
    # re-run is fully skipped
    summary2 = dataset.build_corpus(str(tmp_path),
                                    names=["LSD", "MDMA", "Ketamine"], delay=0)
    assert summary2["skipped"] == 3 and summary2["written"] == 0
