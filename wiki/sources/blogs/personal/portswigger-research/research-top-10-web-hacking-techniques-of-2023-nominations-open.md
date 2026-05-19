---
source: portswigger-research
source_url: https://portswigger.net/research/top-10-web-hacking-techniques-of-2023-nominations-open
title: "Top 10 web hacking techniques of 2023 - nominations open | PortSwigger Research"
published: 2024-01-09T14:33:50
description: "Update: The results are in! Check out the final top ten here or scroll down to view all nominations Over the last year, numerous security researchers have shared their discoveries with the community t"
---

# Top 10 web hacking techniques of 2023 - nominations open

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Tuesday, 9 January 2024 at 14:33 UTC

- **Updated:** Monday, 20 May 2024 at 14:00 UTC


![](https://portswigger.net/cms/images/9e/92/6b3b-article-article.png)

**Update: The results are in! [Check out the final top ten here](https://portswigger.net/research/top-10-web-hacking-techniques-of-2023) or [scroll down to view all nominations](https://portswigger.net/research/top-10-web-hacking-techniques-of-2023-nominations-open#nominations)**

Over the last year, numerous security researchers have shared their discoveries with the community through blog posts, presentations and whitepapers. Many of these posts contain innovative ideas waiting for the right person to adapt and combine them into new discoveries in future.

However, the sheer volume can leave good techniques overlooked and quickly forgotten. Since 2006, the community has come together every year to help by building two valuable resources

- A full list of all notable web security research from the last year
- A refined list of the top ten most valuable pieces of work

Check out the [full project archive](https://portswigger.net/research/top-10-web-hacking-techniques) for past nominees and winners. Read on to find out how you can make your nominations from 2023!

This year, we'll target the following timeline:

### Timeline

- Jan 9-21: Collect community nominations
- Jan 23-30: Community vote to build shortlist of top 15
- Feb 1-13: Expert panel vote on final 15
- Feb 15: Results announced!

### What should I nominate?

The aim is to highlight research containing novel, practical techniques that can be re-applied to different systems. Individual vulnerabilities like log4shell are valuable at the time but age relatively poorly, whereas underlying techniques such as JNDI Injection can often be reapplied to great effect. Nominations can also be refinements to already-known attack classes, such as Exploiting [XXE](https://portswigger.net/web-security/xxe) with Local DTD Files. For further examples, you might find it useful to check out [previous year's top 10s](https://portswigger.net/research/top-10-web-hacking-techniques).

### How to make a nomination

To submit, simply provide a URL to the research, and an optional brief comment explaining what's novel about the work. Feel free to make as many nominations as you like, and nominate your own work if you think it's worthy!

#### [Click here to submit a nomination](https://docs.google.com/forms/d/e/1FAIpQLSc5CaiPUIlII3DLS6i1xK9ya3XRJRU8uW7vFRhT3toYSrrsTQ/viewform?usp=sf_link)

Please note that I'll filter out nominations that are non-web focused, just tools, or not clearly innovative to keep the number of options in the community vote manageable. We don't collect email addresses - to get notified when the voting stage starts, follow [@PortSwiggerRes](https://twitter.com/portswiggerres) or [@albinowax@infosec.exchange](https://infosec.exchange/@albinowax).

### Nominations

I've made a few nominations myself to get things started, and I'll update this list with fresh community nominations every few days. In the spirit of excessive automation, I've included AI-assisted summaries of each entry.

- [Ransacking your password reset tokens](https://positive.security/blog/ransack-data-exfiltration)

Brute-force attack on Ruby on Rails applications using the Ransack library, to exfiltrate password reset tokens through character-by-character prefix matching via search filters.

- [mTLS: When certificate authentication is done wrong](https://github.blog/2023-08-17-mtls-when-certificate-authentication-is-done-wrong/)

Vulnerabilities in mutual TLS leading to user impersonation, privilege escalation, and information leakage.

- [Smashing the state machine: the true potential of web race conditions](https://portswigger.net/research/smashing-the-state-machine)

Concept of "everything is multi-step" for web [race conditions](https://portswigger.net/web-security/race-conditions), expanding the traditional limit-overrun attack scope by exploiting hidden sub-states within web applications and introducing a jitter-resistant "single-packet attack".

- [Bypass firewalls with of-CORs and typo-squatting](https://trufflesecurity.com/blog/of-cors/)

Exploitation of [Cross-Origin Resource Sharing](https://portswigger.net/web-security/cors) ( [CORS](https://portswigger.net/web-security/cors)) misconfigurations on internal networks using typo-squatting domains to probe for and exfiltrate sensitive data without violating bug bounty rules.

- [RCE via LDAP truncation on hg.mozilla.org](https://0day.click/recipe/pash/)

Achieved Remote Code Execution (RCE) on Mozilla's server by exploiting LDAP query truncation with NULL byte injection to bypass input sanitization, enabling [command injection](https://portswigger.net/web-security/os-command-injection).

- [Cookie Bugs - Smuggling & Injection](https://blog.ankursundara.com/cookie-bugs/)

Exploiting inconsistent parsing of dquoted cookie values, leading to cookie smuggling, and how incorrect delimiters allow cookie injection, enabling CSRF token spoofing and potential authentication bypasses.

- [OAuth 2.0 Redirect URI Validation Falls Short, Literally](https://dl.acm.org/doi/pdf/10.1145/3627106.3627140)

OAuth exploitation via path confusion.

- [Prototype Pollution in Python](https://blog.abdulrah33m.com/prototype-pollution-in-python/)

Class Pollution in Python via recursive merge functions manipulating \`\_\_class\_\_\` special attributes.

- [Pretalx Vulnerabilities: How to get accepted at every conference](https://www.sonarsource.com/blog/pretalx-vulnerabilities-how-to-get-accepted-at-every-conference/)

Leveraging Python's site-specific configuration hooks for .pth files to gain arbitrary code execution via limited file write vulnerability.

- [From Akamai to F5 to NTLM... with love.](https://blog.malicious.group/from-akamai-to-f5-to-ntlm/)

Leveraging HTTP request smuggling and cache poisoning via Akamai and F5 BIGIP systems to redirect and steal sensitive data including authorization tokens and NTLM credentials.

- [can I speak to your manager? hacking root EPP servers to take control of zones](https://hackcompute.com/hacking-epp-servers/)

Exploiting XXE vulnerabilities in EPP servers and local file disclosure in CoCCA Registry Software to gain control of entire ccTLD zones.

- [Blind CSS Exfiltration: exfiltrate unknown web pages](https://portswigger.net/research/blind-css-exfiltration)

Using CSS :has selector to perform blind exfiltration of sensitive data without JavaScript.

- [Server-side prototype pollution: Black-box detection without the DoS](https://portswigger.net/research/server-side-prototype-pollution)

Leveraging non-destructive techniques like JSON response manipulation and CORS header injection for the safe black-box detection of server-side prototype pollution.

- [Tricks for Reliable Split-Second DNS Rebinding in Chrome and Safari](https://www.intruder.io/research/split-second-dns-rebinding-in-chrome-and-safari)

Exploiting delayed DNS responses with Safari and Chrome's prioritization of IPv6 to perform split-second DNS rebinding attacks.

- [HTML Over the Wire](https://bountyplz.xyz/bugbounty/2023/07/30/HTML-Over-The-Wire.html)

Exploiting "HTML Over the Wire" libraries' features for CSRF token leakage via cross-origin POST requests with injected links.

- [SMTP Smuggling - Spoofing E-Mails Worldwide](https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide/)

Exploiting differences in SMTP protocol interpretation to bypass SPF and DMARC email validation checks and send spoofed emails.

- [DOM-based race condition: racing in the browser for fun - RyotaK's Blog](https://blog.ryotak.net/post/dom-based-race-condition/)

Exploiting race conditions in AngularJS applications by delaying the loading of AngularJS with a connection pool exhaustion attack to enable DOM-based XSS via pasted clipboard data with ng- directives.

- [You Are Not Where You Think You Are, Opera Browsers Address Bar Spoofing Vulnerabilities](https://medium.com/@renwa/you-are-not-where-you-think-you-are-opera-browsers-address-bar-spoofing-vulnerabilities-aa36ad8321d8)

Address bar spoofing techniques in Opera browsers, exploiting features like intent URLs, extension updates, and fullscreen mode

- [CVE-2022-4908: SOP bypass in Chrome using Navigation API](https://joaxcar.com/blog/2023/10/06/cve-2022-4908-sop-bypass-in-chrome-using-navigation-api/)

Abusing Navigation API's \`navigation.entries()\` to leak the navigation history array from cross-origin windows.

- [SSO Gadgets: Escalate (Self-)XSS to ATO](https://security.lauritz-holtmann.de/post/xss-ato-gadgets/)

Leveraging SSO gadgets in OAuth2/OIDC implementations to convert Self-XSS to ATO.

- [Three New Attacks Against JSON Web Tokens](https://i.blackhat.com/BH-US-23/Presentations/US-23-Tervoort-Three-New-Attacks-Against-JSON-Web-Tokens-whitepaper.pdf)

Novel JWT implemtation flaws

- [Introducing wrapwrap: using PHP filters to wrap a file with a prefix and suffix](https://www.ambionics.io/blog/wrapwrap-php-filters-suffix)

Leveraging PHP filter chains to prepend and append arbitrary content to file data, facilitating SSRF to RCE and local file inclusion attacks.

- [PHP filter chains: file read from error-based oracle](https://www.synacktiv.com/publications/php-filter-chains-file-read-from-error-based-oracle)

Combining memory exhaustion and encoding translations via PHP filter chains to perform error-based local file content leakage.

- [SSRF Cross Protocol Redirect Bypass](https://blog.doyensec.com/2023/03/16/ssrf-remediation-bypass.html)

Bypassing SSRF filters using cross-protocol redirection from HTTPS to HTTP.

- [A New Vector For “Dirty” Arbitrary File Write to RCE](https://blog.doyensec.com/2023/02/28/new-vector-for-dirty-arbitrary-file-write-2-rce.html)

Leveraging uWSGI configuration parsing for remote code execution via a tainted PDF utilizing polymorphic content and automatic reload behavior.

- [How I Hacked Microsoft Teams and got $150,000 in Pwn2Own](https://speakerdeck.com/masatokinugawa/how-i-hacked-microsoft-teams-and-got-150000-dollars-in-pwn2own)

RCE in Microsoft Teams through a combination of bugs including XSS via chat message, lack of context isolation, and JS execution outside the sandbox.

- [AWS WAF Clients Left Vulnerable to SQL Injection Due to Unorthodox MSSQL Design Choice](https://www.gosecure.net/blog/2023/06/21/aws-waf-clients-left-vulnerable-to-sql-injection-due-to-unorthodox-mssql-design-choice/)

Terminating MSSQL queries with ' ' instead of ';' to bypass AWS WAF.

- [BingBang: AAD misconfiguration led to Bing.com results manipulation and account takeover](https://www.wiz.io/blog/azure-active-directory-bing-misconfiguration)

Leveraging AAD multi-tenant misconfiguration for unauthorized application access leading to Bing.com result manipulation and XSS attacks.

- [MyBB Admin Panel RCE CVE-2023-41362](https://blog.sorcery.ie/posts/mybb_acp_rce/)

Exploiting catastrophic backtracking in MyBB's admin panel regex to bypass template safety checks and execute arbitrary code.

- [Source Code at Risk: Critical Code Vulnerability in CI/CD Platform TeamCity](https://www.sonarsource.com/blog/teamcity-vulnerability/)

Bypassing TeamCity server authentication check with unsanitized input handling for request interceptor pre-handling paths.

- [Code Vulnerabilities Put Skiff Emails at Riskr](https://www.sonarsource.com/blog/code-vulnerabilities-put-skiff-emails-at-risk/)

Bypassing Skiff's HTML sanitization to achieve XSS and steal decrypted emails.

- [How to break SAML if I have paws?](https://speakerdeck.com/greendog/how-to-break-saml-if-i-have-paws)

Attacking SAML implementations through XML signature wrapping, plaintext injections, signature exclusion, flawed certificate validation, and more.

- [JMX Exploitation Revisited](https://codewhitesec.blogspot.com/2023/03/jmx-exploitation-revisited.html)

Leveraging JMX StandardMBean and RequiredModelMBean for RCE by dynamic MBean creation and arbitrary method invocation.

- [Java Exploitation Restrictions in Modern JDK Times](https://codewhitesec.blogspot.com/2023/04/java-exploitation-restrictions-in.html)

Bypassing Java deserialization gadget execution restrictions in modern JDKs using JShell API for JDK versions >= 15 and --add-opens with Reflection for JDK >= 16.

- [Exploiting Hardened .NET Deserialization](https://github.com/thezdi/presentations/blob/main/2023_Hexacon/whitepaper-net-deser.pdf)

Bypassing .NET deserialization security using novel gadget chains.

- [Unserializable, but unreachable: Remote code execution on vBulletin](https://www.ambionics.io/blog/vbulletin-unserializable-but-unreachable)

Exploiting class autoloading in PHP for remote code execution by including arbitrary files using crafted unserialize payloads in vBulletin.

- [Cookieless DuoDrop: IIS Auth Bypass & App Pool Privesc in ASP.NET Framework](https://soroush.me/blog/2023/08/cookieless-duodrop-iis-auth-bypass-app-pool-privesc-in-asp-net-framework-cve-2023-36899/)

Bypassing IIS authentication and impersonating parent application pool identities in ASP.NET using double cookieless pattern.

- [Hunting for Nginx Alias Traversals in the wild](https://labs.hakaioffsec.com/nginx-alias-traversal/)

Leveraging Nginx alias misconfigurations for directory traversal attacks.

- [DNS Analyzer - Finding DNS vulnerabilities with Burp Suite](https://sec-consult.com/blog/detail/dns-analyzer-finding-dns-vulnerabilities-with-burp-suite/)

Using Burp Collaborator with DNS Analyzer extension to identify DNS vulnerabilities that facilitate Kaminsky-style DNS cache poisoning attacks.

- [Oh-Auth - Abusing OAuth to take over millions of accounts](https://salt.security/blog/oh-auth-abusing-oauth-to-take-over-millions-of-accounts)

Manipulating OAuth token verification logic to facilitate account takeovers.

- [nOAuth: How Microsoft OAuth Misconfiguration Can Lead to Full Account Takeover](https://www.descope.com/blog/post/noauth)

Leveraging mutable and unverified "email" claim within Microsoft Azure AD OAuth applications for account takeover.

- [One Scheme to Rule Them All: OAuth Account Takeover](https://blog.ostorlab.co/one-scheme-to-rule-them-all.html)

Exploiting OAuth with app impersonation via custom scheme hijacking for account takeover.

- [Exploiting HTTP Parsers Inconsistencies](https://rafa.hashnode.dev/exploiting-http-parsers-inconsistencies)

Exploiting HTTP parser inconsistency for ACL bypass and cache poisoning.

- [New ways of breaking app-integrated LLMs](https://github.com/greshake/llm-security)

Indirect prompt injection attacks on application-integrated LLMs enabling remote control, data exfiltration, and persistent compromise.

- [State of DNS Rebinding in 2023](https://research.nccgroup.com/2023/04/27/state-of-dns-rebinding-in-2023/)

Advancements and trends in DNS rebinding attacks, examining their effectiveness against modern web security measures

- [Fileless Remote Code Execution on Juniper Firewalls](https://vulncheck.com/blog/juniper-cve-2023-36845)

PHP environment variable manipulation technique that bypasses the need for a file upload, exploiting the auto\_prepend\_file PHP feature and the Appweb web server's handling of environment variables and stdin.

- [Thirteen Years On: Advancing the Understanding of IIS Short File Name (SFN) Disclosure!](https://soroush.me/blog/2023/07/thirteen-years-on-advancing-the-understanding-of-iis-short-file-name-sfn-disclosure/)

Revealing full file names in IIS that contain ~DIGIT patterns using file name enumeration techniques.

- [Metamask Snaps: Playing in the Sand](https://osec.io/blog/2023-11-01-metamask-snaps)

Exploiting untrusted code execution via JSON sanitization bypass within Metamask Snaps environment.

- [Uncovering a crazy privilege escalation from Chrome extensions](https://0x44.xyz/blog/cve-2023-4369/index.html)

Escalation to arbitrary code execution via chrome:// URL XSS and filesystem: protocol abuse in Chrome extensions on ChromeOS.

- [Code Vulnerabilities Put Proton Mails at Risk](https://www.sonarsource.com/blog/code-vulnerabilities-leak-emails-in-proton-mail/?utm_source=twitter&utm_medium=social&utm_campaign=protonmail&utm_content=security&utm_term=mofu)

DOMPurify sanitization bypass in Proton Mail via svg to proton-svg renaming leading to XSS.

- [Hacking into gRPC-Web](https://infosecwriteups.com/hacking-into-grpc-web-a54053757a45)

Exploiting gRPC-Web to discover hidden services and parameters, leading to vulnerabilities like SQL injection.

- [Yelp ATO via XSS + Cookie Bridge](https://hackerone.com/reports/2089042)

Achieving Account Takeover (ATO) on yelp.com and biz.yelp.com through Cross-Site Scripting (XSS) coupled with Cookie Bridging.

- [HTTP Request Splitting vulnerabilities exploitation](https://offzone.moscow/upload/iblock/11a/sagouc86idiapdb8f29w41yaupqv6fwv.pdf)

Leveraging nginx misconfigurations to perform HTTP request splitting via control characters in variables.

- [XSS in GMAIL Dynamic Email](https://asdqw3.medium.com/xss-in-gmail-dynamic-email-amp-for-email-3872d6052a0d)

Exploitation of CSS parsing in Gmail's AMP for Email allowed injection of meta tag for potential phishing, bypassing strict CSP with no effective XSS.

- [Azure B2C Crypto Misuse and Account Compromise](https://www.praetorian.com/blog/azure-b2c-crypto-misuse-and-account-compromise/)

Extracting public RSA keys to craft valid OAuth refresh tokens and compromise Azure AD B2C user accounts.

- [Compromising F5 BIGIP with Request Smuggling](https://www.praetorian.com/blog/refresh-compromising-f5-big-ip-with-request-smuggling-cve-2023-46747/)

Exploiting the AJP protocol with HTTP request smuggling to bypass authentication and execute arbitrary system commands on F5 BIG-IP systems identified by CVE-2023-46747.

- [EmojiDeploy: Smile! Your Azure web service just got RCE’d](https://ermetic.com/blog/azure/emojideploy-smile-your-azure-web-service-just-got-rced/)

Exploiting same-site misconfiguration and origin check bypass in Azure Kudu SCM to achieve RCE through CSRF via ZIP file deployments.

- [One Supply Chain Attack to Rule Them All](https://adnanthekhan.com/2023/12/20/one-supply-chain-attack-to-rule-them-all/)

Exploiting self-hosted GitHub Action runners for persistent access and executing arbitrary code on internal GitHub infrastructure to compromise CI/CD secrets and potentially tamper with GitHub's runner images for supply chain attacks.

- [draw.io CVEs](https://lude.rs/h4ck1ng/draw.io_cves.html)

OAuth token leakage due to a whitespace bypass in URL validation.

- [Leaking Secrets From GitHub Actions: Reading Files And Environment Variables, Intercepting Network/Process Communication, Dumping Memory](https://karimrahal.com/2023/01/05/github-actions-leaking-secrets/)

Leveraging command injection in GitHub Actions to read environment variables and files, intercept network and process communication, and dump memory for extracting secrets.

- [fuzzuli](https://github.com/musana/fuzzuli)

Dynamic generation of wordlists based on domain name transformations to discover backup files.

- [The GitHub Actions Worm: Compromising GitHub Repositories Through the Actions Dependency Tree](https://www.paloaltonetworks.com/blog/prisma-cloud/github-actions-worm-dependencies/)

Leveraging GitHub Actions' dependency tree to spread malware recursively across repositories using compromised Actions.

- [From an Innocent Client-Side Path Traversal to Account Takeover](https://kapytein.nl/from-an-innocent-client-side-path-traversal-to-account-takeover)

Leveraging client-side path traversal in fetch requests and OAuth error redirection for account takeover.

- [tRPC Security Research: Hunting for Vulnerabilities in Modern APIs](https://medium.com/@LogicalHunter/trpc-security-research-hunting-for-vulnerabilities-in-modern-apis-b0d38e06fa71)

Leveraging Type errors and improperly secured trpc-panel endpoints to identify and exploit tRPC API vulnerabilities.

- [Chained to hit: Discovering new vectors to gain remote and root access in SAP Enterprise Software](https://i.blackhat.com/BH-US-23/Presentations/US-23-Genuer-chained-to-hit-discovering-new-vectors-to-gain-remote-and-root-access-in-sap-enterprise-software-wp.pdf)

Exploiting SAP Enterprise via the P4 protocol and JNDI reference injection.

- [AWS WAF Bypass: invalid JSON object and unicode escape sequences](https://blog.sicuranext.com/aws-waf-bypass/)

Bypassing AWS WAF via invalid JSON with duplicated parameter names.

- [Cookie Crumbles: Breaking and Fixing Web Session Integrity](https://www.usenix.org/conference/usenixsecurity23/presentation/squarcina)

Exposing session integrity vulnerabilities due to implementation or specification inconsistencies across browsers and web frameworks.

- [Memcached Command Injections at Pylibmc](https://btlfry.gitlab.io/notes/posts/memcached-command-injections-at-pylibmc/)

Exploiting Flask-Session with Memcached command injection utilizing crc32 collision and python pickle deserialization for RCE.


[Top 10 Hacking Techniques](https://portswigger.net/research/top-10-web-hacking-techniques)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[05 February 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) [06 January 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open) [04 February 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024) [08 January 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024-nominations-open)