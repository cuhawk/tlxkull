import type { Finding, RunMeta } from "../types.js";

const ORDER: Finding["confidence"][] = ["high", "medium", "low", "lead"];
const HEADER: Record<Finding["confidence"], string> = {
  high: "High-confidence",
  medium: "Medium-confidence",
  low: "Low-confidence",
  lead: "Leads (manual review)"
};

export function renderReport(meta: RunMeta, findings: Finding[]): string {
  const lines: string[] = [];
  lines.push(`# ${meta.host} — cache/smuggling sweep`);
  lines.push("");
  lines.push(`- Run: ${meta.ts} · ${meta.duration_ms}ms · ${meta.endpoints_probed} endpoints · ${meta.probes_sent} probes · ${findings.length} findings`);
  lines.push(`- Modules: ${meta.modules_run.join(", ")}`);
  if (meta.interrupted) lines.push(`- **Interrupted before completion**`);
  lines.push("");

  for (const level of ORDER) {
    const group = findings.filter((f) => f.confidence === level);
    if (group.length === 0) continue;
    lines.push(`## ${HEADER[level]} (${group.length})`);
    for (const f of group) {
      lines.push("");
      lines.push(`### ${f.id} · ${f.subtype} → ${f.endpoint}`);
      lines.push(`- Module: ${f.module}`);
      lines.push(`- Primitive: \`${JSON.stringify(f.primitive)}\``);
      lines.push(`- Evidence: \`${JSON.stringify(f.evidence)}\``);
      lines.push(`- PoC:`);
      lines.push("");
      lines.push("```bash");
      lines.push(f.poc_curl);
      lines.push("```");
      lines.push("");
      lines.push(`- Wiki: [${f.wiki_ref}](../../${f.wiki_ref})`);
    }
    lines.push("");
  }
  return lines.join("\n");
}
