// tests/unit/traversal_in_key.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepTraversalInKey } from "../../src/modules/cache_deception/traversal_in_key";

describe("sweepTraversalInKey", () => {
  it("flags traversal payload when no-auth response leaks marker", async () => {
    const sender = {
      send: vi.fn().mockResolvedValue({ requestId: "r", response: { status: 200, headers: { "x-cache": "HIT" }, body: "alice@x.com" } })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/share/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/share/", headers: {}, body: "", status: 200 };
    const findings = await sweepTraversalInKey(sender, endpoint, baseline, [{ kind: "email", value: "alice@x.com" }], ["/api/auth/session"]);
    expect(findings[0].subtype).toBe("traversal-in-cache-key");
  });
});
