import { describe, it, expect } from "vitest";
import { FindingSchema, ConfidenceSchema, ModuleSchema } from "../../src/types";

describe("FindingSchema", () => {
  it("accepts a well-formed finding", () => {
    const valid = {
      id: "cp-001",
      module: "cache-poison",
      subtype: "unkeyed-header",
      endpoint: "GET /en/index",
      primitive: { header: "X-Forwarded-Host" },
      confidence: "high",
      evidence: { baseline_id: "raw/baselines/8f.json", probe_id: "raw/probes/91.json" },
      poc_curl: "curl -H ...",
      wiki_ref: "wiki/techniques/cache-poisoning/unkeyed-header.md"
    };
    expect(() => FindingSchema.parse(valid)).not.toThrow();
  });

  it("rejects invalid confidence", () => {
    expect(() => ConfidenceSchema.parse("bogus")).toThrow();
  });

  it("rejects unknown module", () => {
    expect(() => ModuleSchema.parse("xss")).toThrow();
  });
});
