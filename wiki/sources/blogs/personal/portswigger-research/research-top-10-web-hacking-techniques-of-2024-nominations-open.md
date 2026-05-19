---
source: portswigger-research
source_url: https://portswigger.net/research/top-10-web-hacking-techniques-of-2024-nominations-open
title: "Top 10 web hacking techniques of 2024: nominations open | PortSwigger Research"
published: 2025-01-08T14:07:27
description: "Nominations are now open for the top 10 new web hacking techniques of 2024! Every year, security researchers from all over the world share their latest findings via blog posts, presentations, PoCs, an"
---

# Top 10 web hacking techniques of 2024: nominations open

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Wednesday, 8 January 2025 at 14:07 UTC

- **Updated:** Wednesday, 22 January 2025 at 08:54 UTC


![](https://portswigger.net/cms/images/27/7b/e196-article-top10-article.png)

Nominations are now open for the top 10 new web hacking techniques of 2024!

Every year, security researchers from all over the world share their latest findings via blog posts, presentations, PoCs, and whitepapers. These contributions are all invaluable, but some stand out for their innovative approaches and the potential to be re-applied or adapted in new ways. Since 2006, the community has come together annually to sift through this wealth of research and identify the top ten techniques that truly push the boundaries of web security.

Now it’s time to look back on 2024’s breakthroughs and forward to recognizing the most influential, inventive, and reusable research. Whether you’re an industry veteran or new to the project, you can explore our [dedicated top 10 page](https://portswigger.net/research/top-10-web-hacking-techniques) to learn about the origins, history, and purpose of this initiative—plus an archive of past winners and highlights. Nominate your favorites, cast your votes, and help us crown the standout web hacking techniques of 2024!

This year, we'll target the following timeline:

### Timeline

- Jan 8-14: Collect community nominations for the top research from 2024
- Jan 15-21: Community votes on nominations to build a shortlist of the top 15
- Jan 22: Launch panel vote on shortlist to select and order the 10 finalists
- Feb 04: Publish top 10 of 2024!

### What should I nominate?

The aim is to highlight research containing novel, practical techniques that can be re-applied to different systems. Individual vulnerabilities like log4shell are valuable at the time but typically age poorly, whereas underlying techniques such as JNDI Injection can be reapplied to great effect. Nominations can also be refinements to already-known attack classes, such as Exploiting [XXE](https://portswigger.net/web-security/xxe) with Local DTD Files. For further examples, you might find it useful to check out [previous year's top 10s.](https://portswigger.net/research/top-10-web-hacking-techniques)

### Making a nomination

To submit, simply provide a URL to the research, and an optional brief comment explaining what's novel about the work. Feel free to make as many nominations as you like, and nominate your own work if you think it's worthy!

#### [Click here to submit a nomination](https://docs.google.com/forms/d/e/1FAIpQLSfwU40vy3u2nC1oen8Ywk3-NWX-pHhurKjxTR_t4flBhqXIlw/viewform?usp=sf_link)

Please note that I'll filter out nominations that are non-web focused, just tools, or not clearly innovative to keep the number of options in the community vote manageable. We don't collect email addresses - to get notified when the voting stage starts, follow @PortSwiggerRes on [X](https://x.com/portswiggerres), [LinkedIn](https://www.linkedin.com/showcase/portswigger-research), or [BlueSky](https://bsky.app/profile/portswiggerres.bsky.social).

### Nominations

I've made a few nominations myself to get things started, and I'll update this list with fresh community nominations every few days. In the spirit of excessive automation, I've included AI-assisted summaries of each entry.

[Gotta cache 'em all: bending the rules of web cache exploitation](https://portswigger.net/research/gotta-cache-em-all)

Novel techniques exploiting URL parsing discrepancies to achieve arbitrary [web cache poisoning](https://portswigger.net/web-security/web-cache-poisoning) and deception.

[Listen to the whispers: web timing attacks that actually work](https://portswigger.net/research/listen-to-the-whispers-web-timing-attacks-that-actually-work)

Making HTTP/2 timing attacks feasible and effective across diverse web environments by addressing network and server noise through novel techniques like single-packet sync and exploiting scoped [SSRF](https://portswigger.net/web-security/ssrf) opportunities.

[Splitting the email atom: exploiting parsers to bypass access controls](https://portswigger.net/research/splitting-the-email-atom)

Exploiting email parsing discrepancies using encoded words and unicode overflows for [access control](https://portswigger.net/web-security/access-control) bypass and potential RCE in web applications.

[Confusion Attacks: Exploiting Hidden Semantic Ambiguity in Apache HTTP Server!](https://blog.orange.tw/posts/2024-08-confusion-attacks-en/)

Exploiting architectural flaws in Apache HTTP Server's module interactions to achieve insecure path access, predictable handler manipulation, and authentication bypass.

[Insecurity through Censorship: Vulnerabilities Caused by The Great Firewall](https://www.assetnote.io/resources/research/insecurity-through-censorship-vulnerabilities-caused-by-the-great-firewall)

Exploiteing China's DNS poisoning for subdomain takeover via Fastly or [XSS](https://portswigger.net/web-security/cross-site-scripting) via vulnerable cPanel installations.

[Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie)

Bypassing WAFs using legacy support in cookie parsers through the $Version attribute and quoted-string encoding.

[ChatGPT Account Takeover - Wildcard Web Cache Deception](https://nokline.github.io/bugbounty/2024/02/04/ChatGPT-ATO.html)

Exploiting path traversal confusion in CDN and web server URL parsing to cache sensitive API endpoints for auth token theft.

[Why Code Security Matters - Even in Hardened Environments](https://www.sonarsource.com/blog/why-code-security-matters-even-in-hardened-environments/)

Exploiting an arbitrary file write vulnerability in a Node.js application to achieve remote code execution by writing to pipe file descriptors exposed via procfs.

[Remote Code Execution with Spring Properties](https://srcincite.io/blog/2024/11/25/remote-code-execution-with-spring-properties.html)

Leveraging Spring Boot's logging configuration properties to achieve remote code execution through Logback's JoranConfigurator.

[Exploring the DOMPurify library: Bypasses and Fixes](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes)

Mutation XSS by leveraging node flattening, stack of open elements, and namespace confusion to bypass DOMPurify

[Bench Press: Leaking Text Nodes with CSS](https://blog.pspaul.de/posts/bench-press-leaking-text-nodes-with-css/)

Leaking text node content by using CSS animations to measure character heights and exfiltrating data via image requests.

[Source Code Disclosure in ASP.NET apps](https://swarm.ptsecurity.com/source-code-disclosure-in-asp-net-apps/)

Using .NET cookieless sessions to obtain source code.

[http-garden: Differential fuzzing REPL for HTTP implementations.](https://github.com/narfindustries/http-garden)

Platform for finding novel HTTP request smuggling vectors.

[plORMbing your Prisma ORM with Time-based Attacks](https://www.elttam.com/blog/plorming-your-primsa-orm/)

Using time-based attacks on Prisma ORM to leak sensitive data by crafting queries that exploit relational filtering to cause significant execution delays.

[Introducing lightyear: a new way to dump PHP files](https://www.ambionics.io/blog/lightyear-file-dump)

Automated high-speed exploitation with PHP filter chains

[The Ruby on Rails \_json Juggling Attack](https://nastystereo.com/security/rails-_json-juggling-attack.html)

The \_json juggling attack manipulates JSON parameters to bypass authorization in Ruby on Rails by exploiting the handling of \_json keys.

[Encoding Differentials: Why Charset Matters](https://www.sonarsource.com/blog/encoding-differentials-why-charset-matters/)

Exploiting ISO-2022-JP encoding to bypass sanitization and inject JavaScript when charset information is missing.

[A Race to the Bottom - Database Transactions Undermining Your AppSec](https://blog.doyensec.com/2024/07/11/database-race-conditions.html)

Detailed analysis of patterns that enable race condition attacks on database transactions

[Response Filter Denial of Service (RFDoS): shut down a website by triggering WAF rule](https://blog.sicuranext.com/response-filter-denial-of-service-a-new-way-to-shutdown-a-website/)

DoS technique exploiting overly inclusive WAF rules to block legitimate content delivery.

[Unveiling TE.0 HTTP Request Smuggling: Discovering a Critical Vulnerability in Thousands of Google Cloud Websites](https://www.bugcrowd.com/blog/unveiling-te-0-http-request-smuggling-discovering-a-critical-vulnerability-in-thousands-of-google-cloud-websites/)

A novel HTTP Request Smuggling vector affecting Google Cloud-hosted websites.

[DoubleClickjacking: A New Era of UI Redressing](http://paulosyibelo.com/2024/12/doubleclickjacking-what.html)

DoubleClickjacking exploits the timing gap between mousedown and onclick events to bypass clickjacking protections and hijack user actions.

[Devfile file write vulnerability in GitLab](https://gitlab-com.gitlab.io/gl-security/security-tech-notes/security-research-tech-notes/devfile/)

Exploiting YAML parser differentials and path traversal in tar file extraction to achieve arbitrary file write in GitLab.

[Breaking Down Multipart Parsers: File upload validation bypass](https://blog.sicuranext.com/breaking-down-multipart-parsers-validation-bypass/)

Techniques to bypass multipart/form-data parsers by exploiting discrepancies in parameter handling, boundary recognition, and content validation, including duplicated parameters, omission of necessary delimiters, and alternate encoding sequences.

[Supply Chain Attacks: A New Era](https://osec.io/blog/2024-06-10-supply-chain-attacks-a-new-era)

Bypassing Lavamoat’s policy file sandboxing through crafted multiline source map comments and evading SnowJS realm isolation via the deprecated document.execCommand function.

[Abusing Intended Feature And Bypassing Facial Recognition.pptx](https://docs.google.com/presentation/d/16mvSEvpnNYrYcJe4XA_Nwd9OwEuf4UTE/edit?usp=sharing&ouid=101230982661442785272&rtpof=true&sd=true)

Bypassing facial recognition by exploiting AI's inability to distinguish between live human faces and deepfake images.

[Arc Browser UXSS, Local File Read, Arbitrary File Creation and Path Traversal to RCE](https://medium.com/@renwa/arc-browser-uxss-local-file-read-arbitrary-file-creation-and-path-traversal-to-rce-b439f2a299d1)

Techniques to exploit Arc Browser include installing malicious boosts via UI spoofing, achieving Local File Read and Path Traversal for Remote Code Execution by manipulating boost configuration paths.

[Beyond the Limit: Expanding single-packet race condition with a first sequence sync for breaking the 65,535 byte limit](https://flatt.tech/research/posts/beyond-the-limit-expanding-single-packet-race-condition-with-first-sequence-sync/)

Expanding single-packet attack's capabilities by utilizing IP fragmentation and TCP sequence number reordering to exploit limit-overrun vulnerabilities.

[HTTP/2 CONTINUATION Flood: Technical Details](https://nowotarski.info/http2-continuation-flood-technical-details/)

HTTP/2 CONTINUATION Flood attack enables denial of service by exhausting server resources with an unending stream of headers lacking an END\_HEADERS flag.

[Exploring Javascript events & Bypassing WAFs via character normalization](https://0x999.net/blog/exploring-javascript-events-bypassing-wafs-via-character-normalization)

AI fail

[From Arbitrary File Write to RCE in Restricted Rails apps](https://blog.convisoappsec.com/en/from-arbitrary-file-write-to-rce-in-restricted-rails-apps/)

Abusing Bootsnap's cache manipulation to execute arbitrary code in restricted Rails environments.

[Go Go XSS Gadgets: Chaining a DOM Clobbering Exploit in the Wild](https://buer.haus/2024/02/23/go-go-xss-gadgets-chaining-a-dom-clobbering-exploit-in-the-wild/)

Chaining DOM Clobbering with postMessage and CSP bypasses to escalate XSS.

[Statamic CMS](https://bastionsecurity.co.nz/advisories/statamic-cms-cve-2024-52600.html)

Path traversal through filename manipulation in file uploads.

[Exploiting Number Parsers in JavaScript](https://logicalhunter.me/exploiting-number-parsers-in-javascript/)

Exploiting discrepancies in JavaScript number parsers for DoS via parameter pollution.

[\[EN\] Unsecure time-based secret and Sandwich Attack](https://www.aeth.cc/public/Article-Reset-Tolkien/secret-time-based-article-en.html)

AI fail

[DoubleClickjacking: A New Era of UI Redressing](https://www.paulosyibelo.com/2024/12/doubleclickjacking-what.html)

DoubleClickjacking is a novel UI redressing technique exploiting timing and event-order quirks in double-click sequences to bypass clickjacking protections.

[Cross Window Forgery: A New Class of Web Attack](https://www.paulosyibelo.com/2024/02/cross-window-forgery-web-attack-vector.html?m=1)

The paper introduces "Cross Window Forgery," a new web attack technique using browser navigation and keystrokes to execute actions on different websites via URL fragments.

[Exploiting Client-Side Path Traversal to Perform Cross-Site Request Forgery - Introducing CSPT2CSRF](https://blog.doyensec.com/2024/07/02/cspt2csrf.html)

Exploiting Client-Side Path Traversal for CSRF by chaining GET and POST actions (CSPT2CSRF).

[Class Pollution in Ruby: A Deep Dive into Exploiting Recursive Merges](https://blog.doyensec.com/2024/10/02/class-pollution-ruby.html)

Recursive merge technique in Ruby to achieve class pollution for privilege escalation and RCE.

[Unveiling the Prototype Pollution Gadgets Finder](https://blog.doyensec.com/2024/02/17/server-side-prototype-pollution-Gadgets-scanner.html)

Automated exploitation of server-side prototype pollution using gadget identification.

[Hijacking OAUTH flows via Cookie Tossing](https://snyk.io/articles/hijacking-oauth-flows-via-cookie-tossing/)

Hijacking OAUTH flows via Cookie Tossing for Account Takeovers

[Break the Wall from Bottom: Automated Discovery of Protocol-Level Evasion Vulnerabilities in Web Application Firewalls](https://www.jianjunchen.com/p/wafmanis.sp24.pdf)

Automated discovery of protocol-level evasion vulnerabilities in WAFs using a novel testing methodology that exploits parsing discrepancies between WAF and web applications.

[Old new email attacks](https://blog.slonser.info/posts/email-attacks/)

Exploiting inconsistent parsing of email headers across services for email spoofing and SMTP injection.

[CVE-2023-5480: Chrome new XSS Vector](https://blog.slonser.info/posts/cve-2023-5480/)

Exploiting Service Worker registration in JIT-installed workers for XSS via manipulated payment manifests in Chrome.

[Wormable XSS www.bing.com. XSS on www.bing.com context via Maps…](https://medium.com/@pedbap/wormable-xss-www-bing-com-7d7cb52e7a12)

Wormable XSS on Bing using KML file and mixed-case JavaScript to bypass blacklist.

[Another vision for SSRF](https://gccybermonks.com/posts/ssrfvision/)

Using SSRF to capture session cookies by directing requests to a controlled server.

[WorstFit: Unveiling Hidden Transformers in Windows ANSI!](https://blog.orange.tw/posts/2025-01-worstfit-unveiling-hidden-transformers-in-windows-ansi/)

Exploiting Windows Best-Fit character conversion for attacks like Path Traversal, Argument Injection, and RCE across various applications.

[Lost in Translation - WAF Bypasses By Abusing Data Manipulation Processes](https://docs.google.com/presentation/d/1jW0o1YO3FNXlXVkAziM_wSGQqRdLP2kmfoBb6mF1bGY/edit?usp=sharing)

Abusing edge-side includes and Unicode manipulation to bypass WAF.

[Piloting Edge Copilot](https://speakerdeck.com/shhnjk/piloting-edge-copilot)

Sending javascript: URL via postMessage to exploit an XSS vulnerability on Bing.

[POST to XSS: Leveraging Pseudo Protocols to Gain JavaScript Evaluation in SSO Flows](https://security.lauritz-holtmann.de/post/sso-security-redirect-uri-iii/)

Exploiting the javascript: pseudo-protocol with auto-submitting forms in OAuth 2.0 Form Post Response Mode and SAML POST-Binding to achieve XSS.

[Bypassing CSP via URL Parser Confusions: XSS on Netlify’s Image CDN](https://sudistark.github.io/2024/08/31/bypassing-csp-via-url-parser-confusions-xss-on-netlify-s-image-cdn.html)

Bypassing strict CSP using URL parser confusions to achieve XSS on Netlify's Image CDN.

[Iconv, set the charset to RCE: Exploiting the glibc to hack the PHP engine](https://www.ambionics.io/blog/iconv-cve-2024-2961-p3)

Exploiting a buffer overflow in glibc's iconv function to achieve remote code execution in PHP applications, such as Roundcube, by manipulating session variables or leveraging deserialization vulnerabilities.

[Zoom Session Takeover - Cookie Tossing Payloads, OAuth Dirty Dancing, Browser Permissions Hijacking, and WAF abuse](https://nokline.github.io/bugbounty/2024/06/07/Zoom-ATO.html)

Cookie tossing to escalate XSS vulnerabilities, OAuth Dirty Dancing for session takeover, and leveraging XSS for browser permission hijacking and DoS through WAF Frame-up techniques.

[Unveiling Rhino’s Blind Spot: Exploiting Custom Code Execution in Apigee](https://codesent.io/blog/code-sentinels-1/discovering-rhinos-blind-spot-1)

Exploiting the interplay between JavaCallout and JavaScript policies in Apigee to bypass security controls and achieve Remote Code Execution.

[NetModule Router Software Race Condition Leads to Remote Code Execution](https://pentest.blog/advisory-netmodule-router-software-race-condition-leads-to-remote-code-execution/)

A race condition in NetModule Router Software enables remote code execution by exploiting process state files.

[SQL Injection Isn't Dead Smuggling Queries at the Protocol Level](https://www.youtube.com/watch?v=Tfg1B8u1yvE)

Protocol-level SQL injection attacks via database wire protocol smuggling.

[Excessive Expansion: Uncovering Critical Security Vulnerabilities in Jenkins](https://www.sonarsource.com/blog/excessive-expansion-uncovering-critical-security-vulnerabilities-in-jenkins/)

The text describes leveraging the "expandAtFiles" functionality in Jenkins to read arbitrary files and potentially execute arbitrary code on the server.

[Joomla: PHP Bug Introduces Multiple XSS Vulnerabilities](https://www.sonarsource.com/blog/joomla-multiple-xss-vulnerabilities/)

Exploiting inconsistencies in PHP mbstring functions to bypass Joomla's input sanitization leading to XSS vulnerabilities.

[Gudifu: Guided Differential Fuzzing for HTTP Request Parsing Discrepancies](https://dl.acm.org/doi/10.1145/3678890.3678904)

Gudifu uses guided differential fuzzing to discover HTTP request parsing discrepancies that can lead to new attack vectors such as HTTP request smuggling and cache poisoning.

[MSSQL Identified as Vulnerable to Emoji String Exploitation](https://decrypt.lol/posts/2024/11/29/mssql-identified-as-vulnerable-to-emoji-string-exploitation/)

Exploiting Unicode collation logic discrepancies in MSSQL to treat a goblin emoji as an empty string, enabling brute-force attacks.

[Ruby 3.4 Universal RCE Deserialization Gadget Chain](https://nastystereo.com/security/ruby-3.4-deserialization.html)

Developing a universal RCE deserialization gadget chain for Ruby 3.4 that leverages RubyGems autoloading, uses 'rake' and 'make' commands for execution, and suppresses exceptions using an UncaughtThrowError object.

[CVE-2024-50603: Aviatrix Network Controller Command Injection Vulnerability](https://www.securing.pl/en/cve-2024-50603-aviatrix-network-controller-command-injection-vulnerability)

Injecting malicious payloads via unsanitized cloud\_type parameter to execute arbitrary commands on Aviatrix Network Controller.

[CORS vulnerabilities: Weaponizing permissive CORS configurations](https://outpost24.com/blog/exploiting-permissive-cors-configurations/)

Reflected arbitrary origins and alternate domain/subdomain trust in CORS configurations can permit unauthorized data exfiltration.

[Attacking PowerShell CLIXML Deserialization](https://www.truesec.com/hub/blog/attacking-powershell-clixml-deserialization)

Exploiting PowerShell's CLIXML deserialization can lead to Remote Code Execution by leveraging user-defined types, CimInstance rehydration, and vulnerabilities in widely deployed modules, allowing VM escape and attacks on PowerShell Remoting.

[Ruby-SAML / GitLab Authentication Bypass (CVE-2024-45409)](https://projectdiscovery.io/blog/ruby-saml-gitlab-auth-bypass)

Exploiting XPath vulnerabilities to bypass SAML signature validation in Ruby-SAML.

[World of SELECT-only PostgreSQL Injections](https://phrack.org/issues/71/8#article)

Offline manipulation of PostgreSQL filenodes for privilege escalation and RCE.

[Hacking Giants Through a Race Condition in GitHub Actions Artifacts](https://unit42.paloaltonetworks.com/github-repo-artifacts-leak-tokens/)

The text does not contain a novel or innovative web hacking technique.

[Hacking Millions of Modems (and Investigating Who Hacked My Modem)](https://samcurry.net/hacking-millions-of-modems)

Unauthorized access to ISP-managed TR-069 APIs via authorization bypass, leading to full device takeover.

[Exploiting the Unexploitable Insights from the Kibana Bug Bounty](https://media.defcon.org/DEF%20CON%2032/DEF%20CON%2032%20presentations/DEF%20CON%2032%20-%20Mikhail%20Shcherbakov%20-%20Exploiting%20the%20Unexploitable%20Insights%20from%20the%20Kibana%20Bug%20Bounty.pdf)

AI fail.

[DEF CON 32 - SQL Injection Isn't Dead: Smuggling Queries at the Protocol Level](https://media.defcon.org/DEF%20CON%2032/DEF%20CON%2032%20presentations/DEF%20CON%2032%20-%20Paul%20Gerste%20-%20SQL%20Injection%20Isn%27t%20Dead%20Smuggling%20Queries%20at%20the%20Protocol%20Level.pdf)

AI fail.

[Teaching the Old .NET Remoting New Exploitation Tricks](https://code-white.com/blog/teaching-the-old-net-remoting-new-exploitation-tricks/)

Bypassing .NET Remoting security by leveraging XAML parsing to perform deserialization attacks that create privileged objects like WebClient for remote code execution despite TypeFilterLevel.Low and CAS restrictions.

[Efficient Detection of Java Deserialization Gadget Chains via Bottom-up Gadget Search and Dataflow-aided Payload Construction](https://secsys.fudan.edu.cn/_upload/article/files/8a/3c/d8d0e5a142dbbfaa39a58edc76b0/88ab6956-5447-4e4c-8ad8-6785c3fec057.pdf)

Using a bottom-up approach to more efficiently detect Java deserialization gadget chains and leveraging data flow dependencies for payload generation.

[Undefined-oriented Programming: Detecting and Chaining Prototype Pollution Gadgets in Node.js Template Engines for Malicious Consequences](https://yinzhicao.org/UoP/UoP-Oakland.pdf)

Detecting and chaining indirect JavaScript prototype pollution gadgets using undefined properties for complex attack vectors like ACE and RCE..

[JNDI Injection Remote Code Execution via Path Manipulation in MemoryUserDatabaseFactory](https://srcincite.io/blog/2024/07/21/jndi-injection-rce-via-path-manipulation-in-memoryuserdatabasefactory.html)

JNDI injection to manipulate the pathname in MemoryUserDatabaseFactory for remote code execution via crafted XML and directory creation using BeanFactory method invocation.

[GitHub Actions exploitation: untrusted input](https://www.synacktiv.com/publications/github-actions-exploitation-untrusted-input)

GitHub Actions can be exploited through misconfigurations such as untrusted input in triggers (e.g., pull\_request\_target), potentially allowing arbitrary code execution and unauthorized repository modifications.

[a-deep-dive-into-openapi-security.pdf](https://0xpwn.wordpress.com/wp-content/uploads/2024/09/a-deep-dive-into-openapi-security.pdf)

AI fail.

[\[EN\] Multi-sandwich attack with MongoDB Object ID or the scenario for real-time monitoring of web application invitations: a new use case for the sandwich attack](https://www.aeth.cc/public/Article-Reset-Tolkien/multi-sandwich-article-en.html)

Multi-sandwich attack exploiting MongoDB Object ID's predictable counter to monitor and intercept tokens in real-time.

[Secret Web Hacking Knowledge: CTF Authors Hate These Simple Tricks](https://www.youtube.com/watch?v=Sm4G6cAHjWM&feature=youtu.be)

The text does not contain a novel or innovative web hacking technique.

[Facebook Messenger Bug Hunting - A Bug's E2E Lifecycle](https://www.youtube.com/watch?v=M_QPvazEii0)

The text does not contain a novel or innovative web hacking technique.

[Android Exploit to RCE: $5000 Bounty](https://blog.voorivex.team/from-an-android-hook-to-rce-5000-bounty)

Tricking a headless browser into executing arbitrary JavaScript for server-side RCE with DNS tunneling for data exfiltration.

[XSS Vulnerabilities in Excalidraw Affecting Meta (CVE-2024-32472)](https://elmahdi4.wordpress.com/2024/10/25/xss-vulnerabilities-in-excalidraw-affecting-meta-cve-2024-32472/)

Sandbox escape via gist.github iframe in Excalidraw allows arbitrary JavaScript execution.

[1 bug, $50,000+ in bounties, how Zendesk intentionally left a backdoor in hundreds of Fortune 500 companies](https://gist.github.com/hackermondev/68ec8ed145fcee49d2f5e2b9d2cf2e52)

Exploiting Zendesk's lack of email spoofing safeguards to hijack ticket threads and gain unauthorized access to Slack accounts using OAuth.

[Hacking Kia: Remotely Controlling Cars With Just a License Plate](https://samcurry.net/hacking-kia)

Exploiting Kia's dealer token generation to remotely control vehicles using only a license plate and a sequence of backend API requests.

[Using YouTube to steal your files Ʊ](https://lyra.horse/blog/2024/09/using-youtube-to-steal-your-files/)

Chaining multiple open redirect vulnerabilities in YouTube and Google Docs to perform a clickjacking attack granting editor access to Google Drive files.

[Bidding Like a Billionaire - Stealing NFTs With 4-Char CSTIs](https://matanber.com/blog/4-char-csti)

Exploiting Vue.js CSTI through ENS name truncation to achieve XSS and manipulate NFT bids.

[Chaining Three Bugs to Access All Your ServiceNow Data](https://www.assetnote.io/resources/research/chaining-three-bugs-to-access-all-your-servicenow-data)

Bypassing ServiceNow's template injection mitigations via sanitized style tag content for code execution.

[Universal Code Execution by Chaining Messages in Browser Extensions](https://spaceraccoon.dev/universal-code-execution-browser-extensions/)

Chaining messaging APIs in browser extensions to bypass Same Origin Policy and trigger native application vulnerabilities for universal code execution.

[Leaking Jupyter instance auth token chaining CVE-2023-39968, CVE-2024-22421 and a chromium bug](https://blog.xss.am/2023/08/cve-2023-39968-jupyter-token-leak/)

Client-side path traversal chained with an open redirect and a Chromium bug to leak authentication and CSRF tokens.

[Next.js and cache poisoning: a quest for the black hole](https://zhero-web-sec.github.io/research-and-things/nextjs-and-cache-poisoning-a-quest-for-the-black-hole)

Exploiting internal headers in Next.js to control HTTP status codes and cache error pages.

[CVE-2024-4367 - Arbitrary JavaScript execution in PDF.js](https://codeanlabs.com/blog/research/cve-2024-4367-arbitrary-js-execution-in-pdf-js/)

Arbitrary JavaScript execution through manipulated FontMatrix in PDF.js font rendering.

[Bypassing WAFs to Exploit CSPT Using Encoding Levels](https://matanber.com/blog/cspt-levels)

Bypassing WAFs by exploiting discrepancies between URL encoding levels and application decoding levels.

[You can't securely execute commands on Windows](https://flatt.tech/research/posts/batbadbut-you-cant-securely-execute-commands-on-windows/)

Command injection through improper escaping of command arguments when executing batch files via CreateProcess on Windows.

[XSS using dirty Content Type in cloud era](https://speakerdeck.com/flatt_security/xss-using-dirty-content-type-in-cloud-era?slide=21)

XSS through manipulation of Content-Type headers.

[Hello Lucee! Let us hack Apple again?](https://projectdiscovery.io/blog/hello-lucee-let-us-hack-apple-again)

Exploiting deserialization in Lucee CFML servers with REST endpoints for RCE and leveraging vulnerable CFML expression parsing for RCE in Mura CMS.

[Rook to XSS: How I hacked chess.com with a rookie exploit](https://skii.dev/rook-to-xss/)

Using a TinyMCE misconfiguration to achieve XSS by manipulating background-image URL attributes.

[Back to the (Clip)board with Microsoft Whiteboard and Excalidraw in Meta (CVE-2023-26140)](https://spaceraccoon.dev/clipboard-microsoft-whiteboard-excalidraw-meta/)

Exploiting the Clipboard API to inject XSS payloads through poisoned clipboard data in collaborative whiteboard applications.

[SMTP Smuggling - Spoofing E-Mails Worldwide](https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide/)

Using different interpretations of SMTP end-of-data sequences to send spoofed emails across domains, bypassing SPF alignment checks (SMTP smuggling).

[Cloudflare Pagesにおける権限昇格と任意ページの改竄](https://blog.ryotak.net/post/cloudflare-pages-privesc-and-page-tampering/)

File read using symbolic links with misconfigured processing, npm package manipulation for privilege escalation using URL versions, and path traversal exploiting lax path validation on Cloudflare Pages.

[Half Measures and Full Compromise: Exploiting Microsoft Exchange PowerShell Remoting](https://chudypb.github.io/exchange-powershell.html)

Chain of Arbitrary File Write, Arbitrary File Read, and Local DLL Loading for RCE on Exchange.

[SOQL injection](https://www.securitum.com/soql_injection__how_to_exfiltrate_sensitive_data_in_real-world_pentests.html)

Exploiting unrestricted SOQL query endpoints to exfiltrate sensitive Salesforce data.

[Few steps on how to take over a whole application](https://www.securitum.com/few_steps_on_how_to_take_over_a_whole_application.html)

Exploiting predictable reset token patterns within audit logs for arbitrary account takeover.

[Crashing servers with digits](https://www.securitum.com/crashing_servers_with_digits.html)

Exploiting floating-point numbers with excessive digits to cause server DoS.

[User info extraction abusing placeholder injection in Zendesk](https://rikeshbaniya.medium.com/tale-of-zendesk-0-day-and-a-potential-25k-bounty-61bcf9c5dc06)

User info extraction using placeholder injection via subject-to-description sanitization bypass in Zendesk.

[Authorization bypass due to cache misconfiguration](https://rikeshbaniya.medium.com/authorization-bypass-due-to-cache-misconfiguration-fde8b2332d2d)

Authorization bypass due to short-term caching vulnerability.

[Dancer in the Dark: Synthesizing and Evaluating Polyglots for Blind Cross-Site Scripting](https://www.usenix.org/conference/usenixsecurity24/presentation/kirchner)

Synthesizing polyglot payloads for detecting blind XSS across multiple injection contexts without feedback channels.

[Parse Me, Baby, One More Time: Bypassing HTML Sanitizer via Parsing Differentials](https://www.ias.cs.tu-bs.de/publications/parsing_differentials.pdf)

Bypassing HTML sanitizers using parsing differentials to exploit mutation-based XSS vulnerabilities.

[MongoDB NoSQL Injection with Aggregation Pipelines](https://soroush.me/blog/2024/06/mongodb-nosql-injection-with-aggregation-pipelines/)

Accessing other collections via NoSQL injection in MongoDB aggregation pipelines using $lookup or $unionWith operators.

[Delinea Protocol Handler - Remote Code Execution via Update Process (CVE-2024-12908)](https://blog.amberwolf.com/blog/2024/december/cve-2024-12908-delinea-protocol-handler---remote-code-execution-via-update-process/)

Exploiting sslauncher URL handler to achieve Remote Code Execution via MSI transform abuse.

[Anyone can Access Deleted and Private Repository Data on GitHub](https://trufflesecurity.com/blog/anyone-can-access-deleted-and-private-repo-data-github)

Cross Fork Object Reference (CFOR) vulnerability enables unauthorized access to sensitive data in deleted and private GitHub repositories using commit hashes.

[plORMbing your Django ORM](https://www.elttam.com/blog/plormbing-your-django-orm/)

Exploiting relational filtering in Django ORM to leak sensitive data through many-to-many relationship and permission models.

[\[Quick note\] How to build CodeQL DB with closed-source project(.NET Assembly) \| by Jang](https://testbnull.medium.com/quick-note-how-to-build-codeql-db-with-closed-source-project-net-assembly-237b829b6778)

The text does not contain a novel or innovative web hacking technique.

[Abusing Arbitrary File Deletes to Escalate Privilege and Other Great Tricks](https://www.zerodayinitiative.com/blog/2022/3/16/abusing-arbitrary-file-deletes-to-escalate-privilege-and-other-great-tricks)

Abusing the Windows Installer service by exploiting an arbitrary folder delete vulnerability to gain SYSTEM-level privilege escalation.

[GHSL-2024-312: Arbitrary code execution and secret exfiltration in Azure API Management Developer Portal](https://securitylab.github.com/advisories/GHSL-2024-312_Azure_API_Management_Developer_Portal/)

Exploiting untrusted data interpolation in CI workflows for code execution.

[How an obscure PHP footgun led to RCE in Craft CMS](https://www.assetnote.io/resources/research/how-an-obscure-php-footgun-led-to-rce-in-craft-cms)

Abusing the register\_argc\_argv PHP configuration to manipulate Craft CMS path handling and achieve Remote Code Execution via the FTP wrapper in Twig templates.

[Zero Day Initiative — SolarWinds Access Rights Manager: One Vulnerability to LPE Them All](https://www.zerodayinitiative.com/blog/2024/12/11/solarwinds-access-rights-manager-one-vulnerability-to-lpe-them-all)

Exploiting pre-auth arbitrary file deletion via gRPC to perform LPE on domain-joined Windows machines.

[Databricks JDBC Attack via JAAS](https://blog.pyn3rd.com/2024/12/13/Databricks-JDBC-Attack-via-JAAS/)

Exploiting krbJAASFile in Databricks JDBC for remote code execution via JNDI injection.

[Gem::SafeMarshal escape](https://nastystereo.com/security/ruby-safe-marshal-escape.html)

Exploiting a deserialization primitive in Gem::SafeMarshal via Ruby's Date class to achieve arbitrary command execution.

[OAuth Non-Happy Path to ATO](https://blog.voorivex.team/oauth-non-happy-path-to-ato)

Using multiple response\_type values in Google OAuth to capture both id\_token and authorization code in the URL fragment for account takeover.

[Tyranid's Lair: Working your way Around an ACL](https://www.tiraniddo.dev/2024/06/working-your-way-around-acl.html)

No novel or innovative web hacking technique.

[CVE-2023–50220 — Inductive Automation Ignition XML Deserialization to RCE](https://petrusviet.medium.com/cve-2023-50220-inductive-automation-ignition-xml-deserialization-to-rce-7b395412c6cf)

Exploiting XML Deserialization vulnerability to achieve RCE using a modified Jython gadget chain.

[Exploiting Exchange PowerShell After ProxyNotShell: Part 1 - MultiValuedProperty](https://www.zerodayinitiative.com/blog/2024/9/4/exploiting-exchange-powershell-after-proxynotshell-part-1-multivaluedproperty)

Exploiting deserialization in Exchange PowerShell by abusing allowed generic types like MultiValuedProperty to achieve RCE.

[A New Attack Interface In Java Application](https://i.blackhat.com/Asia-23/AS-23-Yuanzhen-A-new-attack-interface-in-Java.pdf)

Exploiting Java applications through JDBC drivers

[Top 10 Hacking Techniques](https://portswigger.net/research/top-10-web-hacking-techniques) [top-10-techniques](https://portswigger.net/research/top-10-techniques)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[05 February 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) [06 January 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open) [04 February 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024) [19 February 2024](https://portswigger.net/research/top-10-web-hacking-techniques-of-2023)