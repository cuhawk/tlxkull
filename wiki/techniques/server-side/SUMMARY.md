---
title: Server-Side — summary
slug: server-side-summary
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/server-side, summary, index]
inbound: []
---

# Server-Side — summary

## What this class is

"Server-side" is an umbrella for injection vulnerabilities that execute on the server rather than the client: SSRF (server fetches attacker-controlled URLs), SSTI (template engines evaluate attacker input as code), SQLi (database queries incorporate unsanitized input), command injection, XXE (XML external entity file/SSRF), and HTTP request smuggling (desync between front-end and back-end parsing). These have the highest severity potential — SSRF often yields cloud credential theft (IMDS), SSTI yields RCE, SQLi yields data exfiltration or authentication bypass.

## When to suspect

- **SSRF**: parameters named `url`, `webhook`, `callback`, `dest`, `target`, `fetch`, `proxy`, `redirect`; PDF/image rendering endpoints; integrations that "preview" external URLs; cloud environments (IMDS at 169.254.169.254 / 100.64.0.1)
- **SSTI**: template-like parameter values (`{{7*7}}`, `${7*7}`, `<%= 7*7 %>`); user-controlled subject lines, email templates, report names; framework error pages leaking template engine name
- **SQLi**: `id=`, `user=`, `filter=`, `sort=`, `order=` parameters; error messages containing SQL keywords; boolean-based response differences on `'` vs `''`; `js_analyzer` source flowing to fetch/XHR that returns different data on input mutations
- **Command injection**: `ping`, `host`, `nslookup`, `convert`, `ffmpeg` wrapper endpoints; file name parameters; `exec`, `system`, `popen` in server error traces
- **XXE**: any endpoint consuming XML or multipart with XML parts; DOCX/XLSX/SVG upload; SAML assertion endpoints
- **Request smuggling**: HTTP/1.1 → HTTP/2 proxied apps; mismatched Content-Length vs Transfer-Encoding headers; front-end load balancers (nginx, HAProxy, CDN)

## External references

| Topic | PayloadsAllTheThings path | HackTricks path |
|---|---|---|
| SSRF payloads + cloud IMDS | `../../_external/payloads-all-the-things/Server Side Request Forgery/` | `../../_external/hacktricks/src/pentesting-web/ssrf-server-side-request-forgery/` |
| SSRF cloud-specific | `../../_external/payloads-all-the-things/Server Side Request Forgery/SSRF-Cloud-Instances.md` | `../../_external/hacktricks/src/pentesting-web/ssrf-server-side-request-forgery/cloud-ssrf.md` |
| SSTI payloads (all engines) | `../../_external/payloads-all-the-things/Server Side Template Injection/` | — |
| SQL injection | `../../_external/payloads-all-the-things/SQL Injection/` | — |
| Command injection | `../../_external/payloads-all-the-things/Command Injection/` | `../../_external/hacktricks/src/pentesting-web/command-injection.md` |
| XXE | `../../_external/payloads-all-the-things/XXE Injection/` | — |
| HTTP request smuggling | `../../_external/payloads-all-the-things/Request Smuggling/` | `../../_external/hacktricks/src/pentesting-web/http-request-smuggling/` |
| File upload (server-side RCE vector) | `../../_external/payloads-all-the-things/Upload Insecure Files/` | `../../_external/hacktricks/src/pentesting-web/file-upload/` |

## Related local pages

- [Prototype Pollution SUMMARY](../prototype-pollution/SUMMARY.md) — server-side PP in Node.js can chain to RCE via gadgets
- [Race Conditions SUMMARY](../race-conditions/SUMMARY.md) — SSRF + race can exfiltrate IMDS tokens before rotation
- [AMPScript Template Injection](ampscript-template-injection.md) — SFDC Marketing Cloud SSTI with double-evaluation + `TreatAsContent` chain
- [CBC IV Recovery via 8-Byte Null Block](cbc-iv-recovery-null-block.md) — IV-recovery primitive against unauthenticated CBC
- [cPanel CRLF Session-File Injection](cpanel-crlf-session-injection.md) — \r\n injection into on-disk session record → auth bypass

## Technique pages

- [ORM / query-builder SQL injection](orm-sqli.md) — Django Q objects `_connector`, Nextcloud column-type, FilteredRelation annotation injection

## Sub-patterns to expand

- [ ] `ssrf-cloud-imds.md` — SSRF to AWS/GCP/Azure IMDS credential theft
- [ ] `ssrf-gopher.md` — gopher:// SSRF for SMTP/Redis/internal protocol access
- [ ] `ssti-jinja2.md` — Jinja2 SSTI to RCE
- [ ] `ssti-twig.md` — Twig SSTI
- [ ] `ssti-freemarker.md` — Freemarker SSTI
- [ ] `sqli-boolean-blind.md` — boolean-based blind SQLi methodology
- [ ] `sqli-error-based.md` — error-based extraction
- [ ] `cmd-injection-blind.md` — blind OS command injection via OOB
- [ ] `xxe-oob.md` — out-of-band XXE via DNS/HTTP
- [ ] `smuggling-cl-te.md` — CL.TE request smuggling
- [ ] `smuggling-te-cl.md` — TE.CL request smuggling
