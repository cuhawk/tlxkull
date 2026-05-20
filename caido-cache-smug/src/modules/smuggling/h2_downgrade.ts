import http2 from "node:http2";

export interface H2Capability { alpnProtocols: string[]; }

export function canProbeH2(cap: H2Capability): boolean {
  return cap.alpnProtocols.includes("h2");
}

export interface H2DowngradeResult { candidate: boolean; status?: number; error?: string; }

export async function probeH2Downgrade(target: { host: string; port: number }): Promise<H2DowngradeResult> {
  return new Promise((resolve) => {
    const client = http2.connect(`https://${target.host}:${target.port}`, { rejectUnauthorized: false });
    let resolved = false;
    const finish = (r: H2DowngradeResult) => { if (resolved) return; resolved = true; try { client.close(); } catch {} resolve(r); };
    client.on("error", (e) => finish({ candidate: false, error: e.message }));
    const req = client.request({
      ":method": "POST",
      ":path": "/",
      ":authority": target.host,
      "content-length": "5",
      "transfer-encoding": "chunked"
    });
    req.on("response", (h) => finish({ candidate: typeof h[":status"] === "number" && h[":status"] !== 400, status: h[":status"] as number }));
    req.on("error", (e) => finish({ candidate: false, error: e.message }));
    req.end("0\r\n\r\n");
    setTimeout(() => finish({ candidate: false, error: "timeout" }), 5000);
  });
}
