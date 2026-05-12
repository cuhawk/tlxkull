---
title: MCP Client Identity Metadata Document (CIMD) SSRF
slug: mcp-cimd-ssrf
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/oauth, technique/ssrf, technique/mcp]
inbound: []
---

# MCP Client Identity Metadata Document (CIMD) SSRF

## Pattern

The MCP Authorization specification (built on top of OAuth 2.1 + RFC 8414 +
RFC 7591) introduces a new client registration flow. Instead of the traditional
dynamic client registration POST, the AI agent submits a **client manifest
URI** — a URL pointing to a `client.json` document hosted by the agent. The
authorization server (or a separate metadata verification service) **fetches
this URI** to read and validate the document contents.

This fetch is an SSRF primitive: an attacker-controlled URL is fetched by the
server. Two fetch points exist in the same flow:

1. The top-level `client_manifest_uri` itself.
2. **Nested URIs inside the `client.json`**: `logo_uri` and `jwks_uri`.

Additional attack vectors once SSRF is achieved:
- **Weak domain validation on `redirect_uri`**: The authorization server must
  enforce that all `redirect_uri` values in the document belong to the same
  domain as the manifest. Loose checks can allow leaking codes to
  `attacker.com`.
- **Cache deception**: Because CIMD is a static document, authorization
  servers may cache validation results. Classic cache-key manipulation attacks
  apply.
- **Response-code handling quirks**: The fetching user agent may handle 30x
  redirects, specific HTTP codes, or even JavaScript (if headless browser)
  differently — standard SSRF escalation vectors.

## Preconditions

- Target implements MCP authorization (agent-to-server OAuth flow) using the
  CIMD registration path.
- The authorization server performs an outbound HTTP request to the
  `client_manifest_uri` (or the nested `logo_uri` / `jwks_uri`).
- Server does not strictly pin or whitelist allowed URI schemes/hosts.

## Detection

- Look for a `client_manifest_uri` or `client_json_uri` parameter in OAuth
  `/register` or `/authorize` endpoints.
- Check `.well-known/oauth-authorization-server` or MCP metadata endpoints for
  CIMD support indicators (`supported_registration_types: ["cimd"]`).
- Observe network traffic during an MCP OAuth flow — does the server request
  your hosted document? Confirm via a Caido-captured collaborator URL.

```json
// Minimal attacker-controlled client.json
{
  "client_name": "test",
  "redirect_uris": ["https://attacker.com/callback"],
  "logo_uri": "https://169.254.169.254/latest/meta-data/",
  "jwks_uri": "https://internal-host/private"
}
```

## Triggering

1. Host a `client.json` at an attacker-controlled URL (or Caido collaborator).
2. Submit an OAuth registration / authorization request with
   `client_manifest_uri` pointing to it.
3. Observe whether the server fetches your URL (Caido request log).
4. Escalate: set `logo_uri` or `jwks_uri` to internal metadata endpoints
   (`http://169.254.169.254/latest/meta-data/`,
   `http://localhost:8080/admin`, etc.).
5. Also test redirect-URI domain check: set `redirect_uri` to
   `https://victim.com@attacker.com/callback` or a different domain entirely.

## Bypasses

- **Nested URI bypass**: If the top-level manifest URL is validated by scheme,
  embed the SSRF payload in the nested `logo_uri` or `jwks_uri`.
- **Redirect chain**: Return a 301/302 to an internal host from the manifest
  URL — check if the fetcher follows redirects.
- **Cache poisoning**: If validation results are cached by manifest URL, poison
  the cache with a valid-looking document and then swap the real document to a
  malicious one before cache expires.
- **30x response-code differentiation**: Some fetchers handle 301 vs 307 vs
  308 differently; 307 preserves the method and body, which may expose tokens.

## Seen-in-the-wild

| date | target | notes |
|---|---|---|
| 2026 | (undisclosed LHE target) | Brandon (CT Ep. 169) found SSRF-adjacent behaviors in MCP CIMD flow during a live hacking event; exact target undisclosed. Auth0 token vault already uses this architecture for AI agent integrations. |

## References

- Episode source: `../../sources/podcasts/ct/20260409_mo9LoNHmDhI_OAuth_changes_MCP_Authorization_PKCE_Downgrades_Ep._169.en.vtt`
- Podcast: "OAuth changes, MCP Authorization, & PKCE Downgrades (Ep. 169)" — <https://www.youtube.com/watch?v=mo9LoNHmDhI>
- MCP Authorization spec: <https://spec.modelcontextprotocol.io/specification/basic/authorization/>
- RFC 8414 — OAuth 2.0 Authorization Server Metadata: <https://datatracker.ietf.org/doc/html/rfc8414>
- RFC 7591 — Dynamic Client Registration: <https://datatracker.ietf.org/doc/html/rfc7591>
- [PKCE Downgrade](pkce-downgrade.md)
- [OAuth SUMMARY](SUMMARY.md)
