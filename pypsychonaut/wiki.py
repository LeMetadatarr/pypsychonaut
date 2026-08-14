from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from pypsychonaut._transport import Transport, default_transport
from pypsychonaut.parse import parse_substance_index, parse_substance_list
from pypsychonaut.slang import DRUG_SLANG
from pypsychonaut.types import Effect, ErowidExperience, Reagent, ReagentColor, Substance, SubstanceReagents

SUMMARY_INDEX = "/wiki/Summary_index"

SUBSTANCE_QUERY = """
query Substances($query: String!) {
  substances(query: $query) {
    name
    url
    featured
    class { chemical psychoactive }
    tolerance { full half zero }
    roa {
      oral     { name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
      sublingual   { name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
      buccal       { name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
      insufflated  { name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
      rectal       { name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
      transdermal  { name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
      subcutaneous { name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
      intramuscular{ name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
      intravenous  { name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
      smoked       { name dose { units threshold heavy light { min max } common { min max } strong { min max } }
                 duration { afterglow { min max units } comeup { min max units } duration { min max units }
                            offset { min max units } onset { min max units } peak { min max units }
                            total { min max units } }
                 bioavailability { min max } }
    }
    roas {
      name
      dose { units threshold heavy light { min max } common { min max } strong { min max } }
      duration { afterglow { min max units } comeup { min max units } duration { min max units }
                 offset { min max units } onset { min max units } peak { min max units }
                 total { min max units } }
      bioavailability { min max }
    }
    effects { name url }
    addictionPotential
    toxicity
    crossTolerances
    commonNames
    systematicName
    summary
    images { thumb image }
    uncertainInteractions { name url addictionPotential toxicity summary }
    unsafeInteractions { name url addictionPotential toxicity summary }
    dangerousInteractions { name url addictionPotential toxicity summary }
    reagents { substanceName rawName results { reagent { id name fullName shortName whiteFirstColor }
                startColors { id name hex simple } endColors { id name hex simple }
                isPositive description } }
  }
}
""".strip()

EROWID_QUERY = """
query Erowid($substance: String!, $limit: Int, $offset: Int) {
  erowid(substance: $substance, limit: $limit, offset: $offset) {
    title author substance body
    meta { erowidId gender published year age views }
    erowidNotes
    pullQuotes
    substanceInfo { amount method substance form }
  }
}
""".strip()

EFFECTS_QUERY = """
query EffectsBySubstance($substance: String!) {
  effectsBySubstance(substance: $substance) {
    name
    url
    substances { name }
  }
}
""".strip()

REAGENTS_QUERY = """
query Reagents {
  reagents { id name fullName shortName whiteFirstColor }
}
""".strip()

REAGENT_COLORS_QUERY = """
query ReagentColors {
  reagentColors { id name hex simple simpleColorId }
}
""".strip()

REAGENT_RESULTS_QUERY = """
query ReagentResults($substance: String!) {
  reagentResults(substance: $substance) {
    query
    matchedName
    pwSubstance { name url }
    results {
      reagent { id name fullName shortName whiteFirstColor }
      startColors { id name hex simple simpleColorId }
      endColors { id name hex simple simpleColorId }
      isPositive
      description
    }
  }
}
""".strip()


def _t(transport: Optional[Transport]) -> Transport:
    return transport or default_transport()


def get_substance_list(*, transport: Optional[Transport] = None) -> List[str]:
    return parse_substance_list(_t(transport).get_html(SUMMARY_INDEX))


def get_substance_index(*, transport: Optional[Transport] = None) -> Dict[str, Any]:
    return parse_substance_index(_t(transport).get_html(SUMMARY_INDEX))


def extract_substance_name(sentence: str, *,
                           substance_list: Optional[List[str]] = None,
                           transport: Optional[Transport] = None):
    if substance_list is None:
        substance_list = get_substance_list(transport=transport)
    words = sentence.lower().split(" ")
    found: Any = False
    for slang, canonical in DRUG_SLANG.items():
        slang = slang.lower()
        canonical = canonical.strip()
        for word in words:
            if slang == word:
                found = canonical
                break
    for substance in substance_list:
        sub = substance.lower()
        for word in words:
            if sub == word:
                found = sub
                break
    if found:
        lowered = [s.lower() for s in substance_list]
        if found.lower() in lowered:
            found = substance_list[lowered.index(found.lower())]
    return found


def search_psychonaut_wiki(substance: str, *,
                           resolve_name: bool = True,
                           transport: Optional[Transport] = None) -> List[Substance]:
    t = _t(transport)
    query_term = substance
    if resolve_name:
        resolved = extract_substance_name(substance, transport=t)
        if resolved:
            query_term = resolved
    data = t.graphql(SUBSTANCE_QUERY, {"query": query_term})
    return [Substance.from_graphql(node) for node in (data.get("substances") or [])]


def query_effects(substance: str, *,
                  transport: Optional[Transport] = None) -> List[Effect]:
    data = _t(transport).graphql(EFFECTS_QUERY, {"substance": substance})
    return [Effect.from_graphql(node) for node in (data.get("effectsBySubstance") or [])]


def query_erowid_experiences(substance: str, *,
                             limit: int = 100,
                             transport: Optional[Transport] = None) -> List[ErowidExperience]:
    data = _t(transport).graphql(EROWID_QUERY, {"substance": substance, "limit": limit})
    return [ErowidExperience.from_graphql(node) for node in (data.get("erowid") or [])]


def query_reagents(*, transport: Optional[Transport] = None) -> List[Reagent]:
    data = _t(transport).graphql(REAGENTS_QUERY)
    return [Reagent.from_graphql(node) for node in (data.get("reagents") or [])]


def query_reagent_colors(*, transport: Optional[Transport] = None) -> List[ReagentColor]:
    data = _t(transport).graphql(REAGENT_COLORS_QUERY)
    return [ReagentColor.from_graphql(node) for node in (data.get("reagentColors") or [])]


def query_reagent_results(substance: str, *,
                          transport: Optional[Transport] = None) -> List[Dict[str, Any]]:
    data = _t(transport).graphql(REAGENT_RESULTS_QUERY, {"substance": substance})
    return data.get("reagentResults") or []


def list_wiki_pages(timeout: float = 30.0) -> List[str]:
    try:
        from sitemapper import discover
    except ImportError:
        raise ImportError(
            "list_wiki_pages() requires the 'sitemapper' package; "
            "install it with: pip install sitemapper"
        )
    d = discover("https://psychonautwiki.org", timeout=timeout)
    wiki_urls = [u.loc for u in d.urls if "/wiki/" in u.loc]
    titles = [unquote(url.split("/wiki/")[-1]) for url in wiki_urls]
    return sorted(set(titles))


def fetch_page_text(title: str, *, transport: Optional[Transport] = None) -> str:
    """Fetch the rendered text of a wiki page via MediaWiki action=parse."""
    session = _t(transport).session
    url = ("https://psychonautwiki.org/w/api.php?action=parse&prop=text&format=json"
           f"&page={title.replace(' ', '%20')}")
    r = session.get(url, timeout=30,
                    headers={"User-Agent": "tgbot/1.0 (research; harm-reduction dataset)"})
    if r.status_code >= 400:
        return ""
    try:
        return _clean_html_text(r.json()["parse"]["text"]["*"])
    except (KeyError, ValueError, TypeError):
        return ""


def _clean_html_text(html: str) -> str:
    import re
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "sup"]):
            tag.decompose()
        return re.sub(r"\n{3,}", "\n\n", soup.get_text("\n"))
    except Exception:
        return re.sub(r"<[^>]+>", " ", html)


class PsychonautWiki:
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

    def query_effects(self, substance: str) -> List[Effect]:
        return query_effects(substance, transport=self.transport)

    def query_erowid(self, substance: str, limit: int = 100) -> List[ErowidExperience]:
        return query_erowid_experiences(substance, limit=limit, transport=self.transport)

    def query_reagents(self) -> List[Reagent]:
        return query_reagents(transport=self.transport)

    def query_reagent_colors(self) -> List[ReagentColor]:
        return query_reagent_colors(transport=self.transport)

    def query_reagent_results(self, substance: str) -> List[Dict[str, Any]]:
        return query_reagent_results(substance, transport=self.transport)

    def list_wiki_pages(self, timeout: float = 30.0) -> List[str]:
        return list_wiki_pages(timeout=timeout)

    def fetch_page_text(self, title: str) -> str:
        return fetch_page_text(title, transport=self.transport)

    search_psychonaut_wiki = search
