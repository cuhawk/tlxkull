---
title: Ep 44 — URL Parsing Auth Bypass Magic
slug: 20231109-url-parsing-auth-bypass-magic-ep-44
url: https://www.youtube.com/watch?v=bLeGnHDEj94
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, url-parsing, open-redirect, oauth, facebook, server-side, file-uri, fragment, path-parameter]
inbound: []
---

# Ep 44 — URL Parsing Auth Bypass Magic

- Date: 2023-11-09
- video_id: bLeGnHDEj94
- Speakers: Justin Gardner (JG), Joel Margolis (JM)

## Summary

End-to-end walkthrough of every part of a URL with the attack vectors
that attach to each. Salt Labs' Facebook-login OAuth-app cross-site
ATO: the implicit-flow access token returned by Facebook is for the
*originating app*, not necessarily *this* app — the relying party must
call Facebook's debug-token endpoint to confirm `app_id` matches, but
many don't. Pop any small Facebook app to mint a token; submit to
Grammarly / similar to log in as that user's identity. Canva's
"When URL Parsers Disagree" writeup on `file://` URIs: two parsers
disagree on whether `?` is path-truncation; one consumed the rest of
the path through traversal sequences while the other respected the
question mark, letting `/svg/./?/../etc/passwd` reach the file system.
The 9-part URL anatomy walkthrough — scheme, user, password, host,
port, path, query, fragment, path-parameter — with weaponization tips
for each: `user:pass@` smuggle attacks for open-redirect bypass
(Chrome strips the visible bar but `document.URL` retains it; Firefox
still works under conditions), backslash escape `user\:any@victim`
where naïve parsers treat backslash as different boundary;
illegal-character port injection; fragment as "URL comment" that
truncates SSRI-appended suffixes; path-parameter `;` semicolon abuse
(Orange Tsai's foundational `..;` work).

## Techniques extracted

- [[../../techniques/oauth/facebook-implicit-flow-app-confusion]] — Facebook implicit-flow access token isn't bound to the relying party; without `debug_token` `app_id` validation the relying party authenticates the bearer as Facebook's `me`, regardless of which Facebook app minted the token.
- [[../../techniques/server-side/file-uri-question-mark-parser-skew]] — `file://` URI parsers disagree on whether `?` terminates the path; chained with path-traversal to escape svg/jpeg rendering directories on the disk side.
- [[../../techniques/dom-xss/url-anatomy-bypass-cheatsheet]] — 9-part URL anatomy with the attack vector at each position: scheme, `user:pass@` userinfo, backslash-in-username escapes, illegal-character port, fragment-as-comment truncation, path-parameter `;` Orange-Tsai pattern.

## Tools mentioned

(none with novel quirks)

## Quotes

> "It's like a comment for the URL — the fragment makes everything after it just not do anything, kind of like SQL injection."

> "Allegedly the creator did this on purpose — most people don't know about the userinfo segment, but it's the most useful piece for bypassing open-redirect filters."

> "When URL parsers disagree, that's where the bugs live."

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
