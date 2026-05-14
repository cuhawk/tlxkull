---
title: Blind SSRF → full SSRF via redirect-count + status-code leak
slug: blind-ssrf-redirect-count-status-leak
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/ssrf]
inbound: []
---

# Blind SSRF → full SSRF via redirect-count + status-code leak

Asset­Note (Shubs et al.) research bringing impact to traditionally
unexploitable blind SSRFs.

## Pattern
Backend uses libcurl (or similar) to fetch the user-supplied URL with
`maxredirs` (often 5). The application layer wraps libcurl with its own
error handling. Two parsers, two error states:

1. **0 ≤ redirects ≤ N**: libcurl follows, application parses response.
   If application expects JSON and the final response isn't JSON, you
   leak an *invalid-JSON* error.
2. **redirects > N**: libcurl errors with `TOO_MANY_REDIRECTS`, the
   application falls into a different error branch that — for **HTTP 500**
   responses — echoes the full upstream response back to the attacker.

The asymmetry between libcurl-handled errors and application-handled
errors is the leak primitive. AssetNote landed it in multiple production
apps.

## Preconditions
- Server-side fetch of attacker URL with libcurl-style `maxredirs`.
- Application layer treats redirect-exhaustion differently than per-hop
  status (i.e. has its own try/except wrapping `curl_exec`).
- Upstream returns HTTP 500 (or another status the application happens to
  forward verbatim).

## Detection
1. Submit attacker URL with **1 redirect** to a non-JSON response → look
   for `invalid JSON` error.
2. Submit attacker URL with **30 redirects** → look for `network error` /
   verbose response.
3. Iterate response status codes (301, 302, 303, 305, 307, 308, 200, 500).
   AssetNote saw the response accumulate for status ≥ 305 in one case
   ("pipelined" responses).
4. If 500 leaks the body → write the chain to point at an internal
   endpoint and return 500 with the desired payload.

## Triggering
Attacker redirector pseudo-code:
```python
@app.route("/chain")
def chain():
    n = int(request.args.get("n", 0))
    if n < 30:
        return Response(status=301, headers={"Location": f"/chain?n={n+1}"})
    # Final hop: 500 with target payload
    return Response("INTERNAL ENDPOINT BODY", status=500)
```

For internal-IP reach the chain into `http://169.254.169.254/...`,
`http://localhost:8080/...`, `http://jenkins.internal/`, etc.

## Limitations
- 500-status requirement caps the impact — IMDS (200), file:// (200),
  most internal endpoints return 200 not 500. JG/Joseph predict an
  asset-note-style "blind-SSRF escalation suite" tool with permutations
  across redirect-counts, status-codes, and known internal hostnames.

## Seen in the wild
- {date: 2025-06-26, source: CT Ep 128} — multiple AssetNote engagements.

## References
- AssetNote / Searchlight Cyber blog — Blind SSRF chains
- Critical Thinking Podcast Ep 128
- Related: [[secondary-context-path-traversal]], [[multi-a-dns-rebind]]
