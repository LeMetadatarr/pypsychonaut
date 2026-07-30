"""Public surface is importable and stable."""
import pypsychonaut as pw


def test_version():
    assert isinstance(pw.__version__, str)


def test_exports():
    for name in [
        "Substance", "Roa", "Dose", "Duration", "Range", "Effect",
        "SubstanceClass", "Tolerance", "PsychonautWiki", "Transport",
        "DRUG_SLANG", "SUBSTANCE_QUERY",
        "get_substance_list", "get_substance_index",
        "search_psychonaut_wiki", "extract_substance_name",
    ]:
        assert hasattr(pw, name), name
