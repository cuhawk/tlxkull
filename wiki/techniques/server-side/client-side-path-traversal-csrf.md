---
title: Client-Side Path Traversal (CSPT) — CSRF via URL Traversal
slug: client-side-path-traversal-csrf
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/csrf, technique/path-traversal, technique/server-side, technique/gitlab]
inbound: []
---

# Client-Side Path Traversal (CSPT) — CSRF via URL Traversal

## Pattern

Client-Side Path Traversal (CSPT) occurs when a client-side action (a button
click, UI element) constructs an API request URL from data that includes
`../` sequences. Unlike server-side path traversal (which reads files), CSPT
redirects API requests to unintended endpoints on the same origin, enabling
CSRF-like privilege escalation without needing to forge cross-origin requests.

The GitLab/Sentry case: GitLab's Sentry integration allowed a self-hosted Sentry
server to return errors whose IDs contained `../../admin/make-admin`. When an
elevated GitLab user clicked the "Resolve" button on this error in the GitLab
UI, the client constructed the API URL as:
`PUT /api/v4/sentry_issues/../../admin/make-admin` → normalized to
`PUT /api/v4/admin/make-admin`. The CSRF protection header was present, but
since the request originated from the victim's own browser session on the GitLab
origin, it passed all checks. The attacker controlled the URL path but not the
body — however, URL query parameters could carry payload.

## Preconditions

- Application constructs an API request URL from data that may include
  `../` sequences (API response bodies, object IDs, third-party integrations).
- The victim (higher-privileged user) triggers the action (clicks a button).
- The target endpoint accepts parameters via URL query string (since body is not
  controllable in CSPT).
- Attacker controls a trusted-appearing data source (e.g., self-hosted Sentry,
  configured webhook endpoint, import data).

## Detection

- Identify UI actions that trigger API requests constructed from user/third-party
  controlled identifiers (not just static paths).
- Test: inject `../../arbitrary-path` into an ID field in an API response.
- Observe whether the resulting request hits the traversed URL.
- Add `#` (hash fragment) after the traversal to discard the rest of the appended URL.

## Triggering

1. Configure a self-hosted integration (Sentry, webhook, data source).
2. Return an object with an ID containing the traversal:
   `{"id": "../../admin/users/1?access_level=40"}`
3. Trick a higher-privileged user into clicking the action button on this
   object in the main application's UI.
4. Their browser sends: `PUT https://target.example/api/v4/admin/users/1?access_level=40`
   with their session cookies and CSRF headers.

Example traversal payload (URL-encoded as needed):
```
../../admin/members/1/access_level%3D50%23
```

## Bypasses

- `#` fragment: append `#` to ignore the rest of the URL the client appends.
- Double encoding `%2F..%2F` if the client URL-encodes the ID before joining.
- Varies by JavaScript framework — React, Vue may or may not normalize the URL.

## Seen in the wild

- 2022 — GitLab, significant bounty. Johan Carlsson (uaxcar) exploited CSPT
  via GitLab's Sentry error integration. Malicious Sentry error IDs with `../`
  sequences redirected the `PUT /sentry_issues/:id/resolve` action to
  arbitrary PUT routes across all of GitLab. Impact: self-escalation to admin.
  [BBRE](https://www.youtube.com/watch?v=z27bkSMARA8)

## References

- See also: [secondary-context-path-traversal](secondary-context-path-traversal.md)
- See also: [../csrf/_index.md](../csrf/_index.md)
- Rennie Pak — CSP bypass research
- Impact-chaining cookbook: [cspt-impact-gadgets](cspt-impact-gadgets.md)
- Mobile delivery variant: [cspt-mobile-deeplink-stored-params](../mobile/cspt-mobile-deeplink-stored-params.md)
