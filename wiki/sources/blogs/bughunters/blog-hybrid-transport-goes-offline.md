---
source: bughunters
source_url: https://bughunters.google.com/blog/hybrid-transport-goes-offline
title: "Hybrid Transport Goes Offline! - Google Bug Hunters"
description: "Find out how the FIDO alliances's Hybrid transport architecture was expanded to support authentication in the offline world, increasing reliability and unlocking many new use cases."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/hybrid-transport-goes-offline#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Hybrid Transport Goes Offline!

![](https://storage.googleapis.com/bughunters-article-images/blogs/harshlal.jpg)

Harsh Lal

Software Engineer

Published: Mar 4, 2026

Security Engineering  Android

[RSS Feed](https://bughunters.google.com/feed/en)

# Hybrid Transport Goes Offline!

Hello, fellow innovators and security enthusiasts! Building on our previous
posts on Hybrid transport covering
[cross-device passkeys](https://bughunters.google.com/blog/passkeys) and
[JSON message support](https://bughunters.google.com/blog/hybrid-protocol-the-JSON-upgrade),
we're now pivoting to how [FIDO](https://fidoalliance.org/)'s Hybrid transport
architecture supports the offline world.

## The Internet's invisible leash on FIDO authentication

Today we're diving into a development that I believe is nothing short of
revolutionary for the world of digital identity and security: the introduction
of **offline transport channels** into FIDO's Hybrid transport architecture.

For years, FIDO has been the gold standard for robust, passwordless
authentication. Its promise – strong & easy-to-use security – has been steadily
reshaping how we log in to services. The existing Hybrid transport mechanism is
a marvel of cross-device convenience, typically initiated via a QR code and
relying on a WebSocket tunnel to ferry authentication data securely between your
computer and your phone.

But here’s the rub: that WebSocket tunnel requires a stable internet connection.

Think about it:

- That grocery store with spotty Wi-Fi.
- The basement office where the signal dies.
- The remote location where "connectivity" is a myth.

In these crucial, real-world moments, the requirement for an internet connection
has acted as an invisible leash, limiting FIDO’s full potential, especially as
we move beyond simple logins and into more complex, mission-critical use cases.

## The imperative for offline capability

The digital landscape is rapidly evolving. We are on the cusp of mass adoption
for cutting-edge use cases like:

1. **Digital Credential presentment:** Showing your digital ID, driver's
license, or proof of insurance in a physical setting.
2. **Cross-device payments:** Authorizing a payment from your phone to a
physical terminal.

These flows demand instantaneous, highly reliable transactions in diverse
environments, often where internet reliability is non-existent. We need a
solution that is as reliable as the physical cash or card it replaces.

The initial design of Hybrid transport, while brilliant for online flows, simply
cannot meet the reliability demands of these new, ubiquitous offline scenarios.
The reliance on a WebSocket tunnel means that if the tunnel fails, the entire
cross-device flow collapses.

## Enter the offline transport revolution with BLE

The great news is that the FIDO Alliance, recognizing this critical need, has
made a game-changing move by adding a BLE (Bluetooth Low Energy) **offline**
**transport channel** to the Hybrid transport specification in
[CTAP 2.3](https://fidoalliance.org/specs/fido-v2.3-rd-20251023/fido-client-to-authenticator-protocol-v2.3-rd-20251023.html#hybrid-ble-channel).
This improves the reliability of Hybrid transports by introducing an offline
transport channel – BLE – in addition to the existing online
[WebSocket](https://datatracker.ietf.org/doc/html/rfc6455) channel.

This evolution is fundamentally about empowering users and developers by cutting
the cord of mandatory internet reliance for authentication flows.

### How does this improve the state of the world?

This isn't just a technical tweak; it's a monumental step toward a more secure
and accessible digital world:

- **Unmatched reliability:** By adding channels like Bluetooth Low Energy
(BLE), we introduce powerful fallbacks. If the internet connection is weak
or non-existent, the flow instantly and seamlessly shifts to a reliable
short-range communication method. This dramatically improves the success
rate of FIDO transactions in low-connectivity areas.
- **Empowering new use cases:** Offline capabilities are the necessary
foundation for truly usable Digital Wallets and digital credential
standards. Imagine confidently presenting your digital credentials at an
airport, border crossing, or retail store, knowing the transaction will
succeed regardless of the local network status.

### The technical backbone

The details of the new offline channel specifications, such as the proposed
Hybrid BLE Channel, are clearly laid out in the FIDO Client to Authenticator
Protocol
[specifications](https://fidoalliance.org/specs/fido-v2.3-rd-20251023/fido-client-to-authenticator-protocol-v2.3-rd-20251023.html).
Any changes to the specification are thoroughly reviewed by identity and
security professionals who are
[FIDO members](https://fidoalliance.org/members/); this ensures the security and
privacy guarantees of the protocol are valid. In this case it translates to the
fact that even when the data is traveling over local, short-range wireless
links, it remains uncompromised.

This new architecture ensures secure data transfer tunnel setup between the
client and the authenticator devices (e.g., your phone and a point-of-sale
terminal) using cryptographic keys, providing end-to-end encryption guarantees
along with proximity which is already a salient feature of the Hybrid protocol.

## The future is Hybrid, and it’s offline

The world is moving toward a ubiquitous, physical-digital hybrid existence. Your
smartphone is not just an internet browser; it’s your wallet, your ID, and your
ultimate authenticator.

By integrating offline transport channels, we are making Hybrid transport truly
resilient, accessible, and intuitive. This move solidifies FIDO's position as
the foundational security layer for the next generation of identity, payments,
and digital interactions.

The time for reliable, internet-independent authentication is here. Get ready
for a world where your most sensitive digital transactions succeed every time,
everywhere. Get ready for a world where your most sensitive digital transactions
succeed every time, everywhere – we're looking forward to seeing platforms
starting to support this new standard.

Stay secure, and keep building!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab