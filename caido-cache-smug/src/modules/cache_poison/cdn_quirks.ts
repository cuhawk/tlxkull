import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";

const HOP_BY_HOP_CANDIDATES = ["X-Forwarded-For", "Authorization", "Cookie", "Content-Length"];

export async function sweepCdnQuirks(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage
): Promise<Finding[]> {
  const findings: Finding[] = [];
  const url = `https://${endpoint.host}${endpoint.path}`;

  const lower = await sender.send({ method: "GET", url, headers: baseline.headers, body: "" });
  const mixed = await sender.send({
    method: "GET",
    url,
    headers: { ...baseline.headers, Host: scrambleCase(endpoint.host) },
    body: ""
  });
  if (lower.response.body !== mixed.response.body) {
    findings.push({
      id: `cp-${endpoint.id}-host-casing`,
      module: "cache-poison",
      subtype: "host-casing",
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { host_variant: scrambleCase(endpoint.host) },
      confidence: "low",
      evidence: { lower_id: lower.requestId, mixed_id: mixed.requestId },
      poc_curl: `curl -H 'Host: ${scrambleCase(endpoint.host)}' '${url}'`,
      wiki_ref: "wiki/techniques/server-side/cloudflare-cache-key-header-overflow.md"
    });
  }

  const purge = await sender.send({ method: "PURGE", url, headers: baseline.headers, body: "" });
  if ((purge.response.status ?? 0) >= 200 && (purge.response.status ?? 0) < 400) {
    findings.push({
      id: `cp-${endpoint.id}-purge`,
      module: "cache-poison",
      subtype: "purge-exposed",
      endpoint: `PURGE ${endpoint.path}`,
      primitive: {},
      confidence: "medium",
      evidence: { probe_id: purge.requestId, status: purge.response.status },
      poc_curl: `curl -X PURGE '${url}'`,
      wiki_ref: "wiki/techniques/cache-poisoning/SUMMARY.md"
    });
  }

  for (const hbh of HOP_BY_HOP_CANDIDATES) {
    const probe = await sender.send({
      method: "GET",
      url,
      headers: { ...baseline.headers, Connection: hbh },
      body: ""
    });
    if (probe.response.status !== baseline.status) {
      findings.push({
        id: `cp-${endpoint.id}-hop-${hbh}`,
        module: "cache-poison",
        subtype: "hop-by-hop-strip",
        endpoint: `${endpoint.method} ${endpoint.path}`,
        primitive: { stripped_header: hbh },
        confidence: "low",
        evidence: { probe_id: probe.requestId, baseline_status: baseline.status, probe_status: probe.response.status },
        poc_curl: `curl -H 'Connection: ${hbh}' '${url}'`,
        wiki_ref: "wiki/techniques/server-side/hop-by-hop-smuggling.md"
      });
    }
  }
  return findings;
}

function scrambleCase(host: string): string {
  return host
    .split("")
    .map((c, i) => (i % 2 === 0 ? c.toUpperCase() : c.toLowerCase()))
    .join("");
}
