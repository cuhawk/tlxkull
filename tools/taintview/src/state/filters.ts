import type { Chain } from "./chains";

export type Verdict = "tp" | "fp" | "undet" | "none";

export type VerdictRecord = {
  verdict: Exclude<Verdict, "none">;
  note?: string;
  ts?: string;
  chain_id?: number;
};

export type FilterState = {
  sourceTaxonomies: Set<string>;
  sinkTaxonomies: Set<string>;
  files: Set<string>;
  scoreMin: number;
  depthMax: number;
  verdicts: Set<Verdict>;
};

export function applyFilters(
  chains: Chain[],
  f: FilterState,
  verdictByChain: Record<number, { verdict: Exclude<Verdict, "none"> }>,
): Chain[] {
  return chains.filter((c) => {
    if (c.score < f.scoreMin) return false;
    if (c.depth > f.depthMax) return false;
    if (f.sourceTaxonomies.size > 0 && !f.sourceTaxonomies.has(c.source.taxonomy_id)) return false;
    if (f.sinkTaxonomies.size > 0 && !f.sinkTaxonomies.has(c.sink.taxonomy_id)) return false;
    if (f.files.size > 0 && !(f.files.has(c.source.file) || f.files.has(c.sink.file))) return false;
    const recorded = verdictByChain[c.id]?.verdict;
    const v: Verdict = recorded ?? "none";
    if (!f.verdicts.has(v)) return false;
    return true;
  });
}
