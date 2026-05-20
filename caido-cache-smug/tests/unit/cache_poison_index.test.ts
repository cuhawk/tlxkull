// tests/unit/cache_poison_index.test.ts
import { describe, it, expect, vi } from "vitest";
import { runCachePoison } from "../../src/modules/cache_poison";

describe("runCachePoison", () => {
  it("skips endpoint without cache layer", async () => {
    const sender = { send: vi.fn() } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "", status: 200 };
    const findings = await runCachePoison(sender, endpoint, baseline);
    expect(findings).toHaveLength(0);
  });
});
