// tests/unit/caido_client.test.ts
import { describe, it, expect, vi } from "vitest";
import { CaidoClient } from "../../src/caido/client";

describe("CaidoClient", () => {
  it("builds Authorization header from PAT", () => {
    const c = new CaidoClient({ url: "http://localhost:8080", token: "tok-123" });
    expect(c.authHeader()).toBe("Bearer tok-123");
  });

  it("throws on missing token", () => {
    // @ts-expect-error
    expect(() => new CaidoClient({ url: "http://x" })).toThrow(/token/);
  });
});
