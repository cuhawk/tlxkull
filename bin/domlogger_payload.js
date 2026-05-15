/* DOMLogger payload (T2.1).
 *
 * Inject this into a page via chrome-devtools `evaluate_script` BEFORE
 * the user (or playwright) drives interaction. The script monkey-
 * patches a curated source/sink surface and logs every event to
 * `window.__TLX_DOMLOGGER_EVENTS` (an array). After interaction, dump
 * the array via another `evaluate_script` call:
 *
 *     JSON.stringify(window.__TLX_DOMLOGGER_EVENTS || [])
 *
 * and write to `findings/<id>/domlogger.jsonl`.
 *
 * Inspired by MatanBer/DOMLogger++ but pared down to the source/sink
 * pairs the TLX taint engine cares about. Loads idempotently — safe to
 * inject twice on a single page.
 *
 * Sources hooked:  URL.searchParams.get, location.{href,search,hash},
 *                  history.{push,replace}State, postMessage handlers,
 *                  document.referrer
 * Sinks hooked:    innerHTML / outerHTML setters, eval,
 *                  setTimeout / setInterval (string arg only),
 *                  Function constructor, document.write[ln],
 *                  Element.insertAdjacentHTML
 */
(function () {
  if (window.__TLX_DOMLOGGER_INSTALLED) return;
  window.__TLX_DOMLOGGER_INSTALLED = true;
  window.__TLX_DOMLOGGER_EVENTS = [];

  const log = (kind, payload) => {
    try {
      window.__TLX_DOMLOGGER_EVENTS.push({
        kind,
        ts: Date.now(),
        url: location.href,
        stack: (new Error()).stack.split('\n').slice(2, 6).join('\n'),
        ...payload,
      });
    } catch (_) {}
  };

  // ----- Sources -----
  try {
    const urlGet = URLSearchParams.prototype.get;
    URLSearchParams.prototype.get = function (k) {
      const v = urlGet.call(this, k);
      log('source.urlSearchParams.get', { key: String(k), value: String(v) });
      return v;
    };
  } catch (_) {}

  try {
    const locDesc = Object.getOwnPropertyDescriptor(window, 'location');
    if (!locDesc || !locDesc.configurable) {
      // Best-effort: hook only the readers that are configurable.
      ['href', 'search', 'hash', 'pathname'].forEach((prop) => {
        try {
          const d = Object.getOwnPropertyDescriptor(Location.prototype, prop);
          if (!d || !d.get) return;
          Object.defineProperty(Location.prototype, prop, {
            configurable: true,
            get: function () {
              const v = d.get.call(this);
              log('source.location.' + prop, { value: String(v) });
              return v;
            },
          });
        } catch (_) {}
      });
    }
  } catch (_) {}

  try {
    const origRefDesc = Object.getOwnPropertyDescriptor(Document.prototype, 'referrer');
    if (origRefDesc && origRefDesc.get) {
      Object.defineProperty(Document.prototype, 'referrer', {
        configurable: true,
        get: function () {
          const v = origRefDesc.get.call(this);
          log('source.document.referrer', { value: String(v) });
          return v;
        },
      });
    }
  } catch (_) {}

  ['pushState', 'replaceState'].forEach((m) => {
    try {
      const orig = History.prototype[m];
      History.prototype[m] = function (state, title, url) {
        log('source.history.' + m, { url: String(url || '') });
        return orig.apply(this, arguments);
      };
    } catch (_) {}
  });

  try {
    const origAdd = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function (type, listener, opts) {
      if (type === 'message' && typeof listener === 'function') {
        const wrapped = function (ev) {
          log('source.postMessage', {
            origin: ev.origin,
            data_preview: String(ev.data).slice(0, 200),
          });
          return listener.apply(this, arguments);
        };
        return origAdd.call(this, type, wrapped, opts);
      }
      return origAdd.call(this, type, listener, opts);
    };
  } catch (_) {}

  // ----- Sinks -----
  ['innerHTML', 'outerHTML'].forEach((prop) => {
    try {
      const d = Object.getOwnPropertyDescriptor(Element.prototype, prop);
      if (!d || !d.set) return;
      Object.defineProperty(Element.prototype, prop, {
        configurable: true,
        get: d.get,
        set: function (v) {
          log('sink.element.' + prop, {
            tag: this.tagName,
            id: this.id,
            value_preview: String(v).slice(0, 200),
          });
          return d.set.call(this, v);
        },
      });
    } catch (_) {}
  });

  try {
    const insertOrig = Element.prototype.insertAdjacentHTML;
    Element.prototype.insertAdjacentHTML = function (where, html) {
      log('sink.element.insertAdjacentHTML', {
        tag: this.tagName,
        where,
        value_preview: String(html).slice(0, 200),
      });
      return insertOrig.call(this, where, html);
    };
  } catch (_) {}

  try {
    const origEval = window.eval;
    window.eval = function (s) {
      log('sink.eval', { value_preview: String(s).slice(0, 200) });
      return origEval.call(window, s);
    };
  } catch (_) {}

  ['setTimeout', 'setInterval'].forEach((fn) => {
    try {
      const orig = window[fn];
      window[fn] = function (cb) {
        if (typeof cb === 'string') {
          log('sink.' + fn + '.string', { value_preview: cb.slice(0, 200) });
        }
        return orig.apply(window, arguments);
      };
    } catch (_) {}
  });

  try {
    const F = window.Function;
    window.Function = function () {
      const args = Array.from(arguments);
      log('sink.Function', { value_preview: args.join('|').slice(0, 200) });
      return F.apply(this, args);
    };
    window.Function.prototype = F.prototype;
  } catch (_) {}

  ['write', 'writeln'].forEach((m) => {
    try {
      const orig = document[m].bind(document);
      document[m] = function () {
        log('sink.document.' + m, {
          value_preview: Array.from(arguments).join('').slice(0, 200),
        });
        return orig.apply(document, arguments);
      };
    } catch (_) {}
  });
})();
