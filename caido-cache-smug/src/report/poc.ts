import type { HttpMessage } from "../types.js";

const REDACT_HEADERS = new Set(["cookie", "authorization", "proxy-authorization"]);

export function synthCurl(req: HttpMessage): string {
  const parts: string[] = [`curl -X ${req.method}`];
  for (const [k, v] of Object.entries(req.headers)) {
    const value = REDACT_HEADERS.has(k.toLowerCase()) ? "<redacted>" : v;
    parts.push(`-H '${k}: ${value}'`);
  }
  if (req.body) parts.push(`--data-raw '${req.body.replace(/'/g, "'\\''")}'`);
  parts.push(`'${req.url}'`);
  return parts.join(" ");
}
