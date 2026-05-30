"""HTTP transport for pypsychonaut.

pypsychonaut talks to two PsychonautWiki surfaces:

- the **wiki** at ``https://psychonautwiki.org`` — scraped HTML
  (``Summary_index``), occasionally fronted by a Cloudflare bot check;
- the official **GraphQL API** at ``https://api.psychonautwiki.org`` — a clean
  JSON endpoint that needs no challenge bypass.

Both are routed through the org transport :class:`unblock_requests.CloudflareSession`
— a drop-in ``requests.Session`` subclass that handles Cloudflare (curl_cffi TLS
impersonation, a FlareSolverr proxy, or a Wayback fallback). The GraphQL endpoint
simply travels through the same session as plain JSON.

Transport is configurable two ways — **constructor kwargs** on :class:`Transport`
(or the high-level :class:`pypsychonaut.PsychonautWiki` client), or **environment
variables** as fallback defaults (prefix ``PYPSYCHONAUT_``). Explicit kwargs
always win over the environment.

Modes (passed straight to ``CloudflareSession``):

- ``curl_cffi`` *(default)* — live fetch with Chrome TLS impersonation when the
  ``stealth`` extra is installed, else plain ``requests``;
- ``requests`` — live fetch with plain ``requests``;
- ``wayback`` — fetch the latest Internet Archive snapshot (HTML only);
- ``flaresolverr`` — fetch through a FlareSolverr proxy (live, solved HTML).

Environment fallbacks: ``PYPSYCHONAUT_TRANSPORT``,
``PYPSYCHONAUT_FLARESOLVERR_URL``, ``PYPSYCHONAUT_FLARESOLVERR_TIMEOUT`` (ms),
``PYPSYCHONAUT_WAYBACK_FALLBACK``.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from unblock_requests import CloudflareSession

BASE = "https://psychonautwiki.org"
GRAPHQL_ENDPOINT = "https://api.psychonautwiki.org/"
ENV_PREFIX = "PYPSYCHONAUT"

_VALID_MODES = {"requests", "curl_cffi", "wayback", "flaresolverr"}


class Transport:
    """Resolves *how* PsychonautWiki is fetched, from explicit kwargs with
    environment fallbacks. Wraps a single :class:`CloudflareSession`.

    Args:
        mode:                 ``"requests"`` / ``"curl_cffi"`` / ``"wayback"`` /
                              ``"flaresolverr"``. ``None`` → resolve from the
                              environment, then auto.
        flaresolverr_url:     FlareSolverr base URL; setting this alone selects
                              the ``flaresolverr`` mode.
        flaresolverr_timeout_ms: per-request solve budget (default 60000).
        wayback_fallback:     fall back to the Wayback Machine on any live HTML
                              failure. ``None`` → read the env flag.

    Example::

        from pypsychonaut import Transport
        t = Transport(flaresolverr_url="http://localhost:8191")
        t = Transport(mode="wayback")          # force the Internet Archive
    """

    def __init__(self, *, mode: Optional[str] = None,
                 flaresolverr_url: Optional[str] = None,
                 flaresolverr_timeout_ms: Optional[int] = None,
                 wayback_fallback: Optional[bool] = None) -> None:
        if mode is not None and mode.lower() not in _VALID_MODES:
            raise ValueError(f"mode must be one of {sorted(_VALID_MODES)} or None, got {mode!r}")
        self.mode = mode.lower() if mode else None
        self.flaresolverr_url = flaresolverr_url
        self.flaresolverr_timeout_ms = flaresolverr_timeout_ms
        self.wayback_fallback = wayback_fallback
        self._session: Optional[CloudflareSession] = None

    # -- session ----------------------------------------------------------

    @property
    def session(self) -> CloudflareSession:
        """The shared, lazily-built :class:`CloudflareSession`."""
        if self._session is None:
            self._session = CloudflareSession(
                mode=self.mode,
                flaresolverr_url=self.flaresolverr_url,
                flaresolverr_timeout_ms=self.flaresolverr_timeout_ms,
                wayback_fallback=self.wayback_fallback,
                env_prefix=ENV_PREFIX,
            )
        return self._session

    def _resolved_mode(self) -> str:
        """The transport mode that will actually be used (for introspection)."""
        return self.session._resolved_mode()

    # -- fetch ------------------------------------------------------------

    def get_html(self, path: str, **params: Any) -> str:
        """GET ``{BASE}{path}`` (with query *params*) and return the HTML."""
        url = path if path.startswith("http") else f"{BASE}{path}"
        r = self.session.get(url, params=params or None, timeout=30)
        r.raise_for_status()
        return r.text

    def graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST a GraphQL *query* (+ *variables*) to the API and return ``data``.

        The GraphQL endpoint is a clean JSON API — no Cloudflare bypass needed —
        but it still travels through the configured session. Falls back to a GET
        with the query as a parameter if a POST is rejected.
        """
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        r = self.session.post(
            GRAPHQL_ENDPOINT, json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=30,
        )
        if r.status_code >= 400:
            # the public API also answers GET ?query=...&variables=...
            getparams: Dict[str, Any] = {"query": query}
            if variables:
                getparams["variables"] = json.dumps(variables)
            r = self.session.get(GRAPHQL_ENDPOINT, params=getparams, timeout=30)
        r.raise_for_status()
        body = r.json()
        if body.get("errors"):
            raise RuntimeError(f"GraphQL errors: {body['errors']}")
        return body.get("data") or {}


_DEFAULT_TRANSPORT: Optional[Transport] = None


def default_transport() -> Transport:
    """Return the shared, environment-driven :class:`Transport`."""
    global _DEFAULT_TRANSPORT
    if _DEFAULT_TRANSPORT is None:
        _DEFAULT_TRANSPORT = Transport()
    return _DEFAULT_TRANSPORT
