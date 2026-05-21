---
title: OAuth Authorization Code Theft via CSRF Chain + Captcha Lockout
slug: oauth-csrf-captcha-ato-chain
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/oauth, technique/csrf, technique/ato, technique/facebook]
inbound: []
---

# OAuth Authorization Code Theft via CSRF Chain + Captcha Lockout

## Pattern

OAuth authorization codes are single-use and must be consumed by the correct
party before an attacker can use them. Standard CSRF against the OAuth callback
(stealing the code from the URL) is prevented by the code being used
immediately when the victim lands on the callback page.

This advanced chain (Youssef Sammouda, Facebook $45k) works around this by:

1. **Preventing code consumption**: Force the victim's browser into a captcha
   lockout state so that when they complete the OAuth flow, the callback page
   shows a captcha instead of consuming the code. The code now sits idle in
   the URL.
2. **Forcing captcha state by login CSRF**: The attacker cannot put the
   victim's account into captcha — but they can log the victim into the
   attacker's own account (which is already in captcha state). This requires:
   - CSRF on logout endpoint (log victim out of their account).
   - CSRF on login endpoint (log victim into attacker's account).
3. **Code leakage**: The captcha window is hosted on a sandbox domain but also
   available on a developer testing subdomain. Attackers can upload HTML to
   this sandbox domain. The exploit page (hosted on sandbox domain) and the
   captcha iframe (also on sandbox domain) are same-origin, so the exploit
   can read the captcha iframe's URL — which contains the OAuth code.
4. **Code exchange**: Attacker uses the stolen code to authenticate as the
   victim.

## Preconditions

- Target uses OAuth with authorization code flow.
- Login and logout endpoints are CSRF-vulnerable (no token required).
- Captcha/lockout mechanism is triggered by repeated requests (controllable by attacker).
- Captcha is served from a sandbox domain where attacker can host content.
- Sandbox-hosted iframe is same-origin as the captcha, enabling URL access.

## Detection

This is a complex chained attack. Individual components to test:
- Test login endpoint for CSRF (no CSRF token, no SameSite=Strict).
- Test logout endpoint for CSRF.
- Identify any sandbox/testing domain that hosts the captcha.
- Check if you can upload/host HTML on the sandbox domain.
- Check whether the captcha iframe's URL contains the OAuth code.

## Chain Summary

```
Attacker page (on sandbox domain)
  → CSRF logout victim from their Facebook
  → CSRF login victim into attacker's captcha-locked account  
  → Redirect victim to /connect/gmail OAuth flow
  → Victim completes Google auth, redirected back to Facebook
  → Facebook shows captcha (because account is in lockout) — code in URL
  → Captcha iframe opens (also on sandbox domain = same-origin as attacker page)
  → Attacker page reads iframe.location.href → extracts OAuth code
  → Exchanges code for victim's session token
```

## Seen in the wild

- 2021 — Facebook/Meta, $44,625. Youssef Sammouda. Full ATO on any Facebook
  account that uses Gmail for login. The chain required: 2x login/logout CSRF
  + sandbox domain HTML upload + captcha iframe same-origin leak.
  [BBRE](https://www.youtube.com/watch?v=pk7oYuz4x0Q)

## References

- Youssef Sammouda's blog post on the Facebook chain
- See also: [../oauth/_index.md](../oauth/_index.md)
- See also: [../csrf/_index.md](../csrf/_index.md)
- Related: [postmessage-ato](../postmessage/_index.md) — Facebook postMessage ATO
