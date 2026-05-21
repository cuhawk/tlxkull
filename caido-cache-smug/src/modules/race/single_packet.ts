import http2 from "node:http2";
import type { RaceResponse } from "./detect.js";

export interface PacketRequest {
  method: string;
  path: string;
  headers: Record<string, string>;
  body?: string;
}

export interface SinglePacketOpts {
  host: string;
  port: number;
  timeoutMs: number;
  rejectUnauthorized?: boolean;
}

export async function singlePacketSend(
  opts: SinglePacketOpts,
  requests: PacketRequest[]
): Promise<RaceResponse[]> {
  const url = `https://${opts.host}:${opts.port}`;
  const session = http2.connect(url, { rejectUnauthorized: opts.rejectUnauthorized ?? false });

  const sessionReady = new Promise<void>((resolve, reject) => {
    const onConnect = () => { cleanup(); resolve(); };
    const onError = (err: Error) => { cleanup(); reject(err); };
    const cleanup = () => {
      session.off("connect", onConnect);
      session.off("error", onError);
    };
    session.once("connect", onConnect);
    session.once("error", onError);
  });

  try {
    await Promise.race([
      sessionReady,
      timeout(opts.timeoutMs, "h2-connect-timeout")
    ]);
  } catch (err) {
    try { session.close(); } catch { /* swallow */ }
    throw err;
  }

  const start = Date.now();
  const streams: http2.ClientHttp2Stream[] = [];
  const pending: Promise<RaceResponse>[] = [];

  for (const req of requests) {
    const reqHeaders = {
      ":method": req.method,
      ":path": req.path,
      ":scheme": "https",
      ":authority": opts.host,
      ...req.headers
    };
    const stream = session.request(reqHeaders, { endStream: false });
    streams.push(stream);
    pending.push(collectResponse(stream, opts.timeoutMs));
  }

  const socket = session.socket as { cork?: () => void; uncork?: () => void } | undefined;
  if (socket?.cork) socket.cork();
  try {
    for (let i = 0; i < streams.length; i++) {
      const body = requests[i].body ?? "";
      streams[i].end(body);
    }
  } finally {
    if (socket?.uncork) socket.uncork();
  }

  let responses: RaceResponse[];
  try {
    responses = await Promise.all(pending);
  } finally {
    try { session.close(); } catch { /* swallow */ }
  }
  const totalElapsed = Date.now() - start;
  return responses.map((r) => ({ ...r, elapsedMs: r.elapsedMs || totalElapsed }));
}

function collectResponse(
  stream: http2.ClientHttp2Stream,
  timeoutMs: number
): Promise<RaceResponse> {
  return new Promise((resolve) => {
    const start = Date.now();
    let status = 0;
    const headers: Record<string, string> = {};
    const chunks: Buffer[] = [];
    let settled = false;

    const settle = () => {
      if (settled) return;
      settled = true;
      resolve({
        status,
        headers,
        body: Buffer.concat(chunks).toString("utf8"),
        elapsedMs: Date.now() - start
      });
    };

    stream.setTimeout(timeoutMs, () => {
      try { stream.close(http2.constants.NGHTTP2_CANCEL); } catch { /* swallow */ }
      settle();
    });

    stream.on("response", (hdrs) => {
      for (const [k, v] of Object.entries(hdrs)) {
        if (k === ":status") status = Number(v);
        else if (typeof v === "string") headers[k] = v;
        else if (Array.isArray(v)) headers[k] = v.join(",");
      }
    });
    stream.on("data", (c: Buffer) => chunks.push(c));
    stream.on("end", settle);
    stream.on("error", settle);
    stream.on("close", settle);
  });
}

function timeout(ms: number, msg: string): Promise<never> {
  return new Promise((_, reject) => setTimeout(() => reject(new Error(msg)), ms));
}
