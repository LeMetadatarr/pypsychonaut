"""Example 08 — fetch the rendered page text for a substance.

Run::

    python examples/08_fetch_page_text.py
"""
import pypsychonaut as pw


def main() -> None:
    text = pw.fetch_page_text("LSD")
    print(f"LSD page: {len(text)} chars")
    print()
    print(text[:800])


if __name__ == "__main__":
    main()
