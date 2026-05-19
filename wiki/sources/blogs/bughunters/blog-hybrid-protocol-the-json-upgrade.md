---
source: bughunters
source_url: https://bughunters.google.com/blog/hybrid-protocol-the-JSON-upgrade
title: "Hybrid Protocol: The JSON Upgrade - Google Bug Hunters"
description: "This post highlights how Hybrid transport is being extended to support generic JSON messages – paving the way for a host of new, secure authentication and credential use cases."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/hybrid-protocol-the-JSON-upgrade#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Hybrid Protocol: The JSON Upgrade

![](https://storage.googleapis.com/bughunters-article-images/blogs/harshlal.jpg)

Harsh Lal

Software Engineer

Published: Feb 23, 2026

Security Engineering  Android

[RSS Feed](https://bughunters.google.com/feed/en)

# Hybrid Protocol: The JSON Upgrade

As discussed in a [previous post](https://bughunters.google.com/blog/passkeys), the
[FIDO Alliance](https://fidoalliance.org/)'s Hybrid protocol has been a
game-changer for cross-device authentication, offering a secure, encrypted
channel between a source and a destination device, typically to handle
FIDO-specific operations like passkey assertion and registration via CTAP
(Client to Authenticator Protocol) messages. But what if this secure tunnel
could carry more than just CTAP messages?

Well, now it can. In this post, we are excited to share the significant strides
being made in extending the Hybrid transport to support generic JSON messages, a
critical evolution that paves the way for a host of new, secure authentication
and credential use cases.

## The limitation of CTAP and the need for flexibility

Historically, the Hybrid protocol has been tightly coupled with CTAP (Client to
Authenticator Protocol) messages. CTAP is the language roaming authenticators
use to communicate with clients/platforms. While essential for FIDO operations,
this dependency created a bottleneck: any new message type or protocol wishing
to use Hybrid for secure cross-device communication required a formal
specification update, significantly slowing down the development & adoption of
new use cases.

As secure authentication mechanisms evolve, emerging use cases – such as digital
credentials and passkey import/export – primarily rely on transmitting raw JSON
data and may not adhere to the strict schema defined in CTAP specifications. For
instance, securely presenting a verified digital Driver's License from a user's
Android phone to a website on a macOS device requires a transport mechanism that
can handle the raw JSON credential data, not just CTAP assertion commands. The
Hybrid protocol offers the ideal secure transport layer, but forcing complex
JSON payloads into a rigid CTAP structure was inefficient and constrained
innovation.

## The JSON solution: Flexibility meets security

The solution that was implemented involves creating an explicit mechanism for
transmitting raw JSON payloads over the existing secure Hybrid channel. This
separation of concerns ensures that the integrity of the secure transport is
maintained, while the data payload becomes infinitely more flexible.

By defining a new MessageType dedicated to JSON, the Hybrid protocol can now
securely transport _any_ message type. This move is formally addressed in the
latest _CTAP 2.2_ specification under the
[feature description for JSON-based messages](https://fidoalliance.org/specs/fido-v2.2-ps-20250714/fido-client-to-authenticator-protocol-v2.2-ps-20250714.html#sctn-feature-descriptions-jsonBasedMessages).

## What this means for the ecosystem

The addition of generic JSON transport transforms the Hybrid Protocol from a
FIDO-specific component into a robust, generic, cross-device secure transport
layer for all digital identity needs.

### 1\. Enabling cutting-edge identity use cases

This feature directly unlocks several critical, emerging use cases:

- **Digital Credentials:** Secure presentation and verification of digital
identity documents (like driver's licenses, passports, and health cards)
across devices becomes seamless.
- **Passkey management:** Operations like passkey import and export – which
involve transferring raw credential data – can now be performed securely
over the Hybrid channel.
- **Decentralized Identity:** Any protocol relying on secure JSON messaging
for verification or data exchange (e.g., decentralized identifiers or
verifiable credentials) can leverage Hybrid as its trusted conduit.

### 2\. Maintaining FIDO's trust model

Crucially, this expansion doesn't compromise the security of FIDO Hybrid flows.
The underlying infrastructure – the secure, encrypted tunnel – remains intact,
ensuring that all data transmitted, whether it’s a CTAP or JSON, is protected
against man-in-the-middle attacks and eavesdropping.

## Conclusion

This evolution of the Hybrid protocol signifies that the foundational technology
built for passkeys is now ready to support the entire digital identity
landscape. The future of secure, cross-device communication is here, and it
speaks fluent JSON. Stay tuned for further updates on how this generic JSON
support will continue to shape the secure web!

* * *

_For more technical details, you can refer to Fido specifications_
_[here](https://fidoalliance.org/specs/fido-v2.2-ps-20250714/fido-client-to-authenticator-protocol-v2.2-ps-20250714.html#sctn-feature-descriptions-jsonBasedMessages)._

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab