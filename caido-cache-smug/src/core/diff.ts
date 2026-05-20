import type { HttpMessage } from "../types.js";

export interface DiffOpts {
  ignoreHeaders?: string[];
  ignoreBodyRegex?: RegExp[];
}
export interface DiffResult {
  statusChanged: boolean;
  headersAdded: string[];
  headersRemoved: string[];
  bodyChanged: boolean;
  bodyParity: number;
}

export function bodyParity(a: string, b: string): number {
  if (a === b) return 1;
  const longer = a.length >= b.length ? a : b;
  const shorter = a.length >= b.length ? b : a;
  if (longer.length === 0) return 1;
  let same = 0;
  for (let i = 0; i < shorter.length; i++) if (longer[i] === shorter[i]) same++;
  return same / longer.length;
}

function normalize(body: string, ignore: RegExp[] = []): string {
  let s = body;
  for (const r of ignore) s = s.replace(new RegExp(r, "g"), "");
  return s;
}

export function diffResponses(a: HttpMessage, b: HttpMessage, opts: DiffOpts = {}): DiffResult {
  const aBody = normalize(a.body, opts.ignoreBodyRegex);
  const bBody = normalize(b.body, opts.ignoreBodyRegex);
  const ignore = new Set((opts.ignoreHeaders ?? []).map((h) => h.toLowerCase()));
  const ak = Object.keys(a.headers).filter((k) => !ignore.has(k.toLowerCase()));
  const bk = Object.keys(b.headers).filter((k) => !ignore.has(k.toLowerCase()));
  return {
    statusChanged: a.status !== b.status,
    headersAdded: bk.filter((k) => !ak.includes(k)),
    headersRemoved: ak.filter((k) => !bk.includes(k)),
    bodyChanged: aBody !== bBody,
    bodyParity: bodyParity(aBody, bBody)
  };
}
