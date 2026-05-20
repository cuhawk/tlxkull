import net from "node:net";
import tls from "node:tls";

export interface RawOpts {
  host: string;
  port: number;
  tls: boolean;
  raw: string;
  timeoutMs: number;
}
export interface RawResult {
  bytes: string;
  elapsedMs: number;
  timedOut: boolean;
}

export function rawSend(opts: RawOpts): Promise<RawResult> {
  return new Promise((resolve) => {
    const start = Date.now();
    const socket = opts.tls
      ? tls.connect({ host: opts.host, port: opts.port, servername: opts.host, rejectUnauthorized: false })
      : net.connect({ host: opts.host, port: opts.port });
    let buf = "";
    let done = false;
    const finish = (timedOut: boolean) => {
      if (done) return;
      done = true;
      try { socket.destroy(); } catch {}
      resolve({ bytes: buf, elapsedMs: Date.now() - start, timedOut });
    };
    socket.setTimeout(opts.timeoutMs);
    socket.on("connect", () => socket.write(opts.raw));
    socket.on("secureConnect", () => socket.write(opts.raw));
    socket.on("data", (chunk) => { buf += chunk.toString("latin1"); });
    socket.on("end", () => finish(false));
    socket.on("close", () => finish(false));
    socket.on("timeout", () => finish(true));
    socket.on("error", () => finish(false));
  });
}
