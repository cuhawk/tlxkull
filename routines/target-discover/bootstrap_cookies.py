#!/usr/bin/env python3
"""Bootstrap routines/target-discover/cookies/<platform>.json from
running Chrome's CDP debug endpoint (http://127.0.0.1:9222).

Stdlib only — no pip deps. Uses CDP's Network.getCookies (Chrome serves
cookies via its own API; no on-disk SQLite decryption).

Prereq: launch Chrome with debug port via launch_chrome_debug.sh.

Usage:
    python3 bootstrap_cookies.py                  # all 4 platforms
    python3 bootstrap_cookies.py hackerone        # one
    python3 bootstrap_cookies.py --port 9222
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import struct
import sys
import urllib.parse
import urllib.request
from hashlib import sha1
from pathlib import Path

PLATFORMS = {
    "hackerone": ["https://hackerone.com", "https://api.hackerone.com"],
    "intigriti": ["https://app.intigriti.com", "https://www.intigriti.com"],
    "bugcrowd":  ["https://bugcrowd.com", "https://researcher.bugcrowd.com"],
    "synack":    ["https://platform.synack.com", "https://login.synack.com"],
}

COOKIES_DIR = Path(__file__).resolve().parent / "cookies"


# ---- stdlib WebSocket client (RFC 6455) ------------------------------------

class WSClient:
    def __init__(self, url: str):
        u = urllib.parse.urlparse(url)
        if u.scheme != "ws":
            raise ValueError(f"only ws:// supported, got {u.scheme}")
        host = u.hostname
        port = u.port or 80
        path = u.path + (f"?{u.query}" if u.query else "")
        self.sock = socket.create_connection((host, port), timeout=10)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        # read response headers
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("ws handshake: connection closed")
            buf += chunk
        if b" 101 " not in buf.split(b"\r\n", 1)[0]:
            raise RuntimeError(f"ws handshake failed: {buf[:200]!r}")
        expected = base64.b64encode(
            sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
        )
        if expected not in buf:
            raise RuntimeError("ws handshake: bad Sec-WebSocket-Accept")
        # any leftover bytes after headers begin frame stream
        header_end = buf.index(b"\r\n\r\n") + 4
        self._recv_buf = buf[header_end:]

    def send_text(self, text: str) -> None:
        payload = text.encode("utf-8")
        header = bytearray([0x81])  # FIN + text opcode
        mask_bit = 0x80
        if len(payload) < 126:
            header.append(mask_bit | len(payload))
        elif len(payload) < (1 << 16):
            header.append(mask_bit | 126)
            header += struct.pack(">H", len(payload))
        else:
            header.append(mask_bit | 127)
            header += struct.pack(">Q", len(payload))
        mask = os.urandom(4)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def _recv_exact(self, n: int) -> bytes:
        while len(self._recv_buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("ws: connection closed mid-frame")
            self._recv_buf += chunk
        out, self._recv_buf = self._recv_buf[:n], self._recv_buf[n:]
        return out

    def recv_text(self) -> str:
        # may need to skip control frames (ping/pong/close)
        while True:
            h = self._recv_exact(2)
            fin = h[0] & 0x80
            opcode = h[0] & 0x0F
            masked = h[1] & 0x80
            length = h[1] & 0x7F
            if length == 126:
                length = struct.unpack(">H", self._recv_exact(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self._recv_exact(8))[0]
            mask = self._recv_exact(4) if masked else None
            payload = self._recv_exact(length)
            if mask:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            if opcode == 0x9:        # ping → pong
                self.sock.sendall(b"\x8a\x00")
                continue
            if opcode in (0xA, 0x8):  # pong, close — skip / handle
                if opcode == 0x8:
                    raise RuntimeError("ws: server closed")
                continue
            if opcode == 0x1:        # text
                if not fin:
                    raise RuntimeError("ws: fragmented frames unsupported")
                return payload.decode("utf-8")

    def close(self) -> None:
        try:
            self.sock.sendall(b"\x88\x80" + os.urandom(4))  # masked close
        except Exception:
            pass
        self.sock.close()


# ---- CDP wrappers ----------------------------------------------------------

def first_ws_url(port: int) -> str:
    targets = json.loads(urllib.request.urlopen(
        f"http://127.0.0.1:{port}/json", timeout=3).read())
    for t in targets:
        if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
            return t["webSocketDebuggerUrl"]
    raise RuntimeError("no page target with webSocketDebuggerUrl found")


def cdp_call(ws: WSClient, method: str, params: dict | None = None,
             req_id: int = 1) -> dict:
    ws.send_text(json.dumps({"id": req_id, "method": method,
                              "params": params or {}}))
    while True:
        resp = json.loads(ws.recv_text())
        if resp.get("id") == req_id:
            if "error" in resp:
                raise RuntimeError(f"cdp error {method}: {resp['error']}")
            return resp.get("result", {})


def normalize(c: dict) -> dict:
    same_site_map = {"None": "no_restriction", "Lax": "lax", "Strict": "strict"}
    exp = c.get("expires", -1)
    return {
        "name": c["name"],
        "value": c["value"],
        "domain": c["domain"],
        "path": c.get("path", "/"),
        "expirationDate": exp if exp > 0 else None,
        "secure": c.get("secure", False),
        "httpOnly": c.get("httpOnly", False),
        "sameSite": same_site_map.get(c.get("sameSite", "Lax"), "lax"),
        "session": c.get("session", False),
    }


# ---- main ------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("platform", nargs="?", choices=list(PLATFORMS), default=None)
    ap.add_argument("--port", type=int, default=9222)
    args = ap.parse_args()

    COOKIES_DIR.mkdir(exist_ok=True)
    try:
        ws_url = first_ws_url(args.port)
    except Exception as exc:
        print(f"ERR: cannot reach CDP at :{args.port} — {exc}", file=sys.stderr)
        print("hint: run `bash routines/target-discover/launch_chrome_debug.sh` first",
              file=sys.stderr)
        sys.exit(1)

    targets = [args.platform] if args.platform else list(PLATFORMS)
    ws = WSClient(ws_url)
    req_id = 1
    try:
        for plat in targets:
            res = cdp_call(ws, "Network.getCookies",
                           {"urls": PLATFORMS[plat]}, req_id=req_id)
            req_id += 1
            cookies = [normalize(c) for c in res.get("cookies", [])]
            out_path = COOKIES_DIR / f"{plat}.json"
            out_path.write_text(json.dumps(cookies, indent=2))
            out_path.chmod(0o600)
            print(f"{plat}: {len(cookies)} cookies -> {out_path}")
    finally:
        ws.close()

    print("\ndone. Now quit debug Chrome, reopen normally.")
    print("Validate: python3 routines/target-discover/validate_cookies.py")


if __name__ == "__main__":
    main()
