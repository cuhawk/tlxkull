/* DOM verification contract reader.
 *
 * Companion to browser-confirm. The PoC HTML / target page emits
 * `data-verify-*` attributes; this script reads them and returns a
 * structured result so chrome-devtools MCP can verify exploit
 * outcome deterministically — no LLM-judging a screenshot.
 *
 * Contract attributes (set by the PoC HTML before triggering the sink):
 *   [data-verify-trigger]   — element responsible for firing the sink
 *                              (a button, a link, a form). Value is a
 *                              short human-readable name.
 *   [data-verify-source]    — where the tainted value came from
 *                              ("url:#hash", "url:?q", "postMessage",
 *                              "form:#input", ...).
 *   [data-verify-sink]      — sink that should fire ("innerHTML",
 *                              "eval", "document.write", ...).
 *   [data-verify-result]    — set BY the PoC payload itself when the
 *                              sink fires. Value is the canonical
 *                              canary value ("TLX_XSS_CANARY_<id>" or
 *                              equivalent).
 *   [data-verify-evidence]  — optional, longer evidence string (e.g.
 *                              the actual cookie / token exfilled).
 *
 * Inject after navigation + PoC interaction. Returns JSON via the
 * standard chrome-devtools `evaluate_script` result channel.
 *
 * Inspired by Tar's "DOM-contract" idea from Designing-with-Claude
 * (Code with Claude London 2026). Idempotent; calling twice returns
 * the same snapshot.
 */
(function () {
  const READ_KEYS = [
    "data-verify-trigger",
    "data-verify-source",
    "data-verify-sink",
    "data-verify-result",
    "data-verify-evidence",
  ];

  const collect = () => {
    const nodes = document.querySelectorAll(
      "[data-verify-trigger], [data-verify-source], [data-verify-sink], [data-verify-result], [data-verify-evidence]"
    );
    const out = [];
    nodes.forEach((n, idx) => {
      const entry = { _idx: idx, tag: n.tagName.toLowerCase() };
      for (const k of READ_KEYS) {
        if (n.hasAttribute(k)) {
          entry[k.replace(/^data-verify-/, "")] = n.getAttribute(k);
        }
      }
      // Include outer-html shape so the report can render which element
      // carried the contract — capped at 200 chars to avoid bloat.
      try {
        const outer = n.outerHTML || "";
        entry._outer_excerpt = outer.length > 200 ? outer.slice(0, 200) + "…" : outer;
      } catch (e) {
        entry._outer_excerpt = "<unreadable>";
      }
      out.push(entry);
    });
    return out;
  };

  // Capture document-level verification flags (some PoCs set these on
  // window/document rather than on a DOM node).
  const docFlags = {};
  for (const k of READ_KEYS) {
    try {
      const v =
        (window.__TLX_VERIFY && window.__TLX_VERIFY[k.replace(/^data-verify-/, "")]) ||
        document.documentElement.getAttribute(k);
      if (v) docFlags[k.replace(/^data-verify-/, "")] = v;
    } catch (e) {}
  }

  const entries = collect();
  const result_value = (entries.find((e) => e.result) || {}).result || docFlags.result || null;
  const sink = (entries.find((e) => e.sink) || {}).sink || docFlags.sink || null;
  const source = (entries.find((e) => e.source) || {}).source || docFlags.source || null;
  const trigger = (entries.find((e) => e.trigger) || {}).trigger || docFlags.trigger || null;
  const evidence = (entries.find((e) => e.evidence) || {}).evidence || docFlags.evidence || null;

  return JSON.stringify({
    _ts: new Date().toISOString(),
    url: location.href,
    fired: Boolean(result_value),
    trigger: trigger,
    source: source,
    sink: sink,
    result_canary: result_value,
    evidence: evidence,
    entry_count: entries.length,
    entries: entries,
    document_flags: docFlags,
  });
})();
