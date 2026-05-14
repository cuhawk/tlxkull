---
title: Unicode surrogate normalization to Solr/Elasticsearch wildcard
slug: unicode-surrogate-wildcard
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/unicode, technique/sql-like-injection]
inbound: []
---

# Unicode surrogate → `?` → search-engine wildcard

CT Research Lab micro-blog (Ep 149).

## Pattern
When a backend pipes a string through Unicode normalization (UTF-8 →
UTF-16 → ISO-8859-1 / Windows-1252 fallback, or a defensive sanitizer
that strips "invalid" codepoints), **unpaired surrogates** like
U+DC2A get replaced with a literal `?` (Unicode REPLACEMENT char or
ASCII `?`). When the resulting `?` lands in a Solr / Elasticsearch
query string, it is interpreted as the single-character wildcard —
attacker now controls the query pattern from a field that was
supposed to be a literal string.

This is a Unicode-normalization SQLi cousin specific to Lucene-syntax
backends.

## Preconditions
- Server-side pipeline that normalizes attacker input through layers
  that turn unpaired surrogates into `?`.
- Final consumer is a Lucene-syntax backend (Solr, Elasticsearch,
  OpenSearch) using `query_string` / `simple_query_string` / classic
  Lucene parsers.

## Detection
- Inject codepoint U+DC2A (and other unpaired surrogates) into every
  string field reaching search. Observe response.
- Look for queries that return *more* results than the literal input
  should — telltale wildcard explosion.

## Triggering
URL-encoded:
```
GET /search?q=%ED%B0%AA HTTP/1.1
```
(`%ED%B0%AA` is UTF-8 encoding of U+DC2A.)

Goes through normalization → becomes `?` → Lucene parser sees
`q=?` → wildcard match → full result-set dump.

## Bypasses / hardening
- Reject unpaired surrogates at the input boundary rather than
  silently substituting.
- Pass the original bytes to Lucene as a phrase query (`"..."`),
  not as a query-string parse.

## Seen in the wild
- {date: 2025, source: CT Ep 149} — CT Research Lab micro-blog.

## References
- Critical Thinking Podcast Ep 149
- Lucene query-string syntax (`?` wildcard semantics)
