// tests/unit/rand.test.ts
import { describe, it, expect } from "vitest";
import { canary, cacheBuster, randHex } from "../../src/core/rand";

describe("rand", () => {
  it("canary returns unique subdomain pattern", () => {
    const a = canary();
    const b = canary();
    expect(a).toMatch(/^cnry-[a-z0-9]{8}\.evil\.test$/);
    expect(a).not.toBe(b);
  });

  it("cacheBuster returns 8-hex string", () => {
    expect(cacheBuster()).toMatch(/^[a-f0-9]{8}$/);
  });

  it("randHex(n) returns hex of length n", () => {
    expect(randHex(16)).toMatch(/^[a-f0-9]{16}$/);
  });
});
