# postMessage → innerHTML XSS

## Pattern
Attacker page A opens a window/iframe of victim page V and posts a
message. V's `message` handler reads `event.data` and writes it to
`innerHTML` (or `outerHTML` / `insertAdjacentHTML`).

## Why exploit works
- No `event.origin` check on the receiver — any origin can post.
- Loose check (`startsWith`, `endsWith`, `includes`) — bypassable via
  subdomain or suffix manipulation.
- Sanitizer absent OR misconfigured (`ALLOWED_ATTR` includes `on*`,
  `ALLOW_UNKNOWN_PROTOCOLS=true`).

## Confirmation
Open `https://attacker.example/?target=https://victim.example/...`
which embeds the victim and posts:

```js
victim.contentWindow.postMessage({ html: "<img src=x onerror=alert(1)>" }, "*");
```

## References
- Doyensec, Securitum and Snyk research from 2018-2024.
- OWASP ASVS V14.4.6 (Cross-origin messaging).
