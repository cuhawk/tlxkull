// tests/unit/diff.test.ts
import { describe, it, expect } from "vitest";
import { diffResponses, bodyParity } from "../../src/core/diff";

describe("diff", () => {
  it("flags status change", () => {
    const d = diffResponses({ status: 200, headers: {}, body: "" }, { status: 302, headers: {}, body: "" });
    expect(d.statusChanged).toBe(true);
  });
  it("computes body parity", () => {
    expect(bodyParity("aaaaaaaaaa", "aaaaaaaaaa")).toBe(1);
    expect(bodyParity("aaaaaaaaaa", "bbbbbbbbbb")).toBeLessThan(0.5);
  });
  it("respects ignore_body_regex", () => {
    const d = diffResponses(
      { status: 200, headers: {}, body: '{"t":1}' },
      { status: 200, headers: {}, body: '{"t":2}' },
      { ignoreBodyRegex: [/"t":\d+/] }
    );
    expect(d.bodyChanged).toBe(false);
  });
});
