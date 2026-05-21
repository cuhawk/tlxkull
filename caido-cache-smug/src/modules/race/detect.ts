import { createHash } from "node:crypto";
import type { Confidence } from "../../types.js";

export interface RaceResponse {
  status: number;
  headers: Record<string, string>;
  body: string;
  elapsedMs: number;
}

export interface Classification {
  confidence: Confidence;
  signal: string;
  classes: ResponseClass[];
}

export interface ResponseClass {
  hash: string;
  status: number;
  count: number;
  markers: string[];
}

const STATE_CHANGE_MARKERS = [
  "already",
  "duplicate",
  "exists",
  "limit reached",
  "limit exceeded",
  "exceeded",
  "taken",
  "in use",
  "concurrent",
  "race"
];

const JSON_MARKER_RX = /"(id|ref|code|token|nonce|reference)"\s*:\s*"?([A-Za-z0-9._-]{4,64})"?/g;

export function classify(serial: RaceResponse[], parallel: RaceResponse[]): Classification {
  const serialClasses = bucket(serial);
  const parallelClasses = bucket(parallel);

  if (serial.length === 0 || parallel.length === 0) {
    return { confidence: "lead", signal: "empty-volley", classes: parallelClasses };
  }

  const serialUniform = serialClasses.length === 1;
  const parallelDiverse = parallelClasses.filter((c) => c.count >= 2).length >= 2;

  const stateChangeSubset = subsetStateChangeMarker(parallel);
  const jsonMarkerLeak = jsonMarkerDivergence(serial, parallel);
  const distinctStatuses = new Set(parallel.map((r) => r.status)).size;

  if (parallelDiverse && serialUniform && stateChangeSubset) {
    return { confidence: "high", signal: "diverse+state-marker", classes: parallelClasses };
  }
  if (parallelDiverse && serialUniform) {
    return { confidence: "medium", signal: "diverse-response-classes", classes: parallelClasses };
  }
  if (jsonMarkerLeak.detected) {
    return {
      confidence: "high",
      signal: `json-marker-leak:${jsonMarkerLeak.field}`,
      classes: parallelClasses
    };
  }
  if (distinctStatuses >= 2 && serialUniform) {
    return { confidence: "medium", signal: "status-divergence", classes: parallelClasses };
  }
  if (stateChangeSubset && serialUniform) {
    return { confidence: "medium", signal: "state-marker-subset", classes: parallelClasses };
  }
  if (parallelClasses.length > serialClasses.length) {
    return { confidence: "low", signal: "distribution-shift", classes: parallelClasses };
  }
  return { confidence: "lead", signal: "no-divergence", classes: parallelClasses };
}

function bucket(responses: RaceResponse[]): ResponseClass[] {
  const buckets = new Map<string, ResponseClass>();
  for (const r of responses) {
    const hash = createHash("sha1")
      .update(`${r.status}\n${normalizeBody(r.body)}`)
      .digest("hex")
      .slice(0, 12);
    const existing = buckets.get(hash);
    if (existing) {
      existing.count += 1;
    } else {
      buckets.set(hash, {
        hash,
        status: r.status,
        count: 1,
        markers: extractMarkers(r.body)
      });
    }
  }
  return [...buckets.values()].sort((a, b) => b.count - a.count);
}

function normalizeBody(body: string): string {
  return body
    .replace(/\b\d{10,}\b/g, "<num>")
    .replace(/"(?:id|ref|nonce|token)"\s*:\s*"[^"]+"/gi, '"<marker>"')
    .replace(/\s+/g, " ")
    .slice(0, 4096);
}

function extractMarkers(body: string): string[] {
  const out: string[] = [];
  for (const m of body.matchAll(JSON_MARKER_RX)) out.push(`${m[1]}=${m[2]}`);
  return out.slice(0, 8);
}

function subsetStateChangeMarker(responses: RaceResponse[]): boolean {
  if (responses.length < 2) return false;
  const matches = responses.map((r) => {
    const lower = r.body.toLowerCase();
    return STATE_CHANGE_MARKERS.some((m) => lower.includes(m));
  });
  const trueCount = matches.filter(Boolean).length;
  return trueCount > 0 && trueCount < responses.length;
}

function jsonMarkerDivergence(
  serial: RaceResponse[],
  parallel: RaceResponse[]
): { detected: boolean; field: string } {
  const serialValues = collectMarkerValues(serial);
  const parallelValues = collectMarkerValues(parallel);
  for (const [field, parSet] of parallelValues.entries()) {
    const serSet = serialValues.get(field) ?? new Set<string>();
    if (parSet.size >= 2 && serSet.size <= 1) {
      return { detected: true, field };
    }
  }
  return { detected: false, field: "" };
}

function collectMarkerValues(responses: RaceResponse[]): Map<string, Set<string>> {
  const out = new Map<string, Set<string>>();
  for (const r of responses) {
    for (const m of r.body.matchAll(JSON_MARKER_RX)) {
      const field = m[1];
      const value = m[2];
      let set = out.get(field);
      if (!set) {
        set = new Set();
        out.set(field, set);
      }
      set.add(value);
    }
  }
  return out;
}
