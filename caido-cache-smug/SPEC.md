# caido-cache-smug — Design Spec

**Status:** draft v1
**Date:** 2026-05-20
**Owner:** soural1417@gmail.com
**Scope:** Standalone CLI tool. Not integrated into the TLX skill chain.

---

## 1. Purpose

Given a host that already has captured traffic inside a Caido project, sweep every unique in-scope endpoint for three vulnerability classes:

1. **Web cache poisoning** (integrity attack on shared cache)
2. **Web cache deception** (confidentiality attack via path/extension keying)
3. **HTML smuggling** (client-side payload delivery patterns embedded in responses)

Optional fourth class (`--aggressive-smuggling`):

4. **HTTP request smuggling** (CL/TE, TE.CL, TE.TE, H2.CL, H2.TE) with chained cache-poison delivery.

Optional fifth class (`--race`):

5. **Race conditions** (TOCTOU / state-collision via HTTP/2 single-packet attack or HTTP/1.1 last-byte sync, per James Kettle, "Smashing the state machine"). Detection-only by default (GET/HEAD parallel replay + response divergence). Mutating verbs gated behind `--race-allow-mutate` with explicit endpoint allowlist.

Output: machine-readable `findings.json` and human-readable `report.md` per run.

---

## 2. Non-goals

- Integration with the TLX skill chain or per-target workspace layout. Tool is standalone and operates on any Caido project, regardless of TLX status.
- Crawling. Tool assumes Caido already holds captured traffic for the host. No browser automation, no spider.
- Region/POP cache variance testing. Single-POP only.
- Connection-state smuggling (TLS resumption layer). Out of scope.
- LLM ASCII / Tag-Unicode smuggling. Not a web-app vector.
- Mutating verbs (POST/PUT/PATCH/DELETE) by default. GET/HEAD only unless the user adds an explicit aggressive flag in a future revision.

---

## 3. Form factor

CLI tool, TypeScript on Node 20+, using `@caido/sdk-client` for Caido GraphQL access via Personal Access Token (PAT).

Distributed via `npm pack` tarball; run locally via `npx caido-cache-smug` after `npm link`. Not published to public npm (avoids leaking technique inventory).

---

## 4. CLI surface

```
caido-cache-smug --host <hostname>
                 [--caido-url http://localhost:8080]
                 [--caido-token <PAT> | env CAIDO_API_TOKEN]
                 [--project <name>]
                 [--max-requests 500]
                 [--rps 5]
                 [--out ./out/<host>/<ts>/]
                 [--passive-only]
                 [--modules cache-poison,cache-deception,html-smuggling]
                 [--auth-cookie <name=value>]
                 [--aggressive-smuggling]
                 [--collaborator <fqdn>]
                 [--race]
                 [--race-concurrency 20]
                 [--race-allow-mutate]
                 [--race-endpoints <path>]
```

Behavior:

- `--host` is required. Matches Caido HTTPQL filter `req.host.cont:<host>`.
- `--project` defaults to the currently selected project in Caido. If none selected, error out.
- `--caido-token` falls back to `CAIDO_API_TOKEN` env. If neither, error out.
- `--rps` default 5. Token-bucket throttle applied to all outbound sends.
- `--passive-only` skips Module A and Module B sub-probes B1–B5 (all of which send requests); keeps Module C (response-body scan) and B6 (CSPT passive scan), and surfaces cache-header analysis from baselines.
- `--modules` default = `cache-poison,cache-deception,html-smuggling`. `smuggling` only included if `--aggressive-smuggling` also set.
- `--collaborator` enables out-of-band confirmation for smuggling probes (Module D). Without it, Module D marks primitives as `candidate` rather than `confirmed`.
- `--race` enables Module E. Detection mode probes GET/HEAD candidates only.
- `--race-concurrency` parallel-request count per probe (default 20, max 50). HTTP/2 single-packet attack uses this for stream count; HTTP/1.1 last-byte sync uses this for socket count.
- `--race-allow-mutate` opens POST/PUT/PATCH/DELETE replay. Requires `--race-endpoints` allowlist file (one `METHOD path` per line, blank lines and `#` comments allowed). Pre-flight prompt always shown in mutation mode.
- `--race-endpoints` allowlist path, required when `--race-allow-mutate` is set. Endpoints outside the allowlist are skipped, never probed.
- Pre-flight prompts user `y/N` before first send if any of `--aggressive-smuggling`, `--race-allow-mutate`, or `--rps > 20`.

---

## 5. Pipeline

```
1. connect       → @caido/sdk-client, PAT auth, select --project
2. discover      → caido_list_requests, HTTPQL filter req.host.cont:<host>
                 → dedupe by (method, path, sorted query keys)
                 → cap at --max-requests
                 → CDN fingerprint via Server / Via / CF-Ray / X-Akamai-* / X-Cache headers
3. fetch baseline → caido_get_request per unique endpoint
4. modules (in parallel, rps-throttled global queue):
   a. cache-poison
   b. cache-deception
   c. html-smuggling
   d. smuggling (if --aggressive-smuggling)
   e. race (if --race)
5. score + dedupe → confidence per finding
6. write          → out/<host>/<ts>/{findings.json, report.md, raw/<id>.json, ...}
```

All active sends go through `caido_send_request` so traffic stays inside the Caido project (replayable post-hoc).

Modules D and E bypass `caido_send_request`. Module D needs raw-socket framing; Module E needs sub-millisecond send-coalescing that Caido's GraphQL pipeline serializes away. After a confirmed primitive, the raw transcript is re-imported into Caido for replay history.

---

## 6. Probe modules

### 6.1 Module A — `cache-poison`

Targets endpoints with cache indicators (`Age`, `X-Cache`, `CF-Cache-Status`, `Via`, `s-maxage`, `Cache-Control: public`).

**A1. Unkeyed-header sweep** (per `wiki/techniques/cache-poisoning/unkeyed-header.md`)

Header dictionary (`data/unkeyed_headers.json`):
- `X-Forwarded-Host`, `X-Forwarded-Scheme`, `X-Forwarded-Proto`, `X-Forwarded-Port`, `X-Forwarded-For`
- `X-Host`, `X-Original-URL`, `X-Rewrite-URL` (Symfony/IIS)
- `X-Forwarded-Server` (Apache mod_rewrite)
- `X-HTTP-Method-Override`, `X-Method-Override` (GitLab DoS case)
- `Forwarded` (RFC 7239)
- `User-Agent`, `Accept-Language`, `Content-Type` (GitHub error-state DoS case)

Per probe: canary value `cnry-<rand>.evil.test`; cache-buster `?cb=<rand>` per attempt.

Reflection scan: response body, redirect `Location`, `<base href>`, `<script src>`, `<link href>`, `<meta property="og:image">`, JSON values.

Confirm: re-send same `cb` without canary header → expect cached canary in response → `X-Cache: HIT` or `Age: > 0`.

**A2. Parameter cloaking** (per `wiki/techniques/server-side/cache-parameter-cloaking.md`)

- Fat GET: send GET with `Content-Type: application/x-www-form-urlencoded` + body `injected=poison`.
- Semicolon skew: `?legit=1;injected=poison`.
- Excluded-param padding: `?utm_source=x&injected=poison&fbclid=y`.

**A3. URL-parser discrepancy / Static Path Deception** (per `url-parser-discrepancy.md` + HackTricks cache-poisoning-via-url-discrepancies)

Suffix set (`data/url_parser_suffixes.json`):
- `;.js`, `.css` (trailing dot)
- `/%2Fadmin`, `/..%2fadmin`
- `%252e%252e` (double encoded `..`)
- `%0d%0a` (CRLF)
- `?file=.js` (param injection)
- `#.js` (fragment leak)
- Mixed-case `/Admin`
- Trailing whitespace
- `%2F..%2F<route>` (ChatGPT-style)

Per-CDN adjustment: Cloudflare adds the default 50-extension list to the keying suffixes; Akamai adds `.aspx%3F<rand>.js`.

**A4. Cloudflare cache-key header overflow** (per `cloudflare-cache-key-header-overflow.md`)

Trigger only when CDN fingerprint = Cloudflare. Pad 94+ junk `X-Junk-N: a` headers, append one mutation header (`X-HTTP-Method-Override: DELETE` first). Binary-search cap at 50 / 100 / 200 if first attempt fails.

**A5. CDN quirks**

- Host header casing: send `Host: TaRgEt.CoM` (Cloudflare normalization mismatch).
- PURGE verb exposure: `curl -X PURGE <url>` — confirm only, no destructive verb without user opt-in (PURGE on shared cache is destructive; treat as detection-only via response code).
- Hop-by-hop header strip: `Connection: <header>` for each candidate header — observe whether back-end behaves differently when header is stripped.

**A6. Persistence loop** (per Shopify cross-host case)

For confirmed candidates only: 100-shot reseed loop, cross-host probe. Reports number of seconds the poison survives.

### 6.2 Module B — `cache-deception`

**B1. Path-append static-extension fuzz** (per `wiki/techniques/server-side/web-cache-deception.md` + Cloudflare default-cache list in HackTricks)

Per endpoint with auth + extracted user marker:

Marker extraction (`src/core/marker.ts`):
- email regex
- CSRF token (look for `csrf_token`, `_token`, `X-CSRF-Token`)
- JSON `id` / `email` / `username` / `user_id`
- Session-bound HTML fragments (e.g., `<span class="user-name">...</span>`)

Suffix set (`data/static_extensions.json`):
`/poc.css`, `/poc.js`, `/poc.png`, `/poc.jpg`, `/poc.gif`, `/poc.svg`, `/poc.woff`, `/poc.woff2`, `/poc.ico`, `/poc.pdf`, `/poc.avif` (Armor bypass), `/poc.webp`, `/poc.ttf`, `/poc.otf`, `/poc.eot`.

**B2. Delimiter discrepancy** (per HackTricks WCD + PortSwigger lab list)

Variants: `;.css`, `%23.css`, `%3F.css`, `%00.css`, `%0A.css`, `/..%2fx.css`, `%2f..%2fstyle.css`, `\..\x.css`, `.aspx%3F<rand>.js` (.NET).

**B3. Cache-prevention parameter trick** (TechCrunch case)

Append `?cb=<rand>` (origin treats as cache-buster, edge ignores). Auth'd fetch, then no-auth fetch same URL.

**B4. Path traversal in cache key** (per ChatGPT `/share/%2F..%2Fapi/auth/session?cb=...` HackTricks case)

For each cacheable prefix discovered (`/static/`, `/public/`, `/share/`, `/assets/`), append `%2F..%2F<target>` permutations.

**B5. Confidentiality verification**

Per candidate:
1. Baseline auth'd → extract marker.
2. Variant auth'd → cache populate.
3. Variant no-auth → check marker reflection.

Confidence:
- **high** = no-auth body contains baseline marker.
- **medium** = no-auth body ≥90% parity with baseline + cache HIT.
- **low** = cache HIT only, no marker leak.

**B6. CSPT-cache-deception passive** (per `cspt-cache-deception-chain.md`)

Passive scan baseline JS responses for `fetch(\`...${userInput}...\`)` patterns. Flag candidates only as `lead` — active confirmation requires JS execution which is out of scope.

### 6.3 Module C — `html-smuggling`

Passive scan baseline response bodies + every JS asset linked from them.

**C1. Blob/download primitives**

Indicators:
- `new Blob([` near `URL.createObjectURL`
- `<a download` with dynamic `href` assignment
- `msSaveOrOpenBlob`
- `data:application/octet-stream;base64,`
- `atob(` of >200-char string near `Uint8Array` / `Blob`
- Service Worker registration with `fetch` handler returning synthesized `Content-Disposition`

**C2. Form attribute smuggling** (per `wiki/techniques/dom-xss/form-attribute-smuggling.md`)

- `<input form="..."` outside the named form
- `formaction=` / `formtarget=` overrides on inputs

**C3. URL-credential payload smuggling** (per `wiki/techniques/dom-xss/url-credential-payload-smuggling.md`)

- Sinks: `document.URL`, `<a>.username`, `<a>.password`
- Flag pages embedding `document.URL` into `<a id="x">` (DOM clobbering combo)

**C4. Well-known-data-type smuggling** (per CT Ep 72 — Slonser)

- Inline base64 payloads >1KB in `<img src=data:image/...>`, SVG `<foreignObject>`, PDF data URIs
- JPEG/PDF metadata download triggers

**Scoring:** N indicators sum per response. Threshold ≥2 = finding. Active step (GET/HEAD only): probe any download-trigger URL discovered, capture `Content-Disposition`.

### 6.4 Module D — `smuggling` (flag-gated)

Off by default. Enabled only via `--aggressive-smuggling`. Raw-socket implementation bypasses `@caido/sdk-client`.

**Implementation**

- HTTP/1.1: Node `net.Socket` (http) / `tls.Socket` (https) with manual byte-level writes.
- HTTP/2: Node `http2.connect` with manual `:method`/`:path` pseudo-headers + body framing.
- Fresh TCP/TLS per probe — no connection reuse → bounds blast radius.

**Probes**

- **CL.TE timing probe**: `Content-Length: 6` + `Transfer-Encoding: chunked` + body `0\r\n\r\nG` — if back honors TE, terminates early, leaves `G` on socket. Detect via subsequent request timing.
- **TE.CL timing probe**: invert.
- **TE.TE obfuscation**: `Transfer-Encoding: xchunked`, `Transfer-Encoding:\tchunked`, `Transfer-encoding\r\n: chunked`, etc.
- **H2.CL / H2.TE downgrade**: HTTP/2 request with embedded `content-length` / `transfer-encoding` pseudo-headers.
- **Hop-by-hop strip** (per `hop-by-hop-smuggling.md`): `Connection: Content-Length`.
- **Akamai edge variant** (per `akamai-edge-smuggling.md`): triggered only if `Server: AkamaiGHost` / `X-Akamai-*` fingerprint detected.

**Detection methods**

1. **Differential timing**: malformed request → measure response time. >5s gap from baseline = candidate.
2. **Out-of-band confirmation via collaborator**: smuggle inner `GET http://<collaborator>/<rand>` → wait for hit (requires `--collaborator <fqdn>`). Without collaborator, primitive marked `candidate` only.
3. **Cache chain**: if smuggle confirmed + target has cacheable URL, run Module A's `smuggling-to-cache` sub-probe → smuggle inner GET against static asset, observe cache populate.

**Hard guardrails**

- Pre-flight prompt: print program/host + ask `y/N` confirm before first send.
- Rate limit hard floor: ≤1 rps in aggressive mode, ignores global `--rps`.
- Max 50 probes per endpoint; halt on first confirmed primitive.

### 6.5 Module E — `race` (flag-gated)

Off by default. Enabled via `--race`. Detects TOCTOU / state-collision bugs by firing N parallel-coalesced requests at a single endpoint and looking for response divergence beyond what serial replay produces.

Bypasses `caido_send_request` because timing margin is sub-millisecond; the GraphQL queue serializes requests on the way out.

**E1. Candidate selection** (`src/modules/race/candidate.ts`)

Score each endpoint on:
- Path keyword match (`data/race_keywords.json`): `apply`, `redeem`, `coupon`, `promo`, `transfer`, `withdraw`, `claim`, `gift`, `vote`, `like`, `follow`, `signup`, `register`, `invite`, `confirm`, `verify`, `mfa`, `otp`, `2fa`, `purchase`, `checkout`, `subscribe`, `cancel`, `refund`, `tip`, `donate`, `vault`.
- Auth-bound: baseline carries `Cookie`, `Authorization`, or `X-Auth-*`.
- Verb sensitivity: POST/PUT/PATCH/DELETE > GET with `?token=` / `?code=` / `?ref=` query > plain GET.
- Idempotency hints: absence of `Idempotency-Key` / `Request-Id` on mutating verbs.

Endpoints with score ≥2 enter the candidate set. Mutating-verb candidates are only probed when `--race-allow-mutate` is set AND the endpoint appears in `--race-endpoints` allowlist.

**E2. Single-packet attack** (`src/modules/race/single_packet.ts`)

HTTP/2 only. Open one `http2.connect` session, create N streams with HEADERS frames (END_STREAM = false), then `socket.cork()` the underlying TCP socket, write a final END_STREAM frame per stream, and `uncork()`. All END_STREAM frames flush in a single TCP segment → server processes them inside one event-loop tick.

Default N = 20 (`--race-concurrency`). Hard cap 50.

Detection signal (`src/modules/race/detect.ts`):
- **Status histogram**: ≥2 distinct codes when ≥80% of serial baseline replays returned the same code.
- **Body class diversity**: hash response bodies, count distinct classes. >1 class with each ≥2 members = primitive.
- **Marker leak**: extract `id`, `ref`, `code`, `token` JSON values; ≥2 distinct values returned where serial replay returned 1.
- **State-change marker**: response contains `already`, `duplicate`, `exists`, `limit`, `exceeded`, `taken` in subset of responses but not all → partial state advance = lock-bypass candidate.

**E3. Last-byte sync** (`src/modules/race/last_byte.ts`)

HTTP/1.1 fallback when target negotiates HTTP/1.1 only, or when `http2.connect` errors. Open N TCP sockets to the same host, write the full request minus the last byte on each, then write the last byte on all sockets in a tight loop inside the same `setImmediate` callback.

Less precise than H2 single-packet (TCP-level coalescing varies with kernel scheduling), but works on HTTP/1.1-only origins.

**E4. Serial-baseline calibration**

Before each parallel volley, send 5 serial copies via the same socket-strategy (no coalescing). This baselines the expected response distribution. The parallel result is only a finding if its distribution differs from the serial baseline beyond noise threshold.

**Confidence**

- **high**: distinct response classes (≥2 each, status or marker divergence) + state-change marker present + serial baseline uniform.
- **medium**: distinct response classes but no explicit state-change marker, OR state-change marker present but parallel-vs-serial delta < clean.
- **low**: response distribution differs from serial but no causal chain (e.g., random load-balancer flap).
- **lead**: candidate identified but probing was gated off (mutation without `--race-allow-mutate`, or endpoint absent from allowlist).

**Hard guardrails**

- Pre-flight prompt before first probe in mutation mode. Prints endpoint count + lists first 10 by score.
- Max 3 volleys per endpoint (calibration + 2 attempts). Halt on first confirmed primitive.
- Rate limit hard floor: each volley counts as 1 against the global rps token bucket, not N.
- Allowlist is the source of truth for mutating verbs. Empty allowlist + `--race-allow-mutate` = error.
- DELETE on any path ending `/<numeric-id>` is rejected even when allowlisted (require explicit `--race-allow-destructive`, not in this spec).
- Auth cookie passed via `--auth-cookie` is redacted from `findings.json` and `report.md`; raw transcripts in `raw/race/<id>.raw` retain it for replay (file-permission 0600).

---

## 7. Output structure

```
./out/<host>/<YYYYMMDD-HHMMSS>/
├── run.json                  # invocation, config, totals, timings
├── findings.json             # all findings, machine-readable
├── report.md                 # human report, grouped by module
├── raw/
│   ├── baselines/<id>.json   # baseline req+resp per endpoint
│   ├── probes/<id>.json      # every probe send (req + resp + diff)
│   └── smuggling/<id>.raw    # raw socket transcripts (Module D only)
├── endpoints.jsonl           # deduped endpoints actually probed
└── errors.jsonl              # per-probe errors w/ context
```

### `findings.json` schema (`zod`-validated)

```json
{
  "schema_version": 1,
  "host": "target.example",
  "ts": "2026-05-20T12:00:00Z",
  "findings": [
    {
      "id": "cp-001",
      "module": "cache-poison",
      "subtype": "unkeyed-header",
      "endpoint": "GET /en/index",
      "primitive": {"header": "X-Forwarded-Host", "canary": "cnry-abc123.evil.test"},
      "confidence": "high",
      "evidence": {
        "baseline_id": "raw/baselines/8f.json",
        "probe_id": "raw/probes/91.json",
        "reflection_loc": "body:<script src>",
        "cache_hit_confirmed": true,
        "x_cache_first": "MISS",
        "x_cache_second": "HIT",
        "age_second": 12
      },
      "poc_curl": "curl -H 'X-Forwarded-Host: ...' 'https://target.example/en/index?cb=...'",
      "wiki_ref": "wiki/techniques/cache-poisoning/unkeyed-header.md"
    }
  ]
}
```

### `report.md` shape

```
# <host> — cache/smuggling sweep
- Run: <ts>, <duration>, <N endpoints>, <M probes>, <K findings>
- Modules: cache-poison, cache-deception, html-smuggling[, smuggling]

## High-confidence (N)
### cp-001 · unkeyed-header X-Forwarded-Host → /en/index
[evidence summary, PoC curl, wiki ref]

## Medium-confidence (M)
...

## Leads (passive only — needs manual confirmation)
- cspt-cache-deception candidates: N
- html-smuggling indicator hits below threshold: M
```

### Confidence ladder (uniform across modules)

- **high**: payload reflected + cache HIT confirmed + marker leak (deception) / canary persistence (poison) / OOB hit (smuggling)
- **medium**: reflection observed but cache persistence unconfirmed OR ≥90% body parity without explicit marker / smuggling timing-only
- **low**: indicator present, no causal chain proven
- **lead**: passive-only signal, needs human

---

## 8. Project layout

```
caido-cache-smug/
├── README.md                # usage, examples, threat-model, ROE guardrails
├── package.json             # name=caido-cache-smug, bin entry
├── tsconfig.json
├── .gitignore               # node_modules, out/, .env
├── .env.example             # CAIDO_API_TOKEN, CAIDO_URL placeholders
├── src/
│   ├── cli.ts               # arg parse (commander), env, dispatch
│   ├── caido/
│   │   ├── client.ts        # @caido/sdk-client wrapper, PAT auth
│   │   ├── discover.ts      # caido_list_requests filter by host, dedupe
│   │   └── send.ts          # caido_send_request wrapper + rate limiter
│   ├── core/
│   │   ├── throttle.ts      # token-bucket, --rps
│   │   ├── diff.ts          # response diff (status, headers, body parity)
│   │   ├── cdn.ts           # CDN fingerprint (CF, Akamai, Fastly, Cloudfront, Varnish, nginx)
│   │   ├── marker.ts        # extract user marker from baseline
│   │   └── cache.ts         # cache-indicator parse (X-Cache, Age, CF-Cache-Status, Via)
│   ├── modules/
│   │   ├── cache_poison/    # 7 files per Section 6.1
│   │   ├── cache_deception/ # 6 files per Section 6.2
│   │   ├── html_smuggling/  # 4 files per Section 6.3
│   │   ├── smuggling/       # 7 files per Section 6.4, flag-gated
│   │   └── race/            # 5 files per Section 6.5, flag-gated
│   ├── report/
│   │   ├── findings.ts
│   │   ├── markdown.ts
│   │   └── poc.ts
│   └── types.ts             # shared types: Endpoint, Probe, Finding, Confidence
├── data/
│   ├── unkeyed_headers.json
│   ├── url_parser_suffixes.json
│   ├── delimiters.json
│   ├── static_extensions.json
│   ├── cdn_fingerprints.json
│   └── race_keywords.json
├── tests/
│   ├── fixtures/
│   ├── unit/
│   └── integration/         # mock Caido API + mock target
└── docs/
    ├── threat-model.md
    ├── modules.md
    └── examples/
        └── target-acme.md
```

### Dependencies

- `@caido/sdk-client` — Caido GraphQL
- `commander` — CLI
- `undici` — HTTP for non-Caido sends (only Module D raw socket; otherwise all via Caido)
- `pino` — structured logs
- `zod` — config + finding schema validation
- Dev: `vitest`, `@types/node`, `typescript`, `tsx`

### Distribution

- `npm link` for local install during dev.
- `npm pack` → standalone tarball; runs via `npx caido-cache-smug`.
- Not published to public npm.

### Run lifecycle

1. `npx caido-cache-smug --host acme.example --project acme-2026 --rps 5`
2. Connects to Caido, prints discovery count, prompts `y/N` to proceed.
3. Streams per-probe progress to stderr; structured logs to `out/.../run.log`.
4. On SIGINT: flush partial findings + write `interrupted: true` to `run.json`.

---

## 9. Threat model and rules-of-engagement guardrails

- **Scope.** `--host` is a single host; tool sends no request to any other host. If a discovered endpoint references a different host (cross-host redirects, CDN-internal hostnames), it is logged but not probed.
- **GET/HEAD only.** No POST/PUT/PATCH/DELETE. PURGE detection is response-based (no PURGE sent unless `--allow-purge` is set, which is not in this spec).
- **Rate limit.** Default 5 rps; Module D forces ≤1 rps regardless of `--rps`.
- **Pre-flight confirmation.** Required for aggressive smuggling or rps > 20.
- **No auth-secret leakage.** Auth cookies passed via `--auth-cookie` are written to `raw/` files but never to `findings.json` or `report.md`. Output files redact the cookie value.
- **Destructive smuggling.** CL/TE probes can desync the back-end connection pool; flag-gated, single-host, pre-flight prompted.
- **Race conditions.** Default detection-mode is GET/HEAD only (no mutation). Mutation mode is doubly gated (`--race-allow-mutate` + explicit `--race-endpoints` allowlist) and always pre-flight prompted. Numeric-ID DELETE paths are categorically rejected even when allowlisted.

---

## 10. Wiki coverage matrix

| Wiki page | Covered by |
|---|---|
| `cache-poisoning/SUMMARY.md` | A1–A6 |
| `cache-poisoning/unkeyed-header.md` | A1 |
| `cache-poisoning/url-parser-discrepancy.md` | A3 |
| `cache-poisoning/smuggling-to-cache.md` | D + A chain |
| `server-side/cache-parameter-cloaking.md` | A2 |
| `server-side/cloudflare-cache-key-header-overflow.md` | A4 |
| `server-side/web-cache-deception.md` | B1, B2, B3 |
| `server-side/cookie-clear-path-confusion.md` | A1 (`Set-Cookie` reflection scan in cache layer; partial) |
| `server-side/hop-by-hop-smuggling.md` | D (hop-by-hop strip probe) + A5 |
| `server-side/akamai-edge-smuggling.md` | D (Akamai variant) |
| `server-side/nginx-trim-strip-mismatch.md` | A3 (suffix set includes `\xa0` variants when nginx fingerprinted) |
| `dom-xss/cspt-cache-deception-chain.md` | B6 (passive lead only) |
| `dom-xss/form-attribute-smuggling.md` | C2 |
| `dom-xss/url-credential-payload-smuggling.md` | C3 |
| `_external/payloads-all-the-things/Web Cache Deception/` | B1, B2 |
| `_external/hacktricks/.../cache-deception/README.md` | A1–A3, B1–B4 |
| `_external/hacktricks/.../cache-poisoning-via-url-discrepancies.md` | A3, B4 |
| `_external/hacktricks/.../cache-poisoning-to-dos.md` | A1, A4 (mutation-as-DoS detection) |
| `race-conditions/SUMMARY.md` (to author) | E1–E4 |
| `race-conditions/single-packet-attack.md` (to author) | E2 |
| `race-conditions/last-byte-sync.md` (to author) | E3 |

---

## 11. Open questions

None blocking. Future revisions may add:

- `--allow-purge` flag for active PURGE probing.
- Multi-host mode (`--host a,b,c`) with isolated reports per host.
- Region/POP variance via SOCKS proxy chain.
- Connection-state smuggling once TLS-layer detection technique is documented.
