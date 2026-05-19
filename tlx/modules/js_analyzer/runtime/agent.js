/* eslint-disable */
/*
 * TLX runtime augmentation agent.
 *
 * Plan: plans/ARCHITECTURE_EVOLUTION.md §7.2.
 *
 * Passive monkeypatches on dangerous JS primitives. Captures runtime
 * evidence the static analyzer cannot derive: eval bodies, webpack
 * runtime chunk resolution, sink fires with call stacks, postMessage
 * traffic, prototype writes. Buffers in window.__tlx_runtime__ and
 * flushes to a localhost collector configured via window.__tlx_cfg__.
 *
 * Loading pattern: inject as one inline <script> via Caido response
 * rewrite or chrome-devtools evaluate_script. Idempotent: re-load
 * detects existing patches and short-circuits.
 *
 * Strictly passive. No DOM mutation. No external network beyond the
 * configured collector. Out-of-scope URLs drop events.
 */
(function () {
  'use strict';
  var W = (typeof window !== 'undefined') ? window : self;
  if (W.__tlx_runtime__ && W.__tlx_runtime__._installed) return;

  var DEFAULT_CFG = {
    collector: 'http://127.0.0.1:38731/ingest',
    scope: [],                 // list of host substrings; empty = no scope guard
    max_buffer: 4000,
    flush_interval_ms: 3000,
    max_arg_preview: 256,
    agent_version: '0.1.0'
  };
  var CFG = Object.assign({}, DEFAULT_CFG, W.__tlx_cfg__ || {});

  var BUF = [];
  var SEEN_EVAL = new Set();

  function host() {
    try { return (W.location && W.location.host) || ''; }
    catch (e) { return ''; }
  }

  function in_scope() {
    if (!CFG.scope || !CFG.scope.length) return true;
    var h = host();
    for (var i = 0; i < CFG.scope.length; i++) {
      if (h.indexOf(CFG.scope[i]) !== -1) return true;
    }
    return false;
  }

  function preview(v) {
    if (v === null || v === undefined) return null;
    try {
      var s;
      if (typeof v === 'string') s = v;
      else if (typeof v === 'function') s = '[function ' + (v.name || 'anon') + ']';
      else if (typeof v === 'object') s = JSON.stringify(v);
      else s = String(v);
      return s.length > CFG.max_arg_preview
        ? s.slice(0, CFG.max_arg_preview) + '...(' + s.length + ')'
        : s;
    } catch (e) {
      return '[unserializable]';
    }
  }

  function stack() {
    try {
      var e = new Error();
      if (!e.stack) return [];
      return e.stack.split(/\r?\n/).slice(2, 8);
    } catch (e) { return []; }
  }

  // Heuristic taint match: simple keyword scan vs. common DOM source
  // labels. Conservative — we only stamp the labels; the static
  // reconciler is the authority on what counts as taint.
  var TAINT_LABELS = [
    ['document.location', 'dom_location'],
    ['window.location',   'dom_location'],
    ['document.URL',      'dom_location'],
    ['location.hash',     'location_hash'],
    ['location.search',   'location_search'],
    ['document.cookie',   'dom_cookie'],
    ['document.referrer', 'dom_referrer'],
    ['name="message"',    'postmessage_payload'],
    ['localStorage',      'storage_local'],
    ['sessionStorage',    'storage_session']
  ];

  function taint_match(s) {
    if (!s || typeof s !== 'string') return [];
    var out = [];
    for (var i = 0; i < TAINT_LABELS.length; i++) {
      if (s.indexOf(TAINT_LABELS[i][0]) !== -1) out.push(TAINT_LABELS[i][1]);
    }
    return out;
  }

  function push(kind, meta, args_preview) {
    if (!in_scope()) return;
    if (BUF.length >= CFG.max_buffer) BUF.shift();
    BUF.push({
      ts: Date.now() / 1000,
      kind: kind,
      url: (W.location && W.location.href) || '',
      fn_caller: stack(),
      args_preview: args_preview || [],
      args_taint_match: (args_preview || [])
        .map(function (s) { return taint_match(s); })
        .reduce(function (a, b) { return a.concat(b); }, []),
      meta: meta || {}
    });
  }

  // --- Patches -----------------------------------------------------

  // eval
  try {
    var origEval = W.eval;
    W.eval = function (src) {
      if (typeof src === 'string') {
        var h = String(src.length) + ':' + src.slice(0, 64);
        if (!SEEN_EVAL.has(h)) {
          SEEN_EVAL.add(h);
          push('eval_source', { body_len: src.length }, [preview(src)]);
        }
      }
      return origEval.apply(this, arguments);
    };
  } catch (e) { /* read-only on some browsers */ }

  // Function constructor
  try {
    var OrigFunction = W.Function;
    function PatchedFunction() {
      var args = Array.prototype.slice.call(arguments);
      var body = args[args.length - 1];
      if (typeof body === 'string') {
        push('eval_source', { via: 'Function', body_len: body.length },
             args.map(preview));
      }
      return OrigFunction.apply(this, args);
    }
    PatchedFunction.prototype = OrigFunction.prototype;
    W.Function = PatchedFunction;
  } catch (e) { }

  // setTimeout / setInterval with string body
  ['setTimeout', 'setInterval'].forEach(function (k) {
    try {
      var orig = W[k];
      W[k] = function () {
        if (typeof arguments[0] === 'string') {
          push('eval_source', { via: k, body_len: arguments[0].length },
               [preview(arguments[0])]);
        }
        return orig.apply(this, arguments);
      };
    } catch (e) { }
  });

  // Element.prototype.innerHTML / outerHTML
  function patchSetter(proto, prop) {
    try {
      var d = Object.getOwnPropertyDescriptor(proto, prop);
      if (!d || !d.set) return;
      var origSet = d.set;
      Object.defineProperty(proto, prop, {
        configurable: true,
        enumerable: d.enumerable,
        get: d.get,
        set: function (v) {
          push('sink_fire', { prop: prop, tag: (this.tagName || '').toLowerCase() },
               [preview(v)]);
          return origSet.call(this, v);
        }
      });
    } catch (e) { }
  }
  try {
    if (W.Element && W.Element.prototype) {
      patchSetter(W.Element.prototype, 'innerHTML');
      patchSetter(W.Element.prototype, 'outerHTML');
    }
  } catch (e) { }

  // document.write
  try {
    if (W.HTMLDocument && W.HTMLDocument.prototype) {
      var origWrite = W.HTMLDocument.prototype.write;
      W.HTMLDocument.prototype.write = function (s) {
        push('sink_fire', { prop: 'document.write' }, [preview(s)]);
        return origWrite.apply(this, arguments);
      };
    }
  } catch (e) { }

  // setAttribute for on* event handlers
  try {
    if (W.Element && W.Element.prototype) {
      var origSetAttr = W.Element.prototype.setAttribute;
      W.Element.prototype.setAttribute = function (name, value) {
        if (typeof name === 'string' && name.length > 2 &&
            name.charAt(0) === 'o' && name.charAt(1) === 'n') {
          push('sink_fire', {
            prop: 'setAttribute',
            attr_name: name,
            tag: (this.tagName || '').toLowerCase()
          }, [preview(value)]);
        }
        return origSetAttr.apply(this, arguments);
      };
    }
  } catch (e) { }

  // postMessage send + receive
  try {
    var origPM = W.postMessage;
    W.postMessage = function (msg, origin) {
      push('postmessage_out', { target_origin: origin }, [preview(msg)]);
      return origPM.apply(this, arguments);
    };
  } catch (e) { }
  try {
    W.addEventListener('message', function (e) {
      push('postmessage_in', {
        origin: e.origin || '',
        source_is_self: e.source === W ? 1 : 0
      }, [preview(e.data)]);
    }, true);
  } catch (e) { }

  // Promise.prototype.then (registration only)
  try {
    if (W.Promise && W.Promise.prototype && W.Promise.prototype.then) {
      var origThen = W.Promise.prototype.then;
      W.Promise.prototype.then = function (onFulfilled, onRejected) {
        if (typeof onFulfilled === 'function') {
          push('continuation', {
            handler_kind: 'promise_then',
            handler_name: onFulfilled.name || 'anon'
          }, []);
        }
        return origThen.apply(this, arguments);
      };
    }
  } catch (e) { }

  // Webpack runtime detection. We don't patch __webpack_require__
  // (its body is bundled per-bundle); instead, we periodically inspect
  // window for known globals and emit one resolution record per
  // chunkId we observe.
  var wp_seen = new Set();
  function wp_scan() {
    try {
      var modules = W.__webpack_modules__ ||
                    (W.webpackChunk && W.webpackChunk[0] && W.webpackChunk[0][1]);
      if (!modules) return;
      var keys = Object.keys(modules);
      for (var i = 0; i < keys.length; i++) {
        var k = keys[i];
        if (wp_seen.has(k)) continue;
        wp_seen.add(k);
        var src = '';
        try {
          var fn = modules[k];
          src = (typeof fn === 'function') ? String(fn) : String(fn[0] || '');
        } catch (e) {}
        push('webpack_resolve', { chunkId: k, body_len: src.length }, [preview(src)]);
      }
    } catch (e) { }
  }

  // Reflect.set / Object.defineProperty for __proto__ writes
  try {
    if (W.Reflect && W.Reflect.set) {
      var origSet = W.Reflect.set;
      W.Reflect.set = function (target, prop, val, receiver) {
        if (prop === '__proto__' || prop === 'constructor' || prop === 'prototype') {
          push('set_proto', { prop: prop }, [preview(val)]);
        }
        return origSet.apply(this, arguments);
      };
    }
  } catch (e) { }
  try {
    var origDP = W.Object.defineProperty;
    W.Object.defineProperty = function (obj, prop, desc) {
      if (prop === '__proto__' || prop === 'constructor' || prop === 'prototype') {
        push('set_proto', { prop: prop, via: 'defineProperty' },
             [preview(desc && desc.value)]);
      }
      return origDP.apply(this, arguments);
    };
  } catch (e) { }

  // --- Flush -------------------------------------------------------

  function flush() {
    if (!BUF.length) return;
    if (!in_scope()) { BUF.length = 0; return; }
    var batch = BUF.splice(0, BUF.length);
    try {
      if (W.navigator && W.navigator.sendBeacon) {
        var blob = new Blob([JSON.stringify({ batch: batch })],
                            { type: 'application/json' });
        W.navigator.sendBeacon(CFG.collector, blob);
      } else if (W.fetch) {
        W.fetch(CFG.collector, {
          method: 'POST',
          mode: 'no-cors',
          keepalive: true,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ batch: batch })
        }).catch(function () {});
      }
    } catch (e) { }
  }

  setInterval(flush, CFG.flush_interval_ms);
  setInterval(wp_scan, CFG.flush_interval_ms);
  if (W.addEventListener) W.addEventListener('beforeunload', flush, true);

  W.__tlx_runtime__ = {
    _installed: true,
    _version: CFG.agent_version,
    _cfg: CFG,
    flush: flush,
    buffer: function () { return BUF.slice(); },
    push: push
  };
})();
