---
source: bughunters
source_url: https://bughunters.google.com/blog/fido
title: "The Evolution of FIDO Experiences on Android - Google Bug Hunters"
description: "Based on the FIDO specification, online authentication has undergone a significant transformation in the past years, moving beyond simple passwords to more secure, phishing-resistant methods."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/fido#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# The Evolution of FIDO Experiences on Android

![](https://storage.googleapis.com/bughunters-article-images/blogs/harshlal.jpg)

Harsh Lal

Software Engineer

Published: Jan 27, 2026

Security Engineering  Android

[RSS Feed](https://bughunters.google.com/feed/en)

# The Evolution of FIDO Experiences on Android

The landscape of online authentication has undergone a significant
transformation, moving beyond simple passwords to more secure,
phishing-resistant methods. At the forefront of this evolution is the
[FIDO (Fast Identity Online) Alliance](https://fidoalliance.org/), and Android's
implementation of FIDO specifications has played a crucial role in bringing
these modern security features to the masses.

In this post, we will take a closer look at how FIDO has evolved on Android over
the past years.

### Early Days with Passwords

Passwords have been around for a long while and have been used for online
services since the early days of the internet as a means of user authentication.
They have been the primary gatekeepers for our digital lives and data. They are
ubiquitous and everywhere. There is barely any online service where you have not
seen a username/password field. ( _You might have thought it was everywhere? Well_
_no, because [passkeys](https://fidoalliance.org/passkeys/) have arrived._)

Passwords are not without issues.

1. **Password Complexity -> Password Reuse**

Passwords, in order to be secure, need to be something that is not easily
guessable by computers. But humans are not great at remembering complex
sequences of words. Hence once memorized, people often reuse them.

2. **Storage -> Prone to Data breach**

And if they don't memorize the password - they might write it on a
[sticky note](https://en.wikipedia.org/wiki/Sticky_note). This is equally
bad. Or the responsible ones might use a password manager. But passwords are
what’s known as
“ [symmetric secrets](https://en.wikipedia.org/wiki/Symmetric-key_algorithm)”.
It means that there’s a risk that your password could be exfiltrated from
the remote service in the event of a data breach.

3. **Phishing -> Can be leaked**

Even with all the precautions taken to ensure passwords are stored securely,
there is always a risk that a malicious actor can get hold of your password
in transit via phishing when you use it to authenticate yourself to an
online service.


### Introduction of Universal Second Factor

Clearly the issue with passwords needed to be addressed. The U2F standard
(Universal Second Factor) was developed in 2014 as an answer to this. It was
then contributed to the FIDO Alliance. U2F was designed to add a strong,
phishing-resistant second factor to existing password-based logins (see
[The Key to working smarter faster and safer](https://www.youtube.com/watch?v=LUHOs_ggvi4),
a decade-old post on YouTube discussing security keys).

A typical flow using security keys as a second factor comes after entering
username and password, and looks like the following on Android. Here you can see
an intro page describing the multiple mechanisms that can be used to connect to
the security key. Once the security key is connected using a USB port - you have
to allow Android permission to talk to the security key. Then the key flashes
and one has to touch the metal disc on the security key to complete a successful
authentication ceremony. There are a lot of steps in the flow which can be
confusing for not-so-tech-savvy users. But that’s how any new technology is. It
evolves over time to address user concerns until a point where it becomes second
nature.

![](https://storage.googleapis.com/bughunters-article-images/blogs/fido_07.svg)

_Fig. 1. Steps for setting up a security key on Android before FIDO2 support_

### Advent of Passkeys

A lot of things have changed since the early days of U2F as a second factor
authentication mechanism. FIDO2 now replaces U2F and the
[FIDO UAF (Universal Authentication Framework)](https://fidoalliance.org/specs/fido-uaf-v1.2-ps-20201020/fido-uaf-protocol-v1.2-ps-20201020.html)
standards, designed to enable truly passwordless authentication across the web.
It consists of two components: the W3C's Web Authentication
( [WebAuthn](https://www.w3.org/TR/webauthn-3)) standard and the FIDO Alliance's
Client to Authenticator Protocol 2
( [CTAP2](https://fidoalliance.org/specs/fido-v2.2-ps-20250714/fido-client-to-authenticator-protocol-v2.2-ps-20250714.html)).
For Android this meant supporting new security standards & improvements in terms
of simplicity, usability, and security. This led to the birth of passkeys, now
[adopted](https://blog.google/technology/safety-security/the-beginning-of-the-end-of-the-password/)
by all major platforms.

A _passkey_ is a FIDO authentication credential, built upon FIDO standards, that
enables users to sign in to applications and websites. This sign-in process is
streamlined, using the same mechanism a user employs to unlock their device,
such as biometrics, a PIN, or a pattern. Functioning as a FIDO cryptographic
credential, a passkey is securely linked to a user's account for a specific
website or application. Consequently, users are no longer required to input
usernames, passwords, or extra factors; instead, they simply confirm the sign-in
using their device's unlock method (e.g., biometrics, PIN, or pattern). These
passkeys can be saved in a software password manager for ease of use, or a
hardware security key for power users.

Below is the same flow as earlier in the post passkey world. Besides the obvious
UI improvements where Android now delights users with
[Material3](https://m3.material.io/) Design language, the experience of using a
passkey has changed as well. Note that the first option presented below is a
passkey stored locally on device (via a PasswordManager). If one doesn’t exist
then the flow proceeds to offer different options like using a security key or
presenting a passkey from a different device (phone/tablet). Android now uses
[bottomsheets](https://developer.android.com/reference/com/google/android/material/bottomsheet/BottomSheetDialogFragment)
instead of an older fullscreen experience, which aids in providing users with
more context about the service they are authenticating to. The number of screens
has also been optimized, there aren't additional pop ups when a security key is
plugged into the device during the flow. Introduction of
[Credential Manager APIs](https://developer.android.com/identity/credential-manager)
makes this integration easier for developers as well.

![](https://storage.googleapis.com/bughunters-article-images/blogs/fido_08.svg)

_Fig. 2. Steps for setting up a security key on Android post FIDO2 support_

### Android Support for FIDO

Android now supports FIDO2 specs over USB, which was [announced in November\\
2023](https://blog.google/products/android/new-android-features-november-2023/)
with the addition of PIN support. This allows setting a PIN for security keys
using a specialized algorithm (PIN protocol), which allows users to set a PIN on
a key without saving the actual PIN in the Operating System or the Security Key.
Below are the screens that allow for setting and using a PIN on security keys on
Android.

![](https://storage.googleapis.com/bughunters-article-images/blogs/fido_09.svg)

_Fig. 3. Steps for setting up and using a PIN on a security key on Android_

Android has been constantly improving its FIDO support and adding new features
and functionalities to keep their users more secure. While these milestones
represent significant progress toward a passwordless future, our journey doesn’t
stop here. We are continuing to build on this momentum by looking at how to
address key enhancements, such as expanding FIDO2 support over NFC, introducing
native credential management for physical security keys etc. While the FIDO
alliance constantly meets and iterates over specifications, Google is committed
to addressing these changes in Android to bring the best of security and privacy
to its users. Feature requests and bugs can be followed along in the
[public issue tracker](https://issuetracker.google.com/issues?q=componentid:1301097%20status:open).
The FIDO Alliance also constantly meets and iterates on the specification to
address usability, security, privacy, enterprise etc. needs and as such the spec
keeps evolving. All this means is that new features continually need to be added
to Android to keep improving security and the user experience. For example, with
the advent of quantum computers, the FIDO specification will need to evolve to
handle cryptographic algorithms that keep your data safe in a post-quantum
world. But with the [industry](https://fidoalliance.org/members/) putting their
resources into tackling the problem, it seems like passkeys as a technology is
headed in the right direction. A lot has been done, a lot more to do.

In a follow-up post, we will talk about the usage of passkeys on security keys
and how to effectively utilize them. Stay tuned!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab