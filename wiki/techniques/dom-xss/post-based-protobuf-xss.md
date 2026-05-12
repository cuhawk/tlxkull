---
title: POST-based Raw Protobuf XSS via Form Submission
slug: post-based-protobuf-xss
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/protobuf, technique/xss]
inbound: []
---

# POST-based Raw Protobuf XSS via Form Submission

## Pattern

A target endpoint accepts binary (wire-format) protobuf in a POST body and
reflects or stores it without content-type enforcement. To achieve a
**top-level navigation XSS** via a cross-origin HTML form POST
(`text/plain` content type), the binary protobuf payload must survive four
browser-imposed constraints:

1. **DOM string mutation**: Non-ASCII bytes get mangled when inserted into the
   DOM. Constrain every byte to the pure ASCII range `0x01–0x7F`.
2. **Bare LF (0x0a) → CRLF normalization**: Browser rewrites a lone `0x0a` to
   `0x0d 0x0a`. Protobuf wire type 2 (length-delimited / string) for field #1
   uses tag byte `0x0a`. Workaround: insert a junk field whose last byte is
   `0x0d` immediately before the offending field, synthesizing a real CRLF
   sequence the browser will not "fix".
3. **Equals sign requirement**: A `text/plain` form submission body must
   contain an `=` character (key=value). To control placement, pad a protobuf
   field so that the `0x3d` byte (`=`) lands at a position that puts most of
   the payload in the "value" (right of `=`), which the browser handles more
   permissively.
4. **Trailing CRLF appended by browser**: Browser appends `\r\n` (2 bytes) at
   the end of the form submission. Absorb them by defining the last string
   field with a **declared length 2 bytes longer** than the actual content
   provided — the appended bytes get parsed as the tail of that defined string,
   preserving protobuf byte offsets.

## Preconditions

- Target endpoint reflects or stores binary protobuf content that is later
  rendered in a browser context without escaping.
- No `Content-Type` enforcement — endpoint processes `text/plain` the same as
  `application/x-protobuf`.
- XSS requires top-level navigation (not injectable via `fetch`/XHR).
- Endpoint is cross-origin reachable via an HTML form POST.

## Detection

- Traffic analysis: look for requests with `Content-Type: application/x-protobuf`
  or `application/octet-stream` to endpoints that appear to render user data.
- `js_analyzer`: sinks consuming protobuf field values that land in
  `innerHTML`, `document.write`, or frame `src`.
- Decode protobuf bodies with `protoscope` (see Tools) and check for
  reflection in rendered responses.

## Triggering

### Tool: protoscope

```bash
# Decode existing binary protobuf to human-readable form
protoscope < existing_payload.bin > decoded.txt

# Edit decoded.txt, then re-encode
protoscope -s < decoded.txt > modified.bin

# Base64 for use in Caido replay
base64 < modified.bin
```

### Payload construction checklist

```
1. Draft XSS payload in JS: ensure all bytes in 0x01-0x7F.
2. Identify all protobuf fields needed; assign field numbers.
3. Pad fields to push 0x0d before any field whose tag is 0x0a (wire type 2,
   low field numbers).
4. Insert a field whose last byte is 0x0d immediately before that 0x0a field:
   → browser sees 0x0d 0x0a = valid CRLF, will not add a CR.
5. Place a field such that its wire-format encoding contains 0x3d (=) at the
   desired key/value split point.
6. Make the final string field's declared length = actual_content_length + 2.
7. Re-encode via protoscope. Verify byte-for-byte with xxd.
8. Deliver via HTML form (text/plain, method=POST):
```

```html
<form id="f" method="POST"
      action="https://target.com/vulnerable-endpoint"
      enctype="text/plain">
  <!-- payload is embedded as the "value" portion after the = sign -->
  <input name="<protobuf_key_prefix>" value="<protobuf_value_suffix>">
</form>
<script>document.getElementById('f').submit();</script>
```

## Bypasses

- **Content-type whitelist**: if the server validates `Content-Type`, note that
  HTML forms with `enctype="text/plain"` bypass the check when the endpoint
  doesn't enforce it. If it does enforce, check whether the check is on the
  outer request or per-part.
- **Length-prefixed fields**: if strict field length checking occurs, ensure
  the +2 trick for the final field aligns with declared length.
- **XSS payload sanitisation in protobuf string fields**: if HTML-encoding
  occurs after deserialization, you need a rendering context that interprets
  the encoded output (e.g., a field rendered via innerHTML after
  protobuf-to-JS-object conversion with no second-pass sanitization).

## Seen-in-the-wild

| date | target | notes |
|---|---|---|
| 2026 | (undisclosed, heavy protobuf user) | Justin Gardner (CT Ep. 171): required binary-level protobuf in POST body; ASCII-range constraint, CRLF padding, equals-sign alignment, and trailing-CRLF absorption all needed to produce a working top-level-navigation XSS. |

## References

- Episode source: `../../sources/podcasts/ct/20260423_l5fs7Okdj3o_Path-Scoped_Cookie_Hacks_with_Uppercase_Post-based_Raw_Protobuf_XSS_Ep_171.en.vtt`
- Podcast: "Path-Scoped Cookie Hacks with Uppercase & Post-based Raw Protobuf XSS (Ep. 171)" — <https://www.youtube.com/watch?v=l5fs7Okdj3o>
- protoscope tool: <https://github.com/protocolbuffers/protoscope>
- [DOM-XSS SUMMARY](SUMMARY.md)
- [Path-Scoped Cookie Bypass](../server-side/path-scoped-cookie-bypass.md) — sister technique from the same episode
