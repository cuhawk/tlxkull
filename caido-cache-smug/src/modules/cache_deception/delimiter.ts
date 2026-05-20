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
