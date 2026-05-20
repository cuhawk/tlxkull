export interface Marker {
  kind: "email" | "csrf" | "id" | "username";
  value: string;
}

const EMAIL = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
const CSRF = /(?:csrf[_-]?token|_token|x-csrf-token)["'\s:=]+([A-Za-z0-9+/=_-]{16,})/gi;
const ID = /["']?id["']?\s*[:=]\s*["']?(\d{3,}|[a-f0-9-]{8,})/gi;
const USERNAME = /["']?username["']?\s*[:=]\s*["']([^"']{3,32})["']/gi;

export function extractMarkers(body: string): Marker[] {
  const out: Marker[] = [];
  for (const m of body.matchAll(EMAIL)) out.push({ kind: "email", value: m[0] });
  for (const m of body.matchAll(CSRF)) out.push({ kind: "csrf", value: m[1] });
  for (const m of body.matchAll(ID)) out.push({ kind: "id", value: m[1] });
  for (const m of body.matchAll(USERNAME)) out.push({ kind: "username", value: m[1] });
  return dedupe(out);
}

function dedupe(arr: Marker[]): Marker[] {
  const seen = new Set<string>();
  return arr.filter((m) => {
    const k = `${m.kind}:${m.value}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}
