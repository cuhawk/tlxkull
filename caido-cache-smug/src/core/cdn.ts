import fp from "../../data/cdn_fingerprints.json";

export type CdnFamily = "cloudflare" | "akamai" | "fastly" | "cloudfront" | "varnish" | "nginx";

export function fingerprintCdn(headers: Record<string, string>): CdnFamily | null {
  const h: Record<string, string> = {};
  for (const k of Object.keys(headers)) h[k.toLowerCase()] = headers[k];

  for (const [family, def] of Object.entries(fp) as Array<[CdnFamily, any]>) {
    for (const hk of def.headerKeys ?? []) if (h[hk]) return family;
    if (def.serverRegex && new RegExp(def.serverRegex, "i").test(h["server"] ?? "")) return family;
    if (def.viaRegex && new RegExp(def.viaRegex, "i").test(h["via"] ?? "")) return family;
    if (def.servedByRegex && new RegExp(def.servedByRegex, "i").test(h["x-served-by"] ?? "")) return family;
  }
  return null;
}
