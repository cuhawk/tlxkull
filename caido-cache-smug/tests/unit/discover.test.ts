// tests/unit/discover.test.ts
import { describe, it, expect } from "vitest";
import { dedupeEndpoints, buildHostQuery } from "../../src/caido/discover";

describe("discover helpers", () => {
  it("buildHostQuery returns HTTPQL string", () => {
    expect(buildHostQuery("api.acme.test")).toBe('req.host.cont:"api.acme.test"');
  });
  it("dedupe by method + path + sorted query keys", () => {
    const reqs = [
      { id: "1", method: "GET", host: "x", path: "/a", query: { a: "1", b: "2" }, caido_request_id: "1" },
      { id: "2", method: "GET", host: "x", path: "/a", query: { b: "5", a: "9" }, caido_request_id: "2" },
      { id: "3", method: "GET", host: "x", path: "/b", query: {}, caido_request_id: "3" }
    ];
    const out = dedupeEndpoints(reqs);
    expect(out).toHaveLength(2);
  });
});
