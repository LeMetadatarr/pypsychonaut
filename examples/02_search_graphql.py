"""Example 02 — structured data from the GraphQL API.

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

    print("\nfull to_dict():")
    print(json.dumps(s.to_dict(), indent=2)[:500])


if __name__ == "__main__":
    main()
