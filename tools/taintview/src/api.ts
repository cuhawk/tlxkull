import type { Chain } from "./state/chains";
import type { Verdict, VerdictRecord } from "./state/filters";

const base = ""; // same-origin

async function getJson<T>(url: string): Promise<T> {
  const r = await fetch(base + url);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} on ${url}`);
  return (await r.json()) as T;
}

export async function listTargets(): Promise<string[]> {
  const { targets } = await getJson<{ targets: string[] }>("/api/targets");
  return targets;
}

export async function getChains(name: string): Promise<Chain[]> {
  const { chains } = await getJson<{ chains: Chain[] }>(`/api/target/${encodeURIComponent(name)}/chains`);
  return chains;
}

export async function getOpus(name: string, chainId: number): Promise<string | null> {
  const r = await fetch(`/api/target/${encodeURIComponent(name)}/opus/${chainId}`);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`${r.status} on opus/${chainId}`);
  const body = (await r.json()) as { markdown: string };
  return body.markdown;
}

export type SnippetPayload = {
  qname: string;
  file: string;
  line: number;
  end_line: number;
  start: number;
  end: number;
  source: string;
};

export async function getSnippet(name: string, qname: string): Promise<SnippetPayload | { error: string }> {
  const r = await fetch(`/api/target/${encodeURIComponent(name)}/snippet?qname=${encodeURIComponent(qname)}`);
  if (r.status === 404) return { error: (await r.json()).detail };
  if (!r.ok) throw new Error(`${r.status} on snippet`);
  return (await r.json()) as SnippetPayload;
}

export async function getVerdicts(name: string): Promise<Record<string, VerdictRecord>> {
  const { verdicts } = await getJson<{ verdicts: Record<string, VerdictRecord> }>(
    `/api/target/${encodeURIComponent(name)}/verdicts`,
  );
  return verdicts;
}

export async function postVerdict(
  name: string,
  chainId: number,
  verdict: Exclude<Verdict, "none">,
  note: string,
): Promise<VerdictRecord> {
  const r = await fetch(`/api/target/${encodeURIComponent(name)}/verdict/${chainId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ verdict, note }),
  });
  if (!r.ok) throw new Error(`${r.status} on verdict POST`);
  return (await r.json()) as VerdictRecord;
}
