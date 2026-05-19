---
source: daniel-miessler
source_url: https://danielmiessler.com/blog/rudimentary-threat-model-framework-password-vs-touchid-vs-faceid
title: "A Rudimentary Threat Model Framework for Password vs. TouchID vs. FaceID | Daniel Miessler"
description: "There’s been a lot of discussion around Apple’s replacement of TouchID with FaceID on the new iPhone X. There’s conversation around the overal"
---

There’s been a lot of discussion around Apple’s replacement of TouchID with [FaceID](https://www.bbc.com/news/technology-41266216?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-rudimentary-threat-model-framework-for-password-vs-touchid-vs-faceid) > on the new iPhone X. There’s conversation around the overall security of biometric authentication vs. as well as comparisons of TouchID security vs. that of FaceID.

Unfortunately, the usual question being asked is something like:

Which is more secure?

But what they should be asking is a more nuanced:

For my particular situation, am I more secure using a password, TouchID, or FaceID?

This is the reason Threat Modeling is important: it highlights the fact that it’s impossible to understand the efficacy of a control without understanding how it’ll be attacked.

I built the system above to highlight this concept as it relates to different types of personal device authentication. It’s a crude model, but it shows the key considerations and how they map to reality. Here’s the structure of the model.

First it captures realworld scenarios that you might face (threats).

It has you prioritize which of those scenarios matter the most.

Then it captures how well the three options (password, TouchID, and FaceID) will do against those scenarios.

So here’s the methodology for determining which auth system makes the most sense *for you*.

You put your top three (3) scenarios in order, and each gets a multiplier. Your first most important gets 3x, the second gets 2x, and third gets 1x.

Then the four (4) different security levels (LOW, MEDIUM, HIGH, MAX) are given numeric values as well, going from one to four (1-4). See above.

Then for each scenario you multiply the scenario multiplier by the control value (1-4 based on the rating), and then add them up going down the scenarios.

Now we run the numbers multiplying the scenario weight by the control strength for each control.

So, considering just the Password control

Convenience (3) x LOW (1) = 3

Shoulder-surfing (2) x LOW (1) = 2

Law enforcement (1) x HIGH (3) = 3

3 + 2 + 3 = **8**.

So, considering just the TouchID control

Convenience (3) x HIGH (3) = 9

Shoulder-surfing (2) x MAX (4) = 8

Law enforcement (1) x MED (2) = 2

9 + 8 + 2 = **19**.

So, considering just the FaceID control

Convenience (3) x MAX (4) = 12

Shoulder-surfing (2) x MAX (4) = 8

Law enforcement (1) x LOW (1) = 1

12 + 8 + 1 = **21**.

**So we end up with the relative strength—for this set of scenarios—being: Passwords (8), TouchID (19), and FaceID (21).** So with the highest score, FaceID wins.

What’s important here is that these numbers represent **a combination** of both your most important scenarios (the weighting of the multiplier) AND the effectiveness of the controls across those various situations.

Given as an English sentence we’d basically be saying:

Based on me valuing these scenarios the most, and the effectiveness of each authentication system in those situations, FaceID seems best match for me, with TouchID being pretty close and passwords lagging pretty far behind.

And here’s the key: I only spent a few moments coming up with those ratings, and there are more scenarios that could be added. And as you update the data in the model, your recommended authentication method (the highest score) might change along with it.

Hopefully this will help some folks understand Threat Modeling a bit more—at least at a basic level—and thus enable clearer thinking about how various security measures can be rated for practical effectiveness.

We could obviously debate pretty much every rating for every scenario, but the chance of getting security material means the ease of stealing someone’s fingerprint, stealing someone’s face, or stealing their password. And there’s obviously a difference between getting an image of a face vs. getting something that will unlock a device. So keep that all in mind.

For the law enforcement stuff I assumed you didn’t have time, or didn’t remember, to enable the Cop Mode feature that then requires a password be used instead of TouchID or FaceID

I think it’s interesting that if someone grabs your phone from you or in front of you, the first reaction is to look at them, which is precisely what will unlock it. I think we’re about to have to train people to look away, or close their eyes, when this happens.

I also think there should be an Apple Watch or Mac-based way to lock the phone remotely if someone does this trick to take and then unlock your device using your own face.