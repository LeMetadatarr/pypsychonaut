"""Example 01 — the substance catalogue (scraped from the wiki index).

Run::

    python examples/01_substance_list.py
"""
import pypsychonaut as pw


def main() -> None:
    names = pw.get_substance_list()
    print(f"{len(names)} substances in the Summary_index")
    print("sample:", names[:10])

    index = pw.get_substance_index()
    print("\ncategories:", list(index)[:8])


if __name__ == "__main__":
    main()
