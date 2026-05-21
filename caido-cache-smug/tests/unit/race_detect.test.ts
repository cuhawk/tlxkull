import { describe, it, expect } from "vitest";
import { classify, type RaceResponse } from "../../src/modules/race/detect";

function r(status: number, body: string, elapsedMs = 10): RaceResponse {
  return { status, headers: {}, body, elapsedMs };
}

describe("classify", () => {
  it("returns high on diverse responses + state-change marker", () => {
    const serial = Array.from({ length: 5 }, () => r(200, '{"ok":true,"coupon":"applied"}'));
    const parallel = [
      r(200, '{"ok":true,"coupon":"applied"}'),
      r(200, '{"ok":true,"coupon":"applied"}'),
      r(409, '{"error":"already applied"}'),
      r(409, '{"error":"already applied"}')
    ];
    const v = classify(serial, parallel);
    expect(v.confidence).toBe("high");
    expect(v.signal).toMatch(/state-marker|diverse|json-marker/);
  });

  it("returns high on JSON marker leak", () => {
    const serial = Array.from({ length: 5 }, () => r(200, '{"id":"abc1234567"}'));
    const parallel = [
      r(200, '{"id":"abc1234567"}'),
      r(200, '{"id":"def2345678"}'),
      r(200, '{"id":"ghi3456789"}'),
      r(200, '{"id":"jkl4567890"}')
    ];
    const v = classify(serial, parallel);
    expect(v.confidence).toBe("high");
    expect(v.signal).toContain("json-marker-leak:id");
  });

  it("returns lead when parallel matches serial", () => {
    const serial = Array.from({ length: 5 }, () => r(200, '{"ok":true}'));
    const parallel = Array.from({ length: 20 }, () => r(200, '{"ok":true}'));
    const v = classify(serial, parallel);
    expect(v.confidence).toBe("lead");
    expect(v.signal).toBe("no-divergence");
  });

  it("returns medium on status divergence without state marker", () => {
    const serial = Array.from({ length: 5 }, () => r(200, "ok"));
    const parallel = [r(200, "ok"), r(200, "ok"), r(500, "boom"), r(500, "boom")];
    const v = classify(serial, parallel);
    expect(["medium", "high"]).toContain(v.confidence);
  });

  it("returns lead on empty volley", () => {
    const v = classify([], []);
    expect(v.confidence).toBe("lead");
  });
});
