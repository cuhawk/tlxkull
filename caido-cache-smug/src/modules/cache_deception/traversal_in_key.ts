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
