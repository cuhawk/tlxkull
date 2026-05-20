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
