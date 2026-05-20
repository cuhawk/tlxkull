import type { RawOpts, RawResult } from "./raw_socket.js";
type RawFn = (opts: RawOpts) => Promise<RawResult>;

export interface HopByHopResult { header: string; differential: boolean; baselineMs: number; probeMs: number; }

export async function probeHopByHop(
  raw: RawFn,
  target: { host: string; port: number; tls: boolean },
  candidates: string[]
): Promise<HopByHopResult[]> {
  const opts = { host: target.host, port: target.port, tls: target.tls, timeoutMs: 5000 };
  const baseline = await raw({ ...opts, raw: `GET / HTTP/1.1\r\nHost: ${target.host}\r\nConnection: close\r\n\r\n` });
  const results: HopByHopResult[] = [];
  for (const hdr of candidates) {
    const probe = await raw({
      ...opts,
      raw: `GET / HTTP/1.1\r\nHost: ${target.host}\r\nConnection: ${hdr}\r\n${hdr}: x\r\n\r\n`
    });
    results.push({
      header: hdr,
      differential: Math.abs(probe.elapsedMs - baseline.elapsedMs) > 1000,
      baselineMs: baseline.elapsedMs,
      probeMs: probe.elapsedMs
    });
  }
  return results;
}
