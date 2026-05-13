export type TaintEnd = {
  qname: string;
  file: string;
  line: number;
  taxonomy_id: string;
};

export type Chain = {
  id: number;
  source: TaintEnd;
  sink: TaintEnd;
  depth: number;
  path: string[];
  score: number;
  scoring: Record<string, unknown>;
  variants: unknown[];
  is_hot: boolean;
  reach: "reachable" | "unreachable" | "unknown";
};

export type GraphNode = {
  id: string;
  role: "source" | "sink" | "hop" | "both";
  chainCount: number;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  weight: number;
  chainIds: number[];
};

export type GraphModel = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export function buildGraphModel(chains: Chain[]): GraphModel {
  const isSource = new Set<string>();
  const isSink = new Set<string>();
  const isHop = new Set<string>();
  const chainsByNode = new Map<string, Set<number>>();
  const edgeMap = new Map<string, { source: string; target: string; chainIds: Set<number> }>();

  for (const ch of chains) {
    if (ch.path.length === 0) continue;
    const src = ch.path[0];
    const sink = ch.path[ch.path.length - 1];
    isSource.add(src);
    isSink.add(sink);
    for (let i = 1; i < ch.path.length - 1; i++) isHop.add(ch.path[i]);
    for (const node of ch.path) {
      if (!chainsByNode.has(node)) chainsByNode.set(node, new Set());
      chainsByNode.get(node)!.add(ch.id);
    }
    for (let i = 0; i < ch.path.length - 1; i++) {
      const a = ch.path[i];
      const b = ch.path[i + 1];
      const key = `${a}>>${b}`;
      if (!edgeMap.has(key)) edgeMap.set(key, { source: a, target: b, chainIds: new Set() });
      edgeMap.get(key)!.chainIds.add(ch.id);
    }
  }

  const allIds = new Set<string>([...isSource, ...isSink, ...isHop]);
  const nodes: GraphNode[] = [...allIds].map((id) => {
    const src = isSource.has(id);
    const snk = isSink.has(id);
    let role: GraphNode["role"];
    if (src && snk) role = "both";
    else if (src) role = "source";
    else if (snk) role = "sink";
    else role = "hop";
    return { id, role, chainCount: chainsByNode.get(id)?.size ?? 0 };
  });

  const edges: GraphEdge[] = [...edgeMap.entries()].map(([key, e]) => ({
    id: key,
    source: e.source,
    target: e.target,
    chainIds: [...e.chainIds],
    weight: e.chainIds.size,
  }));

  return { nodes, edges };
}
