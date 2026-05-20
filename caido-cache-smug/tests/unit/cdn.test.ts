// tests/unit/cdn.test.ts
import { describe, it, expect } from "vitest";
import { fingerprintCdn } from "../../src/core/cdn";

describe("fingerprintCdn", () => {
  it("detects Cloudflare via CF-Ray", () => {
    expect(fingerprintCdn({ "cf-ray": "abc-EWR" })).toBe("cloudflare");
  });
  it("detects Akamai via Server", () => {
    expect(fingerprintCdn({ server: "AkamaiGHost" })).toBe("akamai");
  });
  it("returns null when unknown", () => {
    expect(fingerprintCdn({ server: "WeirdProxy/1.0" })).toBeNull();
  });
});
