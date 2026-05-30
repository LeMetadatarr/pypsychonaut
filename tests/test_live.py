"""Live smoke tests — hit the real PsychonautWiki GraphQL API.

Deselected by default; run with::

    pytest -m live
"""
import pytest

import pypsychonaut as pw


@pytest.mark.live
class TestLive:
    def test_live_substance_lookup(self):
        results = pw.search_psychonaut_wiki("LSD")
        assert len(results) >= 1
        s = results[0]
        assert s.name
        assert isinstance(s.name, str)
        assert len(s.name) > 0
