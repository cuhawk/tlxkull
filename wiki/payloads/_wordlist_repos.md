---
title: External wordlist + param-list repos by category
slug: external-wordlist-repos
created_utc: 2026-05-18T18:00:00Z
updated_utc: 2026-05-18T18:00:00Z
tags: [payload-corpus, external-repo, recon, param-discovery]
inbound: []
---

# External wordlist + payload repos — curated index

**Purpose:** inventory of high-signal GitHub repos for param/wordlist
sources. Kept for reference, NOT auto-integrated. Reach for these
when target-static + target-live + cross-target dictionaries don't
turn up the right param name.

**Status:** none of the below are vendored / cloned into TLX. Add
them under `wiki/_external/<repo>/` only if a specific engagement
needs offline access.

---

## Tier 0 — already vendored (do not re-clone)

| Repo | Path | Notes |
|------|------|-------|
| `swisskyrepo/PayloadsAllTheThings` | `wiki/_external/payloads-all-the-things/` | Comprehensive. XSS / SQLi / SSRF / IDOR / open-redirect — categorized payloads + bypass tips. |
| `carlospolop/hacktricks` | `wiki/_external/hacktricks/` | Methodology + bypass tricks. Pentesting playbook. |

---

## Param-discovery tools (active scanners)

| Repo | Maintainer | Use |
|------|------------|-----|
| [`s0md3v/Arjun`](https://github.com/s0md3v/Arjun) | s0md3v | HTTP parameter discovery — state-of-the-art active param fuzz tool. Heuristic-driven, picks names from internal dict + delivers diff-based hit detection. |
| [`Sh1Yo/x8`](https://github.com/Sh1Yo/x8) | Sh1Yo | Hidden parameter discovery — Rust-based, fast, parallel. Used by elite hunters. |
| [`PortSwigger/param-miner`](https://github.com/PortSwigger/param-miner) | PortSwigger | Burp Suite extension. Header + URL param mining. Hash-based diff detection. |
| [`lc/gau`](https://github.com/lc/gau) | lc | GetAllURLs — fetches URLs from Wayback, CommonCrawl, OTX, URLScan. Source for live param observation. |
| [`tomnomnom/waybackurls`](https://github.com/tomnomnom/waybackurls) | tomnomnom | Wayback URL fetcher. Pipeline-friendly. |
| [`projectdiscovery/katana`](https://github.com/projectdiscovery/katana) | ProjectDiscovery | JS-aware crawler — extracts endpoints + params from rendered pages. |
| [`BishopFox/jsluice`](https://github.com/BishopFox/jsluice) | BishopFox | JS-aware analysis: extracts URLs, params, secrets from minified JS. CT podcast favorite. |
| [`tomnomnom/qsreplace`](https://github.com/tomnomnom/qsreplace) | tomnomnom | Replace query string values for batch fuzzing. |
| [`tomnomnom/unfurl`](https://github.com/tomnomnom/unfurl) | tomnomnom | URL parser/extractor — pipe with qsreplace + gau. |

---

## Comprehensive wordlist collections

| Repo | Maintainer | Notes |
|------|------------|-------|
| [`danielmiessler/SecLists`](https://github.com/danielmiessler/SecLists) | Daniel Miessler | Swiss army knife. `Discovery/Web-Content/` + `Fuzzing/` + `Passwords/`. |
| [`assetnote/wordlists`](https://github.com/assetnote/wordlists) | Assetnote | High-quality categorized: params, snipers, manual, kiterunner-routes. Hosted at wordlists.assetnote.io. |
| [`assetnote/commonspeak2-wordlists`](https://github.com/assetnote/commonspeak2-wordlists) | Assetnote | Generated from BigQuery (Stack Overflow + GitHub data). Reflects current dev usage. |
| [`six2dez/OneListForAll`](https://github.com/six2dez/OneListForAll) | six2dez | Combined wordlists organized by purpose. Used in reconftw. |
| [`fuzzdb-project/fuzzdb`](https://github.com/fuzzdb-project/fuzzdb) | community | Historic, very comprehensive. Includes attack vectors per vuln class. |
| [`Bo0oM/fuzz.txt`](https://github.com/Bo0oM/fuzz.txt) | Bo0oM | Single high-quality fuzz wordlist. Manual curation. |
| [`xmendez/wfuzz`](https://github.com/xmendez/wfuzz) | xmendez | Comes with wordlists `wordlist/`. |
| [`1N3/IntruderPayloads`](https://github.com/1N3/IntruderPayloads) | 1N3 | Burp Intruder-formatted payload sets per vuln class. |

---

## XSS-specific payload + scanner repos

| Repo | Maintainer | Notes |
|------|------------|-------|
| [`payloadbox/xss-payload-list`](https://github.com/payloadbox/xss-payload-list) | payloadbox | Curated payload corpus. 4k+ entries. Includes filter bypass variants. |
| [`hahwul/dalfox`](https://github.com/hahwul/dalfox) | hahwul | Param-aware DOM + reflected XSS scanner. Pipeline-friendly. Strong reflection detection. |
| [`s0md3v/XSStrike`](https://github.com/s0md3v/XSStrike) | s0md3v | Smart XSS detection — fuzzy-context payload generation. |
| [`brutelogic/xss-payload-list`](https://github.com/brutelogic/) | brutelogic | Variant collection. Brute Logic is a respected XSS-focused researcher. |
| [`PortSwigger/web-security-academy-payloads`](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) | PortSwigger | XSS cheat sheet — gold-standard reflected/stored/DOM payload set. Web-hosted. |
| [`KathanP19/HowToHunt`](https://github.com/KathanP19/HowToHunt) | Kathan | Methodology — per-vuln-class hunting playbooks (XSS chapter has param lists). |

---

## SSRF-specific repos

| Repo | Maintainer | Notes |
|------|------------|-------|
| [`swisskyrepo/SSRFmap`](https://github.com/swisskyrepo/SSRFmap) | swisskyrepo | Automatic SSRF exploitation framework. |
| [`cujanovic/SSRF-Testing`](https://github.com/cujanovic/SSRF-Testing) | cujanovic | SSRF payloads + bypass tricks (DNS rebinding, IP encoding, gopher://, dict://). |
| [`tarunkant/Gopherus`](https://github.com/tarunkant/Gopherus) | tarunkant | Generates gopher:// payloads for SSRF-to-RCE on Redis / MySQL / FastCGI / SMTP. |
| [`lukasikic/awesome-ssrf`](https://github.com/lukasikic/awesome-ssrf) | lukasikic | Awesome list — papers, blogs, talks. |
| [`assetnote/blind-ssrf-chains`](https://github.com/assetnote/blind-ssrf-chains) | Assetnote | SSRF-to-RCE chain catalog. |
| Common SSRF param names | (see _ssrf_param_list below) | url, callback, target, dest, redirect, return, host, etc. |

**Common SSRF param names** (when sprayer needs to identify SSRF-vulnerable endpoints):
```
url, callback, next, redirect, redirect_uri, redirect_url, target,
dest, destination, return, return_to, returnTo, return_url,
returnURL, host, hostname, server, image_url, image, img, source,
src, ref, share, link, fetch, proxy, upload, file, path, page,
data, params, xml, location, validate, domain, feed, api, redir,
remote, navigation, open, view, show, val, validate, callback_url,
webhook, webhook_url, notification_url, oauth_callback
```

---

## IDOR / BAC-specific repos

IDOR is mostly behavior-driven (rotate IDs, swap auth contexts). Wordlists less useful than for SSRF. Useful repos:

| Repo | Notes |
|------|-------|
| [`Vulnerable-API-Project/VAmPI`](https://github.com/erev0s/VAmPI) | Vulnerable API for testing IDOR tools. |
| [`OWASP/API-Security`](https://github.com/OWASP/API-Security) | API top-10 reference. BOLA = IDOR. |
| [`Sjord/jwtcrack`](https://github.com/Sjord/jwtcrack) | JWT secret cracking — IDOR often uses JWT IDs. |
| Common IDOR param names | id, uid, uuid, user_id, account_id, team_id, org_id, organization_id, group_id, customer_id, profile_id, project_id, site_id, deploy_id, doc_id, file_id, image_id, post_id, comment_id, thread_id, conv_id, ticket_id |

---

## Open-redirect + URL-manipulation

| Repo | Notes |
|------|-------|
| [`assetnote/wordlists`](https://github.com/assetnote/wordlists) | `assetnote.io/url-manipulation` category. |
| [`Cyber-Guy1/Open-Redirect-Payloads`](https://github.com/Cyber-Guy1) | Open-redirect payload collection. |
| [`payloadbox/open-redirect-payload-list`](https://github.com/payloadbox/open-redirect-payload-list) | Payload variants. |
| Common open-redirect params | redirect, redirect_uri, url, return, return_to, returnTo, return_url, next, target, dest, destination, goto, link, continue, callback, page, view, location |

---

## Per-vuln-class param-name dictionaries (manual curation worth keeping local)

The aim: small high-precision lists per vuln class. Spray these
BEFORE seclists fallback.

```
# wiki/payloads/params_by_vuln_class.json (suggested future file)
{
  "ssrf": ["url", "callback", "redirect", "target", "dest", "host", ...],
  "open_redirect": ["redirect", "redirect_uri", "next", "return_to", ...],
  "idor_id": ["id", "uid", "user_id", "account_id", "team_id", ...],
  "xss_reflective": ["q", "query", "search", "msg", "error", "message", ...],
  "xss_stored": (n/a — stored XSS is field-based, not param-based),
  "lfi_rfi": ["file", "path", "page", "include", "template", "view"],
  "csrf_token": ["csrf", "csrf_token", "_token", "authenticity_token", ...]
}
```

---

## Methodology + hunter blogs

| Source | Why |
|--------|-----|
| `wiki/sources/podcasts/ct/` | Critical Thinking Podcast transcripts — Justin Gardner + Joel Margolis. Live param-mining war stories. |
| [`KathanP19/HowToHunt`](https://github.com/KathanP19/HowToHunt) | Per-vuln-class chapter style. |
| [`OWASP/wstg`](https://github.com/OWASP/wstg) | OWASP Web Security Testing Guide — methodology baseline. |
| [`harshad-shah/awesome-bug-bounty`](https://github.com/harshad-shah/awesome-bug-bounty) | Awesome list pointer. |
| [`assetnote/blog`](https://blog.assetnote.io/) | High-quality engineering writeups. |
| [`PortSwigger/research`](https://portswigger.net/research) | New techniques, often before they're known broadly. |

---

## Curation principle

Add to `wiki/_external/` ONLY when:
1. An engagement needs offline access (air-gapped or rate-limited
   research session), AND
2. The repo passes a quality bar — actively maintained, signal > noise.

Otherwise keep this index as the lookup. Pulling a 6k-line `common.txt`
into the repo adds noise to grep + git size.

---

## Related

- [[../techniques/recon/live-dom-instrumentation-patterns]] — when to use which wordlist tier
- [[../techniques/recon/scope-aware-chain-triage]] — scope before spray
- [[../techniques/recon/adjacent-function-gap]] — orthogonal static technique
- [`bin/extract_params.py`](../../bin/extract_params.py) — target-static + target-live extractor
- [`wiki/payloads/param-dictionary.json`](./param-dictionary.json) — cross-target aggregate
