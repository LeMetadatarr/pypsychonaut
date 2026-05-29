"""Slang lexicon + substance-name extraction (offline, cached list)."""
from pypsychonaut.slang import DRUG_SLANG
from pypsychonaut.wiki import extract_substance_name

SUBSTANCES = ["LSD", "MDMA", "Ketamine", "DMT", "Cannabis"]


def test_slang_mapping_is_populated():
    assert DRUG_SLANG["acid"] == "lsd"
    assert DRUG_SLANG["ecstasy"] == "mdma"
    assert len(DRUG_SLANG) > 50


def test_extract_via_slang_case_matches_list():
    # "acid" → "lsd" via slang, then case-matched to "LSD" in the list
    assert extract_substance_name("took some acid last night",
                                  substance_list=SUBSTANCES) == "LSD"


def test_extract_direct_substance_token():
    assert extract_substance_name("i tried ketamine once",
                                  substance_list=SUBSTANCES) == "Ketamine"


def test_extract_no_match_returns_false():
    assert extract_substance_name("just had a sandwich",
                                  substance_list=SUBSTANCES) is False
