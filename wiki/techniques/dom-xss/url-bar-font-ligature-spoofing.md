---
title: URL-bar spoofing via font ligatures
slug: url-bar-font-ligature-spoofing
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/url-spoof, technique/browser-bug]
inbound: []
---

# URL-bar spoofing via font ligatures

## Pattern
The font used by Chrome's address bar defined ligatures mapping certain
codepoint sequences to the stylized Google-logo glyphs. The actual DNS
hostname was something like `googlelogoligature.net` (or the per-letter
variants `g_logo`, `e_logo_ligature`, `l_logo_ligature` ...) but the
rendered glyphs in the URL bar showed `Google` in the official styled form.
A registered attacker domain could thus impersonate `Google.com` /
`Google.net` visually in the URL bar — full-throttle URL-bar spoofing.

Google paid $15K and patched not the font, but with a blacklist:
`domain.host_name.find_unsafe_ligature(...)` rejecting any hostname that
matches the known ligature triggers. Future research direction: any new
ligature pushed into the URL-bar font is a re-bypass.

## Preconditions
- Chrome <= patch version that introduced the ligature deny-list.
- Attacker can register the literal hostname containing the ligature
  codepoints.

## Detection
- Diff the URL-bar font for ligature definitions; any sequence that maps
  to a brand-styled glyph is a spoof candidate.
- Test trick still works inside Google search results (the patch is
  scoped to the URL bar specifically).

## Triggering
Open a target like `googlelogoligature.net` in the affected Chrome —
the URL bar renders styled `Google.net`. Body error message reveals
the actual hostname (`googlelogoligature.net was not found`) confirming
the DNS-vs-render gap.

## Bypasses / further research
- Find a new ligature codepoint not in the deny-list (the fix is a
  blacklist, not a font fix).
- Any other brand whose font ligatures escape into security-sensitive
  rendering surfaces (URL bar, address bar of mobile browsers, share
  sheets).

## Seen in the wild
- {date: 2025, source: CT Ep 128} — $15K Chrome bounty.

## References
- Critical Thinking Podcast Ep 128
- Chromium bug tracker — URL-bar Google-logo ligature spoof
- Related: [[restricted-character-bypass]]
