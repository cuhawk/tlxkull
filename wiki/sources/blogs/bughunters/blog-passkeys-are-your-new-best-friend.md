---
source: bughunters
source_url: https://bughunters.google.com/blog/passkeys-are-your-new-best-friend
title: "Passkeys are Your New Best Friend - Google Bug Hunters"
description: "Find out more about how passkeys, which are designed to replace passwords, work and which advantages they bring."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/passkeys-are-your-new-best-friend#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Passkeys are Your New Best Friend

![](https://storage.googleapis.com/bughunters-article-images/blogs/harshlal.jpg)

Harsh Lal

Software Engineer

Published: Mar 30, 2026

Security Engineering  Android

[RSS Feed](https://bughunters.google.com/feed/en)

# Passkeys are Your New Best Friend

For decades, we've been told to create long, complex passwords, change them
often, and never reuse them. It’s a battle we're all losing. But a new
technology called **passkeys** is fundamentally changing the game. Built on the
[FIDO (Fast Identity Online)](https://fidoalliance.org/passkeys/) and
[WebAuthn standards](https://en.wikipedia.org/wiki/WebAuthn), passkeys replace
shared secrets (passwords) with cryptographic key pairs.

## The Security Model: What Makes Passkeys "phishing-resistant"?

Unlike a password, which is a string of characters you send to a website, a
passkey consists of two parts:

1. A **Private Key:** Stored securely on your device (like your phone or
laptop) and never shared with anyone.
2. A **Public Key:** Stored on the website’s server.

This asymmetric cryptographic model provides unique security guarantees. While
symmetric cryptography relies on a single shared secret known to both parties
(e.g., a password), passkeys use a key pair where each key performs a specific
function that the other cannot. The _private key_ is used to create a digital
signature, which serves as a non-repudiation guarantee – proof that the request
originated from the legitimate owner of the private key. The _public key_,
stored by the service, can verify this signature or be used to encrypt data so
that only the corresponding private key can decrypt it. This ensures that even
if a server is compromised and the public keys are leaked, they are useless for
authentication without the physical device's private key.

In practice, this works as follows: When you sign in, the website sends a
"challenge." Your device uses its private key to sign that challenge and sends
the signature back. The website then uses your public key to verify the response
from the device.

### Why this is safer than passwords:

- **Domain Binding:** A passkey is tied to the specific website it was created
for. An attacker can't trick you into using your "google.com" passkey on a
"fake-google.com" site because your browser simply won't allow the exchange.
- **No Data Breaches:** If a website is hacked, the hackers can only
exfiltrate public keys, which are useless for signing in without your
physical device's private key.
- **Built-in 2FA:** To use a passkey, you must unlock your device using
biometrics (fingerprint/face) or a PIN. This effectively provides two-factor
authentication in one seamless step.

* * *

## Hybrid "Magic": Signing In Across Devices

A common question regarding passkeys is: _"What if I want to sign in on a public_
_computer or a friend’s laptop where my passkey isn't stored?"_

This is where **Hybrid Transport** (also known as cross-device sign-in) comes
in. This functionality allows your phone to act as your "authenticator" for a
"client" device (like a smart TV or a laptop). You can read more about this
[here](https://bughunters.google.com/blog/passkeys).

### How the Hybrid Flow Works:

1. **Initiation:** The laptop shows a QR code.
2. **Proximity Check:** You scan the code with your phone. This uses
**Bluetooth Low Energy (BLE)** to prove the two devices are in the same
room. This prevents an attacker in another location from trying to trick you
– since most attackers aren't physically proximate to their victims, this
significantly reduces your chances of getting phished.
3. **Encrypted Tunnel:** An end-to-end encrypted tunnel is established between
the devices.
4. **The Signature:** You verify your identity on your phone (e.g., using
FaceID), and the phone sends the cryptographic signature to the laptop to
grant you access.

* * *

## Addressing Your Security Concerns: FAQs

When we move away from passwords, it's natural to worry about new risks. Here is
how the passkey model handles common threats:

| _Threat_ | _How Passkeys Protect You_ |
| --- | --- |
| **Device Theft** | A thief cannot use your passkeys without your biometric (fingerprint/face) or your device's screen lock PIN. |
| **Lost Device** | Most passkeys are "syncable." They are backed up in your cloud account (Google Password Manager). You can recover them on a new device. |
| **Credential Exfiltration** | Since there is no password to type, there is nothing for a "keylogger" or a packet-sniffer to record and reuse later. |

## Can a Passkey be Compromised?

While passkeys are a massive leap forward, no system is perfect. The primary
risks involve:

- **Sync Account Hijacking:** If someone hacks into your cloud account, they
could theoretically access your synced passkeys. However, major providers
usually require your old device’s screen lock to unlock the keys on a new
device, making such attacks difficult.
- **Social Engineering:** An attacker might try to convince you to scan a QR
code they've generated to get access to your account. Hence always ensure
you are the one who initiated the sign-in request on the screen you are
looking at. However, this kind of attack is difficult to do at scale as an
attacker would have to be in your physical location for the attack to be
feasible.

## Conclusion

Passkeys represent a "passwordless" future that is both easier to use and vastly
more secure. By moving away from things we _know_ (passwords) to things we
_have_ (devices), we are finally closing the door on the most common ways
accounts are hacked today.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab