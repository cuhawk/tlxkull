import type { Endpoint } from "../types.js";
import type { CaidoClient } from "./client.js";

export function buildHostQuery(host: string): string {
  return `req.host.cont:"${host}"`;
}

export function dedupeEndpoints(endpoints: Endpoint[]): Endpoint[] {
  const seen = new Set<string>();
  const out: Endpoint[] = [];
  for (const e of endpoints) {
    const qk = Object.keys(e.query).sort().join(",");
    const key = `${e.method} ${e.host} ${e.path} ${qk}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(e);
  }
  return out;
}

const LIST_QUERY = `
  query ListRequests($filter: String!, $first: Int!) {
    requests(filter: $filter, first: $first) {
      edges { node { id method host path query } }
    }
  }
`;

interface RawEdge { node: { id: string; method: string; host: string; path: string; query: string } }

export async function discoverEndpoints(
  client: CaidoClient,
  host: string,
  max: number
): Promise<Endpoint[]> {
  const data = await client.graphql<{ requests: { edges: RawEdge[] } }>(LIST_QUERY, {
    filter: buildHostQuery(host),
    first: max
  });
  const raw: Endpoint[] = data.requests.edges.map((e) => ({
    id: e.node.id,
    method: e.node.method,
    host: e.node.host,
    path: e.node.path,
    query: parseQuery(e.node.query),
    caido_request_id: e.node.id
  }));
  return dedupeEndpoints(raw);
}

function parseQuery(q: string): Record<string, string> {
  if (!q) return {};
  const out: Record<string, string> = {};
  for (const part of q.replace(/^\?/, "").split("&")) {
    if (!part) continue;
    const [k, v = ""] = part.split("=");
    out[decodeURIComponent(k)] = decodeURIComponent(v);
  }
  return out;
}
