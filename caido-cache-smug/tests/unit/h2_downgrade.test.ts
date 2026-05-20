// tests/unit/h2_downgrade.test.ts
import { describe, it, expect } from "vitest";
import { canProbeH2 } from "../../src/modules/smuggling/h2_downgrade";

describe("h2_downgrade", () => {
  it("reports unavailable when target advertises only HTTP/1.1", () => {
    expect(canProbeH2({ alpnProtocols: ["http/1.1"] })).toBe(false);
  });
  it("reports available when h2 in ALPN", () => {
    expect(canProbeH2({ alpnProtocols: ["h2", "http/1.1"] })).toBe(true);
  });
});
