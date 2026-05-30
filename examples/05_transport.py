"""Example 05 — configuring the transport.

PsychonautWiki's wiki pages can sit behind a Cloudflare bot check; the GraphQL
API does not. Both route through :class:`unblock_requests.CloudflareSession`.
Pick how pages are fetched with constructor kwargs on the ``PsychonautWiki``
client (shown here) or environment variables (``PYPSYCHONAUT_TRANSPORT`` etc.).

Run::

    python examples/05_transport.py
"""
import pypsychonaut as pw


def main() -> None:
    # default — curl_cffi Chrome TLS impersonation (install the stealth extra)
    default = pw.PsychonautWiki()
    print("default transport:", default.transport._resolved_mode())

    # solve Cloudflare live via a FlareSolverr box
    live = pw.PsychonautWiki(flaresolverr_url="http://localhost:8191")
    print("flaresolverr:", live.transport._resolved_mode())

    # force the Internet Archive for wiki HTML (the GraphQL API is unaffected)
    archived = pw.PsychonautWiki(wayback=True)
    print("wayback:", archived.transport._resolved_mode())

    # try live first, fall back to the archive on a blocked HTML fetch
    resilient = pw.PsychonautWiki(wayback_fallback=True)
    print("with wayback fallback:", resilient.transport._resolved_mode())


if __name__ == "__main__":
    main()
