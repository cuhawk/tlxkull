import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import type { CaidoSender } from "../../caido/send.js";
import { hasCacheLayer } from "../../core/cache.js";
import { fingerprintCdn } from "../../core/cdn.js";
import { canary, cacheBuster } from "../../core/rand.js";
import { sweepUnkeyedHeaders } from "./unkeyed_header.js";
import { sweepParamCloaking } from "./param_cloaking.js";
import { sweepUrlParser } from "./url_parser.js";
import { sweepCfHeaderOverflow } from "./cf_header_overflow.js";
import { sweepCdnQuirks } from "./cdn_quirks.js";
import unkeyedHeaders from "../../../data/unkeyed_headers.json" with { type: "json" };
import urlSuffixes from "../../../data/url_parser_suffixes.json" with { type: "json" };

export async function runCachePoison(
  sender: CaidoSender,
  endpoint: Endpoint,
  baseline: HttpMessage
): Promise<Finding[]> {
  if (!hasCacheLayer(baseline.headers)) return [];
  const cdn = fingerprintCdn(baseline.headers);
  const out: Finding[] = [];
  out.push(...(await sweepUnkeyedHeaders(sender, endpoint, baseline, unkeyedHeaders as string[], canary, cacheBuster)));
  out.push(...(await sweepParamCloaking(sender, endpoint, baseline, canary, cacheBuster)));
  out.push(...(await sweepUrlParser(sender, endpoint, baseline, urlSuffixes as string[])));
  out.push(...(await sweepCfHeaderOverflow(sender, endpoint, baseline, cdn)));
  out.push(...(await sweepCdnQuirks(sender, endpoint, baseline)));
  return out;
}
