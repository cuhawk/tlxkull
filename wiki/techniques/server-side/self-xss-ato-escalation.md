---
title: Self-XSS → ATO Escalation via Cross-Origin State Smuggling
slug: self-xss-ato-escalation
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/server-side, technique/xss, technique/ato, technique/csrf]
inbound: []
---

# Self-XSS → ATO Escalation via Cross-Origin State Smuggling

## Pattern

Self-XSS (where the only way to trigger XSS is if the victim pastes attacker
payload into their own browser console or a form that only affects their own
session) is classically dismissed as unexploitable because the attacker cannot
trigger it on behalf of the victim. However, it becomes exploitable when
combined with any mechanism that allows the attacker to control what appears
in the victim's session-specific storage or UI without direct cookie access.

The escalation technique: if the attacker can log the victim into the attacker's
own account (via CSRF on a login endpoint), the self-XSS payload stored in
the attacker's profile is now rendered in the victim's browser session. The
XSS then runs in the victim's browser context but with the attacker's account
— unless the victim had previously logged in and the XSS can exfiltrate session
state, or unless the flow is: log victim out → log victim into attacker account
→ XSS fires → attacker's JS exfiltrates victim's CSRF token or forces a new
login OAuth flow.

Matan Berson's approach (16-year-old, AWC winner): self-XSS stored in profile +
CSRF on login endpoint → victim is logged in as attacker → XSS in victim's
browser → uses victim's browser session context to make authenticated API calls
as the attacker, escalating to account takeover by changing the attacker account's
email/password with victim's browser doing the requests.

## Preconditions

- Self-XSS exists in user-controlled content rendered in the authenticated session.
- Login CSRF is possible (no CSRF token on login form, or SameSite bypass).
- The XSS can interact with session-scoped resources (cookies, tokens, OAuth flows).

## Detection

- Find self-XSS: profile fields, custom messages, stored templates that reflect
  unsanitized HTML.
- Test login CSRF: `POST /login` without CSRF token from a cross-origin form.
- If both exist: the chain may be viable.

## Triggering

1. Store XSS payload in attacker's own profile (self-XSS).
2. Trick victim into visiting attacker-controlled page that:
   a. Issues CSRF login request with attacker credentials.
   b. Victim is now browsing as attacker.
   c. Navigate victim to the profile page where the self-XSS renders.
   d. XSS executes — victim's browser now runs attacker's JS in the application's origin.
3. XSS exfiltrates victim's stored cookies (if HttpOnly is absent) or forces
   OAuth flow to capture victim's tokens.

## Seen in the wild

- 2020–2022 — Multiple programs. Matan Berson's specialization: found and chained
  self-XSS + login CSRF at numerous programs, earning over $150,000 through AWC
  and HackerOne. His approach prioritized self-XSS as an entry point rather than
  dismissing them. Started at age 16. BBRE episode covered his methodology.
  [BBRE](https://www.youtube.com/watch?v=_VGEtJSRkjg)

## References

- See also: [../csrf/_index.md](../csrf/_index.md)
- See also: [../oauth/_index.md](../oauth/_index.md)
- "Login CSRF" — classic OWASP taxonomy entry
