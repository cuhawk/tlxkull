// tests/unit/unkeyed_header.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepUnkeyedHeaders } from "../../src/modules/cache_poison/unkeyed_header";

describe("sweepUnkeyedHeaders", () => {
  it("returns finding when canary reflected in body + cache HIT confirmed on follow-up", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: { "x-cache": "MISS" }, body: '<base href="https://cnry-xx.evil.test/">' } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT", age: "3" }, body: '<base href="https://cnry-xx.evil.test/">' } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, caido_request_id: "b", id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "", status: 200 };
    const findings = await sweepUnkeyedHeaders(sender, endpoint, baseline, ["X-Forwarded-Host"], () => "cnry-xx.evil.test", () => "cb1");
    expect(findings).toHaveLength(1);
    expect(findings[0].confidence).toBe("high");
    expect(findings[0].subtype).toBe("unkeyed-header");
  });
});
