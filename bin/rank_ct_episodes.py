"""Rank Critical Thinking podcast episodes by technique-density.

Heuristic:
  - +3 per keyword in title from technique whitelist
  - +1 for file-size > median (long episode → more material)
  - HARD veto for keywords in skip list (pure interview / mental / recap)
Sorted desc, top 20 selected.

Outputs JSON to stdout for Phase 2 consumption.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TRANSCRIPTS = REPO / "wiki" / "sources" / "podcasts" / "ct" / "whisper" / "transcripts"

TECH_KEYWORDS = [
    "SSRF", "CSRF", "XSS", "CSP", "Smuggl", "Cache", "SAML", "OAuth",
    "Parser", "Parsing", "DOM", "IDOR", "Race", "WordPress", "Mobile",
    "Methodology", "Write-up", "Writeup", "Write-ups", "Top 10",
    "Client-side", "Clickjack", "Prototype", "Hash", "Truncation",
    "Normalization", "Unicode", "Iframe", "Sandbox", "Gadget",
    "PostMessage", "Auth Bypass", "Auth Bypasses", "RCE", "JWT",
    "Path Traversal", "CSPT", "Protobuf", "ATO", "Supply Chain",
    "DOMPurify", "Recon", "GraphQL", "JSON", "Salesforce",
    "ServiceNow", "Chrome Extension", "Browser", "Web Cache",
    "Web Cache Deception", "Bypass", "Encryption Oracle",
    "Hop", "MCP", "Cross-Origin", "Headers", "Subdomain",
    "Source Review", "Source-code", "Whitebox", "White Box",
    "VRP", "Wildcard", "DOM-Clobbering", "Passkey", "Frontend",
    "SSTI", "Esoteric", "PostMessage", "Image Injection", "Cookies",
    "Cookie", "Self-XSS", "Blind SSRF", "PKCE", "DTMF",
]

SKIP_KEYWORDS = [
    "Mental", "Burnout", "Goals", "Hacker Stats", "Best Moments",
    "Horror Stories", "Halloween", "Hacker Wife", "Relationships",
    "Doctor", "Dr.", "Mentorship", "Mentee", "Q_A",
    "Wall Street", "Burgers", "Metallica",
    "Million_Dollar_Hacker", "Million-Dollar_Hacker", "Black_Badge",
    "MVH_DEFCON", "Korea_LHE",
    "Drama", "Naughty_List", "Acropalypse",
    "Live_Chat", "Live_Hacking_Event_Inside",
    "Inside_Scoop", "Recap_With", "Pwn2Own_VS_H1",
]


def parse(stem: str) -> dict | None:
    m = re.match(r"^(\d{8})_([A-Za-z0-9_-]{11})_(.+)$", stem)
    if not m:
        return None
    rest = m.group(3)
    ep = None
    em = re.search(r"_(?:Ep\.?|EP\.?)_?(\d+)$", rest)
    if em:
        ep = int(em.group(1))
        rest = rest[: em.start()]
    return {
        "date": f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}",
        "video_id": m.group(2),
        "title": rest.replace("_", " ").strip(),
        "ep_no": ep,
        "base": stem,
    }


def score(title: str, size: int, median: int) -> int:
    title_lc = title.lower()
    if any(kw.replace("_", " ").lower() in title_lc.replace("_", " ")
           for kw in SKIP_KEYWORDS):
        return -1
    score = 0
    for kw in TECH_KEYWORDS:
        if kw.lower() in title_lc:
            score += 3
    if size > median:
        score += 1
    return score


def main() -> None:
    files = sorted(TRANSCRIPTS.glob("*.txt"))
    sizes = [p.stat().st_size for p in files]
    sizes.sort()
    median = sizes[len(sizes) // 2] if sizes else 0

    rows = []
    for p in files:
        meta = parse(p.stem)
        if not meta:
            continue
        sz = p.stat().st_size
        s = score(meta["title"], sz, median)
        rows.append({**meta, "size": sz, "score": s, "path": str(p)})

    # Filter vetoed (score == -1) then sort by score desc, size desc.
    eligible = [r for r in rows if r["score"] >= 0]
    eligible.sort(key=lambda r: (-r["score"], -r["size"]))
    top = eligible[:20]

    print(json.dumps({
        "total_eps": len(rows),
        "eligible": len(eligible),
        "selected": len(top),
        "median_size": median,
        "top": top,
    }, indent=2))


if __name__ == "__main__":
    main()
