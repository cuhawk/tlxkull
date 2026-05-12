---
title: PortSwigger — Access control vulnerabilities
slug: portswigger-access-control
url: https://portswigger.net/web-security/access-control
fetched_utc: 2026-05-12T00:00:00Z
kind: article
extracted: true
extract_model: sonnet
tags: [source, technique/idor, ref/portswigger]
inbound: []
---

# PortSwigger — Access control vulnerabilities

## TL;DR

- Access control vulnerabilities arise when authorization constraints are inadequately enforced, enabling vertical (privilege escalation) or horizontal (cross-user) access.
- Unprotected admin URLs, parameter tampering (`?admin=true`, `?role=1`), and header overrides (`X-Original-URL`) are common vertical escalation vectors.
- Horizontal privilege escalation typically involves IDOR: modifying an object ID in a parameter to access another user's resource.
- Multi-step process bypasses skip early controlled steps to reach unprotected final stages; Referer-based access control is trivially bypassable.
- IDOR is explicitly covered as a sub-type, bridging access control and object-level authorization.

## Sub-sections

- What is access control?
  - Vertical access controls
  - Horizontal access controls
  - Context-dependent access controls
- Examples of broken access controls
  - Vertical privilege escalation
  - Horizontal privilege escalation
  - Horizontal to vertical privilege escalation
  - Insecure direct object references
  - Access control vulnerabilities in multi-step processes
  - Referer-based access control
  - Location-based access control
- How to prevent access control vulnerabilities
