---
title: XML DOCTYPE ATTLIST attribute hijack
slug: xml-attlist-attribute-hijack
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/saml, technique/xml, technique/parser-discrepancy]
inbound: []
---

# XML DOCTYPE ATTLIST attribute hijack

## Pattern
XML's inline DOCTYPE supports more than entities. You can also declare
`<!ELEMENT>` and `<!ATTLIST>`. `<!ATTLIST>` declares a default value for an
attribute on a named element — i.e. you can **inject attributes into
existing elements** that weren't typed in the body of the document.

In SAML's REXML/Nokogiri round-trip context (see
[[saml-roundtrip-attribute-mutation]]) this lets you change which
`<ds:Signature>` element gets validated. By `<!ATTLIST ds:Signature
xmlns:ds CDATA #FIXED "http://www.w3.org/2000/09/xmldsig#">` you switch
the namespace of an attacker-crafted signature so REXML's xpath selector
matches it.

## Preconditions
- Target XML parser honors inline DOCTYPE declarations and applies ATTLIST
  defaults (REXML does; many do).
- Some other primitive provides the actual content insertion (here, the
  single-quote round-trip mutation).

## Detection
- Run a probe with `<!ATTLIST someelem extra-attr CDATA #FIXED "x">` and
  inspect post-parse DOM for the injected attribute.
- ATTLIST works even when external DTD fetching is disabled — only the
  inline subset is consulted.

## Bypasses / hardening
- `XMLConstants.FEATURE_SECURE_PROCESSING` / `XML_PARSE_NOENT` block
  entity expansion but typically *not* ATTLIST.
- Reject documents that contain a DOCTYPE entirely.

## Seen in the wild
- {date: 2025, source: CT Ep 116} — PortSwigger SAMLuel used ATTLIST to
  retarget the SP's signature-reference xpath.

## References
- W3C XML 1.0 §3.3 Attribute-List Declarations
- PortSwigger SAMLuel writeup
- Critical Thinking Podcast Ep 116
- Related: [[saml-roundtrip-attribute-mutation]]
