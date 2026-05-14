---
title: SAMLuel — single-quote round-trip attribute mutation
slug: saml-roundtrip-attribute-mutation
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/saml, technique/auth-bypass, technique/parser-discrepancy]
inbound: []
---

# SAMLuel — single-quote round-trip attribute mutation

PortSwigger research (Gareth Heyes + Zach) — Ruby SAML, unauth ATO on
GitLab.

## Pattern
Ruby SAML uses **two different XML parsers** on the same document:

1. **REXML** parses the document and validates the XMLDSig signature.
2. The (signed) DOM is **re-serialized to a string** and then **re-parsed by
   Nokogiri** to extract claims.

REXML preserves single-quoted attributes. Nokogiri serialization normalizes
them to double-quoted. A single-quoted attribute value that contains a
double-quote survives round 1 unchanged; round 2 sees the double-quote as
the attribute terminator and the rest of the value tokenizes as new XML
content — including attacker-controlled assertions, comments, signature
references.

## Preconditions
- Target uses Ruby SAML (or any other dual-parser flow — same primitive
  applies to any "validate-once, consume-twice" architecture).
- Attacker can craft the IdP-signed payload (or supply a signature; see
  [[ws-fed-metadata-signature-reuse]]).

## Detection
- Look for SAML stacks with two-parser pipelines: ruby-saml,
  python-saml + lxml-twice, dotnet System.Xml + XmlReader.
- Submit a probe assertion with `Attribute Name='foo'` (single-quoted) and
  a payload containing `"`. If the post-validation logic parses your
  smuggled content, you have the gap.

## Triggering
Sketch (PortSwigger writeup has full PoC):
```xml
<saml:Assertion ...>
  <ds:Signature>
    <ds:Reference URI='#assertion' />
    ...
  </ds:Signature>
  <saml:AttributeStatement>
    <saml:Attribute Name='value"<!-- comment><saml:Assertion ID="evil">
        ...attacker assertion...
      </saml:Assertion --><!--'/>
  </saml:AttributeStatement>
</saml:Assertion>
```
REXML sees a legitimate single-quoted attribute. Nokogiri re-parses and
the embedded `<saml:Assertion ID="evil">` becomes a sibling assertion the
SP authenticates against.

## Related primitives
- [[xml-attlist-attribute-hijack]] — DOCTYPE `<!ATTLIST>` to change which
  signature reference is followed across the round-trip.
- [[ws-fed-metadata-signature-reuse]] — sources a valid IdP signature.

## Bypasses / hardening
- Single-parser SAML stacks (libxmlsec1) are immune.
- Re-validate the signature *after* claim extraction, on the same DOM
  used for consumption.

## Seen in the wild
- {date: 2025, source: CT Ep 116} — PortSwigger / Ports­Wigger landed unauth
  ATO on GitLab.

## References
- PortSwigger blog — SAMLuel
- Critical Thinking Podcast Ep 116
- Related: [[xsw]], [[signature-exclusion]]
