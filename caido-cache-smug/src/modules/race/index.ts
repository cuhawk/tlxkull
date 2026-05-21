import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import {
  scoreEndpoint,
  inAllowlist,
  isDestructiveNumericIdPath,
  type CandidateScore
} from "./candidate.js";
import { classify, type RaceResponse } from "./detect.js";
import { singlePacketSend, type PacketRequest } from "./single_packet.js";
import { lastByteSync, type LastByteRequest } from "./last_byte.js";
import raceKeywords from "../../../data/race_keywords.json" with { type: "json" };

export interface RaceOpts {
  enabled: boolean;
  concurrency: number;
  allowMutate: boolean;
  allowlist: ReadonlyArray<{ method: string; path: string }>;
  authCookie?: string;
  timeoutMs?: number;
}

export async function runRace(
  endpoint: Endpoint,
  baseline: HttpMessage,
  opts: RaceOpts
): Promise<Finding[]> {
  if (!opts.enabled) return [];

  const candidate = scoreEndpoint(endpoint, baseline, raceKeywords as string[]);
  if (candidate.score < 2) return [];

  if (candidate.mutating) {
    if (!opts.allowMutate || !inAllowlist(endpoint, opts.allowlist)) {
      return [mkLead(endpoint, candidate, "gated:mutation-not-allowlisted")];
    }
    if (isDestructiveNumericIdPath(endpoint)) {
      return [mkLead(endpoint, candidate, "gated:destructive-numeric-id")];
    }
  }

  const headers = buildHeaders(baseline.headers, opts.authCookie);
  const concurrency = Math.min(Math.max(opts.concurrency, 2), 50);
  const timeoutMs = opts.timeoutMs ?? 10_000;
  const port = inferPort(baseline);
  const useTls = inferTls(baseline);

  const target = { host: endpoint.host, port, timeoutMs };
  const body = endpoint.method.toUpperCase() === "GET" ? undefined : "";

  const packetReq: PacketRequest = { method: endpoint.method, path: endpoint.path, headers, body };
  const lastByteReq: LastByteRequest = { ...packetReq };

  const serial = await runSerial(target, useTls, lastByteReq, 5);

  let parallel: RaceResponse[] = [];
  let transport: "h2-single-packet" | "h1-last-byte" = "h2-single-packet";
  try {
    parallel = await singlePacketSend(
      target,
      Array.from({ length: concurrency }, () => packetReq)
    );
  } catch {
    if (!useTls) {
      parallel = await lastByteSync(
        { ...target, tls: false },
        Array.from({ length: concurrency }, () => lastByteReq)
      );
      transport = "h1-last-byte";
    } else {
      parallel = await lastByteSync(
        { ...target, tls: true },
        Array.from({ length: concurrency }, () => lastByteReq)
      );
      transport = "h1-last-byte";
    }
  }

  const verdict = classify(serial, parallel);
  if (verdict.confidence === "lead" && verdict.signal === "no-divergence") return [];

  return [
    {
      id: `race-${endpoint.id}-${transport}`,
      module: "race",
      subtype: transport,
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: {
        concurrency,
        transport,
        score: candidate.score,
        reasons: candidate.reasons
      },
      confidence: verdict.confidence,
      evidence: {
        signal: verdict.signal,
        serial_classes: serial.length,
        parallel_classes: verdict.classes.length,
        parallel_summary: verdict.classes.slice(0, 5).map((c) => ({
          status: c.status,
          count: c.count,
          markers: c.markers
        })),
        serial_status: serial.map((r) => r.status),
        parallel_status: parallel.map((r) => r.status)
      },
      poc_curl: synthesizePoc(endpoint, headers, opts.authCookie, concurrency),
      wiki_ref: "wiki/techniques/race-conditions/SUMMARY.md"
    }
  ];
}

async function runSerial(
  target: { host: string; port: number; timeoutMs: number },
  useTls: boolean,
  req: LastByteRequest,
  count: number
): Promise<RaceResponse[]> {
  const out: RaceResponse[] = [];
  for (let i = 0; i < count; i++) {
    const [r] = await lastByteSync({ ...target, tls: useTls }, [req]);
    out.push(r);
  }
  return out;
}

function mkLead(endpoint: Endpoint, candidate: CandidateScore, reason: string): Finding {
  return {
    id: `race-${endpoint.id}-lead`,
    module: "race",
    subtype: "lead",
    endpoint: `${endpoint.method} ${endpoint.path}`,
    primitive: { score: candidate.score, reasons: candidate.reasons, gated: reason },
    confidence: "lead",
    evidence: { gated: reason },
    poc_curl: `# gated: ${reason}`,
    wiki_ref: "wiki/techniques/race-conditions/SUMMARY.md"
  };
}

function buildHeaders(
  baselineHeaders: Record<string, string>,
  authCookie: string | undefined
): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(baselineHeaders ?? {})) {
    const lower = k.toLowerCase();
    if (lower === "host" || lower.startsWith(":") || lower === "content-length" || lower === "connection") continue;
    out[lower] = v;
  }
  if (authCookie) out["cookie"] = authCookie;
  if (!out["user-agent"]) out["user-agent"] = "caido-cache-smug/race";
  if (!out["accept"]) out["accept"] = "*/*";
  return out;
}

function inferPort(baseline: HttpMessage): number {
  if (baseline.url) {
    try {
      const u = new URL(baseline.url);
      if (u.port) return Number(u.port);
      return u.protocol === "http:" ? 80 : 443;
    } catch { /* swallow */ }
  }
  return 443;
}

function inferTls(baseline: HttpMessage): boolean {
  if (baseline.url) {
    try { return new URL(baseline.url).protocol === "https:"; } catch { /* swallow */ }
  }
  return true;
}

function synthesizePoc(
  endpoint: Endpoint,
  headers: Record<string, string>,
  authCookie: string | undefined,
  concurrency: number
): string {
  const url = `https://${endpoint.host}${endpoint.path}`;
  const headerArgs = Object.entries(headers)
    .filter(([k]) => k !== "cookie")
    .map(([k, v]) => `  -H '${k}: ${escapeShellSingleQuote(v)}'`)
    .join(" \\\n");
  const cookieLine = authCookie ? `  -b '$CAIDO_COOKIE' \\\n` : "";
  return [
    `# Race volley — ${concurrency} parallel single-packet ${endpoint.method} requests`,
    `# Replay manually with turbo-intruder (gate=race), or use this curl-parallel loop:`,
    `for i in $(seq 1 ${concurrency}); do`,
    `  curl --http2 -sk -X ${endpoint.method} \\`,
    headerArgs ? `${headerArgs} \\` : "",
    cookieLine,
    `    '${url}' &`,
    `done; wait`
  ]
    .filter((line) => line !== "")
    .join("\n");
}

function escapeShellSingleQuote(value: string): string {
  return value.replace(/'/g, "'\\''");
}
