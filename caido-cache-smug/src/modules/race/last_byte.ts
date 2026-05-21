import net from "node:net";
import tls from "node:tls";
import type { RaceResponse } from "./detect.js";

export interface LastByteRequest {
  method: string;
  path: string;
  headers: Record<string, string>;
  body?: string;
}

export interface LastByteOpts {
  host: string;
  port: number;
  tls: boolean;
  timeoutMs: number;
}

export async function lastByteSync(
  opts: LastByteOpts,
  requests: LastByteRequest[]
): Promise<RaceResponse[]> {
  const sockets: SocketState[] = [];
  for (const req of requests) {
    const raw = buildRaw(opts.host, req);
    const state = openSocket(opts, raw);
    sockets.push(state);
  }

  await Promise.all(sockets.map((s) => s.ready));

  for (const s of sockets) {
    s.socket.write(s.headBytes);
  }

  await new Promise<void>((resolve) => setImmediate(resolve));

  for (const s of sockets) {
    s.socket.write(s.lastByte);
  }

  return Promise.all(sockets.map((s) => s.response));
}

interface SocketState {
  socket: net.Socket | tls.TLSSocket;
  ready: Promise<void>;
  headBytes: Buffer;
  lastByte: Buffer;
  response: Promise<RaceResponse>;
}

function openSocket(opts: LastByteOpts, raw: Buffer): SocketState {
  const start = Date.now();
  const socket = opts.tls
    ? tls.connect({
        host: opts.host,
        port: opts.port,
        servername: opts.host,
        rejectUnauthorized: false
      })
    : net.connect({ host: opts.host, port: opts.port });

  const ready = new Promise<void>((resolve, reject) => {
    const onReady = () => resolve();
    const onError = (err: Error) => reject(err);
    socket.once(opts.tls ? "secureConnect" : "connect", onReady);
    socket.once("error", onError);
  });

  const headBytes = raw.subarray(0, raw.length - 1);
  const lastByte = raw.subarray(raw.length - 1);

  const response: Promise<RaceResponse> = new Promise((resolve) => {
    const chunks: Buffer[] = [];
    let settled = false;
    socket.setTimeout(opts.timeoutMs);
    const settle = () => {
      if (settled) return;
      settled = true;
      try { socket.destroy(); } catch { /* swallow */ }
      resolve(parseResponse(Buffer.concat(chunks), Date.now() - start));
    };
    socket.on("data", (chunk: Buffer) => chunks.push(chunk));
    socket.on("end", settle);
    socket.on("close", settle);
    socket.on("timeout", settle);
    socket.on("error", settle);
  });

  return { socket, ready, headBytes, lastByte, response };
}

function buildRaw(host: string, req: LastByteRequest): Buffer {
  const body = req.body ?? "";
  const headers: Record<string, string> = {
    Host: host,
    Connection: "close",
    "Content-Length": String(Buffer.byteLength(body)),
    ...req.headers
  };
  const lines = [`${req.method} ${req.path} HTTP/1.1`];
  for (const [k, v] of Object.entries(headers)) lines.push(`${k}: ${v}`);
  lines.push("", body);
  return Buffer.from(lines.join("\r\n"), "utf8");
}

function parseResponse(buf: Buffer, elapsedMs: number): RaceResponse {
  const sep = buf.indexOf("\r\n\r\n");
  const headPart = sep >= 0 ? buf.subarray(0, sep).toString("latin1") : buf.toString("latin1");
  const body = sep >= 0 ? buf.subarray(sep + 4).toString("utf8") : "";
  const lines = headPart.split(/\r?\n/);
  const statusLine = lines[0] ?? "";
  const statusMatch = statusLine.match(/HTTP\/\d\.\d\s+(\d{3})/);
  const status = statusMatch ? Number(statusMatch[1]) : 0;
  const headers: Record<string, string> = {};
  for (const line of lines.slice(1)) {
    const idx = line.indexOf(":");
    if (idx <= 0) continue;
    headers[line.slice(0, idx).trim().toLowerCase()] = line.slice(idx + 1).trim();
  }
  return { status, headers, body, elapsedMs };
}
