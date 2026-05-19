---
source: detectify
source_url: https://labs.detectify.com/writeups/ai-agents-building-security-tests/
title: "AI agents building security tests - architecture and prompts - Labs Detectify"
author: "Detectify Labs"
published: 2025-09-25T14:10:59+00:00
description: "The Detectify AI Agent Alfred fully automates the creation of security tests for new vulnerabilities, from research to a merge request. In its first six ..."
---

[Home](https://labs.detectify.com/)/ [Writeups](https://labs.detectify.com/category/writeups/)/ [AI agents building security tests – architecture and prompts](https://labs.detectify.com/writeups/ai-agents-building-security-tests/)

[Writeups](https://labs.detectify.com/category/writeups/ "Writeups")

# AI agents building security tests – architecture and prompts

![](https://labsadmin.detectify.com/app/uploads/2023/08/logo-graphic-labs.svg)

**Detectify Labs** Sep 25, 2025

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/writeups/ai-agents-building-security-tests/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/writeups/ai-agents-building-security-tests/ "Share on LinkedIn")

![AI agents building security tests – architecture and prompts](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2025%2F09%2FAlfred.png&w=3840&q=75)

**The [Detectify](https://detectify.com/) AI Agent Alfred fully automates the creation of security tests for new vulnerabilities, from research to a merge request. In its first six months, it generated 450 validated tests, focusing on the most critical threats with an average CVSS score of 8.5. This process is highly efficient, with 70% of the tests needing no manual adjustments, allowing our [human security researchers](https://detectify.com/crowdsource/what-is-crowdsource) to concentrate on more complex, high-impact issues. How did we build this? Which prompts did we use? What did we learn?**

There’s a lot of hype surrounding “AI hacking”. The headlines are full of FUD (Fear, Uncertainty, and Doubt) about autonomous agents breaking into systems. But what’s the reality? Is it truly about LLMs doing the hacking, or is there a more strategic, powerful use for them?

At the same time, the volume of new vulnerabilities is exploding, with over 40,000 new CVEs published in 2024 and an even faster pace in 2025, reaching over 21,500 by June. This continuous surge amounts to an average of 133 new vulnerabilities every day.

Now, imagine using AI agents for a more scalable purpose: automating the weaponization of security vulnerabilities.

To turn this into a reality, we decided to focus on building a system with two core principles:

1. **Source everything out there.**
2. **Automate what matters.**

Our AI Security Researcher [Alfred](https://blog.detectify.com/product-updates/introducing-alfred-for-ai-built-vulnerability-assessments/) is a workflow based on a 10-step process, implemented in Go as a chain of agents implemented in OpenAI-mini mode. Alfred takes a vulnerability from a simple data point to a fully functional merge request for a security test. Let’s see how:

### **Step 1: The Funnel of Sourcing**

Alfred continuously sources vulnerabilities from over 200 sources, including CERTs (like CERT-EU and CERT-SE), public vendor advisories (like Acunetix and Rapid7), and news sites and communities (like Reddit and HackerNews). This creates a broad pool of potential threats, providing a much wider range of vulnerabilities compared to relying solely on the NVD, which has a [significant backlog and is not as up-to-date](https://nvd.nist.gov/general/news/nvd-program-transition-announcement).

![](https://labsadmin.detectify.com/app/uploads/2025/09/Source-vulnerabilites-1024x249.png)

### **Step 2: Getting All the References**

Once a vulnerability is identified, Alfred gets all supporting references. This includes scouring GitHub commits, vendor advisories, and even social media mentions to collect every piece of technical information available.

![](https://labsadmin.detectify.com/app/uploads/2025/09/Source-and-support-1024x635.png)

### **Step 3: Prioritizing with EPSS**

We don’t process everything at once. To ensure we’re focusing on the most critical threats, Alfred sorts all vulnerabilities by their Exploit Prediction Scoring System (EPSS) score. EPSS is a data-driven framework that provides a daily estimate of the probability of a vulnerability being exploited in the next 30 days. This allows us to prioritize what matters most—vulnerabilities that are likely to be weaponized in the wild.

### **Step 4: Grouping and Structuring Data**

Alfred fetches all content from all URLs and has an LLM group the content into categories. The LLM uses critical rules to categorize content as a “poc” if executable exploit code is present, or other descriptive categories like “advisory,” “remediation,” or “analysis”.

```
Categorize this security content related to %s using your best judgment.

CRITICAL RULES:

- You MUST use "poc" if and ONLY if executable exploit code is present with sufficient detail to reproduce the exploit

- For all other content, choose a descriptive category that best represents the content (e.g., "advisory", "remediation", "analysis", "detection", "discussion", etc.)

- Choose a single category that most accurately describes the primary nature of the content

- Be specific and descriptive with your chosen category

- Create a concise title (5-10 words) that accurately summarizes the document's content and its type (e.g., "WordPress RCE Exploit Code" or "Apache Advisory for CVE-2024-1234")

IMPORTANT: "poc" has a strict definition - it MUST contain actual code or commands that could be executed to exploit the vulnerability.

Your response must be a single JSON object with two properties:

{"category": "category_name", "title": "Your concise document title"}`
```

### **Step 5: Note-taking**

An LLM will learn the exploit and take notes on how it works. Alfred’s task is to analyze content and extract all technical information necessary to understand and potentially reproduce the vulnerability. The analysis is based strictly on the provided content, without adding information from its own knowledge or assumptions. These notes are a precise, exhaustive documentation of the attack vector, prerequisites, and every technical detail needed for reproduction.

```
Your task is to analyze this content related to vulnerability and extract ALL technical information necessary to understand and potentially reproduce the vulnerability.

IMPORTANT: Base your analysis STRICTLY on the content provided. Do not add information from your own knowledge or assumptions.

Document EXHAUSTIVELY:

- The complete attack vector and exploitation methodology

- ALL technical details about how the vulnerability works

- EVERY prerequisite and environmental requirement

- ALL steps in the exploitation process

- EXACT specifications of any unusual formatting or techniques

- FULL details on target behavior during and after exploitation

- (Prompt cut to fit text)

For ANY code, commands, or HTTP requests:

- Include them COMPLETELY and EXACTLY as presented

- Preserve ALL syntax, formatting, and structure

- Document ALL parameters, flags, and options

- Note ALL external dependencies or tools required

REMEMBER: These notes will become your ONLY reference for future analysis of this vulnerability. You will never see this content again, so be exhaustive, precise, and avoid omitting ANY technical details.`
```

### **Step 6: Triaging for Feasibility**

Alfred acts as a security analyst to triage how feasible a vulnerability is for implementation. It evaluates the previously documented notes and answers a series of true/false questions based only on the technical details provided. Questions include whether the vulnerability is exploitable, relies on HTTP/HTTPS, requires authentication, or is intrusive.

Yourobjectiveistoevaluateandtriagenotesofasecurityvulnerabilitythatyoupreviouslyhavebeendocumenting.Baseyouranalysisstrictlyonthetechnicaldetailsprovidedinthevulnerabilitydescription,withoutmakingassumptionsabouttypicalexploitationpatterns.

```
IMPORTANT: Your task is to carefully analyze the provided vulnerability information and answer each question with true or false. Accuracy is critical as your responses will be used in an automated system.

Your goal is answer the following questions (pay attention to the quoted prefix to the questions):

"exploitable": Set to false if the provided technical information…

"http": Is this vulnerability carried out over HTTP/HTTPS protocols (including HTTP/2, HTTP/3)

"authenticated": Does this vulnerability require any form of authentication

"multistep": Does this vulnerability require requests to be executed sequentially with dependencies

"time_based": Does the vulnerability detection rely on specific timing intervals, including time-based blind injections

"pingback": Does exploitation require the vulnerable system to initiate a connection back to attacker-controlled infrastructure (including HTTP, DNS, SMTP, LDAP, or internal network callbacks)?

"fingerprint": Does the implementation rely on passive reconnaissance

"manual_configuration": Does successful exploitation require prior knowledge of specific values

"intrusive": Does this vulnerability test include payloads that could cause permanent damage or disruption to the target system? Examples include:

Deleting files or data (rm, DROP TABLE) without recovery

Modifying critical system files or configurations that could prevent normal operation

(Prompt cut to fit text)
```

### **Step 7: Select good candidates for implementation**

Alfred selects good candidates for implementation based on a ranking system. The system adds bias for vulnerabilities with proof-of-concepts, newer CVEs, higher EPSS and CVSS scores, and more relevant sources to prioritize the most relevant vulnerabilities.

```
Preliminary filtering, only act on unauthenticated and network-based (Internet-facing) vulnerabilities.

This preliminaryFiltering-repository instance is presorted on EPSS in descending order.

Rank all vulnerabilities based on the rules below, higher scores means that vulnerabilities are more relevant and will be acted upon first.

// Add bias for vulnerabilities with proof-of-concepts

// Add bias and prioritize newer CVEs

// Add the source count

// Add bias for EPSS percentile

// Add bias for CVSSv3 scores

// Add bias for CVSSv2 scores

// Add bias towards more relevant sources

// Add bias for recent sources, so that recent mentions in news-sites, CERTs, etc. are prioritized

// Add slight bias on "source mentions" seen during the past three months
```

### **Step 8: Develop the Test Module**

The next step is development, which happens through rapid iterations until “it works”. Alfred’s goal is to port its technical notes into a standardized JSON specification for a Detectify test module. A computer will parse this output, so exact adherence to the schema is critical. A key requirement is to always use concrete, executable payloads—never placeholders. For command injection, for example, Alfred must use actual commands that work across both Windows and Unix/Linux systems.

![](https://labsadmin.detectify.com/app/uploads/2025/09/Develop-1024x410.png)

```

Your goal is to port security vulnerability notes to a standardized Unicorn Module JSON specification. This specification describes the format for HTTP requests and assertions to test for specific vulnerabilities."

INPUT: You will receive unstructured notes about a security vulnerability.
OUTPUT: A computer will parse your response, so exact adherence to the schema is critical."

REQUIRED INFORMATION: At minimum, your output must include:

- Valid type and version fields
- Appropriate labels including the CVE identifier (if available)
- At least one request and response signature
- Properly formatted finding metadata

PAYLOAD IMPLEMENTATION REQUIREMENTS:

- Always use concrete, executable payloads - NEVER use template variables like {{command}} or similar placeholders
- For command injection vulnerabilities, include actual commands not a placeholder
- DO NOT include a 'Host' header in your request modifiers - the system automatically handles this

(Prompt cut to fit text)

CROSS-OS COMPATIBILITY REQUIREMENTS:

- When crafting command injection payloads, use commands or techniques that work across both Windows and Unix/Linux systems
(Prompt cut to fit text)

Here are common errors to avoid:

* When using request modifiers, the HTTP method is specified as a string, not as JSON array
* When providing the CVSS, the type attribute must be \"cvss\" in lowercase
(Prompt cut to fit text)

(70+ rows with prompts and instructions)
```

### **Step 9: Creating the Merge Request**

Once the module is ready, Alfred opens a merge request in GitLab. This allows our internal team of security researchers to review the generated test and ensure it meets our high-quality standards.

![](https://labsadmin.detectify.com/app/uploads/2025/09/10-1024x803.png)

### **Step 10: Getting it Production Ready**

The final step is to fix smaller issues and prepare the test for production, such as fixing reference title formatting and extending regex assertions.

### **Wow, it actually works**

So, what was the outcome of the first six operational months? The results speak for themselves:

- Alfred created approximately 450 validated test modules during a test period of just a few months.
- The vulnerabilities it focused on were highly critical, with an average CVSS score of 8.5 and a median of 9.8.
- An impressive 70% of the generated tests needed “very limited manual adjustment” and were considered fully automated and weaponized.
- The entire process is extremely cost-effective, with LLM costs running at just a few hundred dollars per month.

### **What does this mean for security researchers?**

Alfred exemplifies how AI agents can be powerful tools for security defenders: it significantly accelerates security research by automating the tedious tasks of sourcing, triaging, and test development. This innovation allows our internal security researchers and Crowdsource community of ethical hackers more time to concentrate on what they do best: discovering complex, high-impact vulnerabilities that demand a creative human touch.

For [Detectify](http://detectify.com/) customers, this means they get access to vulnerability assessments for relevant CVEs faster than ever before. For us, Alfred is a big help in making the internet a more secure place, one automated test at a time.

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/writeups/ai-agents-building-security-tests/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/writeups/ai-agents-building-security-tests/ "Share on LinkedIn")

![](https://labsadmin.detectify.com/app/uploads/2023/08/logo-graphic-labs.svg)

**Detectify Labs**

## Check out more content

Combining response-type switching, invalid state and redirect-uri quirks using OAuth, with third-party javascript-inclusions has multiple vulnerable scenarios where authorization codes or tokens could leak to …

July 06, 2022

CloudKit, the data storage framework by Apple, has various access controls. These access controls could be misconfigured, even by Apple themselves, which affected Apple’s own apps using CloudKit. This blog post explains in detail three bugs found in iCrowd+, Apple News and Apple Shortcuts with different criticality uncovered by Frans Rosen while hacking Cloudkit. All bugs were reported to and fixed by the Apple Security Bounty program.

September 13, 2021

Security researchers in the Detectify Crowdsource community, Ai Ho (@j3ssiejjj) and Bao Bui (@Jok3rDb), found an undocumented security issue in Adobe Experience Manager (AEM) that bypassed authentication, and left the application open to information disclosure attacks

June 28, 2021

Here’s how I (@Almroot) bought the domain name used in the NS delegations for the ccTLD of the Democratic Republic of Congo (.cd) and temporarily took over 50% of all DNS traffic for the TLD

January 15, 2021