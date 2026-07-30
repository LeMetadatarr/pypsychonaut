"""Substance lookup functions backed by PsychonautWiki.

Two surfaces:

- :func:`get_substance_list` / :func:`get_substance_index` scrape the wiki's
  ``Summary_index`` HTML page (the catalogue of substances);
- :func:`search_psychonaut_wiki` queries the official GraphQL API
  (``api.psychonautwiki.org``) for structured dose/duration/effect data.

:func:`extract_substance_name` normalises free text into a canonical substance
name using the :data:`pypsychonaut.slang.DRUG_SLANG` lexicon and the live
substance list, so a phrase like ``"took some acid last night"`` resolves to
``"LSD"`` before hitting the API.

:func:`list_wiki_pages` discovers all wiki page titles via the site's sitemap
(coverage extends beyond GraphQL substances to include effects, article stubs,
and cross-references).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from pypsychonaut._transport import Transport, default_transport
from pypsychonaut.parse import parse_substance_index, parse_substance_list
from pypsychonaut.slang import DRUG_SLANG
from pypsychonaut.types import Substance

SUMMARY_INDEX = "/wiki/Summary_index"

# The substance query, cleaned up from the legacy URL-encoded blob into a
# readable GraphQL document with a typed ``$query`` variable.
SUBSTANCE_QUERY = """
query Substances($query: String!) {
  substances(query: $query) {
    name
    url

    # chemical / psychoactive class membership
    class {
      chemical
      psychoactive
    }

    # baseline-reset tolerance notes
    tolerance {
      full
      half
      zero
    }

    # routes of administration
    roas {
      name

      dose {
        units
        threshold
        heavy
        light { min max }
        common { min max }
        strong { min max }
      }

      duration {
        afterglow { min max units }
        comeup { min max units }
        duration { min max units }
        offset { min max units }
        onset { min max units }
        peak { min max units }
        total { min max units }
      }

      bioavailability { min max }
    }

    # subjective effects
    effects {
      name
      url
    }
  }
}
""".strip()


def _t(transport: Optional[Transport]) -> Transport:
    return transport or default_transport()


def get_substance_list(*, transport: Optional[Transport] = None) -> List[str]:
    """Return the flat list of substance names from ``Summary_index``.

    Example::

        import pypsychonaut as pw
        names = pw.get_substance_list()
        print(len(names), "substances", names[:5])
    """
    return parse_substance_list(_t(transport).get_html(SUMMARY_INDEX))


def get_substance_index(*, transport: Optional[Transport] = None) -> Dict[str, Any]:
    """Return the nested category → substance → url index from ``Summary_index``."""
    return parse_substance_index(_t(transport).get_html(SUMMARY_INDEX))


def extract_substance_name(sentence: str, *,
                           substance_list: Optional[List[str]] = None,
                           transport: Optional[Transport] = None):
    """Resolve a free-text *sentence* to a canonical substance name.

    Checks the slang lexicon first, then the live substance list, matching
    whole whitespace-split tokens. Returns the canonical name (case-matched to
    PsychonautWiki's spelling) or ``False`` when no substance is found.

    Args:
        substance_list: pass a cached list to avoid re-fetching ``Summary_index``.

    Example::

        import pypsychonaut as pw
        pw.extract_substance_name("took some acid last night")   # 'LSD'
    """
    if substance_list is None:
        substance_list = get_substance_list(transport=transport)

    words = sentence.lower().split(" ")
    found: Any = False

    # check for drug slang names
    for slang, canonical in DRUG_SLANG.items():
        slang = slang.lower()
        canonical = canonical.strip()
        for word in words:
            if slang == word:
                found = canonical
                break

    # check substance list (overrides slang when an exact token matches)
    for substance in substance_list:
        sub = substance.lower()
        for word in words:
            if sub == word:
                found = sub
                break

    if found:
        # match case — PsychonautWiki doesn't like lower-case
        lowered = [s.lower() for s in substance_list]
        if found.lower() in lowered:
            found = substance_list[lowered.index(found.lower())]

    return found


def search_psychonaut_wiki(substance: str, *,
                           resolve_name: bool = True,
                           transport: Optional[Transport] = None) -> List[Substance]:
    """Query the GraphQL API for a substance, returning typed :class:`Substance`.

    Args:
        substance:    a substance name or a free-text phrase.
        resolve_name: when ``True`` (default), run *substance* through
                      :func:`extract_substance_name` first to normalise slang.

    Example::

        import pypsychonaut as pw
        subs = pw.search_psychonaut_wiki("LSD")
        s = subs[0]
        print(s.name, [r.name for r in s.roas])
    """
    t = _t(transport)
    query_term = substance
    if resolve_name:
        resolved = extract_substance_name(substance, transport=t)
        if resolved:
            query_term = resolved
    data = t.graphql(SUBSTANCE_QUERY, {"query": query_term})
    return [Substance.from_graphql(node) for node in (data.get("substances") or [])]


def list_wiki_pages(timeout: float = 30.0) -> List[str]:
    """Return all wiki page titles discovered via the PsychonautWiki sitemap.

    The sitemap covers the entire wiki (substances, effects, article stubs, and
    cross-references), whereas :func:`get_substance_list` returns only substances
    catalogued on ``Summary_index``. This function is useful for building
    comprehensive datasets or crawling the full knowledge base.

    Args:
        timeout: Per-request timeout in seconds (default 30s).

    Returns:
        A list of URL-decoded wiki page titles (e.g., ``["LSD", "Psilocybin", ...]``).

    Raises:
        ImportError: if ``sitemapper`` is not installed.

    Example::

        import pypsychonaut as pw
        all_pages = pw.list_wiki_pages()
        print(len(all_pages), "pages in PsychonautWiki")
    """
    try:
        from sitemapper import discover
    except ImportError:
        raise ImportError(
            "list_wiki_pages() requires the 'sitemapper' package; "
            "install it with: pip install sitemapper"
        )

    d = discover("https://psychonautwiki.org", timeout=timeout)
    wiki_urls = [u.loc for u in d.urls if "/wiki/" in u.loc]
    # Extract and URL-decode the page title from each /wiki/<Title> URL
    titles = [unquote(url.split("/wiki/")[-1]) for url in wiki_urls]
    return sorted(set(titles))  # deduplicate and sort


class PsychonautWiki:
    """High-level client with a configurable transport.

    Mirrors the module-level functions, but every call uses the transport you
    configure here. The substance list is fetched lazily and cached so repeated
    :meth:`extract_substance_name` calls don't re-hit the wiki.

    Args:
        transport:            ``"requests"`` / ``"curl_cffi"`` / ``"wayback"`` /
                              ``"flaresolverr"``, or a ready :class:`Transport`.
        flaresolverr_url:     FlareSolverr base URL; setting it selects the
                              ``flaresolverr`` transport.
        flaresolverr_timeout_ms: per-request solve budget.
        wayback:              force the Internet Archive (HTML only).
        wayback_fallback:     fall back to the archive on any live HTML failure.

    Example::

        import pypsychonaut as pw
        client = pw.PsychonautWiki()
        subs = client.search("ecstasy")     # slang → MDMA
    """

    def __init__(self, transport=None, *, flaresolverr_url: Optional[str] = None,
                 flaresolverr_timeout_ms: Optional[int] = None,
                 wayback: bool = False,
                 wayback_fallback: Optional[bool] = None) -> None:
        if isinstance(transport, Transport):
            self.transport = transport
        else:
            mode = "wayback" if wayback else transport
            self.transport = Transport(
                mode=mode,
                flaresolverr_url=flaresolverr_url,
                flaresolverr_timeout_ms=flaresolverr_timeout_ms,
                wayback_fallback=wayback_fallback,
            )
        self._substance_list: Optional[List[str]] = None

    @property
    def substance_list(self) -> List[str]:
        if self._substance_list is None:
            self._substance_list = get_substance_list(transport=self.transport)
        return self._substance_list

    def get_substance_list(self) -> List[str]:
        return self.substance_list

    def get_substance_index(self) -> Dict[str, Any]:
        return get_substance_index(transport=self.transport)

    def extract_substance_name(self, sentence: str):
        return extract_substance_name(sentence, substance_list=self.substance_list,
                                      transport=self.transport)

    def search(self, substance: str, *, resolve_name: bool = True) -> List[Substance]:
        return search_psychonaut_wiki(substance, resolve_name=resolve_name,
                                      transport=self.transport)

    def list_wiki_pages(self, timeout: float = 30.0) -> List[str]:
        """Return all wiki page titles discovered via the sitemap.

        See :func:`list_wiki_pages` for details.
        """
        return list_wiki_pages(timeout=timeout)

    # legacy-compatible alias
    search_psychonaut_wiki = search
