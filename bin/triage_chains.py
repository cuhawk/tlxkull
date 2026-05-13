#!/usr/bin/env python3
"""chain-triage scorer.

Reads chains/_raw.json (output of js_get_chains, captured by the
chain-triage skill) plus bin/triage_weights.json, writes:
  chains/all.jsonl   (every chain, scored, sorted desc)
  chains/hot.jsonl   (top N where N = min(hot_count_max, max(2, ceil(total*hot_count_ratio))))

Dedupes by (source.qname, sink.qname, source.taxonomy_id, sink.taxonomy_id),
keeping the shortest-path representative for each group. All variants for
the same source/sink pair are recorded under chain.variants in all.jsonl.

Usage:
  bin/triage_chains.py <target_dir>
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS_PATH = ROOT / "bin" / "triage_weights.json"

SINK_TAXONOMY_MAP = {
    "setTimeout_string": "settimeout_string",
    "setInterval_string": "settimeout_string",
    "Function_string": "function_constructor",
    "eval_call": "eval_string",
    "innerHTML_assign": "dom_xss_inner_html",
    "outerHTML_assign": "dom_xss_outer_html",
    "document_write_call": "dom_xss_document_write",
    "react_dangerouslySetInnerHTML": "dom_xss_dangerously_set_inner_html",
    "angular_modern_bypassSecurityTrust": "dom_xss_dangerously_set_inner_html",
    "vue_v_html": "dom_xss_dangerously_set_inner_html",
    "open_redirect": "open_redirect_location",
    "postMessage_no_origin": "postmessage_no_origin_check",
    "url_to_fetch": "url_to_fetch",
}
SOURCE_TAXONOMY_MAP = {
    "location_search": "url_query",
    "location_hash": "url_hash",
    "location_href": "url_query",
    "document_referrer": "document_referrer",
    "window_name": "window_name",
    "postMessage_event": "postmessage_data",
    "JSON_parse_call": None,
}
FW_BONUS_KEY = {
    "angular_modern_bypassSecurityTrust": ("angular", "bypassSecurityTrustHtml"),
    "react_dangerouslySetInnerHTML": ("react", "dangerously_set_inner_html"),
    "vue_v_html": ("vue", "v_html"),
}


def score(chain: dict, weights: dict, frameworks: list[str]) -> dict:
    w = weights["weights"]
    sink_tax = chain["sink"]["taxonomy_id"]
    src_tax = chain["source"]["taxonomy_id"]
    norm_sink = SINK_TAXONOMY_MAP.get(sink_tax, sink_tax)
    norm_src = SOURCE_TAXONOMY_MAP.get(src_tax, src_tax)
    sink_sev = weights["sink_severity"].get(norm_sink, 0.5)
    src_sev = weights["source_severity"].get(norm_src, 0.4) if norm_src else 0.3
    path_len = max(1, len(chain.get("path", [])) - 1)
    fw_match = 0.0
    if sink_tax in FW_BONUS_KEY:
        fw, key = FW_BONUS_KEY[sink_tax]
        if fw in frameworks:
            fw_match = weights["framework_bonus"].get(fw, {}).get(key, 0.0)
    sanit_penalty = 0.0  # TLX's chain payload doesn't currently flag sanitizers
    composite = (
        w["w_sev"] * sink_sev
        + w["w_src"] * src_sev
        - w["w_path"] * math.log(1 + path_len)
        + w["w_fw"] * fw_match
        - w["w_sanit"] * sanit_penalty
    )
    return {
        "composite": round(composite, 4),
        "sink_sev": sink_sev,
        "src_sev": src_sev,
        "path_len": path_len,
        "fw_match": fw_match,
        "norm_sink": norm_sink,
        "norm_src": norm_src,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target_dir")
    args = ap.parse_args()
    tdir = Path(args.target_dir).resolve()
    raw = json.loads((tdir / "chains" / "_raw.json").read_text())
    weights = json.loads(WEIGHTS_PATH.read_text())
    status_path = tdir / "status.json"
    frameworks = []
    if status_path.exists():
        st = json.loads(status_path.read_text())
        frameworks = st.get("phases", {}).get("index", {}).get("frameworks", [])

    chains_in = raw["chains"]
    enriched = []
    for c in chains_in:
        s = score(c, weights, frameworks)
        enriched.append({**c, "scoring": s})

    # dedupe by (src.qname, sink.qname, src.tax, sink.tax) keep shortest path
    groups: dict[tuple, list[dict]] = {}
    for c in enriched:
        k = (
            c["source"]["qname"], c["sink"]["qname"],
            c["source"]["taxonomy_id"], c["sink"]["taxonomy_id"],
        )
        groups.setdefault(k, []).append(c)
    deduped = []
    for k, gs in groups.items():
        gs.sort(key=lambda x: (len(x.get("path", [])), x["id"]))
        rep = gs[0].copy()
        rep["variants"] = [
            {"id": v["id"], "path": v["path"], "depth": v["depth"]}
            for v in gs
        ]
        deduped.append(rep)
    deduped.sort(key=lambda x: x["scoring"]["composite"], reverse=True)

    chains_dir = tdir / "chains"
    with (chains_dir / "all.jsonl").open("w") as f:
        for c in deduped:
            f.write(json.dumps(c) + "\n")

    total = len(deduped)
    hot_max = weights.get("hot_count_max", 20)
    hot_ratio = weights.get("hot_count_ratio", 0.1)
    hot_n = min(hot_max, max(2, math.ceil(total * hot_ratio)))
    # if total small, allow all through (don't drop sub-set of equals)
    if total <= 10:
        hot_n = total
    hot = deduped[:hot_n]
    with (chains_dir / "hot.jsonl").open("w") as f:
        for c in hot:
            f.write(json.dumps(c) + "\n")

    sink_dist: dict[str, int] = {}
    source_dist: dict[str, int] = {}
    for c in deduped:
        sink_dist[c["sink"]["taxonomy_id"]] = sink_dist.get(c["sink"]["taxonomy_id"], 0) + 1
        source_dist[c["source"]["taxonomy_id"]] = source_dist.get(c["source"]["taxonomy_id"], 0) + 1

    summary = {
        "total_raw": len(chains_in),
        "total_deduped": total,
        "hot": len(hot),
        "sink_dist": sink_dist,
        "source_dist": source_dist,
        "frameworks": frameworks,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
