import type { Endpoint, Finding } from "../../types.js";
import { rawSend } from "./raw_socket.js";
import { probeClTe } from "./cl_te.js";
import { probeTeCl } from "./te_cl.js";
import { probeTeTe } from "./te_te.js";
import { probeHopByHop } from "./hop_by_hop.js";
import { probeH2Downgrade } from "./h2_downgrade.js";

export interface SmugglingOpts { aggressive: boolean; collaborator?: string; }

export async function runSmuggling(endpoint: Endpoint, opts: SmugglingOpts): Promise<Finding[]> {
  if (!opts.aggressive) return [];
  const target = { host: endpoint.host, port: 443, tls: true };
  const findings: Finding[] = [];

  const cl = await probeClTe(rawSend, target);
  if (cl.candidate) findings.push(mkFinding(endpoint, "cl-te", cl as unknown as Record<string, unknown>));

  const tc = await probeTeCl(rawSend, target);
  if (tc.candidate) findings.push(mkFinding(endpoint, "te-cl", tc as unknown as Record<string, unknown>));

  const tt = await probeTeTe(rawSend, target);
  for (const r of tt) if (r.candidate) findings.push(mkFinding(endpoint, `te-te:${r.obfuscation}`, r as unknown as Record<string, unknown>));

  const hbh = await probeHopByHop(rawSend, target, ["Content-Length", "Cookie", "Authorization"]);
  for (const r of hbh) if (r.differential) findings.push(mkFinding(endpoint, `hop-by-hop:${r.header}`, r as unknown as Record<string, unknown>));

  const h2 = await probeH2Downgrade({ host: target.host, port: target.port });
  if (h2.candidate) findings.push(mkFinding(endpoint, "h2-downgrade", h2 as unknown as Record<string, unknown>));

  return findings;
}

function mkFinding(endpoint: Endpoint, subtype: string, evidence: Record<string, unknown>): Finding {
  const confirmed = false;
  return {
    id: `sm-${endpoint.id}-${subtype.replace(/[^a-z0-9]/gi, "_")}`,
    module: "smuggling",
    subtype,
    endpoint: `${endpoint.method} ${endpoint.path}`,
    primitive: { variant: subtype },
    confidence: confirmed ? "high" : "medium",
    evidence,
    poc_curl: `# raw socket — see raw/<id>.raw transcript`,
    wiki_ref: "wiki/techniques/request-smuggling/SUMMARY.md"
  };
}
