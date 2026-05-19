---
title: DOM XSS via file import / filename preview sink
slug: filename-preview-xss
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/dom-xss, sink/filename-preview, technique/file-upload]
inbound: []
---

# DOM XSS via file import / filename preview sink

## Pattern

Web apps that render a preview of the selected filename before upload
(e.g. `file.name` displayed in an `<img alt>`, `<div>`, or used in a
`document.write` / `innerHTML` template) create a DOM XSS sink reachable
without a server round-trip. The payload lives in the filename of a
crafted file — the attacker sends the victim a link that auto-triggers
the import dialog or exploits social engineering to get them to open a
prepared file.

The canonical flow:
```
<input type="file"> → file selected → JS reads file.name
→ innerHTML = `<span>${file.name}</span>`   ← sink
```

Because the payload is in the filename (not the URL), traditional XSS
filters and Reflected/Stored distinctions don't apply — this is a
pure client-side taint from the `File` API.

## Preconditions

- Application renders `file.name` (or derived metadata) into the DOM
  without sanitisation.
- Victim can be induced to select a crafted file (phishing, pre-loaded
  shared workspace, import-by-URL functionality that sets a filename).
- CSP must not block inline script or the payload must use an allowed
  gadget (e.g. `<img src=x onerror=...>` where `img` is permitted).

## Detection

- Search JS bundles for: `file.name`, `\.name`, `fileName`, `filename`
  flowing into `innerHTML`, `outerHTML`, `insertAdjacentHTML`,
  `document.write`, `eval`, or framework template interpolation.
- `js_analyzer` tag: `dom-xss` + source `File.name`.
- Look for `<input type="file">` preview UI — file picker, drag-drop
  zone, import wizard. Any UI that shows "Importing: <filename>" is
  worth testing.

## Triggering

1. Create a file whose name is a payload:
   ```
   touch '<img src=x onerror=alert(document.domain)>.csv'
   ```
   (macOS/Linux allow most chars except `/` and NUL in filenames.)
2. Open the target's import / upload UI.
3. Select the crafted file — if the preview fires without sanitisation,
   the payload executes.

For one-click / CSRF chaining: embed a `<input type=file>` in an iframe
with `webkitdirectory` pointing to an attacker-controlled shared dir,
or use `DataTransfer` API in a drag-and-drop target if the browser
version supports it.

## Bypasses

- `textContent` instead of `innerHTML`: safe — bypass not applicable.
- Sanitiser on `file.name`: check for incomplete encoding (single-encode
  `<` as `&lt;` but leave `>` raw; try unicode variants).
- Filename length limit: use shorter payloads (`<svg onload=...>`).
- Framework auto-escaping: check if template literal or JSX interpolation
  uses `dangerouslySetInnerHTML` or `v-html`.

## Seen-in-the-wild

- **2026-04-14 — Fizzy.do (Basecamp) import filename preview** (Basecamp / xavlimsg, H1 #3608199, High, $500, 67 votes): Crafted filename injected into the import page DOM, enabling a second form submission in the victim's session to change email, create PAT, or delete the account — full account takeover. See [H1 #3608199](../../sources/hacktivity/3608199.md).

## References

- [[js-hoisting-xss]]
- [[waf-bypass]]
- [[taint-flow-open-redirect]]
- [DOM XSS SUMMARY](SUMMARY.md)
