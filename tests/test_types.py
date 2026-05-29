"""Type construction from a real GraphQL JSON fixture (no network)."""
import json
import os

from pypsychonaut.types import Substance

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _node():
    with open(os.path.join(FIX, "substance_lsd.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    return data["data"]["substances"][0]


def test_substance_from_graphql():
    s = Substance.from_graphql(_node())
    assert s.name == "LSD"
    assert s.page_url == "https://psychonautwiki.org/wiki/LSD"
    assert s.substance_class.chemical == ["Lysergamides"]
    assert s.substance_class.psychoactive == ["Psychedelic"]
    assert s.tolerance.zero == "5 days"


def test_roa_dose_and_duration():
    s = Substance.from_graphql(_node())
    assert len(s.roas) == 1
    roa = s.roas[0]
    assert roa.name == "sublingual"
    assert roa.dose.units == "µg"
    assert roa.dose.threshold == 15.0
    assert roa.dose.common.min == 75.0 and roa.dose.common.max == 150.0
    assert roa.duration.onset.units == "minutes"
    assert roa.duration.total.min == 8.0 and roa.duration.total.max == 12.0
    assert roa.bioavailability.min == 71.0


def test_effects_and_to_dict():
    s = Substance.from_graphql(_node())
    assert s.effects and s.effects[0].name == "LSD"
    d = s.to_dict()
    assert d["name"] == "LSD"
    assert d["class"]["psychoactive"] == ["Psychedelic"]
    assert d["roas"][0]["dose"]["common"] == {"min": 75.0, "max": 150.0}
    # round-trips through json
    assert json.loads(json.dumps(d))["name"] == "LSD"
