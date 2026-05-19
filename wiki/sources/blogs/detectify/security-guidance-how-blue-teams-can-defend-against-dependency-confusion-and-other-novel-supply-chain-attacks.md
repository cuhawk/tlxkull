---
source: detectify
source_url: https://labs.detectify.com/security-guidance/how-blue-teams-can-defend-against-dependency-confusion-and-other-novel-supply-chain-attacks/
title: "How blue teams can defend against Dependency Confusion and other novel supply chain attacks - Labs Detectify"
author: "Detectify"
published: 2021-09-02T12:43:56+00:00
description: "Supply chain attacks keep evolving, and one of the most interesting methods to emerge lately is Dependency Confusion. Detectify Crowdsource hacker Aleksandr Krasnov shares how ..."
---

[Home](https://labs.detectify.com/)/ [Security guidance](https://labs.detectify.com/category/security-guidance/)/ [How blue teams can defend against Dependency Confusion and other novel supply chain attacks](https://labs.detectify.com/security-guidance/how-blue-teams-can-defend-against-dependency-confusion-and-other-novel-supply-chain-attacks/)

[Security guidance](https://labs.detectify.com/category/security-guidance/ "Security guidance")

# How blue teams can defend against Dependency Confusion and other novel supply chain attacks

**Aleksandr Krasnov** Sep 02, 2021

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/how-blue-teams-can-defend-against-dependency-confusion-and-other-novel-supply-chain-attacks/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/how-blue-teams-can-defend-against-dependency-confusion-and-other-novel-supply-chain-attacks/ "Share on LinkedIn")

**Supply chain attacks keep evolving, and one of the most interesting methods to emerge lately is Dependency Confusion. Detectify [Crowdsource](https://detectify.com/crowdsource/what-is-crowdsource) hacker Aleksandr Krasnov shares how security engineers can defend against it.**

Supply chain attacks come in many shapes and sizes but one of the most interesting is arguably Dependency Confusion. This article covers fundamental practical steps that you as a security engineer (whether you’re in appsec, infrasec, offsec, netsec, or anything else) may take in order to minimize the vector of an attack, as well as tips on how to get buy-in from senior management to get the security budget you need.

## **What is Dependency Confusion?**

Dependency confusion attacks trick users into installing a malicious dependency or library instead of the one they intended to install. It is not an entirely new attack method in itself, but it has gotten [a lot of attention](https://arstechnica.com/gadgets/2021/03/more-top-tier-companies-targeted-by-new-type-of-potentially-serious-attack/) this year following security researcher [Alex Birsan’s research writeup](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610) where he presented a proof-of-concept. Alex was able to get companies such as Apple, Microsoft and Tesla to automatically download and install counterfeit code by giving the submissions the same package names as dependencies used by these companies.

## **How does it work?**

Dependency confusion occurs when an attacker creates a malicious dependency that either sounds awfully familiar to the one you are using day-to-day, or one that has a name of your private dependency. By default, you may be importing a malicious dependency by accident (e.g. typo in your terminal) or unintentionally (e.g. server pulls the public available library before checking in your private ones).

After the installation of that dependency, the “fun” begins. Malicious dependency could be as tiny as changing a few DOM elements in your web asset to something as big as a ransomware.

That should raise some hair, and you might be thinking in blue team terms on how to defend from it.

## **Here’s a checklist of how to assess if you are prone to this type of attack:**

**Get an inventory of all projects**

This is a crucial step in understanding what packages are being run where. Ideally, you have a dedicated vulnerability management team that got your back with regards to this step. If not, there is some “fun” work that is ahead of you.

When talking about the inventory you would want to ensure you have relevant stakeholders in place. In other words, know your developers and know your DevOps folks. Ideally, have a dedicated technical lead per each project that is aware how libraries are used, imported, and executed.

**Assess your SDLC process and the role of dependencies in it**

This is a step that requires the most of your attention since the earlier in SDLC you can identify a library, the less exposure it can get.

**Know your registries**

This is more on a mitigation side but something that needs to be tackled. This point requires going a bit deeper into it, with two potential scenarios.

## _Scenarios:_

_**Scenario 1: You are NOT using a private registry**_

In this scenario you have your projects sitting somewhere and all you rely on is manifest file. Your CI tool imports those dependencies from the manifest file and you are good to go.

In this scenario you may want to look into how to harden libraries used. Firstly, ensure that manifest files are calling out the specific version of each library. Secondly, consider using a registry that will store your libraries there and have a manifest file solemnly for a reason of a reverse proxy. This way, you can concentrate on the hygiene of your libraries directly in the registry/artifactory of your choice.

**_Scenario 2: You are using a private registry_**

In this scenario you have some custom libraries as well as public ones, but you store your private libraries in the registry.

Consider using manifest file as a reverse proxy for your dependencies and shift/move all your dependencies in the artifactory for the hygiene purposes.

Those two scenarios are considerably good steps forward but that is not enough. Let us figure out what to do next.

## **Mitigation: The Five Guardrails of your Dependencies**

Guardrails are things that do not necessarily block engineers from work but rather guide them in a more secure way of working. Engineers are your friends, so let us try to be good servants for the work they do by ensuring they do it successfully with full confidence in their code from a security standpoint, by following these mitigation steps:

**Guardrail 1: Naming conventions**

Ensure that you have a policy in your organization around naming conventions, declaring or registering a namespace, who and how to contribute to a registry. All of that is essential to ensure there is an alignment in the right naming convention to reduce chances of unintentional downloads.

**Guardrail 2: Block proxying some packages**

Ensure that there is a block in proxying public packages that have the same name as your private ones. For instance, `your_company_private` is your private package but that means that a random person on the Internet won’t create the very same package that is publicly accessible. If that is the case, ensure that you do not proxy the public package that has the same name as your private ones – it’s also called _package collision_.

**Guardrail 3: Internal package manager is your friend**

Ensure that not a single library can be pulled directly via `pip/npm/etc install something` but rather use the internal package manager that is pulling packages directly from your private registry or artifactory. Account for the failure by ensuring there is a control around somebody trying to pull a public library – either blocking the download or isolating the environment on which a library could be used.

**Guardrail 4: Restrict access to your registry**

Ensure only the right thing or a person can access your registry. That includes not only monitoring and RBAC around the registry as far as developers, but also ensuring that deployed hosts will not be pulling libraries but only do that at build time. That is highly essential and a proper monitoring in place is quite essential here.

**Guardrail 5: Clean up**

This is an obvious step but sometimes forgotten. Clean all old dependencies, remove dependencies that do not follow your naming conventions, and ensure your developers are aware of the changes.

## **Now what?**

Alright, you have come up with the plan, outlined necessary steps. Now it comes down to the most annoying part – to ensure your management is onboard with you doing all of that work.

Supply Chain attacks speak in numbers and therefore justification for your budget should also be in numbers. The best solution that you could do would be to perform a quick internal red team exercise of compiling an easy dependency that just sends a ping request to your laptop and infects your codebase. Assess how much perimeter you have covered and provide a numerical figure of how the attack could propagate.

The next step is to provide some information around how ransomware could work in this way – assess common APT actors and their estimated damage to a company. This way you could speak in a hypothetical scenario of a compromise, how much it could propagate, and how much damage could be done – all numerical figures that would speak to the management.

## **Getting management buy-in**

The next thing is to come up with a long-term strategy on solving this problem including how you plan to perfect and re-evaluate it every so often. Attacks are evolving so your best bet is to minimize the perimeter.

Last thing before meeting with the management is to identify vendors or tools that you plan to use.

With all of this in mind, you should be good to clearly present the magic trio of: **The What** (your small red team exercise), **The Why** (justification via numbers and potentially use MITRE to describe), and **The How** (list of tools, architecture, and budget ask) to your management to get the security budget for your needs.

Good luck and happy threat intel! 🙂

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/how-blue-teams-can-defend-against-dependency-confusion-and-other-novel-supply-chain-attacks/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/how-blue-teams-can-defend-against-dependency-confusion-and-other-novel-supply-chain-attacks/ "Share on LinkedIn")

**Aleksandr Krasnov**

Security Researcher and Detectify Crowdsource hacker

## Check out more content

The smaller our attack surface, the fewer things we need to worry about. An excellent way of reducing the attack surface (and our cognitive load) is using AWS Service Control Policies (SCPs.) In this post, I’ll describe how we approached it.

March 26, 2024

It’s no secret that cloud architectures have several characteristics that make SSRF attacks challenging to defend against. While SSRFs are not a new threat vector, …

September 23, 2022

TL/DR: AWS QuickSight makes it easy to build visualizations, perform ad-hoc analysis, and quickly get business insights from their data, anytime, on any device. Hacker …

May 30, 2022

TL/DR: On December 2, open-source analytics solution Grafana released an emergency security patch for critical zero-day Path Traversal vulnerability CVE-2021-43798, after proof-of-concept code to exploit …

December 15, 2021