import type { Finding } from "../../types.js";

const CSPT_PATTERN = /fetch\(\s*`[^`]*\$\{[^}]*(?:params|location|searchParams|hash|name|getAttribute)[^}]*\}[^`]*`\s*[,)]/g;

export function scanCsptPassive(jsBody: string, sourceUrl: string): Finding[] {
  const out: Finding[] = [];
  const re = new RegExp(CSPT_PATTERN.source, "g");
  let m: RegExpExecArray | null;
  while ((m = re.exec(jsBody)) !== null) {
    out.push({
      id: `cd-cspt-${hash(sourceUrl + m.index)}`,
      module: "cache-deception",
      subtype: "cspt-cache-deception-candidate",
      endpoint: sourceUrl,
      primitive: { snippet: m[0].slice(0, 200) },
      confidence: "lead",
      evidence: { offset: m.index, source: sourceUrl },
      poc_curl: `# manual: open ${sourceUrl} and trace input to fetch`,
      wiki_ref: "wiki/techniques/dom-xss/cspt-cache-deception-chain.md"
    });
  }
  return out;
}

function hash(s: string): string {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h).toString(16);
}
