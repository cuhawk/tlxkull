// tests/unit/marker.test.ts
import { describe, it, expect } from "vitest";
import { extractMarkers } from "../../src/core/marker";

describe("extractMarkers", () => {
  it("finds email", () => {
    const m = extractMarkers("Welcome alice@example.com");
    expect(m).toContainEqual({ kind: "email", value: "alice@example.com" });
  });
  it("finds csrf in JSON", () => {
    const body = JSON.stringify({ csrf_token: "AAAAAAAAAAAAAAAAAAAAAA" });
    const m = extractMarkers(body);
    expect(m.find((x) => x.kind === "csrf")?.value).toBe("AAAAAAAAAAAAAAAAAAAAAA");
  });
  it("finds JSON user id", () => {
    const m = extractMarkers('{"id": 12345, "name": "alice"}');
    expect(m.find((x) => x.kind === "id")?.value).toBe("12345");
  });
});
