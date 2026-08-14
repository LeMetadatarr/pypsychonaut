"""Example 02 — all substance fields from the GraphQL API.

Run::

    python examples/02_search_graphql.py
"""
import json

import pypsychonaut as pw


def main() -> None:
    subs = pw.search_psychonaut_wiki("LSD")
    s = subs[0]
    print(s.name, "—", s.substance_class.psychoactive, s.substance_class.chemical)
    for roa in s.roas:
        common = roa.dose.common.to_dict() if roa.dose and roa.dose.common else None
        total = roa.duration.total.to_dict() if roa.duration and roa.duration.total else None
        print(f"  {roa.name}: common dose {common}, total duration {total}")

    print("\n--- new expanded fields ---")
    print(f"  featured: {s.featured}")
    print(f"  common_names: {s.common_names}")
    print(f"  addiction_potential: {s.addiction_potential}")
    print(f"  toxicity: {s.toxicity}")
    print(f"  cross_tolerances: {s.cross_tolerances}")
    print(f"  images: {len(s.images)} images")
    print(f"  unsafe_interactions: {len(s.unsafe_interactions)} interactions")
    print(f"  dangerous_interactions: {len(s.dangerous_interactions)} interactions")
    print(f"  has reagents: {s.reagents is not None}")

    print("\nto_dict() keys:", list(s.to_dict().keys()))


if __name__ == "__main__":
    main()
