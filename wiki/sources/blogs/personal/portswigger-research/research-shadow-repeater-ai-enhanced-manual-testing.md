---
source: portswigger-research
source_url: https://portswigger.net/research/shadow-repeater-ai-enhanced-manual-testing
title: "Shadow Repeater:AI-enhanced manual testing | PortSwigger Research"
published: 2025-02-20T13:20:19
description: "Have you ever wondered how many vulnerabilities you've missed by a hair's breadth, due to a single flawed choice? We've just released Shadow Repeater, which enhances your manual testing with AI-powere"
---

# Shadow Repeater:AI-enhanced manual testing

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Thursday, 20 February 2025 at 13:20 UTC

- **Updated:** Tuesday, 25 February 2025 at 09:06 UTC


![Shows a few different vectors in different colours](https://portswigger.net/cms/images/6a/14/5e0e-article-shadow_repeater-article.png)

**Have you ever wondered how many vulnerabilities you've missed by a hair's breadth, due to a single flawed choice?**

We've just released Shadow Repeater, which enhances your manual testing with AI-powered, fully automatic variation testing. Simply use Burp Repeater as you normally would, and behind the scenes Shadow Repeater will monitor your attacks, try permutations, and report any discoveries via Organizer.

Shadow Repeater aids deep, targeted testing by analysing your payloads so when you have a near miss due to sending the wrong syntax, incorrect encoding, file path, or simply a typo, it can find the bug for you. It's fully automatic, and doesn't require any changes to your normal manual testing workflow.

## How does Shadow Repeater work

Shadow Repeater monitors your Repeater requests and identifies which parameters you're changing. It then extracts the payloads you've placed in these parameters, and sends them to an AI model which generates variants. Finally, it attacks the target with these payload variations and uses response diffing to identify whether any of them triggered a new interesting code path. This approach allows it to build on a manual tester's expertise to uncover unexpected behaviors, such as unconventional [XSS](https://portswigger.net/web-security/cross-site-scripting) vectors, successful [path traversal](https://portswigger.net/web-security/file-path-traversal) attempts, and even novel vulnerabilities like email splitting attacks.

You can get the source code for [Shadow Repeater on Github](https://github.com/hackvertor/shadow-repeater) and it's available on the BApp store.

Using the AI-powered Shadow Repeater extension to discover SSTI variations with Burp Suite - YouTube

Tap to unmute

[Using the AI-powered Shadow Repeater extension to discover SSTI variations with Burp Suite](https://www.youtube.com/watch?v=Z1uJmfCGpRE) [PortSwigger](https://www.youtube.com/channel/UCkytgKNbJ0L1UuN1K27GAKA)

PortSwigger39K subscribers

## Installation instructions

**In [Burp Suite Professional](https://portswigger.net/burp/pro), go to Extensions->BApp store and search for Shadow Repeater. Click the install button and then navigate to the installed tab then select Shadow Repeater and check the "Use AI" checkbox in the Extension tab.**

![Screenshot of Shadow Repeater Extension tab](https://portswigger.net/cms/images/48/59/649a-article-shadow-repeater-install-screenshot.png)

## Usage

By default, Shadow repeater gets invoked on the 5th repeater request you make, and it requires a parameter or header to be changed. You simply try to hack a target by altering the request in some way. In the background Shadow repeater will send variations and look for differences in the response. When it's found something interesting it will send it to the organiser for inspection.

## The journey to Shadow Repeater

At PortSwigger we had an opportunity to pitch our ideas for an AI feature in a Dragons Den style competition. I thought it wouldn't be cool if Burp could analyse Repeater requests and find variations of whatever you're testing for even unknown vulnerabilities. I failed. I couldn't see how it would work. I choose instead to focus on finding unknown encodings with AI Hackvertor.

Using my experience of improving AI Hackvertor, I found myself more comfortable with how the AI works, how to send user input safely and how to get responses that were actually useful. If you know me, you'll know I can't leave things alone. I once came back to exploit the [AngularJS](https://portswigger.net/web-security/cross-site-scripting/contexts/client-side-template-injection) HTML filter 2 years after I originally tested it. This dragon dens idea was no exception, I came back to work on it recently.

My first breakthrough was to think about differences, previously I was sending entire Repeater requests to the AI for analysis and getting it to parse the request. Parsing entire requests was of course a bad idea. However, I needed this failed experiment to see what the AI was capable of. I thought about using diffing logic in a Github style diff of requests and responses. I chatted with James and he suggested using differences in parameters. So I wrote a Request Differ in Java to analyse the headers, parameters and URL path and only send the changing values to the AI. Now the AI was only analysing a small amount of data that was very focussed on what you are trying to hack.

My second breakthrough was instead of telling the AI to understand what is being tested, I simply told it to find variations of it. This meant giving the AI general instructions to find variations but not going to detail about what it's actually testing. This works surprisingly well: it's aware of the context thanks to the Request Differ and knows the data you're testing. It generated variations for Path Traversal, XSS and other types of vulnerabilities.

I was successfully generating variations of what the user was testing but how do I know the variation is relevant? This is where response diffing comes into play. I borrowed the legend that is Mr Kettle as he'd done extensive work in Backslash Powered Scanner diffing logic. He gave me some code samples on how his response diffing works and I added each variation generated by the AI to the analysis list as well as the user's request and some random control values. I then looked for invariant attributes of the response that changed when a variation was sent. This gave some cool results! This technique was able to find that spaces are allowed in a XSS vector, if a path traversal vector actually works and even unknown vulnerabilities such as email splitting attacks.

This is just one example of what's now possible thanks to AI-powered extensions in Burp Suite. Check it out for yourself - Shadow Repeater is now available from the BApp Store for users on the Early Adopter release channel of Burp Suite Professional.

Feeling inspired? Try [creating an AI-powered extension yourself](https://portswigger.net/burp/documentation/desktop/extensions/creating/creating-ai-extensions) using Burp's built-in Montoya API and its dedicated interfaces for handling traffic between your extension and PortSwigger's trusted AI platform.

## AI security & privacy

We've updated our docs to reflect how we handle data sent to the AI please check out the [detailed documentation](https://portswigger.net/burp/documentation/desktop/extensions/ai-security-privacy-data-handling) and the [blog post](https://portswigger.net/blog/why-its-time-for-appsec-to-embrace-ai-how-portswigger-is-leading-the-charge).

[AI](https://portswigger.net/research/ai) [web security](https://portswigger.net/research/web-security) [Burp Suite](https://portswigger.net/research/burp-suite)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Repeater Strike: manual testing, amplified** 15 July 2025Repeater Strike: manual testing, amplified](https://portswigger.net/research/repeater-strike-manual-testing-amplified) [**Document My Pentest: you hack, the AI writes it up!** 23 April 2025Document My Pentest: you hack, the AI writes it up!](https://portswigger.net/research/document-my-pentest) [**Using form hijacking to bypass CSP** 05 March 2024Using form hijacking to bypass CSP](https://portswigger.net/research/using-form-hijacking-to-bypass-csp)