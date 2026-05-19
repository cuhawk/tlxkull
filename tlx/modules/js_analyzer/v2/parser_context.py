"""V2 §15 — Context-sensitive HTML/JS parser context per sink.

Multiplies into the sink viability factor. Already partially modeled
via ``sink_capabilities.json`` (V1 §4); this module persists the
``sink_contexts`` table so other passes can join on it.

Default ON (``JS_ENABLE_PARSER_CONTEXT=1``). Deterministic — no LLM.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from modules.js_analyzer.v2._common import (
    clear_table,
    exec_ddl,
    write_sidecar,
)

__all__ = ["run"]


_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS sink_contexts (
    node_id INTEGER PRIMARY KEY,
    context_class TEXT NOT NULL,
    encoding_state TEXT NOT NULL,
    execution_viable TEXT NOT NULL,
    rationale TEXT
);
"""


# Sink taxonomy id → (context_class, encoding_state, execution_viable, rationale)
_CONTEXT_MAP: dict[str, tuple[str, str, str, str]] = {
    "innerHTML_assign":             ("html_body",          "raw", "js-event", "innerHTML insertion mode is html_body; script tags inert but event handlers run"),
    "outerHTML_assign":             ("html_body",          "raw", "js-event", "same as innerHTML"),
    "insertAdjacentHTML_call":      ("html_body",          "raw", "js-event", "same parser as innerHTML"),
    "document_write":               ("html_body",          "raw", "js",       "document.write is in script context; <script> runs"),
    "document_writeln":             ("html_body",          "raw", "js",       "same as document.write"),
    "srcdoc_assign":                ("html_body",          "raw", "js",       "iframe srcdoc opens fresh document"),
    "iframe_srcdoc_assign":         ("html_body",          "raw", "js",       "same as srcdoc"),
    "dangerouslySetInnerHTML":      ("html_body",          "raw", "js-event", "React opt-out into html_body"),
    "vue_v_html_sink":              ("html_body",          "raw", "js-event", "Vue v-html opt-out"),
    "angular_inner_html_binding":   ("html_body",          "raw", "js-event", "Angular [innerHTML]"),
    "createContextualFragment":     ("html_body",          "raw", "js-event", "Range.createContextualFragment treats input as html"),
    "setAttribute_dangerous_attr":  ("html_attr_quoted",   "attr-quoted", "js-event", "attribute set; href/src/srcdoc"),
    "setAttribute_dynamic_attr":    ("html_attr_quoted",   "attr-quoted", "js-event", "dynamic attribute name"),
    "event_handler_attr_assign":    ("event_handler_attr", "raw", "js",       "on* attribute is JS"),
    "location_href_assign":         ("url_attr",           "raw", "js-data-uri", "javascript: URI possible"),
    "location_assign_call":         ("url_attr",           "raw", "js-data-uri", "same"),
    "location_replace_call":        ("url_attr",           "raw", "js-data-uri", "same"),
    "location_bare_assign":         ("url_attr",           "raw", "js-data-uri", "same"),
    "frame_location_assign":        ("url_attr",           "raw", "js-data-uri", "iframe location"),
    "window_navigate_legacy":       ("url_attr",           "raw", "js-data-uri", "same"),
    "window_open":                  ("url_attr",           "raw", "js-data-uri", "window.open accepts javascript:"),
    "script_src_assign":            ("url_attr",           "raw", "js",       "script.src loads any URL allowed by CSP"),
    "script_text_assign":           ("html_body",          "raw", "js",       "script.text body becomes inline script"),
    "eval_call":                    ("js_eval",            "raw", "js",       "literal eval"),
    "eval_indirect":                ("js_eval",            "raw", "js",       "(0,eval)(s) equivalent"),
    "new_Function":                 ("js_eval",            "raw", "js",       "Function constructor"),
    "setTimeout_string":            ("js_eval",            "raw", "js",       "string-arg timer"),
    "setInterval_string":           ("js_eval",            "raw", "js",       "same"),
    "setImmediate_string":          ("js_eval",            "raw", "js",       "same"),
    "execScript_legacy":            ("js_eval",            "raw", "js",       "legacy IE/Edge primitive"),
    "vm_runIn_family":              ("js_eval",            "raw", "js",       "server-side vm primitives"),
    "vm_Script_ctor":               ("js_eval",            "raw", "js",       "same"),
    "require_dynamic":              ("js_eval",            "raw", "js",       "node require"),
    "fetch_call":                   ("url_attr",           "url-encoded", "inert", "fetch URL context"),
    "fetch_with_user_input":        ("url_attr",           "url-encoded", "inert", "same"),
    "xhr_open_call":                ("url_attr",           "url-encoded", "inert", "XHR URL context"),
    "axios_call":                   ("url_attr",           "url-encoded", "inert", "axios URL context"),
    "postMessage_send":             ("json_in_script",     "json-stringified", "inert", "JSON serialized payload; receiver re-parses"),
    "document_domain_assign":       ("url_attr",           "raw", "inert", "document.domain mutation"),
    "trusted_types_create_policy":  ("html_body",          "raw", "js-event", "TT policy body parses to HTML"),
    "computed_proto_assign":        ("html_body",          "raw", "html-only", "prototype-pollution write; downstream gadget required"),
}


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    exec_ddl(conn, _CREATE_SCHEMA)
    clear_table(conn, "sink_contexts")

    classified = 0
    by_class: dict[str, int] = {}
    by_exec: dict[str, int] = {}
    for nid, taxid in conn.execute(
        "SELECT DISTINCT node_id, taxonomy_id FROM node_tags WHERE kind='sink'"
    ):
        cfg = _CONTEXT_MAP.get(taxid)
        if not cfg:
            continue
        context_class, encoding_state, exec_viable, rationale = cfg
        conn.execute(
            "INSERT OR REPLACE INTO sink_contexts "
            "(node_id, context_class, encoding_state, execution_viable, rationale) "
            "VALUES (?,?,?,?,?)",
            (nid, context_class, encoding_state, exec_viable, rationale),
        )
        classified += 1
        by_class[context_class] = by_class.get(context_class, 0) + 1
        by_exec[exec_viable] = by_exec.get(exec_viable, 0) + 1
    conn.commit()

    sidecar = {
        "classified": classified,
        "by_context_class": by_class,
        "by_execution_viable": by_exec,
    }
    write_sidecar(target_dir, "sink_contexts.json", sidecar)
    return sidecar
