// tests/unit/cache_buster_param.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepCacheBusterParam } from "../../src/modules/cache_deception/cache_buster_param";

describe("sweepCacheBusterParam", () => {
  it("flags when no-auth re-fetch returns marker", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: {}, body: "alice@x.com" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT" }, body: "alice@x.com" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/api/me", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/api/me", headers: { cookie: "s=1" }, body: "", status: 200 };
    const findings = await sweepCacheBusterParam(sender, endpoint, baseline, [{ kind: "email", value: "alice@x.com" }], () => "cb1");
    expect(findings[0].confidence).toBe("high");
  });
});
