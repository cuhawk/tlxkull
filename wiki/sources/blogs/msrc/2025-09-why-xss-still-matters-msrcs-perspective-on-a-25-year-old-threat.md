---
source: msrc
source_url: https://www.microsoft.com/en-us/msrc/blog/2025/09/why-xss-still-matters-msrcs-perspective-on-a-25-year-old-threat
title: "why-xss-still-matters-msrcs-perspective-on-a-25-year-old-threat"
---

This is the Trace Id: 01ade0a97be6ee48d13d1569f2930960




[Skip to main content](https://www.microsoft.com/en-us/msrc/blog/2025/09/why-xss-still-matters-msrcs-perspective-on-a-25-year-old-threat#mainContent)

# Why XSS still matters: MSRC’s perspective on a 25-year-old threat

[MSRC](https://www.microsoft.com/msrc/blog/category?cat=MSRC "MSRC")

/
By MSRC/
September 4, 2025


Cross-Site Scripting (XSS) has been a known vulnerability class for two decades, yet it continues to surface in modern applications, including those built with the latest frameworks and cloud-native architectures. At Microsoft, we still receive a steady stream of XSS reports across our services, from legacy portals to newly deployed single-page apps. Despite advancements in browser security, content security policies (CSP), and secure-by-default libraries, XSS remains a persistent threat vector with real-world consequences.

That’s why we’re sharing this series: to explore why XSS still matters, how Microsoft approaches detection and mitigation, and what we’ve learned from real-world incidents. Whether you’re a security engineer reviewing bug bounty submissions or a developer building secure-by-default components, understanding the evolving nature of XSS is critical to defending modern web ecosystems.

Our team at the Microsoft Security Response Center (MSRC) has triaged XSS cases that bypassed traditional mitigations, exploited subtle DOM behaviors, and chained with other bugs to achieve impactful outcomes. Some of these cases have qualified for bounty awards and driven internal tooling improvements or policy changes. While this first post focuses on framing the problem, future blog posts will share actionable learnings and best practices to help keep customers safe.

**Real-world case insights: What MSRC XSS reports reveal**

Despite being one of the oldest known web vulnerabilities, Cross-Site Scripting (XSS) continues to dominate Microsoft’s security case landscape. As of mid-2025, MSRC has mitigated over 970 XSS cases since January 2024 alone. These cases span a wide spectrum, ranging from low-impact self-XSS to zero-click stored XSS with Critical severity. They offer a unique lens into the evolving threat landscape and Microsoft’s response strategy.

**XSS by the numbers (July 2024 – July 2025)**

- 15% of all important or critical MSRC cases were XSS

- Out of 265 XSS cases, 263 were rated Important severity and 2 were rated Critical severity $912,300 was paid in XSS bounty awards

- The highest single bounty awarded was $20,000 for high-impact cases such as token theft or zero-click attacks.


![A screenshot of a graph AI-generated content may be incorrect.](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__09__bd120c45?scl=1)

**Patterns across Microsoft’s ecosystem**

Cross-site scripting (XSS) vulnerabilities have been reported across a broad range of Microsoft services enrolled in our bounty programs, including the [Microsoft Copilot Bounty Program](https://www.microsoft.com/en-us/msrc/bounty-ai?msockid=156b869d3af56c910fe393003ba36dea), [Microsoft 365 Bounty Program](https://www.microsoft.com/en-us/msrc/bounty-online-services?msockid=156b869d3af56c910fe393003ba36dea), [Microsoft Dynamics 365 and Power Platform Bounty Program](https://www.microsoft.com/en-us/msrc/bounty-dynamics?msockid=156b869d3af56c910fe393003ba36dea), [Microsoft Identity Bounty Program](https://www.microsoft.com/en-us/msrc/bounty-microsoft-identity?msockid=1d59efa404bd6bff041efa6705aa6a7a), [Microsoft Azure Bounty Program](https://www.microsoft.com/en-us/msrc/bounty-microsoft-azure?msockid=156b869d3af56c910fe393003ba36dea), and the [Xbox Bounty Program](https://www.microsoft.com/en-us/msrc/bounty-xbox?msockid=156b869d3af56c910fe393003ba36dea).

Reports are submitted by both internal and external security researchers and commonly highlight bypasses of sanitization logic, DOM-based vulnerabilities, and edge-case behaviors in modern web frameworks.

These patterns reinforce the importance of proactive validation, secure-by-design principles, and continuous engagement with the security research community to strengthen protections across the Microsoft ecosystem.

**What makes an XSS impactful?**

Not all XSS vulnerabilities pose the same level of risk to customers. At Microsoft, we prioritize case-based factors that directly affect customer security, such as exploitability, data sensitivity, required user interaction, and real-world impact. The guiding principle behind our assessment is simple: reduce risk where it matters to most customers.

Whether it’s a zero-click exploit that could compromise sensitive data or a bypass of sanitization logic in a high-traffic service, our focus is on identifying and mitigating the vulnerabilities that have the greatest potential to affect customer trust and safety. To support the security research community, we’re sharing how MSRC evaluates XSS severity and distinguishes between Critical and lower-severity issues. This transparency helps researchers understand how their findings contribute to customer protection and where their efforts can have the most impact.

**How MSRC classifies XSS severity**

To prioritize customer protection, MSRC evaluates XSS vulnerabilities using a matrix that combines data classification with exploit conditions to determine severity. This approach helps ensure the most impactful issues receive the highest priority.

| **Data Classification** | **Severity** | **Example** |
| --- | --- | --- |
| Highly Confidential | Critical | Zero-click XSS that compromises session tokens or sensitive cookies |
| Confidential | Important | XSS requiring user interaction but still exposing session tokens |
| General/Public | Moderate/Low | XSS on public pages with no sensitive data exposure or requiring self-XSS |

Additional factors that influence severity include **user interaction, attacker prerequisites, and environmental conditions**.

For example, a vulnerability identified on login.microsoftonline.com may initially be rated Critical due to the domain’s sensitivity. However, if successful exploitation requires multiple user interactions or relies on attacker-controlled redirects, the severity may be more accurately assessed as Important. This reflects Microsoft’s approach to contextual risk evaluation, where exploitability and real-world impact are key factors in determining severity.

**Servicing criteria: What qualifies and what falls outside scope**

**In scope:**

- Stored or reflected XSS that executes in a Microsoft domain with access to session tokens or cookies.

- DOM-based XSS that bypasses CSP and executes in a privileged context.

- Zero-click or one-click payloads that affect authenticated users.


**Out of scope:**

- JavaScript Execution in PDF Context (XSS in PDF)
  - JavaScript execution within PDF files typically does not meet Microsoft’s servicing criteria. While PDFs may support limited scripting such as form field validation, their execution context is significantly more constrained than that of HTML documents and lacks domain-based authority. To qualify for servicing, a report must demonstrate a clear escape from the PDF’s restricted environment into a broader or more privileged execution context.
- Self-XSS
  - Scenarios where exploitation requires the victim to manually paste a payload into the browser’s developer console do not meet Microsoft’s servicing criteria. These cases depend on deliberate user actions that fall outside the scope of exploitable, serviceable vulnerabilities.
- XSS that executes only in non-standard browsers or extensions
  - Cross-site scripting (XSS) vulnerabilities that execute only in non-standard or unsupported environments such as outdated browsers or legacy platforms like Internet Explorer do not meet Microsoft’s servicing criteria. These scenarios fall outside the scope of supported configurations and do not reflect modern, real-world usage patterns. To qualify for servicing, vulnerabilities must demonstrate impact within current, supported browser environments.

**XSS submission checklist**

**Reproducibility**

- Provide clear, step-by-step reproduction instructions

- Include a reliable, minimal proof-of-concept (PoC)

- Test across multiple browsers (e.g., Edge, Chrome)

- Ensure payloads work without dev tools or console access


**Exploitability**

- Triggered with zero or one user interaction

- Executes on a Microsoft-owned domain

- Bypasses CSP or other mitigations

- Impacts authenticated users or sensitive workflows


**Impact**

- Results in token theft, session hijack, or data exfiltration

- Exposes confidential or highly confidential data

- Stored or reflected in a scalable/persistent way


**Documentation**

- Include screenshots or video demo

- Explain the security boundary being crossed

- Clearly state the expected vs. actual behavior


**What’s next: Deep dive into XSS payload chaining**

In our upcoming blog series, we’ll take a closer look into the technical mechanics of chaining XSS payloads. We’ll explore advanced techniques such as polyglot attacks and DOM manipulation and then shift focus to defense-in-depth strategies that help mitigate these threats.

**You can expect practical guidance on:**

- Implementing robust input validation

- Applying context-aware output encoding

- Enforcing Content Security Policy (CSP)

- Leveraging modern frameworks that automatically escape user input


While we prepare to dive into these topics, we encourage you to explore the fundamentals of cross-site scripting (XSS) through this Microsoft Learn resource: [The Hacker’s Guide to XSS Injection](https://learn.microsoft.com/en-us/shows/jdconf-2022/the-hackers-guide-to-xss-injection).

**Authors**

Carlston Mills, Security Assurance Engineering, MSRC

Sonal Shrivastava, Security Researcher, MSRC

Kul Subedi, Senior Security Researcher, MSRC

**Acknowledgements**

Special thanks to Michael Hendrickx, Bruce Robinson, and Jarek Stanley for their contributions to this blog.

- [Security Research](https://www.microsoft.com/en-us/msrc/blog/tag?tag=Security%20Research)