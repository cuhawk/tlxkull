// tests/unit/markdown.test.ts
import { describe, it, expect } from "vitest";
import { renderReport } from "../../src/report/markdown";

describe("renderReport", () => {
  it("groups by confidence", () => {
    const md = renderReport({
      host: "x.test",
      ts: "2026-05-20T00:00:00Z",
      duration_ms: 12345,
      endpoints_probed: 10,
      probes_sent: 100,
      modules_run: ["cache-poison"],
      interrupted: false
    }, [
      { id: "a", module: "cache-poison", subtype: "unkeyed-header", endpoint: "GET /", primitive: {}, confidence: "high", evidence: {}, poc_curl: "curl x", wiki_ref: "w" },
      { id: "b", module: "cache-poison", subtype: "host-casing", endpoint: "GET /", primitive: {}, confidence: "low", evidence: {}, poc_curl: "curl y", wiki_ref: "w" }
    ]);
    expect(md).toMatch(/## High-confidence \(1\)/);
    expect(md).toMatch(/## Low-confidence \(1\)/);
  });
});
