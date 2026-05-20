import type { RawOpts, RawResult } from "./raw_socket.js";
type RawFn = (opts: RawOpts) => Promise<RawResult>;

const OBFUSCATIONS = [
  "Transfer-Encoding: xchunked",
  "Transfer-Encoding:\tchunked",
  "Transfer-encoding: chunked\r\nTransfer-Encoding: identity",
  "X: X\r\nTransfer-Encoding: chunked",
  "Transfer-Encoding\n: chunked"
];

export interface TeTeResult { obfuscation: string; candidate: boolean; elapsedMs: number; }

export async function probeTeTe(raw: RawFn, target: { host: string; port: number; tls: boolean }): Promise<TeTeResult[]> {
  const opts = { host: target.host, port: target.port, tls: target.tls, timeoutMs: 5000 };
  const baseline = await raw({ ...opts, raw: `GET / HTTP/1.1\r\nHost: ${target.host}\r\nConnection: close\r\n\r\n` });
  const results: TeTeResult[] = [];
  for (const obf of OBFUSCATIONS) {
    const probe = await raw({
      ...opts,
      raw: `POST / HTTP/1.1\r\nHost: ${target.host}\r\n${obf}\r\nContent-Length: 4\r\nConnection: close\r\n\r\n0\r\n\r\n`
    });
    results.push({
      obfuscation: obf,
      candidate: probe.timedOut || probe.elapsedMs - baseline.elapsedMs > 5000,
      elapsedMs: probe.elapsedMs
    });
  }
  return results;
}
