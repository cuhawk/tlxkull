import { describe, expect, it } from "vitest";
import { buildGraphModel, type Chain } from "../state/chains";

const c = (id: number, path: string[]): Chain => ({
  id,
  source: { qname: path[0], file: "f.js", line: 1, taxonomy_id: "url_query" },
  sink: { qname: path[path.length - 1], file: "g.js", line: 2, taxonomy_id: "dom_innerHTML" },
  depth: path.length - 1,
  path,
  score: 80,
  scoring: {},
  variants: [],
  is_hot: true,
  reach: "unknown",
});

describe("buildGraphModel", () => {
  it("dedupes nodes across chains and tags source/sink/hop roles", () => {
    const chains = [c(1, ["A", "M", "Z"]), c(2, ["B", "M", "Z"])];
    const g = buildGraphModel(chains);
    expect(new Set(g.nodes.map((n) => n.id))).toEqual(new Set(["A", "B", "M", "Z"]));
    const role = (id: string) => g.nodes.find((n) => n.id === id)!.role;
    expect(role("A")).toBe("source");
    expect(role("B")).toBe("source");
    expect(role("M")).toBe("hop");
    expect(role("Z")).toBe("sink");
  });

  it("marks a node both when it is source in one chain and sink in another", () => {
    const chains = [c(1, ["A", "B"]), c(2, ["B", "C"])];
    const g = buildGraphModel(chains);
    const role = (id: string) => g.nodes.find((n) => n.id === id)!.role;
    expect(role("B")).toBe("both");
  });

  it("aggregates edge weights as count of chains that traverse the edge", () => {
    const chains = [c(1, ["A", "M", "Z"]), c(2, ["B", "M", "Z"]), c(3, ["C", "M", "Z"])];
    const g = buildGraphModel(chains);
    const mz = g.edges.find((e) => e.source === "M" && e.target === "Z")!;
    expect(mz.weight).toBe(3);
    expect(new Set(mz.chainIds)).toEqual(new Set([1, 2, 3]));
  });
});
