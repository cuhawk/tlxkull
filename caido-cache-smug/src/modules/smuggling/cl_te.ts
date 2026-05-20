import type { RawOpts, RawResult } from "./raw_socket.js";

type RawFn = (opts: RawOpts) => Promise<RawResult>;

export interface ClTeProbeResult {
  candidate: boolean;
  baselineMs: number;
  probeMs: number;
}

export async function probeClTe(
  raw: RawFn,
  target: { host: string; port: number; tls: boolean }
): Promise<ClTeProbeResult> {
  const opts = { host: target.host, port: target.port, tls: target.tls, timeoutMs: 5000 };
  const baseline = await raw({
    ...opts,
    raw: `GET / HTTP/1.1\r\nHost: ${target.host}\r\nConnection: close\r\n\r\n`
  });
  const probe = await raw({
    ...opts,
    raw:
      `POST / HTTP/1.1\r\n` +
      `Host: ${target.host}\r\n` +
      `Content-Length: 6\r\n` +
      `Transfer-Encoding: chunked\r\n` +
      `Connection: close\r\n\r\n` +
      `0\r\n\r\nG`
  });
  const candidate = probe.timedOut || probe.elapsedMs - baseline.elapsedMs > 5000;
  return { candidate, baselineMs: baseline.elapsedMs, probeMs: probe.elapsedMs };
}
