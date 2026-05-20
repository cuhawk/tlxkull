import { describe, it, expect } from "vitest";
import { startMockTarget } from "../fixtures/mock_target.js";
import { sweepUnkeyedHeaders } from "../../src/modules/cache_poison/unkeyed_header.js";
import { request } from "undici";
import type { CaidoSender } from "../../src/caido/send.js";

class DirectSender {
  constructor(private base: string) {}
  async send(req: { url?: string; method?: string; headers: Record<string, string>; body: string }) {
    const url = (req.url ?? this.base).replace(/^https:/, "http:");
    const r = await request(url, {
      method: req.method ?? "GET",
      headers: req.headers,
      body: req.body || undefined
    });
    const body = await r.body.text();
    return {
      requestId: Math.random().toString(36).slice(2),
      response: {
        status: r.statusCode,
        headers: Object.fromEntries(
          Object.entries(r.headers).map(([k, v]) => [k, String(v)])
        ),
        body
      }
    };
  }
}

describe("end-to-end unkeyed-header against mock target", () => {
  it("detects X-Forwarded-Host reflection", async () => {
    const t = await startMockTarget({ reflectUnkeyed: true });
    const sender = new DirectSender(`http://127.0.0.1:${t.port}`) as unknown as CaidoSender;
    const endpoint = {
      method: "GET",
      host: `127.0.0.1:${t.port}`,
      path: "/",
      query: {},
      id: "b",
      caido_request_id: "b"
    };
    const baseline = {
      method: "GET",
      url: `http://127.0.0.1:${t.port}/`,
      headers: {},
      body: "",
      status: 200
    };
    const findings = await sweepUnkeyedHeaders(
      sender,
      endpoint,
      baseline,
      ["X-Forwarded-Host"],
      () => "cnry-int.evil.test",
      () => "cbint"
    );
    expect(findings).toHaveLength(1);
    t.server.close();
  });
});
