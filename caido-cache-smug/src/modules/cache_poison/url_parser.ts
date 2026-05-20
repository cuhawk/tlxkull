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
      probe.response.body.length > 0 &&
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
