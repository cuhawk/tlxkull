#!/usr/bin/env python3
"""Validate cookies/<platform>.json files exported from Cookie-Editor."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

EXPECTED = {
    "hackerone": {"domain_substr": "hackerone.com",
                  "required": ["__Host-session", "user_session"]},
    "intigriti": {"domain_substr": "intigriti.com",
                  "required": ["_intigriti_session_v2", "AspNet.Cookies"]},
    "bugcrowd":  {"domain_substr": "bugcrowd.com",
                  "required": ["_crowdcontrol_session"]},
    "synack":    {"domain_substr": "synack.com",
                  "required": ["_crowd_control_session", "remember_user_token"]},
}

COOKIES_DIR = Path(__file__).resolve().parent / "cookies"


def check(platform: str) -> bool:
    expect = EXPECTED[platform]
    path = COOKIES_DIR / f"{platform}.json"
    if not path.exists():
        print(f"{platform}: MISSING file {path}")
        return False
    try:
        cookies = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"{platform}: INVALID JSON ({exc})")
        return False
    if not isinstance(cookies, list):
        print(f"{platform}: expected JSON array, got {type(cookies).__name__}")
        return False
    now = time.time()
    names = {c.get("name") for c in cookies if expect["domain_substr"] in
             (c.get("domain") or "")}
    missing = [n for n in expect["required"] if n not in names]
    expired = [c["name"] for c in cookies
               if expect["domain_substr"] in (c.get("domain") or "")
               and c.get("expirationDate", float("inf")) < now]
    msg = []
    if missing:
        msg.append(f"missing={missing}")
    if expired:
        msg.append(f"expired={expired}")
    if msg:
        print(f"{platform}: WARN ({'; '.join(msg)})")
        return False
    print(f"{platform}: ok ({len(cookies)} cookies)")
    return True


def main() -> None:
    targets = sys.argv[1:] or list(EXPECTED)
    bad = [p for p in targets if not check(p)]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
