// tests/unit/persistence_loop.test.ts
import { describe, it, expect, vi } from "vitest";
import { measurePersistence } from "../../src/modules/cache_poison/persistence_loop";

describe("measurePersistence", () => {
  it("reseeds N times and reports survival seconds", async () => {
    const sender = {
      send: vi.fn().mockResolvedValue({
        requestId: "r",
        response: { status: 200, headers: { "x-cache": "HIT", age: "5" }, body: "poison" }
      })
    } as any;
    const result = await measurePersistence(sender, "https://x.test/asset.js", { "X-Forwarded-Host": "evil" }, 3);
    expect(result.reseeds).toBe(3);
    expect(result.survivalSeconds).toBeGreaterThanOrEqual(0);
  });
});
