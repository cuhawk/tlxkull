import { useEffect, useMemo, useRef, useState } from "react";
import { getChains, getVerdicts } from "./api";
import { ChainTable } from "./components/ChainTable";
import { FilterRail } from "./components/FilterRail";
import { Graph } from "./components/Graph";
import { NodeDetail } from "./components/NodeDetail";
import { buildGraphModel, type Chain } from "./state/chains";
import { applyFilters, type FilterState, type VerdictRecord } from "./state/filters";
import { pulsePath } from "./util/animate";

const DEFAULT_FILTERS: FilterState = {
  sourceTaxonomies: new Set(),
  sinkTaxonomies: new Set(),
  files: new Set(),
  scoreMin: 70,
  depthMax: 20,
  verdicts: new Set(["tp", "fp", "undet", "none"]),
};

export function App() {
  const params = new URLSearchParams(window.location.search);
  const target = params.get("target") ?? "";
  const initialSelected = Number(params.get("selected") ?? "") || null;

  const [chains, setChains] = useState<Chain[]>([]);
  const [verdicts, setVerdicts] = useState<Record<string, VerdictRecord>>({});
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [selectedChainId, setSelectedChainId] = useState<number | null>(initialSelected);
  const [selectedQname, setSelectedQname] = useState<string | null>(null);
  const [layout, setLayout] = useState<"cose-bilkent" | "dagre">("cose-bilkent");
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set());
  const [highlightedEdges, setHighlightedEdges] = useState<Set<string>>(new Set());
  const pulserRef = useRef<(id: string) => void>(() => {});

  useEffect(() => {
    if (!target) return;
    getChains(target).then(setChains).catch((e) => console.error(e));
    getVerdicts(target).then(setVerdicts).catch((e) => console.error(e));
  }, [target]);

  const verdictByChainNum = useMemo(() => {
    const out: Record<number, { verdict: "tp" | "fp" | "undet" }> = {};
    for (const [k, v] of Object.entries(verdicts)) out[Number(k)] = { verdict: v.verdict };
    return out;
  }, [verdicts]);

  const filteredChains = useMemo(
    () => applyFilters(chains, filters, verdictByChainNum),
    [chains, filters, verdictByChainNum],
  );

  const model = useMemo(() => buildGraphModel(filteredChains), [filteredChains]);

  const selectedChain = selectedChainId != null
    ? filteredChains.find((c) => c.id === selectedChainId) ?? null
    : null;

  useEffect(() => {
    if (!selectedChain) {
      setHighlightedNodes(new Set());
      setHighlightedEdges(new Set());
      return;
    }
    const nodes = new Set(selectedChain.path);
    const edges = new Set<string>();
    for (let i = 0; i < selectedChain.path.length - 1; i++) {
      edges.add(`${selectedChain.path[i]}>>${selectedChain.path[i + 1]}`);
    }
    setHighlightedNodes(nodes);
    setHighlightedEdges(edges);
  }, [selectedChain]);

  // Auto-animate on URL ?selected=<id>
  const autoAnimatedRef = useRef(false);
  useEffect(() => {
    if (autoAnimatedRef.current || initialSelected == null || filteredChains.length === 0) return;
    const ch = filteredChains.find((c) => c.id === initialSelected);
    if (!ch) return;
    autoAnimatedRef.current = true;
    pulsePath(ch.path, (id) => pulserRef.current(id)).catch(() => {});
  }, [filteredChains, initialSelected]);

  function animate(chainId: number) {
    const ch = filteredChains.find((c) => c.id === chainId);
    if (!ch) return;
    pulsePath(ch.path, (id) => pulserRef.current(id)).catch(() => {});
  }

  if (!target) {
    return <div className="p-4">missing ?target=&lt;name&gt; query param</div>;
  }

  return (
    <div className="grid h-screen" style={{ gridTemplateColumns: "240px 1fr 360px", gridTemplateRows: "40px 1fr 240px" }}>
      <header className="col-span-3 flex items-center px-3 gap-4 border-b border-zinc-800 text-sm">
        <span className="font-semibold">taintview</span>
        <span className="text-zinc-400">target: {target}</span>
        <span className="text-zinc-400">chains: {filteredChains.length}/{chains.length}</span>
        <button
          className="ml-auto text-xs px-2 py-1 bg-zinc-800 rounded"
          onClick={() => setLayout(layout === "cose-bilkent" ? "dagre" : "cose-bilkent")}
        >
          layout: {layout}
        </button>
      </header>
      <div className="border-r border-zinc-800 overflow-hidden">
        <FilterRail chains={chains} filters={filters} setFilters={setFilters} />
      </div>
      <main className="overflow-hidden">
        <Graph
          model={model}
          layout={layout}
          highlightedNodes={highlightedNodes}
          highlightedEdges={highlightedEdges}
          onNodeClick={setSelectedQname}
          registerPulser={(p) => (pulserRef.current = p)}
        />
      </main>
      <div className="border-l border-zinc-800 overflow-hidden">
        <NodeDetail
          target={target}
          selectedChain={selectedChain}
          selectedQname={selectedQname}
          verdict={selectedChainId != null ? verdicts[String(selectedChainId)] : undefined}
          onVerdictSaved={(rec) =>
            setVerdicts((prev) => ({ ...prev, [String(rec.chain_id)]: rec }))
          }
        />
      </div>
      <div className="col-span-3 border-t border-zinc-800 overflow-hidden">
        <ChainTable
          chains={filteredChains}
          selectedId={selectedChainId}
          verdictByChain={verdicts}
          onSelect={setSelectedChainId}
          onAnimate={animate}
        />
      </div>
    </div>
  );
}
