import type { Endpoint, HttpMessage } from "../../types.js";

export interface CandidateScore {
  score: number;
  reasons: string[];
  mutating: boolean;
}

const MUTATING = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const SENSITIVE_QUERY = ["token", "code", "ref", "nonce", "key", "id"];
const AUTH_HEADERS = ["authorization", "cookie", "x-auth-token", "x-api-key", "x-csrf-token"];

export function scoreEndpoint(
  endpoint: Endpoint,
  baseline: HttpMessage,
  keywords: readonly string[]
): CandidateScore {
  const reasons: string[] = [];
  let score = 0;

  const path = endpoint.path.toLowerCase();
  const hits = keywords.filter((k) => path.includes(k));
  if (hits.length > 0) {
    score += 1;
    reasons.push(`keyword:${hits.slice(0, 3).join(",")}`);
  }

  const headerKeys = Object.keys(baseline.headers ?? {}).map((h) => h.toLowerCase());
  const authHit = AUTH_HEADERS.find((h) => headerKeys.includes(h));
  if (authHit) {
    score += 1;
    reasons.push(`auth:${authHit}`);
  }

  const mutating = MUTATING.has(endpoint.method.toUpperCase());
  if (mutating) {
    score += 1;
    reasons.push(`verb:${endpoint.method}`);
    const idempotencyKey = headerKeys.includes("idempotency-key") || headerKeys.includes("request-id");
    if (!idempotencyKey) {
      score += 1;
      reasons.push("no-idempotency-key");
    }
  } else {
    const queryKeys = Object.keys(endpoint.query ?? {}).map((q) => q.toLowerCase());
    const sensitiveQuery = SENSITIVE_QUERY.find((q) => queryKeys.includes(q));
    if (sensitiveQuery) {
      score += 1;
      reasons.push(`query:${sensitiveQuery}`);
    }
  }

  return { score, reasons, mutating };
}

export function inAllowlist(
  endpoint: Endpoint,
  allowlist: ReadonlyArray<{ method: string; path: string }>
): boolean {
  const m = endpoint.method.toUpperCase();
  return allowlist.some(
    (entry) => entry.method.toUpperCase() === m && entry.path === endpoint.path
  );
}

export function isDestructiveNumericIdPath(endpoint: Endpoint): boolean {
  if (endpoint.method.toUpperCase() !== "DELETE") return false;
  return /\/\d+\/?$/.test(endpoint.path);
}
