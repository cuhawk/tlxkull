import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import { extractMarkers } from "../../core/marker.js";
import { cacheBuster } from "../../core/rand.js";
import { sweepPathAppend } from "./path_append.js";
import { sweepDelimiter } from "./delimiter.js";
import { sweepCacheBusterParam } from "./cache_buster_param.js";
import { sweepTraversalInKey } from "./traversal_in_key.js";
import extensions from "../../../data/static_extensions.json" with { type: "json" };
import delimiters from "../../../data/delimiters.json" with { type: "json" };

const TRAVERSAL_INNERS = ["/api/auth/session", "/api/user", "/profile", "/me"];

export async function runCacheDeception(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage
): Promise<Finding[]> {
  const markers = extractMarkers(baseline.body);
  if (markers.length === 0) return [];
  const out: Finding[] = [];
  out.push(...(await sweepPathAppend(sender, endpoint, baseline, markers, extensions as string[])));
  out.push(...(await sweepDelimiter(sender, endpoint, baseline, markers, delimiters as string[])));
  out.push(...(await sweepCacheBusterParam(sender, endpoint, baseline, markers, cacheBuster)));
  out.push(...(await sweepTraversalInKey(sender, endpoint, baseline, markers, TRAVERSAL_INNERS)));
  return out;
}
