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
