// tests/unit/url_parser_cp.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepUrlParser } from "../../src/modules/cache_poison/url_parser";

describe("sweepUrlParser", () => {
  it("flags candidates when origin still serves dynamic content + cache HIT under static-looking key", async () => {
    const sender = {
      send: vi.fn().mockResolvedValue({
        requestId: "r",
        response: { status: 200, headers: { "x-cache": "HIT", "content-type": "text/html" }, body: '{"profile":"alice"}' }
      })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/api/profile", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/api/profile", headers: {}, body: "", status: 200 };
    const findings = await sweepUrlParser(sender, endpoint, baseline, [";.js"]);
    expect(findings).toHaveLength(1);
    expect(findings[0].subtype).toBe("static-path-deception");
  });
});
