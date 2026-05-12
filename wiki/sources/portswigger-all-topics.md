---
title: PortSwigger Web Security Academy — all topics index
slug: portswigger-all-topics
url: https://portswigger.net/web-security/all-topics
fetched_utc: 2026-05-12T00:00:00Z
kind: article
extracted: false
extract_model: null
tags: [source, ref/portswigger, index]
inbound: []
---

# PortSwigger Web Security Academy — all topics index

Index page only. Use this as a hop-table; lazy-fetch per-topic page on
demand into `wiki/sources/portswigger-<topic-slug>.md`.

## Server-side

- [SQL injection](https://portswigger.net/web-security/sql-injection)
- [Authentication](https://portswigger.net/web-security/authentication)
- [Path traversal](https://portswigger.net/web-security/file-path-traversal)
- [Command injection](https://portswigger.net/web-security/os-command-injection)
- [Business logic vulnerabilities](https://portswigger.net/web-security/logic-flaws)
- [Information disclosure](https://portswigger.net/web-security/information-disclosure)
- [Access control](https://portswigger.net/web-security/access-control)
- [File upload vulnerabilities](https://portswigger.net/web-security/file-upload)
- [Race conditions](https://portswigger.net/web-security/race-conditions)
- [Server-side request forgery (SSRF)](https://portswigger.net/web-security/ssrf)
- [XXE injection](https://portswigger.net/web-security/xxe)
- [NoSQL injection](https://portswigger.net/web-security/nosql-injection)
- [API testing](https://portswigger.net/web-security/api-testing)
- [Web cache deception](https://portswigger.net/web-security/web-cache-deception)

## Client-side

- [Cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting)
- [Cross-site request forgery (CSRF)](https://portswigger.net/web-security/csrf)
- [Cross-origin resource sharing (CORS)](https://portswigger.net/web-security/cors)
- [Clickjacking](https://portswigger.net/web-security/clickjacking)
- [DOM-based vulnerabilities](https://portswigger.net/web-security/dom-based)
- [WebSockets](https://portswigger.net/web-security/websockets)

## Advanced

- [Insecure deserialization](https://portswigger.net/web-security/deserialization)
- [Web LLM attacks](https://portswigger.net/web-security/llm-attacks)
- [GraphQL API vulnerabilities](https://portswigger.net/web-security/graphql)
- [Server-side template injection](https://portswigger.net/web-security/server-side-template-injection)
- [Web cache poisoning](https://portswigger.net/web-security/web-cache-poisoning)
- [HTTP Host header attacks](https://portswigger.net/web-security/host-header)
- [HTTP request smuggling](https://portswigger.net/web-security/request-smuggling)
- [OAuth authentication](https://portswigger.net/web-security/oauth)
- [JWT attacks](https://portswigger.net/web-security/jwt)
- [Prototype pollution](https://portswigger.net/web-security/prototype-pollution)
- [Essential skills](https://portswigger.net/web-security/essential-skills)

## Lazy-fetch convention

When a target session needs a topic page, run:

```
curl -sSL "<url>" > wiki/sources/portswigger-<slug>.html
```

Then create `wiki/sources/portswigger-<slug>.md` with frontmatter
mirroring `portswigger-xss-cheatsheet.md`.
