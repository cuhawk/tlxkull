import { describe, it, expect } from "vitest";
import { Throttle } from "../../src/core/throttle";

describe("Throttle", () => {
  it("admits N tokens immediately at start", async () => {
    const t = new Throttle({ rps: 10, burst: 5 });
    const start = Date.now();
    for (let i = 0; i < 5; i++) await t.acquire();
    expect(Date.now() - start).toBeLessThan(50);
  });

  it("paces beyond burst", async () => {
    const t = new Throttle({ rps: 10, burst: 2 });
    const start = Date.now();
    for (let i = 0; i < 4; i++) await t.acquire();
    expect(Date.now() - start).toBeGreaterThanOrEqual(180);
  });

  it("respects hard floor", async () => {
    const t = new Throttle({ rps: 100, burst: 1, hardFloorRps: 1 });
    const start = Date.now();
    await t.acquire();
    await t.acquire();
    expect(Date.now() - start).toBeGreaterThanOrEqual(900);
  });
});
