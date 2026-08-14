"""Example 06 — query effects for a substance.

Run::

    python examples/06_query_effects.py
"""
import pypsychonaut as pw


def main() -> None:
    effects = pw.query_effects("MDMA")
    print(f"Effects for MDMA ({len(effects)}):")
    for e in effects:
        print(f"  {e.name}: substances={e.substances[:5]}")


if __name__ == "__main__":
    main()
