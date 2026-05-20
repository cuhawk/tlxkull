// tests/unit/delimiter.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepDelimiter } from "../../src/modules/cache_deception/delimiter";

describe("sweepDelimiter", () => {
  it("emits finding when delimiter variant leaks marker", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: {}, body: "alice@x.com" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT" }, body: "alice@x.com" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/profile", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/profile", headers: { cookie: "s=1" }, body: "", status: 200 };
    const findings = await sweepDelimiter(sender, endpoint, baseline, [{ kind: "email", value: "alice@x.com" }], [";.css"]);
    expect(findings[0].subtype).toBe("delimiter");
  });
});
