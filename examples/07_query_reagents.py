"""Example 07 — query reagents, colors, and per-substance results.

Run::

    python examples/07_query_reagents.py
"""
import pypsychonaut as pw


def main() -> None:
    print("=== Reagents ===")
    reagents = pw.query_reagents()
    for r in reagents:
        print(f"  {r.full_name} ({r.short_name}) — id={r.id}")

    print("\n=== Reagent colors ===")
    colors = pw.query_reagent_colors()
    for c in colors[:5]:
        print(f"  {c.name}: {c.hex}")
    print(f"  ... ({len(colors)} total)")

    print("\n=== Reagent results for LSD ===")
    results = pw.query_reagent_results("LSD")
    for group in results:
        print(f"  query='{group['query']}' matched='{group.get('matchedName')}'")
        for res in (group.get("results") or []):
            name = res.get("reagent", {}).get("fullName", "?")
            positive = res.get("isPositive")
            desc = res.get("description", "")
            print(f"    {name}: positive={positive}, desc={desc[:60]}")


if __name__ == "__main__":
    main()
