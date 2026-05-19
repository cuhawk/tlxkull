---
source: detectify
source_url: https://labs.detectify.com/ethical-hacking/how-to-supercharge-your-hacking-mindset-workflow-productivity-and-checklist/
title: "Supercharge your hacking: Mindset, workflow, productivity and checklist - Labs Detectify"
author: "Detectify"
published: 2022-10-28T14:46:55+00:00
description: "In this article, Gunnar Andrews writes how hacking is a challenge, but can be made easier with the right environment, workflows and mindset."
---

[Home](https://labs.detectify.com/)/ [Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/)/ [Supercharge your hacking: Mindset, workflow, productivity and checklist](https://labs.detectify.com/ethical-hacking/how-to-supercharge-your-hacking-mindset-workflow-productivity-and-checklist/)

[Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/ "Ethical Hacking")

# Supercharge your hacking: Mindset, workflow, productivity and checklist

**Gunnar Andrews** Oct 28, 2022

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/how-to-supercharge-your-hacking-mindset-workflow-productivity-and-checklist/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/how-to-supercharge-your-hacking-mindset-workflow-productivity-and-checklist/ "Share on LinkedIn")

![Supercharge your hacking: Mindset, workflow, productivity and checklist](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F08%2Fsupercharged-hacking.png&w=3840&q=75)

Approaching a target to hack can feel like climbing a mountain. You may face large scopes, confusing applications, complex user hierarchies…the list goes on. The key to hacking in today’s world of large and/or complicated targets is a combination of two things:

1. A work environment that encourages productivity.
2. A workflow or checklist of steps to have an efficient yet complete engagement.

The following steps are a good blueprint to get you down the path of supercharged hacking!

## **Step 1: Preparing your workspace**

The first step to having a supercharged workflow is your workspace. There are three quick things to keep in mind when preparing yourself and your workspace:

- Desk setup
- Distractions
- Mindset

### Desk setup

Having the tools you need to do the job is vital to the task’s completion. This remains true when you sit down to hack. The ideal setup will include a spacious workspace with as little clutter as possible. If there is too much clutter on your desk or workspace, it is proven that this will distract you. You should have only the necessities. Ideally, a comfortable chair that keeps you at the right height is equally important. Any decorations or personal items on your desk should be in the background, out of your way. Some studies say adding a “flow” to your workspace is a hidden secret. For instance, create a space where incoming tasks are on your left, your PC or workstation is in the middle, and completed tasks are to the right.

### Distractions

Your workflow can’t be supercharged if you are constantly being interrupted. Placing any phones or electronics and other distractions away would be ideal. These electronic distractions should also be silenced. This effort will increase the chance that you stay focused while working. Some people enjoy different types of music or background noise while working. Everyone is different in this regard, but keep in mind that if there is background music, it should not require your constant attention. It should be something you can start and leave alone. Giving yourself breaks is important, but always ensure your working time is as productive as possible.

### Mindset

Your mindset can completely change how you see a challenge. So you must go into your hacking sessions with a good mindset. But what makes a good mindset? Well, I would argue that the following list is a good place to start:

1. Setting personal goals for your day.
2. Remembering your long-term growth is more important than short-term results.
3. Making mission statements.
4. Enjoy the process and enjoy learning!
5. Control your internal language.

The first two things on the list are a solid start. Making small personal daily goals you enjoy chasing will only increase your drive. At the same time, remember that your long-term growth as a supercharged hacker is more important than any specific day’s results! Everyone has bad days, but having a consistent growth mindset is essential. Making a mission statement for yourself ensures that you know the “why” behind why you are hacking in the first place. Enjoying your work is something so few people seem to get now. Find a way to get yourself in a mindset where you enjoy your workflow and the continuous learning that comes with it! All of the above can be increased by ensuring that your internal dialogue with yourself is positive. You decide your mindset!

## **Step 2: Recon**

Now let’s get to hacking! The first step will be performing thorough reconnaissance on your target. Depending on the scope of your target, this could vary a bit, but I am going to split this section into two parts. The first part of our recon workflow will be finding as many in-scope assets as possible. Finding as much of the in-scope infrastructure as possible is key to the rest of the workflow. The second part will be for each specific asset we find and what types of technology are present on each asset. I will have checklists for each section so you can check things off as you go. The idea is to start at the broadest scope possible and then narrow it down. So if you have an open scope program, use the large scope checklist, take the domains from there, use the medium scope checklist, and so on.

### Infrastructure/Asset discovery

#### Large scope (open scope)

- Find ASNs belonging to target ( [amass](https://github.com/OWASP/Amass), [asnlookup](https://github.com/yassineaboukir/Asnlookup), [metabigor](https://github.com/j3ssie/metabigor), [bgp](https://bgp.he.net/))
- Review [acquisitions](https://www.crunchbase.com/)
- Check registrant relationships ( [viewdns](https://viewdns.info/reversewhois/))
- From the above info, gather seed domains for further enumeration

#### Medium scope (\*.example.com)

- Enumerate subdomains ( [amass](https://github.com/OWASP/Amass) or [subfinder](https://github.com/projectdiscovery/subfinder) with all available API keys)
- Subdomain bruteforce ( [puredns](https://github.com/d3mondev/puredns) with [wordlist](https://gist.github.com/six2dez/a307a04a222fab5a57466c51e1569acf))
- Discover subdomain permutations ( [gotator](https://github.com/Josue87/gotator) or [ripgen](https://github.com/resyncgg/ripgen) with [wordlist](https://gist.github.com/six2dez/ffc2b14d283e8f8eff6ac83e20a3c4b4))
- Find subdomains with HTTP ports ( [httpx](https://github.com/projectdiscovery/httpx))
- Subdomain takeover checks ( [nuclei-takeovers](https://github.com/projectdiscovery/nuclei-templates/tree/master/takeovers))
- Shodan queries against domain
- Recursively search subdomains
- Screenshots for visual inspection ( [gowitness](https://github.com/sensepost/gowitness), [webscreenshot](https://github.com/maaaaz/webscreenshot), [aquatone](https://github.com/michenriksen/aquatone))

#### Technology analysis (for enumerated domains)

- Identify cloud assets ( [cloudenum](https://github.com/initstring/cloud_enum))
- Identify web server, technologies, and databases in use ( [httpx](https://github.com/projectdiscovery/httpx), wappalyzer)
- Try to locate interesting files (/robots.txt , /sitemap.xml, /.git, etc)
- Search comments on web pages (Burp Engagement Tools)
- Directory/parameter fuzzing ( [ffuf](https://github.com/ffuf/ffuf) and [wordlist](https://github.com/six2dez/OneListForAll))
- Identify WAFs ( [whatwaf](https://github.com/Ekultek/WhatWaf), [wafw00f](https://github.com/EnableSecurity/wafw00f))
- Google dorking ( [GHDB](https://www.exploit-db.com/google-hacking-database))
- GitHub dorking ( [githound](https://github.com/tillson/git-hound), [gitdorks\_go](https://github.com/damit5/gitdorks%5C_go))
- Passive directory enumeration ( [waymore](https://github.com/xnl-h4ck3r/waymore), [gau](https://github.com/lc/gau))
- Spidering endpoints ( [gospider](https://github.com/jaeles-project/gospider), [xnLinkFinder](https://github.com/xnl-h4ck3r/xnLinkFinder))
- Check potentially vulnerable parameters ( [gf-patterns](https://github.com/1ndianl33t/Gf-Patterns))
- Locate sensitive endpoints (logins, admin panels)
- Get all JS files ( [subjs](https://github.com/lc/subjs), [xnLinkFinder](https://github.com/xnl-h4ck3r/xnLinkFinder))
- JS hardcoded APIs and secrets ( [nuclei-tokens](https://github.com/projectdiscovery/nuclei-templates/tree/4e3f843e15c68f816f0ef6abce5d30b6cf6d4a30/exposures/tokens), [trufflehog](https://github.com/trufflesecurity/trufflehog))
- JS analysis ( [subjs](https://github.com/lc/subjs), [JSA](https://github.com/w9w/JSA), [xnLinkFinder](https://github.com/xnl-h4ck3r/xnLinkFinder), [getjswords](https://github.com/m4ll0k/BBTz))
- Run automated scanner ( [nuclei](https://github.com/projectdiscovery/nuclei))
- Test CORS ( [CORScanner](https://github.com/chenjj/CORScanner), [corsy](https://github.com/s0md3v/Corsy))

## **Step 3: In-depth application analysis**

### User management testing

#### Registration

- Duplicate registration testing (overwriting an existing user)
- Weak password policies (tip: check if a password allows just spaces)
- Fuzz for folders created for new users
- Allowing vital profile actions (ex: changing password) without verifying email
- Test re-registering with same/different passwords
- Try to register with the target’s email
- Check OAuth with social media registration
- Check state parameter on social media registration
- Try to capture integration requests (possible account takeover)
- Check redirections on the registration page after login (tip: try repeating the register request while already logged in)
- Check for cross-site scripting (XSS) on the name or email

#### Authentication

- Username enumeration
- Account recovery function
- “Remember me” function
- SQL Injections
- Auto-complete testing
- Lack of password confirmation on change email, password, or 2FA (try change response)
- User account lockout mechanism on brute force attack
- Check for password wordlist ( [cewl](https://github.com/digininja/CeWL) and [burp-goldenNuggets](https://github.com/GainSec/GoldenNuggets-1))
- Test Oauth login functionality for Open Redirection
- Test response tampering in SAML authentication
- In OTP check guessable codes and race conditions, response manipulation for bypass, or brute force attacks
- If JWT, check common flaws
- Try logging in with easy or default credentials

#### Sessions

- Test tokens for meaning and predictability
- Insecure transmission of tokens
- Check logs for live tokens
- Session termination and fixation checks
- Test for cross-site request forgery (CSRF)
- Check the scope of important cookies
- Decode cookie if possible (ex: base64)
- Check HTTPOnly and Secure flags
- Use the same cookie from a different asset to get a session
- Check controls using multiple accounts
- Insecure access control methods (request parameters, Referer header, etc)
- Check concurrent logins
- Path traversal in cookies
- Try to perform a privileged user’s actions with an unprivileged cookie

#### Profile

- Find IDs for a user, then test to try to access or change other users
- Try CSRF against user account-specific actions
- Change username or email to an existing username or email
- File upload testing on any profile pictures
- Check profile picture URL for ids or tokens
- Try to delete an account, then recover it with the forgot password functionality
- Try parameter pollution to add two values of the same field
- Check if you can add roles manually

#### Forgot/Reset password

- Invalidate session on logout and password reset check
- Check password reset tokens for uniqueness and expiration
- If IDs or sensitive data are present in the reset link, try changing them (possible IDOR in the reset link)
- Request 2 reset passwords links and use the older
- Check for sequential tokens
- Host header injection for token leakage
- Email crafting like victim@gmail.com@target.com
- Capture reset token and use with another email/userID
- Check encryption in reset password token
- Token leak in the referer header
- Append second email param and value
- Understand how a token is generated (timestamp, username, birthdate,…)
- Response manipulation

### Input handling

- Try to discover hidden parameters ( [arjun](https://github.com/s0md3v/Arjun))
- Fuzz all request parameters
- Identify all reflected data
- Check for cross-site scripting (reflected, stored, DOM)
- HTTP header injection in GET & POST
- Remote code execution (RCE) via Referer Header
- SQL injection via User-Agent Header
- Check for any redirections
- Stored attacks (cross-site scripting, file uploads, etc.)
- Check/Fuzz for command injection
- Path traversal, LFI, and RFI checks
- Script injection
- File inclusion
- LDAP injection
- SSI Injection
- XPath injection
- XML external entity (XXE) checks (change content-type to text/xml)
- SQL injection (tip: start checks with ‘ and ‘–+-)
- NoSQL injection
- HTTP Request Smuggling
- SSRF in previously discovered open ports

### Application logic testing

- Identify possibly vulnerable logic
- Test transmission of data
- Test for reliance on client-side input validation
- Handling of incomplete input
- Transaction logic
- Change IDs related to any action
- Tamper/Reuse gift or discount codes
- Try parameter pollution to use gift code two times in the same request
- Parameter pollution on social media sharing links
- Change POST-sensitive requests to GET

## **Step 4: Take good notes**

### Organization

Why are organization and note-taking so important? Well, if you are trying to supercharge your hacking workflow but don’t remember what steps you have done or the results of those tests, then you are bound to repeat tests and forget information.  This leads to a lot of repeat testing, as well as missed findings! That doesn’t sound very supercharged! Staying organized as you complete your workflow is just as vital to your hacking as the other steps. Organizing your thoughts also makes reporting your tests and findings easier! The larger the scope for a target is, the more lost you risk becoming unless you come prepared. So always ensure make sure as you test to keep as detailed notes (and screenshots) as you can.

### What tools?

There is an astonishing amount of productivity tools out there today that include note-taking functionality. So which one do you use? Well, the answer is easy, whichever one works best for you! With so many tools out there, they all are very good and which one you use is 100% up to you. There are a few that are popular:

- [Notion](https://www.notion.so/)
- [Obsidian](https://obsidian.md/)
- [Microsoft OneNote](https://www.microsoft.com/en-us/microsoft-365/onenote/digital-note-taking-app)
- [Evernote](https://evernote.com/)
- [Apple Notes](https://apps.apple.com/us/app/notes/id1110145109)
- [Google Keep](https://www.google.com/keep/)

## **Conclusion**

The above workflow and checklists are a good start to supercharging your hacking, but as with many things, the learning and improving never ends. The goal is to take these steps and use them as a starting point. Where you take them from there is entirely up to you. Maybe you add some more tests or completely new sections, or maybe you add workflows for mobile apps. The goal of the workflow is to get started on your journey. Where you decide to further supercharge your hacking workflow is completely up to you!

* * *

#### **Written by:**  **Gunnar Andrews**

My online alias is G0lden. I am a hacker out of the midwest United States. I came into the hacking world through corporate jobs out of college, and I also do bug bounties. I enjoy finding new ways to hunt bugs and cutting-edge new tools. Making new connections with fellow hackers is the best part of this community for me!

* * *

### Related resources

Why not check out the following?

- [Hakluke’s huge list of resources for beginner hackers](https://labs.detectify.com/2021/08/24/hakluke-list-resources-for-beginner-hackers-2021/)
- [How to hack web applications in 2022: Part 1](https://labs.detectify.com/2022/05/16/how-to-hack-web-applications/)
- [How to hack web applications in 2022: Part 2](https://labs.detectify.com/2022/08/05/how-to-hack-web-applications-in-2022/)
- [Hack with ‘good faith’ – A tool to automate and scale good faith hacking](http://xn--hack%20with%20goodfaith%20-%20a%20tool%20to%20automate%20and%20scale%20good%20faith%20hacking-qw43d8c/)

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/how-to-supercharge-your-hacking-mindset-workflow-productivity-and-checklist/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/how-to-supercharge-your-hacking-mindset-workflow-productivity-and-checklist/ "Share on LinkedIn")

**Gunnar Andrews**

Ethical Hacker

## Check out more content

Why picking targets is so important Many ethical hackers struggle because they are hacking the “wrong” types of targets for them. This is especially true …

December 07, 2022

You will find a common pattern if you read blog posts or watch interviews with some of today’s top ethical hackers. When asked if coding …

November 30, 2022

Docker is an open-source platform that allows you to develop, deploy, and manage multiple applications across one operating system

November 21, 2022

TL/DR: In this world of rapid digitization, companies are moving from traditional on-premise deployments to cloud service providers for handling their infrastructure. In this article, …

July 25, 2022