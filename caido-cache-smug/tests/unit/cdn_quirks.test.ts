// tests/unit/cdn_quirks.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepCdnQuirks } from "../../src/modules/cache_poison/cdn_quirks";

describe("sweepCdnQuirks", () => {
  it("flags host-casing mismatch when bodies differ", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: {}, body: "lowercase" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: {}, body: "mixedcase" } })
        .mockResolvedValueOnce({ requestId: "p3", response: { status: 405, headers: {}, body: "" } })
        .mockResolvedValue({ requestId: "px", response: { status: 200, headers: {}, body: "" } })
    } as any;
    const endpoint = { method: "GET", host: "target.com", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://target.com/", headers: {}, body: "", status: 200 };
    const findings = await sweepCdnQuirks(sender, endpoint, baseline);
    expect(findings.find((f) => f.subtype === "host-casing")).toBeTruthy();
  });
});
