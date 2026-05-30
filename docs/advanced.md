# Transport & Cloudflare

PsychonautWiki has two surfaces:

- the **wiki** (`https://psychonautwiki.org`) — scraped HTML, occasionally
  fronted by a Cloudflare bot check;
- the official **GraphQL API** (`https://api.psychonautwiki.org`) — a clean JSON
  endpoint that needs no challenge bypass.

Both route through `unblock_requests.CloudflareSession` — a drop-in
`requests.Session` subclass — wrapped by `pypsychonaut.Transport`. The parsing
and type layers are independent of how data was fetched.

## Modes

| Mode | Behaviour |
|---|---|
| `curl_cffi` *(default)* | live fetch with Chrome TLS impersonation (`stealth` extra); plain `requests` if curl-cffi is absent |
| `requests` | live fetch with plain `requests` |
| `wayback` | latest Internet Archive snapshot (HTML only) |
| `flaresolverr` | fetch through a FlareSolverr proxy — live, solved HTML |

## Configure

By kwargs:

```python
import pypsychonaut as pw
pw.PsychonautWiki(flaresolverr_url="http://localhost:8191")   # live via FlareSolverr
pw.PsychonautWiki(wayback=True)                          # Internet Archive
pw.PsychonautWiki(wayback_fallback=True)                 # live, then archive
```

By environment (prefix `PYPSYCHONAUT_`, explicit kwargs always win):

```bash
export PYPSYCHONAUT_TRANSPORT=flaresolverr
export PYPSYCHONAUT_FLARESOLVERR_URL=http://localhost:8191
export PYPSYCHONAUT_FLARESOLVERR_TIMEOUT=60000   # ms
export PYPSYCHONAUT_WAYBACK_FALLBACK=1
```

## GraphQL

The GraphQL endpoint is unaffected by Cloudflare modes (it is JSON, not gated),
but still travels through the same session, so any proxy/transport config
applies. `wayback` mode only affects the wiki HTML scrape — GraphQL POSTs go
through regardless.

```python
data = pw.Transport().graphql(pw.SUBSTANCE_QUERY, {"query": "DMT"})
```
