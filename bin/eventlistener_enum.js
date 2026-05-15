/* Inline-handler + event-listener enumeration (T2.4).
 *
 * Inject AFTER navigation via chrome-devtools `evaluate_script` and
 * dump the result via another `evaluate_script` that returns the array.
 *
 * Pattern from IMPL_TIER123.md:
 *   [...document.querySelectorAll('[onclick],[onerror],[onload],
 *                                  [onmouseover],[onfocus],[oninput]')]
 *     .map(e => ({ tag: e.tagName, attrs: [...e.attributes]
 *                    .map(a => [a.name, a.value]) }))
 *
 * Extended with `getEventListeners` enumeration for a curated set of
 * top-level objects when running in DevTools preview mode (the
 * function is only injected by Chrome's devtools, not standard JS).
 *
 * Returns the JSON-serializable array directly so the caller can pipe
 * it to `findings/<id>/event_handlers.json`.
 */
(function () {
  const inlineHandlers = [
    ...document.querySelectorAll(
      '[onclick],[onerror],[onload],[onmouseover],[onfocus],[oninput],' +
      '[onsubmit],[onchange],[onmouseenter],[onmouseleave],[onkeyup],[onkeydown]'
    ),
  ].map((e) => ({
    tag: e.tagName,
    id: e.id || null,
    attrs: [...e.attributes]
      .filter((a) => a.name.startsWith('on'))
      .map((a) => [a.name, String(a.value).slice(0, 300)]),
  }));

  let listenerEnum = null;
  try {
    if (typeof getEventListeners === 'function') {
      const targets = { window, document };
      listenerEnum = {};
      for (const k of Object.keys(targets)) {
        try {
          const map = getEventListeners(targets[k]);
          listenerEnum[k] = Object.fromEntries(
            Object.entries(map).map(([type, arr]) => [
              type,
              arr.map((l) => ({ useCapture: !!l.useCapture, passive: !!l.passive })),
            ]),
          );
        } catch (_) {}
      }
    }
  } catch (_) {}

  return {
    inline_handlers: inlineHandlers,
    inline_handlers_count: inlineHandlers.length,
    listener_enum: listenerEnum,
    ts: Date.now(),
    url: location.href,
  };
})();
