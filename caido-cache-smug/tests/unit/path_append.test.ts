// tests/unit/path_append.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepPathAppend } from "../../src/modules/cache_deception/path_append";

describe("sweepPathAppend", () => {
  it("returns high-confidence when no-auth response contains marker", async () => {
    const sender = {
      send: vi.fn()
        .mockResolvedValueOnce({ requestId: "p1", response: { status: 200, headers: { "x-cache": "MISS" }, body: "alice@example.com" } })
        .mockResolvedValueOnce({ requestId: "p2", response: { status: 200, headers: { "x-cache": "HIT" }, body: "alice@example.com" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/account", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/account", headers: { cookie: "s=1" }, body: "", status: 200 };
    const markers = [{ kind: "email" as const, value: "alice@example.com" }];
    const findings = await sweepPathAppend(sender, endpoint, baseline, markers, [".css"]);
    expect(findings[0].confidence).toBe("high");
  });
});
