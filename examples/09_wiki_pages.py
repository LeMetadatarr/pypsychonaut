"""Example 09 — list all wiki pages from the sitemap.

Run::

    python examples/09_wiki_pages.py
"""
import pypsychonaut as pw


def main() -> None:
    pages = pw.list_wiki_pages()
    print(f"Total pages in sitemap: {len(pages)}")
    print(f"First 10: {pages[:10]}")
    names = pw.get_substance_list()
    subst = [p for p in pages if p in names]
    print(f"Substance pages: {len(subst)} of {len(names)} in index")


if __name__ == "__main__":
    main()
