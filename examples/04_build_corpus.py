"""Example 04 — build a markdown corpus (one file per substance).

Validates on a small, polite sample. The full ``Summary_index`` is a few
hundred substances — feasible, but treat a full run as a homelab job (drop
``limit`` and raise ``delay``).

Run::

    python examples/04_build_corpus.py
"""
from pypsychonaut import dataset


def main() -> None:
    summary = dataset.build_corpus("corpus", limit=5, delay=1.0)
    print("corpus summary:", summary)
    print("wrote markdown files into ./corpus/ — resumable (re-run skips them)")


if __name__ == "__main__":
    main()
