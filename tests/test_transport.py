"""Transport configuration tests (kwargs + env, no network)."""
import pytest

from pypsychonaut import _transport as t


def _clear_env(monkeypatch):
    for suffix in ("TRANSPORT", "FLARESOLVERR_URL", "FLARESOLVERR_TIMEOUT",
                   "WAYBACK_FALLBACK"):
        monkeypatch.delenv(f"PYPSYCHONAUT_{suffix}", raising=False)
        monkeypatch.delenv(f"UNBLOCK_REQUESTS_{suffix}", raising=False)


def test_transport_mode_from_kwargs(monkeypatch):
    _clear_env(monkeypatch)
    assert t.Transport()._resolved_mode() == "curl_cffi"
    assert t.Transport(mode="wayback")._resolved_mode() == "wayback"
    assert t.Transport(flaresolverr_url="http://x:8191")._resolved_mode() == "flaresolverr"


def test_transport_uses_pypsychonaut_env_prefix(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("PYPSYCHONAUT_TRANSPORT", "requests")
    assert t.Transport()._resolved_mode() == "requests"
    # explicit kwarg still wins over env
    assert t.Transport(mode="wayback")._resolved_mode() == "wayback"


def test_transport_rejects_bad_mode():
    with pytest.raises(ValueError):
        t.Transport(mode="nonsense")


def test_session_is_cloudflare_session(monkeypatch):
    _clear_env(monkeypatch)
    from unblock_requests import CloudflareSession
    sess = t.Transport(mode="requests").session
    assert isinstance(sess, CloudflareSession)
    assert sess.env_prefix == "PYPSYCHONAUT"


def test_client_kwargs(monkeypatch):
    _clear_env(monkeypatch)
    import pypsychonaut as pw
    assert pw.PsychonautWiki(wayback=True).transport._resolved_mode() == "wayback"
    c = pw.PsychonautWiki(flaresolverr_url="http://localhost:8191")
    assert c.transport._resolved_mode() == "flaresolverr"
