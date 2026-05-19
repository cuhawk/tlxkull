---
source: msrc
source_url: https://www.microsoft.com/en-us/msrc/blog/2025/11/weaponizing-cross-site-scripting-when-one-bug-isnt-enough
title: "Weaponizing cross site scripting: When one bug isn’t enough"
---

This is the Trace Id: 86c79c99643b638bd8bd9871c8b43eee




[Skip to main content](https://www.microsoft.com/en-us/msrc/blog/2025/11/weaponizing-cross-site-scripting-when-one-bug-isnt-enough#mainContent)

[MSRC](https://www.microsoft.com/msrc/blog/category?cat=MSRC "MSRC")

/
By Carlston Mills, Sonal Shrivastava, Kul Subedi/
November 18, 2025


# Weaponizing cross site scripting: When one bug isn’t enough

Cross-Site Scripting (XSS) is often underestimated as a minor vulnerability. In reality, XSS can open the door to more severe attacks when combined with other vulnerabilities.

This post is the second in our series on XSS. In the [first blog post](https://www.microsoft.com/en-us/msrc/blog/2025/09/why-xss-still-matters-msrcs-perspective-on-a-25-year-old-threat), we explored why XSS remains relevant after 25 years. Here, we go further, showing how XSS moves beyond the classic alert (1) example and why a single bug rarely tells the full story.

We’ll look at real-world techniques for chaining XSS with vulnerabilities such as open redirects, CSRF, weak Content Security Policies (CSP), and poor session protection. These combinations can lead to serious consequences, including token leaks and remote code execution.

The goal: demonstrate why layered defenses matter.

## The myth of “isolated vulnerability”

One of the most common pitfalls in application security is assuming that a vulnerability exists in isolation. In reality, attackers rarely rely on a single flaw. They often combine multiple weaknesses to escalate an attack.  XSS is a great illustration of how a “small” vulnerability can become the pivot for a much larger attacks when chained with other issues.

The right approach? Treat every vulnerability as a potential link in an attack chain, not as an isolated defect.

## Chaining XSS with other vulnerabilities

Here are common combinations that elevate XSS from a nuisance to a critical risk:

| **Chaining components** | **Role in exploit** |
| --- | --- |
| **XSS** | Executes arbitrary JavaScript in victim’s browser |
| **XSS + Open Redirect** | Redirects users to malicious URL |
| **XSS + CSRF** | Injected script triggers state-changing requests in authenticated user session |
| **XSS +Weak CSP/No Trusted Types** | Allows script injection and DOM abuse |
| **XSS+ Weak Session Protection** | Enables cookie theft or session hijacking via use of session cookies not marked HttpOnly/Secure |
| **XSS + SSRF** | Injected scripts can trigger visits to internal services or exfiltrate internal files |
| **XSS + poor logging** | Injecting malicious script into the logs |
| **XSS + Broken Authentication** | Steal tokens or session cookies to impersonate users |

## Real-world chaining techniques

## Technique 1: JSON logging, Unicode escaping, and HTML log viewer leading to XSS and account takeover

In this technique, we will explore how a naive looking vulnerable logging and monitoring service can lead to full account takeover of an admin account.

**Scenario:**

A logging service accepts JSON user input. An attacker embeds an XSS payload in a JSON field and submits it as part of user data. The application writes this JSON to an admin-facing HTML log viewer (for example, <script type="application/json">).

The serialization library escapes < and > as Unicode sequences (\\u003c, \\u003e) during HTML rendering, which appears safe. However, the log viewer later decodes these sequences or uses unsafe rendering methods such as innerHTML. As a result, the payload executes in the admin’s browser.

Because the admin is authenticated, the payload can exfiltrate tokens and send them to an attacker-controlled URL. The attacker can then perform privileged actions, leading to account takeover (ATO).

![Attacker send payload -> <- payload exfils token](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/XSS%20blog%20image%201?scl=1)

The root issue is mismatched contexts **.** JSON serialization escapes for one context (script) while the log viewer renders in another (HTML). The sequence of encoders, decoders, and DOM APIs is critical. If you don’t track which encoding is active, XSS can reappear.

![XSS diagram](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/XSS%20blog%20image%202?scl=1)

## Technique 2: From client-side to remote code execution

XSS is a client-side vulnerability, but when chained with other flaws, it can lead to server-side compromise. Two common approaches include:

**1\. Combining XSS with file upload vulnerabilities**

- **Scenario:** An attacker finds XSS in an SVG upload feature.
- **Action:** The attacker uploads a malicious SVG containing a stored XSS payload.
- **Attack chain:** Payload executes when an admin views the SVG, then exploits a file upload or directory traversal flaw to drop a web shell.
- **Outcome:** Remote code execution on the server.

**2\. Abusing administrative functionality**

- **Scenario:** An attacker injects malicious JavaScript in a comment or profile field.
- **Attack chain:**Payload uses the admin’s session to:
  - Add a new admin user.
  - Upload a malicious file or theme.
  - Modify application files.
- **Outcome:** Persistent backdoor and server compromise.

## Technique 3: PostMessage gone wrong: How sending a sensitive impersonation token to an iframe with wildcard (\*) targetOrigin leads to token leakage

Modern apps often use postMessage() for cross-origin communication. Convenience can turn dangerous when sensitive data is sent carelessly.

**Scenario:**

A parent page needs the iframe to perform an action on behalf of the user. Instead of using a secure server-side handshake, the parent posts an object containing a sensitive impersonation of access token to iframe and uses wildcard origin (\*).

```js
iframe.contentWindow.postMessage(message, "*");
```

Because “\*” accepts messages from any origin and an iframe can be embedded by an attacker, the token can be exfiltrated or used by an unauthorized party-enabling impersonation and data theft.

The issue stems from using \* as the target origin and not verifying the sender in the message handler. This approach trusts any origin and any sender.

**Best practices**

- Avoid sending entire objects that may include secrets.


- Send only minimal identifiers (such as IDs or short codes).


- Have the iframe request sensitive details from the server using its own authenticated channel.


Our blog, [postMessaged and Compromised](https://www.microsoft.com/en-us/msrc/blog/2025/08/postmessaged-and-compromised/), covers this topic in detail.

## Key takeaways

XSS rarely exists in isolation. When combined with other weaknesses, a minor script injection can escalate into full exploitation. Because attacks are composable, defenses must be layered. Treat XSS as a gateway risk, not a standalone bug.

**Key mitigations include:**

- Output encoding and input validation.


- Hardened session management.


- Safe storage practices.


- Strict Content Security Policies.


## What's next

In the final blog of this XSS series, we’ll explore practical mitigation strategies to reduce risk and prevent escalation. Whether you’re a developer or part of a security team, these defenses are essential for building resilient applications.

## Authors

Carlston Mills, Security Assurance Engineering, MSRC

Sonal Shrivastava, Security Researcher, MSRC

Kul Subedi, Senior Security Researcher, MSRC