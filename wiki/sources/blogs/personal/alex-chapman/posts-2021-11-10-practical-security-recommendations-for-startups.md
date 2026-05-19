---
source: alex-chapman
source_url: https://blog.ajxchapman.com/posts/2021/11/10/practical-security-recommendations-for-startups.html
title: "Practical Security Recommendations for Start-ups with Limited Budgets | Alex Chapman’s Blog"
published: 2021-11-10T00:00:00-06:00
description: "Hi, my name is Alex, I’ve been an IT security professional since 2007 and I’ve recently entered the start-up world with my project bughuntr.io. In putting together this project, security has been a primary concern for me. This is both due to my background and the nature of the project, being a training platform for security professionals and enthusiasts alike. In my security career, I’ve been hire"
---

Hi, my name is [Alex](https://twitter.com/ajxchapman), I’ve been an IT security professional since 2007 and I’ve recently entered the start-up world with my project [bughuntr.io](https://bughuntr.io). In putting together this project, security has been a primary concern for me. This is both due to my background and the nature of the project, being a training platform for security professionals and enthusiasts alike. In my security career, I’ve been hired to assess countless web applications, cloud environments and computer networks for security vulnerabilities. In these assessments, it is always clear when security is ‘bolted on’ as a compliance requirement before releasing a product, or added at a later date in response to an incident. Start-ups have a rare opportunity to ‘bake’ security in at the start of a project, but this is often seen as an expensive endeavor. In this post, I aim to ease that fear and provide practical (and cheap) advice for start-ups who want to release a more secure product right from the start.

I should say at this point that no product is ever ‘secure’, security is not a state, but a process. However, there are several (relatively) simple steps a start-up can take to significantly decrease the likelihood of being hacked and reduce the impact should it happen. With that caveat out of the way, here are my top ten Practical Security Recommendations for start-ups of Cloud and SaaS based products:

## Use a Password Manager and Two-Factor Authentication

**Technical Ability**: *Low* **Impact**: *High*

Starting a new project means signing up for all kinds of online services, creating new email addresses, free tier accounts of SaaS products, server credentials, etc., etc., etc. It’s all too tempting to use the same password across these services for ease, however this can lead to simple compromise of those accounts, and any others which share the same password. Hackers will often use compromised passwords from one service to attempt to authenticate to other services. If you share the same password across multiple services then you are at risk. Additionally, if you are able to memorize the password, that will generally mean that it is not of sufficient complexity to be considered ‘secure’. Which password do you think would be easier for a hacker to guess, ‘Start-up Fall2021’ or ‘^zf%Mm3Gxs5BZF!NRhNE5v@oUh6@VBHn’? A password manager can help you maintain secure, unique passwords across all the online services you apply for.

Additionally, where Two-Factor Authentication (2FA) is available, it should be enabled. 2FA requires a second authentication token on top of the correct password. This could be a hardware security key (most secure), a Time based One Time Password (moderately secure) or a One Time Password sent to a mobile device (least secure). Not all services support 2FA, but where it is supported it should be enabled.

If you are about to stop reading here, or only take one thing from this blog post, *please* just go and sign-up for a password manager. It is not a security silver bullet, but it’s one of the closest things we have at this point.

Password Managers with a ‘free’ tier, or ‘free’ offering:

As a bonus, you can keep an eye on if any of your accounts appear in 3rd party data breaches via the free [Have I Been Pwned](https://haveibeenpwned.com/) service.

## Develop with Modern Frameworks

**Technical Ability**: *Medium* **Impact**: *Medium*

Start-ups are in a unique position, when compared with existing companies with established products, in that they can choose the current best-in-class software frameworks to develop upon. Modern software frameworks can significantly reduce the likelihood of introducing vulnerabilities such as [Cross Site Scripting](https://owasp.org/www-community/attacks/xss/) and [SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection). In fact, some modern frameworks do absolute everything in their power to prevent the accidental introduction of these vulnerabilities, to the point of naming functions that *could* introduce them with [‘dangerous’](https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml) in the name.

When starting development on a new product, care should be taken to choose frameworks which have good security abstractions and a history of good security practices.

## Configure an Edge Security Service

**Technical Ability**: *Low / Medium* **Impact**: *Medium*

Edge security services have multiple benefits, including helping to protect your service from bots, hackers and [Distributed Denial of Service](https://www.cloudflare.com/en-gb/learning/ddos/what-is-a-ddos-attack/) attacks. When configured correctly, all traffic for your service will route via the edge service, providing the best protection. Many edge security services also have the benefit of acting as a Content Delivery Network (CDN), meaning they can reduce the load on your backend service infrastructure.

If your service has administration, reporting or diagnostics functionality that needs to be accessed by a limited number of support staff, edge security services can restrict access to those areas to pre-approved IP addresses or users whose browsers supply a particular token. These additional access restrictions can help to mitigate software vulnerabilities which may be discovered in the frameworks that you use to build and host your service, and to mitigate password guessing attacks against administrative login pages.

Security Focused CDN services with a ‘free’ tier:

## Enable HTTP Security Headers

**Technical Ability**: *Low / Medium* **Impact**: *Medium*

Modern web browsers include numerous client side security features which are only enabled if a server indicates that it supports their use. These features are enabled by the server sending specific HTTP headers, and can (non-exhaustively) prevent a user from loading your service over an unencrypted connection, prevent the user’s browser from leaking data from your service to 3rd party websites, or prevent your service from being framed by any other website. Configuring these headers can significantly increase the client side security of your service.

One security header that deserves a special shout-out is the Content Security Policy (CSP) header. A CSP defines what sources content, such as scripts, videos and images, can be loaded and executed from on a website. A robust CSP, whilst somewhat complex to configure, can completely mitigate the risk of client side attacks such as [Cross Site Scripting (XSS)](https://owasp.org/www-community/attacks/xss/).

Free guides and tools which can help you configure HTTP Security Headers:

Free tools which can help build and evaluate a robust CSP:

## Apply Security Patches

**Technical Ability**: *Medium* **Impact**: *High*

When self hosting an application, such as on [Digital Ocean (affiliate link!)](https://m.do.co/c/aff35eb4c833), you need to ensure that operating system and library security patches are applied as they are released. This unfortunately is an on-going process, as security vulnerabilities in operating systems and libraries are constantly being found and fixed. Using [DevOps](https://aws.amazon.com/devops/what-is-devops/) practices and ephemeral infrastructure can help ensure that your service is always deployed to a fully patched system on each release.

As an alternative to self hosting, there are free (and paid) Serverless and Platform as a Service (PaaS) offerings that run your application in a container, which take care of patching of the operating system for you. However, you still need to ensure that the libraries used by your service are kept up to date with security patches.

Serverless / PaaS services with a ‘free’ tier:

## Backup User Data and Source Code

**Technical Ability**: *Medium* **Impact**: *Medium*

With the ever increasing threat of [Ransomware](https://www.malwarebytes.com/ransomware), having verified(!) backups of both user data and source code can save a huge amount of time and money in the event of a ransomware attack or other unforeseen outage. When storing backups of user data, make sure they are encrypted with a securely stored key to prevent disclosure in the event of a malicious hacker obtaining access to the backup files. Source code is often kept in source code repositories, which on top of helping to facilitate development between multiple remote developers, provide a full history of your service source code. When kept in an online source code repository, this can provide sufficient backup for your code.

One important factor of taking backups, which may seem obvious, is that they have to be able to be restored. However, you can only know this for certain by testing your backup and restore processes periodically. A backup that cannot be restored is about as useless as no backup at all.

Source code repositories with a ‘free’ tier:

## Centralize All Logging

**Technical Ability**: *Low* **Impact**: *Medium*

In the event of a successful attack (or any other sort of critical outage), having access to application and system logs can be the difference between being able to quickly remediate the situation, and blindly trying to piece together what happened, in the dark, wearing sunglasses, with a paper bag over your head. Unfortunately, logs stored on a compromised system can no longer be trusted. Using a centralised logging service, on top of aggregating logs from multiple sources, can help provide a ‘trusted’ source of log activity up to the point of a successful attack.

Centralised logging services with a ‘free’ tier:

## Recruit the Good Hackers

**Technical Ability**: *Low* **Impact**: *High*

All software has vulnerabilities which could potentially be exploited by malicious hackers, you only have to look at the monthly patch notes from Microsoft or Apple to see that even the big players can’t get this right all the time. What’s worse than having vulnerabilities in your start-up’s product? Not knowing that you have vulnerabilities in your start-up’s product! Through implementation of a Vulnerability Disclosure Policy (VDP), you can provide a communication channel for good hackers to contact you if they discover a security vulnerability which affects your product.

When money is more available, penetration testing of your product can be considered. That is, hiring professional security professionals to actively search out vulnerabilities in your product. On top of this, a [Bug Bounty](https://www.hackerone.com/vulnerability-management/what-are-bug-bounties-how-do-they-work-examples) program could be started to incentivise good hackers to look for and report vulnerabilities which affect your product. The merits of each are beyond the scope of this post, but it should be noted that these are not cheap options.

Free tools and guides which can help define and implement a VDP:

## Service Containerization

**Technical Ability**: *High* **Impact**: *High*

Containerization is the act of running software within a restrictive execution environment. Whilst the technical ability required to implement containerization securely is quite high, when implemented it can mitigate the risk of entire classes of attacks and vulnerabilities, such as [Command Injection](https://owasp.org/www-community/attacks/Command_Injection), and severely frustrate post-exploitation attacks such as [Privilege Escalation](https://www.beyondtrust.com/blog/entry/privilege-escalation-attack-defense-explained) or persistence.

## Deploy Canary Tokens

**Technical Ability**: *Low* **Impact**: *High*

Once all of the above are implemented, your start-up is still not immune to attack (unfortunately). Whilst you have done everything reasonable (and more!) to secure yourself, Social Engineering, 0days, supply chain attacks, etc. could still be exploited to compromise your service. If an attack is successful against your start-up, you want to know about it fast! Attackers like to try and keep their presence hidden for as long as possible, they don’t often want to advertise the fact that they are there. Canary tokens can help you discover these malicious hackers by creating tempting looking targets (documents, configuration files, services), which create alerts when they are accessed. These can be used as a reliable indication that an attack is occuring and that you should start an investigation.

Free tools to generate basic canary tokens:

# Conclusion

Any start-up which can apply all ten of these recommendations will be head-and-shoulders above the crowd in terms of security, even only applying a handful will significantly decrease the likelihood of a successful hack and reduce the impact should one happen. Security as a process may seem costly to an early stage start-up in both time and money up-front, however it is significantly cheaper to start to include security processes right from the start, and magnitudes cheaper to have them in place than have to recover from an attack.

# Post-Script

I am available for freelance consulting if you would like help implementing any of these strategies, would like to discuss the security of your start-up or would like to include me as a speaker at one of your events. Please feel free to [contact me](/cdn-cgi/l/email-protection#f392998b909c9d80869f87929d908ab3949e929a9fdd909c9e) to discuss requirements, availability and rates.