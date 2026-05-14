---
title: Jinjava SSTI via user-supplied template strings (CVE-2020-12668)
slug: jinjava-ssti-paypal
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/ssti, technique/template-injection, sink/jinjava]
inbound: []
---

# Jinjava SSTI via user-supplied template strings (CVE-2020-12668)

## Pattern

Jinjava is HubSpot's Jinja-like template engine written in Java. Versions
< 2.5.4 allow a crafted template to load arbitrary Java methods via the
expression context — equivalent to RCE on the backend. Any product field
that gets piped through Jinjava for rendering (notifications, payment
memos, push payloads, email templates) becomes an injection sink. The
PayPal case rendered a Jinjava expression placed in the payment-message
field; the rendered output appeared in iOS push notifications and
server-side, allowing LFI of `/etc/passwd` and confirming RCE primitives.

## Preconditions

- Backend uses Jinjava (or another Jinja2-on-JVM port) to render
  user-controlled strings.
- Version < 2.5.4 (or any post-fix version with re-enabled context
  reflection).
- A user-controlled field (memo, comment, display-name, push title)
  flows into the template renderer.

## Detection

- Submit `{{7*7}}` in every free-text field and look for `49` in the
  rendered response, email, or push notification.
- If `49` renders, escalate: `{{''.getClass().forName('java.lang.Runtime')}}`
- Server may strip `class.forName` — try `getClass().getSuperclass()`
  walk to reach `Runtime`.

## Triggering

PayPal-style probe (sender-side):
```
amount: $0.01
message: {{7*7}}
```
Recipient sees `49` instead of the literal expression in their
notification = positive hit.

Escalate to LFI / RCE:
```
{{ ''.getClass().forName('org.apache.commons.io.IOUtils').readLines(
  ''.getClass().forName('java.io.FileReader').newInstance('/etc/passwd')) }}
```

## Bypasses

- Sandbox often blocks `Runtime`/`ProcessBuilder` directly; chain via
  reflection on `Class.forName`.
- If `{{` is filtered, try alternate delimiters configured on the
  template engine (Jinjava supports `<%= %>` if the host overrides).
- Templating may strip whitespace; collapse expression to single line.

## Seen in the wild

- {date: 2020-circa, target: PayPal, finding: $26k crit} — discovered by
  Fisher + Joel + Andre; surfaced as a Jinjava render on payment-message
  field with output mirrored to iOS push notification body. Discussed CT Ep 11.

## References

- CVE-2020-12668 — Jinjava < 2.5.4 arbitrary Java method invocation
- HubSpot Jinjava GitHub advisory
- Critical Thinking Podcast Ep 11
- Related: [[php-filter-chain-rce]] (alternative server-side injection sink class)
