---
source: oversecured
source_url: https://oversecured.com/blog/use-cryptography-in-mobile-apps-the-right-way
title: "Use cryptography in mobile apps the right way | Oversecured Blog"
author: "HubSpot, Inc."
description: "At Oversecured, we scan thousands of apps every month. We observe that some vulnerabilities now come up much less frequently than they did a few years ago. But the same cannot be said"
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

At Oversecured, we scan thousands of apps every month. We observe that some vulnerabilities now come up much less frequently than they did a few years ago. But the same cannot be said of insecure cryptography: we still encounter this particular vulnerability just as often as before. Our internal statistics show that more than 77% of apps contain errors relating to hardcoded or predictable encryption keys, or else to insecure configuration of the encryption algorithm (e.g. weak ciphers or small key sizes).

The job of cryptography is to provide an additional level of protection for the user’s data. But cryptography is used incorrectly in almost all mobile apps or in certain parts of them, such as third-party SDKs. Developers frequently fail to understand what cryptography is being used for, where to obtain encryption keys, and what to do with them, as well as the threat model. In this article we shall try to explain the commonest errors as well as offering some practical tips on how to protect mobile apps.

Do you want to check your mobile apps for these types of vulnerabilities? Oversecured’s mobile app scanner provides an automatic solution that helps to detect vulnerabilities in Android and iOS mobile apps. You can integrate Oversecured into your development process and check every new line of your code, to ensure your users are always protected.

Start securing your apps by starting a free 2-week trial from [Quick Start](https://app.oversecured.com/docs/quick-start/), or you can [book a call](https://calendly.com/oversecured/30min) with our team or [contact us](https://app.oversecured.com/contact-us) to explore further.

## Why to use cryptography in mobile apps

Yes, why? Both Android and iOS offer secure storage, isolated from third-party apps, which an app uses to store sensitive data. Nobody except the app itself (and root) can gain access to files stored in these specified directories. So they need to be protected from the app itself! If you look at a typical list of vulnerabilities you will notice the possibility of access to internal app files, e.g.:

- [via WebView in the Amazon app](https://blog.oversecured.com/Android-Exploring-vulnerabilities-in-WebResourceResponse/)

- via [obtaining access to arbitrary\* content providers](https://blog.oversecured.com/Gaining-access-to-arbitrary-Content-Providers/)

- via [implicit intents](https://blog.oversecured.com/Interception-of-Android-implicit-intents/#typical-vulnerabilities-in-standard-android-actions)

- hundreds of other examples that are not covered by articles on our blog


If the data in these examples had been properly encrypted at the app level, then an attacker would have benefited very little from these vulnerabilities. Reading any files from internal directories would have led only to their encrypted content being leaked. Rewriting these files could have led to an automatic logout from the user’s account, but no more than that.

## How not to encrypt data, on any platform

### Hardcoded cryptographic keys

Secret keys that protect data or internet communications are frequently hardcoded. We provide an example of this kind of vulnerability in our [Oversecured Vulnerable Android App](https://github.com/oversecured/ovaa). The Oversecured result for the vulnerable code segment looks like this:

![](https://framerusercontent.com/images/ivZlRFSCNmBZioCOg00IJBFbA.png?width=2248&height=722)

And an example for iOS from [Oversecured Vulnerable iOS App](https://github.com/oversecured/OversecuredVulnerableiOSApp):

![](https://framerusercontent.com/images/85kDE69jXWfGnjGEARdTN0elSMQ.png?width=2254&height=2712)

An attacker can decompile the app, understand the algorithm and compute the key, and then proceed to remove this level of protection - meaning they will be able to decrypt encrypted data.

## Predictable cryptographic keys

One popular error is to generate encryption keys with a predictable seed value:

SecureRandom secureRandom = newSecureRandom("known\_seed".getBytes());

KeyGenerator generator = KeyGenerator.getInstance("AES");

generator.init(256,secureRandom);

Key key = generator.generateKey();

If pseudorandom values are used:

private byte\[\]generateKey(){

byte\[\]key = newbyte\[128\];

Random random = newRandom();

for(int i = 0;i < 128;i++){

key\[i\] = (byte)random.nextInt(256);

}

returnkey;

}

private byte\[\]encrypt(byte\[\]data){

SecretKeySpec skeySpec = newSecretKeySpec(generateKey(),"AES");

//...

}

If the value of the key is not initialized, which automatically results in a key with all bytes equal to `0`:

private byte\[\]encrypt(byte\[\]data){

byte\[\]key = newbyte\[128\];

SecretKeySpec skeySpec = newSecretKeySpec(key,"AES");

//...

}

Or if the key value is generated securely but then stored in clear in the file system (often in Shared Preferences).

## The right way to encrypt data on Android

Android offers an interface known as [Keystore](https://developer.android.com/training/articles/keystore). Apps can only obtain encryption keys via the programming interface, not by reading files directly. The files containing the encryption keys are themselves stored in `/data/misc/keystore/` and belong to the `keystore` user.

## The right way to encrypt data on iOS

iOS provides a mechanism for working with encryption keys, referred to as Secure Enclave. Similarly to Android, any interactions with these keys are only possible via programming interfaces - not by reading files directly.

You can also generate keys and store them in the Keychain yourself.

## Recommendations for cryptography in mobile apps

So, if Android apps encrypt all sensitive data using keys from Keystore and iOS apps use keys stored in Keychain, it will not be possible to decrypt the data unless there are vulnerabilities permitting arbitrary code execution. Arbitrary code execution is a critical but comparatively uncommon vulnerability. But other, less critical vulnerabilities can reduce the risk of sensitive data stored in the file system being leaked to zero.

Oversecured recommend encrypting any sensitive data that the app stores. This includes user authentication tokens (the user’s credentials should never be stored on the client, under any circumstances!), financial and health data, and the user’s private messaging and communications.

It is also important to delete all user data and destroy encryption keys after the user signs out.

##### Keep reading

[View all](https://oversecured.com/blog)

[![](https://framerusercontent.com/images/OnN0UKCOhnnXin2eBts9J3SaUQ.png?width=5592&height=3259)\\
\\
20 Security Issues Found in Xiaomi Devices\\
\\
Oversecured found and resolved significant mobile security vulnerabilities in Xiaomi devices. Our team discovered 20 dangerous vulnerabilities across various applications and system components that pose a threat to all Xiaomi users. The vulnerabilities\\
\\
Case Study\\
\\
May 2, 2024\\
\\
15\\
\\
min read\\
\\
TOp article](https://oversecured.com/blog/20-security-issues-found-in-xiaomi-devices)

[![](https://framerusercontent.com/images/W9Wn9vbZPPJFNH7MN7Zx6QXches.png?width=2048&height=1194)\\
\\
Android deep link vulnerabilities: how intent filters lead to account takeover\\
\\
A technical guide to Android deep link security. Learn how intent filter misconfigurations lead to account takeover, and how mobile application security testing with SAST and DAST finds these vulnerability chains.\\
\\
Android Security\\
\\
Apr 27, 2026\\
\\
8\\
\\
min read](https://oversecured.com/blog/android-deep-link-vulnerabilities)

[![](https://framerusercontent.com/images/xSiSLs1y7y6Mzr4lWYWCpFoYmM4.png?width=2848&height=1656)\\
\\
Android security checklist: theft of arbitrary files\\
\\
Developers for Android do a lot of work with files and exchange them with other apps, for example, to get photos, images, or user data. \\
\\
Android Security\\
\\
May 20, 2022\\
\\
11\\
\\
min read\\
\\
TOp article](https://oversecured.com/blog/android-security-checklist-theft-of-arbitrary-files)

Book a personalized demo

During the demo with our cybersecurity experts you will get:

A free trial scan of your app

An analysis of your SAST and DAST findings

Practical insights on mobile security of your app

First name

Business email

How did you hear about us?

Book a demo

2026 © Oversecured

follow us

### [LinkedIn](https://www.linkedin.com/company/oversecured/)

### [Twitter (X)](https://x.com/oversecuredinc)

[Privacy Policy](https://oversecured.com/privacy)

[Terms of use](https://oversecured.com/terms)

[go up ↑](https://oversecured.com/blog/use-cryptography-in-mobile-apps-the-right-way#header)

Chat Widget