---
title: Matan Berson (matanber)
slug: matan-berson
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
handles: [matanber]
role: hunter
primary_focus: web
tags: [person, role/hunter, focus/web, focus/csrf, focus/xss, focus/ato, focus/self-xss]
inbound: []
---

# Matan Berson (matanber)

## Identity

- **Real name:** Matan Berson
- **Primary handle:** `matanber`
- **Nationality / base:** Israel
- **Role:** Bug bounty hunter; started at age 16, AWC (Ambassador World Cup) participant.
- **Notoriety:** Earned over $150,000 in bug bounty, primarily through his signature
  self-XSS → login CSRF → ATO technique chain.

## Focus areas

- Login CSRF exploitation (cross-site login of victim into attacker's account)
- Self-XSS escalation to full ATO via login CSRF chain
- CSRF vulnerabilities broadly (logout, link account, state-change endpoints)
- Authentication flows (account linking, OAuth entry points)

## Online presence

- X / Twitter handle: `matanber`

## Key research / posts

- Signature technique: stored XSS in attacker's own profile (self-XSS) + CSRF on
  login endpoint → victim's browser executes attacker's XSS → ATO. Documents that
  self-XSS is not inherently unexploitable; it becomes dangerous when combined with
  login CSRF. Found this pattern at multiple programs.
- AWC competitor representing young Israeli hunters.

## BBRE appearances

- Interview covering his start at age 16, the self-XSS to login CSRF methodology,
  achieving $150,000+ through AWC and HackerOne. Emphasis on not dismissing
  self-XSS as out-of-scope without checking login CSRF.
  [BBRE](https://www.youtube.com/watch?v=_VGEtJSRkjg)

## Notes

- Demonstrates that highly impactful bugs can come from chaining two individually
  low/medium-severity issues (self-XSS rated informational + login CSRF rated low →
  combined = account takeover = critical).
- Best approach when encountering self-XSS: immediately test whether the login
  endpoint is CSRF-vulnerable before writing off the XSS.
