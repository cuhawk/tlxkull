---
source: bughunters
source_url: https://bughunters.google.com/blog/passkeys
title: "A Beginners Guide: Cross-Device Passkeys - Google Bug Hunters"
description: "Find out more about how passkeys can be used across devices using a mechanism called Hybrid transport."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/passkeys#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# A Beginners Guide: Cross-Device Passkeys

![](https://storage.googleapis.com/bughunters-article-images/blogs/harshlal.jpg)

Harsh Lal

Software Engineer

Published: Feb 3, 2026

Security Engineering  Android

[RSS Feed](https://bughunters.google.com/feed/en)

# A Beginners Guide: Cross-Device Passkeys

In the first [post](https://bughunters.google.com/blog/fido) of this series, we
took a closer look at the Evolution of [FIDO](https://fidoalliance.org/)
experiences on Android, and how they significantly shaped the transformation of
online authentication. Building on that discussion, this post focuses on how
passkeys can be used across devices using a mechanism called Hybrid transport.
This is an important piece of the puzzle to make passkeys available everywhere.

## Introduction: Passkeys and the cross-device challenge

[Passkeys](https://www.passkeycentral.org/introduction-to-passkeys/) are a
significant advancement in user authentication, offering a more secure and
convenient alternative to passwords. They are rapidly establishing themselves as
the gold standard for user authentication, fundamentally replacing passwords
with secure, convenient cryptographic public-private key pairs. Passkeys were
designed to be inherently phishing-resistant, immune to brute-force attacks, and
offer a significant increase in sign-in success rates and speed compared to
traditional passwords. Passkeys utilize cryptographic keys stored on end-user
devices, where a private key creates authentication signatures and a public key
is stored on the server for verification.

While most passkeys are designed to be synchronized within a cloud account
ecosystem (like Google Password Manager) for seamless access across the user's
personal devices, a common scenario presents a challenge: logging in on a device
where the passkey isn't immediately available, such as a public terminal or a
friend's laptop or communal devices like TVs.

This is where the concept of **Hybrid transport** – formally defined in the
[CTAP specification](https://fidoalliance.org/specs/fido-v2.2-ps-20250714/fido-client-to-authenticator-protocol-v2.2-ps-20250714.html#sctn-hybrid)
– becomes crucial. Hybrid transport is the secure bridge that allows a user to
access their passkeys across multiple devices using a combination of QR codes
and Bluetooth Low Energy (BLE) technology. Hybrid transport delivers on the
promise that passkeys are yours to keep. It is essential for ensuring robust
passkey adoption by offering flexibility without sacrificing security.

## Understanding Hybrid transport (cross-device sign-in)

Hybrid transport allows users to sign in on a device (the "client," e.g., a
laptop) that does not hold the passkey, by leveraging a second device (the
"authenticator," e.g., a mobile phone) that does.

This method is vital because it addresses the core design principle that private
keys must remain securely bound to the user's device, often protected by
hardware components like a Secure Enclave or Tamper-Proof-Module (TPM). For
passkeys that are not synchronized through the same cloud account or password
manager, Hybrid transport provides a secure, physical-proximity-based method for
authentication.

Following is an example of using a cross-device passkey to log in to a service.
The client device (e.g. a Chrome browser) shows a QR code as below.

![](https://storage.googleapis.com/bughunters-article-images/blogs/passkeys_01.png)

_Fig. 1. A QR code displayed by a client device used to request a passkey._

The authenticator device (e.g. Android Phone) scans the QR code. The camera
detects that this is a passkey request and shows a “ _Use Passkey_” chip as seen
in the first image below. Clicking the “ _Use Passkey_” chip starts the hybrid
encrypted tunnel setup between the client and authenticator. This process
involves exchanging cryptographic keys and handshakes as defined in the
[protocol](https://fidoalliance.org/specs/fido-v2.2-ps-20250714/fido-client-to-authenticator-protocol-v2.2-ps-20250714.html#hybrid-qr-initiated).
A “ _Connecting with another device_” bottomsheet is shown during this step as
seen in the second image below, initiating creation of an End-to-End-Encrypted
Tunnel. Once an E2EE tunnel is set up, the request for a passkey is transmitted
from client to the authenticator. The authenticator, on receiving the request,
queries the password managers on device for the passkey. If one is found, a user
verification prompt is shown to the user, as seen in the third image below. Once
the user accepts, the approval is transmitted securely to the online service
running on the client. The client verifies the approval and grants user access
to their service.

![](https://storage.googleapis.com/bughunters-article-images/blogs/passkeys_02.svg)

_Fig. 2. The process of using a passkey on the authenticator device by scanning_
_a passkey QR code._

As seen here, there was no need to type in a username and/or password and
transmit it. The protocol is designed to prevent the transmission of
user-identifying information in a way that could be intercepted by a
person-in-the-middle attacker. Also, given passkeys are stored in your password
manager – the risk of losing one is far lower than forgetting a password and
having to reset it which is a common avenue for phishing attacks.

### The role of QR codes and Bluetooth

The cross-device authentication flow primarily utilizes QR codes for initiating
the transaction, while Bluetooth Low Energy (BLE) is often employed for a
proximity check, adding an essential layer of security.

| Component | Function in Hybrid Flow | Security Benefit |
| --- | --- | --- |
| QR Code | Initiates the authentication ceremony by encoding a unique, time-sensitive session identifier. | The identifier is one-time use and encrypted, preventing replay attacks and interception. |
| Internet Connection (Websocket) | Transmits the encrypted challenge-response data between the authenticator device and the server. | Provides a reliable data transport channel over the internet. The data transport channel is untrusted, but message exchange using hybrid protocol provides security guarantees by utilizing E2EE(end to end encryption). |
| Bluetooth (BLE) | Performs a proximity check, confirming that the client and authenticator devices are physically close to each other. | Minimizes the risk of man-in-the-middle attacks by confirming physical presence before proceeding with authentication. |

## The step-by-step Hybrid flow (QR code initiated)

The QR code method is the most common type of the Hybrid transport flow and is
critical for cross-platform access.

1. **Initiation**: The user attempts to sign in on a client device (e.g., a
desktop) where their passkey is not present. The service provider displays
an option to "Sign in with a different device," prompting the device to
generate a QR code.
2. **QR Code Generation**: The client device generates a unique, time-sensitive
QR code encoding a FIDO URI with a session identifier.
3. **Scanning**: The user scans the QR code using their authenticator device
(e.g., smartphone), which possesses the passkey.
4. **Data Flow and Challenge**: Scanning the FIDO URI triggers the
authenticator device to communicate with the authentication server. The
server responds by generating a cryptographic challenge unique to this
attempt.
5. **Signature Transmission**: The authenticator device uses its private key to
create a digital signature of the challenge – crucially, the private key
never leaves the device. This signed challenge is sent back to the server
over a secure, encrypted tunnel via the internet.
6. **Validation**: The server validates the signature using the corresponding
public key associated with the user's account. Upon successful validation,
the user is logged in on the client device.

It is important to emphasize: while QR codes and Bluetooth are the visible
components, the actual authentication data exchange relies entirely on
asymmetric cryptography and the fact that the private key does not leave the
device. The specifics of the algorithm are spelled out in the hybrid protocol.
Bluetooth's primary role is confirming the physical proximity of the two
devices.

## Importance for passkey adoption

Hybrid transport directly addresses a major hurdle in passkey adoption: the
perceived inconvenience of accessing accounts on shared or new devices. For more
details on this topic, check out
[this detailed talk](https://www.youtube.com/watch?v=Wt6DO1rdOqU).

- **Enhanced User Experience (UX)**: By providing a mechanism to sign in
without manually entering credentials on an unfamiliar device, Hybrid
transport makes the passkey experience seamless and convenient. This is
particularly appreciated by users who view it as a safer way to access
accounts on public devices, as personal credentials aren't exposed on the
shared machine.
- **Balancing Security and Convenience**: The flow maintains the core security
advantage of passkeys – phishing resistance – while improving usability. The
proximity check via Bluetooth ensures the process requires physical
presence, mitigating remote attack vectors.
- **Driving Adoption**: Features like cross-device sign-in encourage users to
adopt passkeys as their primary authentication method, ultimately
streamlining the overall user experience and improving security across the
board by getting rid of passwords.

Hybrid transport ensures that a user can maintain a high-security posture (using
a passkey) even when switching between operating systems or accessing a service
from a device that is not part of their usual synchronized ecosystem. This
flexibility is essential for mass market adoption and realizing the full
potential of a passwordless future.

In the next post of this series, we will take a look at recent upgrades to
Hybrid transport and how they further improve its capabilities.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab