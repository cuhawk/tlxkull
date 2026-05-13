---
title: Nginx alias off-by-slash traversal
slug: nginx-alias-traversal
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/path-traversal]
inbound: []
---

# Nginx alias traversal

## Pattern
Vulnerable when an nginx `location` directive has NO trailing slash but
its `alias` directive ends WITH a slash. Traversal limited to one
directory up.

```nginx
location /files {          # no trailing slash
    alias /var/www/files/; # trailing slash
}
```

Request `/files../config` resolves to `/var/www/files/../config` →
`/var/www/config`.

Orange Tsai BlackHat 2018.

## Preconditions
- Nginx with the off-by-slash `location`/`alias` mismatch.
- Traversable file present one directory up.

## Detection
- GitHub code-search regex over open-source nginx configs.
- Probe `/path../<file>` style on every observed `/files`, `/static`,
  `/assets`, `/uploads` etc.

## Triggering
```
GET /files../config HTTP/1.1
GET /static../etc/passwd HTTP/1.1
```

## Seen in the wild
- Bitwarden self-hosted — DB exfil (Hawkeye Labs).
- Google — $500 reward for similar.
- Critical Thinking Podcast Ep 26.

## References
- Orange Tsai BlackHat 2018 nginx off-by-slash research
- Hawkeye Labs Bitwarden + Google writeup
- Critical Thinking Podcast Ep 26
