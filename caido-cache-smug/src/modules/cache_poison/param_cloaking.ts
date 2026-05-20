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
