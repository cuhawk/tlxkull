"""DOM enumeration for execution-driven discovery (Phase 7I).

Enumerates form fields and visible buttons on a Playwright page via
page-side JS, returns InteractionSpec dicts ready for
ExecutionLoop._dispatch_one. Form fields get sentinel-injected
values so SinkMonitor can trace the flow.

Tier 1 only — forms + buttons. No postMessage, no anchors, no
custom events. Page navigation is not handled: if a click navigates,
later enumeration sees the new DOM but already-discovered selectors
may stale (path-based selectors are stable per static DOM, not
across navigations).

No anthropic / google.genai imports.
"""
from __future__ import annotations

import asyncio
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


_DEFAULT_INTERACTION_CAP = 50

_ENUMERATE_JS = """
() => {
  const out = [];
  const seen = new Set();
  const FILLABLE_TYPES = new Set([
    'text','email','password','search','url','number','tel',''
  ]);

  function isVisible(el) {
    const r = el.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return false;
    const cs = window.getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') return false;
    return true;
  }

  function isFillable(el) {
    if (el.disabled || el.readOnly) return false;
    if (!isVisible(el)) return false;
    const tag = el.tagName.toLowerCase();
    if (tag === 'select' || tag === 'textarea') return true;
    if (tag === 'input') {
      const t = (el.type || 'text').toLowerCase();
      return FILLABLE_TYPES.has(t);
    }
    return false;
  }

  function isClickable(el) {
    if (el.disabled) return false;
    if (!isVisible(el)) return false;
    return true;
  }

  function selectorFor(el) {
    if (el.id) return '#' + CSS.escape(el.id);
    if (el.name) {
      return el.tagName.toLowerCase()
        + '[name="' + CSS.escape(el.name) + '"]';
    }
    const path = [];
    let cur = el;
    while (cur && cur.nodeType === 1 && cur !== document.body
           && cur !== document.documentElement) {
      const parent = cur.parentElement;
      if (!parent) break;
      const tag = cur.tagName.toLowerCase();
      const sibs = Array.from(parent.children)
        .filter(c => c.tagName === cur.tagName);
      if (sibs.length === 1) {
        path.unshift(tag);
      } else {
        const idx = sibs.indexOf(cur) + 1;
        path.unshift(tag + ':nth-of-type(' + idx + ')');
      }
      cur = parent;
    }
    return path.length ? path.join(' > ') : el.tagName.toLowerCase();
  }

  document.querySelectorAll('input, textarea, select').forEach(el => {
    if (!isFillable(el)) return;
    const sel = selectorFor(el);
    const key = 'fill:' + sel;
    if (seen.has(key)) return;
    seen.add(key);
    out.push({type: 'fill', selector: sel});
  });

  const BTN_SEL =
    'button, input[type="submit"], input[type="button"], [role="button"]';
  document.querySelectorAll(BTN_SEL).forEach(el => {
    if (!isClickable(el)) return;
    const sel = selectorFor(el);
    const key = 'click:' + sel;
    if (seen.has(key)) return;
    seen.add(key);
    out.push({type: 'click', selector: sel});
  });

  return out;
}
"""


async def enumerate_interactions(
    page: Any,
    sentinel: str,
    *,
    cap: int = _DEFAULT_INTERACTION_CAP,
) -> list[dict]:
    """Enumerate fillable inputs + clickable buttons on the page.

    Form inputs get the sentinel as their fill value. Click specs
    have no value. Returns at most ``cap`` entries (fill specs first,
    then clicks, in DOM order).

    Never raises on page-side JS failure; logs at debug, returns [].
    """
    def _enum() -> list[dict]:
        try:
            result = page.evaluate(_ENUMERATE_JS)
            return result if isinstance(result, list) else []
        except Exception as exc:
            logger.debug(
                "page_explorer.enumerate_failed", error=str(exc),
            )
            return []

    raw = await asyncio.to_thread(_enum)

    out: list[dict] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        kind = entry.get("type")
        sel = entry.get("selector")
        if not sel or not isinstance(sel, str):
            continue
        if kind == "fill":
            out.append({
                "type": "fill", "selector": sel, "value": sentinel,
            })
        elif kind == "click":
            out.append({"type": "click", "selector": sel})
        if len(out) >= cap:
            break
    return out


def dedup_against(
    discovered: list[dict],
    user_supplied: list[dict],
) -> list[dict]:
    """Remove discovered specs whose (kind, selector) collide with
    the user-supplied list. Preserves order of ``discovered``.
    Both fill/form_fill and postmessage/post_message aliases are
    treated as the same kind for collision purposes.
    """
    def _norm(t: Any) -> str:
        s = (str(t) if t is not None else "").lower()
        if s in ("form_fill",):
            return "fill"
        if s in ("post_message",):
            return "postmessage"
        return s

    user_keys = {
        (_norm(s.get("type")), s.get("selector"))
        for s in (user_supplied or [])
        if isinstance(s, dict)
    }
    out: list[dict] = []
    for spec in discovered or []:
        if not isinstance(spec, dict):
            continue
        key = (_norm(spec.get("type")), spec.get("selector"))
        if key in user_keys:
            continue
        out.append(spec)
    return out
