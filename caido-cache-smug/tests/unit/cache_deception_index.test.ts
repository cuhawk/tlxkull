// tests/unit/cache_deception_index.test.ts
import { describe, it, expect, vi } from "vitest";
import { runCacheDeception } from "../../src/modules/cache_deception";

describe("runCacheDeception", () => {
  it("skips endpoint without auth markers", async () => {
    const sender = { send: vi.fn() } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "no markers here", status: 200 };
    const findings = await runCacheDeception(sender, endpoint, baseline);
    expect(findings).toHaveLength(0);
  });
});
