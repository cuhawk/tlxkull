---
source: daniel-miessler
source_url: https://danielmiessler.com/blog/faceid-removes-an-authentication-step-except-for-apple-pay
title: "FaceID Adds a Step for Apple Pay, and For Good Reason | Daniel Miessler"
description: "FaceID is an upgrade not just because it’s more accurate than TouchID, or because it’s a faster way to authenticate—it’s an upgrade because you are basically re"
---

I wrote that about FaceID itself, and now that I have the new iPhone X I have had a chance to use it for Apple Pay.

The interesting thing is that while we lost an authentication step with FaceID, we gained one with Apple Pay.

The issue is that *you have to include an explicit action when initiating Apple Pay no matter what*. It cannot just be the proximity of the reader. It that were the only requirement then people would set up a charge on ad-hoc, mobile readers and then sneak up and charge things in your pocket or on your wrist in public places.

That would be bad. So it requires you to do *something*.

**With Apple Pay and TouchID** the $something was holding your thumb on the home button and bringing your phone close to the reader.

**With Apple Pay and FaceID** the $something is double-clicking the right button.

The double-click on the side is also how you enable Apple Pay on the Apple Watch.

But the TouchID with Apple Pay on the phone effectively *felt* like a step was removed because you had to hold the phone anyway. So if you just held your phone from the bottom, with your thumb on the sensor, you basically auto-authenticated the transaction.

So TouchID/ApplePay ended up being one step (hold phone to reader), while FaceID is currently **two** steps (hold phone to reader and double-click the right button).

The reason Apple can’t just use FaceID auth to authenticate Apple Pay transaction is (probably) because when you’re using your phone—say on a Subway—you will be authenticated. So at that point someone could just slide a reader under your phone and instantly authenticate a transaction.

For this reason you need that extra double-click step.

Anyway, just thought that was interesting.