---
source: msrc
source_url: https://www.microsoft.com/en-us/msrc/blog/2026/02/fixing-the-script-journey-to-reduce-xss-exposure
title: "Fixing the script: Journey to reduce XSS exposure"
---

This is the Trace Id: d4e2939b157d3427e5e9a6036615221d




[Skip to main content](https://www.microsoft.com/en-us/msrc/blog/2026/02/fixing-the-script-journey-to-reduce-xss-exposure#mainContent)

# Fixing the script: Journey to reduce XSS exposure

[MSRC](https://www.microsoft.com/en-us/msrc/blog/category?cat=MSRC "MSRC")

/
By Sonal Shrivastava, Kul Subedi, Carlston Mills/
February 12, 2026


Cross‑site scripting (XSS) remains one of the most frequently reported web vulnerabilities—not because developers are unaware of it, but because many deployed mitigations address symptoms rather than root causes. Across vulnerability reports and incident response investigations, both within Microsoft and across the broader ecosystem, a recurring pattern emerges applications often implement escaping, filtering, or other partial controls, yet attacks still achieve script execution.

At its core, XSS mitigation succeeds only when untrusted data is consistently treated as data—not code—at every step of the rendering pipeline and never becomes executable.

This blog is the third in a series focused on reducing XSS exposure. In earlier blog posts ( [Why XSS still matters: MSRC's perspective on a 25-year-old threat](https://www.microsoft.com/en-us/msrc/blog/2025/09/why-xss-still-matters-msrcs-perspective-on-a-25-year-old-threat) & [Weaponizing cross site scripting: When one bug isn’t enough](https://www.microsoft.com/en-us/msrc/blog/2025/11/weaponizing-cross-site-scripting-when-one-bug-isnt-enough)), we discussed why XSS continues to surface despite widespread awareness, and how execution contexts, not payload creativity, determine exploitability. Here, we bring those ideas together in a practical summary of what has proven effective in real applications, and why many common fixes failed.

We're not just observing XSS patterns, we’re sharing what we’ve learned through applying, testing, and refining these defenses at sale. This post is intended as a practical reference for customers and partners who are navigating these same challenges we are: understanding where execution occurs, identifying which mitigations materially reduce risk, and moving beyond one-off fixes toward sustainable defense.

![The diagram shows how unsafe rendering leads to XSS execution ](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/chart1?scl=1)

## Why common fixes fail?

Many XSS fixes appear reasonable at first glance but fail under real‑world conditions. The issue is usually not a lack of effort, but a mismatch between the mitigation and where execution actually happens.

Let’s see a few assumptions which still renders as failed mitigation against XSS:

## 1\. “We sanitized the input”

Input sanitization attempts to remove “bad characters” early in data processing. This approach is fragile because:

- Data may be reused in different contexts later


- Stored and DOM‑based XSS bypass initial filtering entirely


- Attackers only need one unhandled execution path


- Sanitization without contextual awareness is rarely a complete defense


## 2\. “We escaped the output”

Escaping can be effective, but only when it precisely matches the execution context in which the data is interpreted.

Common failure modes include:

- HTML encoding does not protect JavaScript execution


- Attribute encoding does not protect URL or script contexts


- Escaping once does not account for later reinterpretation


- Incorrect or misplaced encoding often creates a false sense of security


## 3\. “We have Content Security Policy”

Content Security Policy (CSP) is valuable but is often misunderstood as a root-cause fix.

In practice:

- CSP can reduce exploit reliability


- CSP does not fix logic‑level DOM injection


- Misconfigurations (for example, unsafe-inline, broad script sources) are common


- CSP should be treated as a mitigation layer, not a replacement for secure rendering.


## XSS mitigations that work in practice

Effective XSS defense is about controlling execution, not filtering strings.

The approaches below consistently reduce exploitability when implemented correctly.

## 1\. Context‑aware server-side output encoding

The most reliable baseline defense is encoding data at the point where it enters the execution context.

Relevant execution contexts include:

- HTML parsing


- JavaScript execution


- Attribute interpretation


- URL handling


- Client‑side DOM manipulationKey principles that consistently hold


- Encode for the specific context (HTML, attribute, JS, URL, CSS)


- Apply encoding as close to the sink as possible


- Avoid reusing encoded data across contexts


- Modern frameworks help by default—but bypassing auto‑escaping or mixing contexts often re‑introduces risk


Mitigations succeed or fail based on whether they prevent attacker‑controlled data from becoming executable in its final context.

## 2\. Avoid dangerous sinks by design.

Some XSS risk can’t be reliably mitigated with escaping alone. Eliminating unsafe patterns reduces the possibility of execution altogether.

High‑risk examples include:

- innerHTML


- document.write


- dynamic script construction


- string‑based DOM manipulation


Reducing attack surface is a long‑term, architectural mitigation

## 3\. DOM XSS‑specific defenses

DOM-based XSS differs from classic injection vulnerabilities:

- Exploitation depends on client‑side logic
  - String escaping is often insufficient
  - Data flow, not parsing syntax, is the core issue

- Effective strategies focus on behavior, not payloads:
  - Using safe DOM APIs instead of string concatenation
  - Treating all client‑side data sources as untrusted
  - Validating data paths, not just values
  - Use Trusted Types

## 4\. Content Security Policy (used correctly)

- When applied thoughtfully, CSP meaningfully reduces the impact of exploitable bugs


- CSP is mot effective when it is used to:
  - Restrict script sources
  - Block inline and dynamic execution
  - Limit exploit payload options CSP does not:
  - Prevent DOM logic vulnerabilities
  - Protect against same‑origin script misuse
  - Replace correct output handling

It is most effective as part of a layered defense strategy.

## 5\. Frameworks: Protection and pitfalls

- Modern frameworks provide strong defaults: automatic escaping, safer templating, and controlled rendering models.


- However, vulnerabilities often re‑enter through:
  - Explicit opt‑outs from escaping
  - Unsafe helper APIs
  - Mixing trusted and untrusted data paths

- Frameworks reduce risk, but they do not eliminate the need to understand execution contexts.


## Defense‑in‑Depth: A sustainable posture

Strong XSS defense emerges from layered controls:

- Safe rendering by default


- Minimal exposure to dangerous APIs


- CSP as an impact‑reduction layer


- Ongoing validation and regression testing


No single mitigation is sufficient on its own. Sustainable improvement comes from aligning defenses across the entire rendering pipeline.

![The diagram shows safe rendering that prevents XSS execution ](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/chart2?scl=1)

## Reducing XSS exposure is a shared responsibility

Reducing XSS exposure is not about trying to outsmart attackers or chasing payload variations. It is about eliminating unintended execution paths. When attacker-controlled data is prevented from becoming executable in its final context, exploitation stops being a creativity contest and becomes a non-event.

We’re sharing this summary because these are the same issues many customers and partners are wrestling with today. The pattern that lead to XSS, such as partial mitigations, misunderstood execution contexts, unsafe rendering assumptions, are not unique to any one organization. This post is intended as a practical reference others can adopt and adapt, informed by lessons learned through real application and iteration.

Eliminating XSS at scale requires shared understanding and shared responsibility. By focusing defenses on execution behavior, avoiding dangerous rendering patterns, and validating fixes based on outcomes rather than symptoms, we can collectively reduce risk and take another step toward securing the ecosystem together.

## Authors

Carlston Mills, Security Assurance Engineering, MSRC

Sonal Shrivastava, Security Researcher, MSRC

Kul Subedi, Senior Security Researcher, MSRC