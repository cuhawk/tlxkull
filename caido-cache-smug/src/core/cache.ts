export interface CacheIndicators {
  hit: boolean;
  age?: number;
  cacheable: boolean;
  cdnFamily?: "cloudflare" | "akamai" | "fastly" | "cloudfront" | "varnish" | "nginx";
  raw: Record<string, string>;
}

function lc(h: Record<string, string>): Record<string, string> {
  const o: Record<string, string> = {};
  for (const k of Object.keys(h)) o[k.toLowerCase()] = h[k];
  return o;
}

export function parseCacheIndicators(headers: Record<string, string>): CacheIndicators {
  const h = lc(headers);
  const hit =
    /HIT/i.test(h["x-cache"] ?? "") ||
    /HIT/i.test(h["cf-cache-status"] ?? "") ||
    /HIT/i.test(h["x-served-by"] ?? "") ||
    /HIT/i.test(h["x-akamai-cache-status"] ?? "");
  const age = h["age"] ? parseInt(h["age"], 10) : undefined;
  const cc = (h["cache-control"] ?? "").toLowerCase();
  const cacheable = /public/.test(cc) || /s-maxage/.test(cc) || age !== undefined;

  let cdnFamily: CacheIndicators["cdnFamily"];
  if (h["cf-ray"] || h["cf-cache-status"] || /cloudflare/i.test(h["server"] ?? "")) cdnFamily = "cloudflare";
  else if (h["x-akamai-request-id"] || /akamai/i.test(h["server"] ?? "")) cdnFamily = "akamai";
  else if (/fastly/i.test(h["x-served-by"] ?? "")) cdnFamily = "fastly";
  else if (h["x-amz-cf-id"]) cdnFamily = "cloudfront";
  else if (/varnish/i.test(h["via"] ?? "")) cdnFamily = "varnish";
  else if (/nginx/i.test(h["server"] ?? "")) cdnFamily = "nginx";

  return { hit, age, cacheable, cdnFamily, raw: h };
}

export function hasCacheLayer(headers: Record<string, string>): boolean {
  const i = parseCacheIndicators(headers);
  return (
    i.hit ||
    i.age !== undefined ||
    i.cacheable ||
    i.cdnFamily !== undefined ||
    /varnish|squid|nginx-cache/i.test(i.raw["via"] ?? "")
  );
}
