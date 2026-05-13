import { describe, expect, it } from "vitest";
import { applyFilters, type FilterState } from "../state/filters";
import type { Chain } from "../state/chains";

const c = (overrides: Partial<Chain> = {}): Chain => ({
  id: 1,
  source: { qname: "a.js::s", file: "a.js", line: 1, taxonomy_id: "url_query" },
  sink: { qname: "b.js::k", file: "b.js", line: 2, taxonomy_id: "dom_innerHTML" },
  depth: 1,
  path: ["a.js::s", "b.js::k"],
  score: 80,
  scoring: {},
  variants: [],
  is_hot: false,
  reach: "unknown",
  ...overrides,
});

const base: FilterState = {
  sourceTaxonomies: new Set(),
  sinkTaxonomies: new Set(),
  files: new Set(),
  scoreMin: 0,
  depthMax: 99,
  verdicts: new Set(["tp", "fp", "undet", "none"]),
};

describe("applyFilters", () => {
  it("returns all chains when filters are wide open", () => {
    const xs = [c({ id: 1 }), c({ id: 2, score: 30 })];
    expect(applyFilters(xs, base, {})).toHaveLength(2);
  });

  it("filters by sourceTaxonomies (empty set = no filter)", () => {
    const xs = [
      c({ id: 1, source: { qname: "a", file: "a", line: 1, taxonomy_id: "url_query" } }),
      c({ id: 2, source: { qname: "a", file: "a", line: 1, taxonomy_id: "JSON_parse_call" } }),
    ];
    const out = applyFilters(xs, { ...base, sourceTaxonomies: new Set(["url_query"]) }, {});
    expect(out.map((c) => c.id)).toEqual([1]);
  });

  it("filters by scoreMin and depthMax", () => {
    const xs = [c({ id: 1, score: 50, depth: 2 }), c({ id: 2, score: 90, depth: 6 })];
    const out = applyFilters(xs, { ...base, scoreMin: 70, depthMax: 5 }, {});
    expect(out).toHaveLength(0);
  });

  it("filters by verdict using the verdicts map", () => {
    const xs = [c({ id: 1 }), c({ id: 2 })];
    const out = applyFilters(
      xs,
      { ...base, verdicts: new Set(["tp"]) },
      { 1: { verdict: "tp" }, 2: { verdict: "fp" } },
    );
    expect(out.map((c) => c.id)).toEqual([1]);
  });

  it("treats unrecorded chains as verdict 'none'", () => {
    const xs = [c({ id: 1 }), c({ id: 2 })];
    const out = applyFilters(xs, { ...base, verdicts: new Set(["none"]) }, { 1: { verdict: "fp" } });
    expect(out.map((c) => c.id)).toEqual([2]);
  });
});
