// tests/unit/param_cloaking.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepParamCloaking } from "../../src/modules/cache_poison/param_cloaking";

describe("sweepParamCloaking", () => {
  it("emits finding when fat GET body param reflected and HIT confirmed", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: { "x-cache": "MISS" }, body: "callback=cnry" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT" }, body: "callback=cnry" } })
        .mockResolvedValueOnce({ requestId: "p3", response: { status: 200, headers: {}, body: "" } })
        .mockResolvedValueOnce({ requestId: "p4", response: { status: 200, headers: {}, body: "" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, caido_request_id: "b", id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "", status: 200 };
    const findings = await sweepParamCloaking(sender, endpoint, baseline, () => "cnry", () => "cb1");
    expect(findings.some((f) => f.subtype === "fat-get")).toBe(true);
  });
});
