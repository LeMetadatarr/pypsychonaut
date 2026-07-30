"""Example 03 — slang normalisation before querying.

``extract_substance_name`` turns free text / street names into the canonical
substance PsychonautWiki indexes, so a phrase resolves before the API call.

Run::

    python examples/03_slang.py
"""
import pypsychonaut as pw


def main() -> None:
    client = pw.PsychonautWiki()       # caches the substance list

    for phrase in ["took some acid last night", "we had molly", "ecstasy", "k"]:
        name = client.extract_substance_name(phrase)
        print(f"{phrase!r:40} -> {name!r}")

    # search resolves slang automatically
    subs = client.search("ecstasy")
    print("\nsearch('ecstasy') ->", [s.name for s in subs])


if __name__ == "__main__":
    main()
