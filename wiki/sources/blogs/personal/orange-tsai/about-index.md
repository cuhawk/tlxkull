---
source: orange-tsai
source_url: https://blog.orange.tw/about/index.html
title: "About | Orange Tsai"
author: "Orange Tsai"
published: 2024-08-12T20:35:52.000Z
description: "Hi, I am Orange, currently the Principal Security Researcher at DEVCORE, and the core member of CHROOT Security Group in Taiwan. I am a RCE enthusiast and mainly focus on Web and Application Security."
---

Hi, I am Orange, currently the Principal Security Researcher at [DEVCORE](https://devco.re/), and the core member of [CHROOT Security Group](https://hitcon.org/) in Taiwan. I am a [RCE enthusiast](https://blog.orange.tw/about/index.html#Selected-RCEs) and mainly focus on Web and Application Security. My research has received several [hacking awards](https://blog.orange.tw/about/index.html#Selected-Honors) and has been accepted by numerous [security conferences](https://blog.orange.tw/talks/).

You can find me on ,  and .

## [Selected Honors](https://blog.orange.tw/about/index.html\#Selected-Honors "Selected Honors") Selected Honors

- 2025 — Author of **Phrack #72**: A 40th Anniversary Release of [Phrack Magazine](https://phrack.org/)!
- 2024 — **1st** of Top 10 Web Hacking Techniques for research of [Confusion Attacks](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024)
- 2024 — 4th of Top 10 Web Hacking Techniques for research of [WorstFit Attack](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024)
- 2022 — **Champion** of Pwn2Own Toronto
- 2021 — **Winner** of Pwnie Awards — “Best Server-Side Bug” for [Exchange Server RCEs](https://blog.orange.tw/about/index.html#)
- 2021 — 3rd of Top 10 Web Hacking Techniques for [Exchange Server RCEs](https://portswigger.net/research/top-10-web-hacking-techniques-of-2021)
- 2021 — **Champion** of Pwn2Own Vancouver
- 2021 — 28th of Top 100 Microsoft Most Valuable Security Researchers
- 2019 — **Winner** of Pwnie Awards — “Best Server-Side Bug” for [SSL VPN RCEs](https://blog.orange.tw/about/index.html#)
- 2019 — 8th of Top 10 Web Hacking Techniques for research of [SSL VPN RCEs](https://portswigger.net/research/top-10-web-hacking-techniques-of-2019)
- 2019 — 4th of Top 10 Web Hacking Techniques for research of [Jenkins RCEs](https://portswigger.net/research/top-10-web-hacking-techniques-of-2019)
- 2019 — 2nd of DEFCON CTF Final as team [HITCON x BFKinesiS](https://blog.orange.tw/about/index.html#)
- 2018 — **1st** of Top 10 Web Hacking Techniques for research of [Breaking Parser Logics](https://portswigger.net/research/top-10-web-hacking-techniques-of-2018)
- 2017 — **1st** of Top 10 Web Hacking Techniques for research of [A New Era Of SSRF](https://portswigger.net/research/top-10-web-hacking-techniques-of-2017)
- 2017 — 2nd of DEFCON CTF Final as team [HITCON](https://ctftime.org/team/8299/)
- 2016 — **1st** of Boston Key Party CTF as team [HITCON](https://ctftime.org/team/5160/)
- 2015 — **1st** of 0CTF Final as team [217](https://ctftime.org/team/5160/)
- 2014 — 2nd of DEFCON CTF Final as team [HITCON](https://ctftime.org/team/8299/)
- 2014 — **1st** of 台灣大專院校資安技能金盾獎
- 2012 — **1st** of 台灣大專院校資安技能金盾獎
- 2011 — **1st** of 台灣大專院校資安技能金盾獎
- 2009 — **1st** of HITCON Wargame Contest

## [Selected RCEs](https://blog.orange.tw/about/index.html\#Selected-RCEs "Selected RCEs") Selected RCEs

### [2024](https://blog.orange.tw/about/index.html\#2024 "2024") 2024

- **Microsoft Excel**
  - [CVE-2024-49026](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-49026) \- We proposed the [WorstFit Attack](https://worst.fit/), which can inject arbitrary arguments into Microsoft Excel, leading to RCE.
- **Apache HTTP Server**
  - We proposed [several attacks](https://blog.orange.tw/2024/08/confusion-attacks-en.html) and rewarded with multiple CVEs.
- **PHP**
  - [CVE-2024-4577](https://blog.orange.tw/2024/06/cve-2024-4577-yet-another-php-rce.html) \- An unauthorized Argument Injection vulnerability.

### [2022](https://blog.orange.tw/about/index.html\#2022 "2022") 2022

- **Sonos One Speaker**
  - An unauthorized RCE, [chained](http://10.26.0.34:4000/data/2023-A-3-Years-Tale-of-Hacking-a-Pwn2Own-Target.pdf) from Information Leakage (CVE-2023-27353) to Stack Overflow (CVE-2023-27355).
- **WSO2 Identity Server**
  - [CVE-2022-29464](https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2022/WSO2-2021-1738/) \- An unauthorized Arbitrary File Upload vulnerability.

### [2021](https://blog.orange.tw/about/index.html\#2021 "2021") 2021

- **Microsoft Exchange Server**
  - [ProxyLogon](https://blog.orange.tw/2021/08/proxylogon-a-new-attack-surface-on-ms-exchange-part-1.html) \- An unauthorized RCE chained with 3 bugs from SSRF (CVE-2021-26855) to Arbitrary File Writing (CVE-2021-27065).
  - [ProxyShell](https://www.zerodayinitiative.com/blog/2021/8/17/from-pwn2own-2021-a-new-attack-surface-on-microsoft-exchange-proxyshell) \- An unauthorized RCE chained with 3 bugs from SSRF (CVE-2021-34473) to Arbitrary File Writing (CVE-2021-31207).
- **Samba**
  - [CVE-2021-44142](https://www.samba.org/samba/security/CVE-2021-44142.html) \- An Out-of-Bounds Read/Write vulnerability.
- **Neta Talk**
  - [CVE-2022-23122](https://www.zerodayinitiative.com/advisories/ZDI-22-529/) \- An unauthorized Out-of-Bounds Write vulnerability.
  - [CVE-2022-23123](https://www.zerodayinitiative.com/advisories/ZDI-22-528/) \- An unauthorized Out-of-Bounds Read vulnerability.
- **Western Digital**
  - We chained Neta Talk bugs, and then [pwned Western Digital NAS](https://www.zerodayinitiative.com/blog/2021/11/1/pwn2ownaustin) in Pwn2own Austin 2021.
- **Sonos One Speaker**
  - [CVE-2022-24046](https://www.zerodayinitiative.com/advisories/ZDI-22-260/) \- An unauthorized Integer Underflow vulnerability.
- **PHPWind**
  - An unauthorized RCE, [chained](https://blog.orange.tw/2021/02/a-journey-combining-web-and-binary-exploitation.html) from PRNG Prediction to PHP Use-After-Free (CVE-2015-0237)

### [2020](https://blog.orange.tw/about/index.html\#2020 "2020") 2020

- **Microsoft Exchange Server**
  - [CVE-2020-17117](https://msrc.microsoft.com/update-guide/en-us/vulnerability/CVE-2020-17117) \- A Command Injection in Exchange PowerShell Remoting.
- **Ivanti MobileIron**
  - [CVE-2020-15505](https://www.ivanti.com/blog/mobileiron-security-updates-available) \- An unauthorized Hessian Deserialization vulnerability.
- **Facebook Bug Bounty**
  - Facebook held an unpatched MobileIron instance, and we then [hacked](https://blog.orange.tw/2020/09/how-i-hacked-facebook-again-mobileiron-mdm-rce.html) it!

### [2019](https://blog.orange.tw/about/index.html\#2019 "2019") 2019

- **Twitter Bug Bounty**
  - Twitter held an unpatched SSL VPN instance, and we then [hacked](https://blog.orange.tw/2019/09/attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain.html) it!
- **Uber Bug Bounty**
  - Uber held several unpatched SSL VPN instances, and we then [hacked](https://blog.orange.tw/2019/07/attacking-ssl-vpn-part-1-preauth-rce-on-palo-alto.html) it!
- **Tesla Bug Bounty**
  - Tesla held several unpatched SSL VPN instances, and we then hacked it!
- **Riot Games Bug Bounty**
  - Riot Games held an unpatched SSL VPN instance, and we then hacked it!
- **Netflix Bug Bounty**
  - Program keeps the report private.
- **Pulse Secure SSL VPN**
  - An unauthenticated RCE, chained from Arbitrary File Reading (CVE-2019-11510) to Command Injection (CVE-2019-11539).
- **Fortinet FortiGate SSL VPN**
  - An unauthenticated RCE, chained from Arbitrary File Reading (CVE-2018-13379) to Heap Overflow (CVE-2018-13383).
- **Palo Alto GlobalProtect SSL VPN**
  - CVE-2017-15944 - An unauthenticated Format String vulnerability.
- **Jenkins**
  - An unauthenticated RCE, chained with 3 bugs from ACL Bypass (CVE-2018-1000861) to [exploit Metaprogramming](https://blog.orange.tw/2019/02/abusing-meta-programming-for-unauthenticated-rce.html).
- **Hinet GPON Modem**
  - An unauthenticated RCE, [chained](https://blog.orange.tw/2019/11/HiNet-GPON-Modem-RCE.html) from ACL Bypass to Command Injection (CVE-2019-13411).

### [2018](https://blog.orange.tw/about/index.html\#2018 "2018") 2018

- **Nuxeo**
  - An unauthenticated RCE, chained with 4 bugs from ACL Bypass to EL Injection.
- **Amazon Bug Bounty**
  - Amazon held an unpatched instance, and we then [hacked](https://blog.orange.tw/2018/08/how-i-chained-4-bugs-features-into-rce-on-amazon.html) it!

### [2017](https://blog.orange.tw/about/index.html\#2017 "2017") 2017

- **GitHub Bug Bounty**
  - An unauthenticated RCE, [chained with 4 bugs](https://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html) from Blind SSRF to unsafe deserialization on GitHub Enterprise.
- **Imgur Bug Bounty**
  - Imgur held an unpatched GitHub Enterprise instance, and we then [hacked](https://hackerone.com/reports/206227) it!

### [2016](https://blog.orange.tw/about/index.html\#2016 "2016") 2016

- **Uber Bug Bounty**
  - The rider site `rider.uber.com` is vulnerable to [Jinja2 SSTI](https://blog.orange.tw/2016/04/bug-bounty-uber-ubercom-remote-code_7.html).
- **Accellion File Transfer**
  - An unauthenticated RCE, chained from SQL Injection (CVE-2016-2351) to Local Root (CVE-2016-2352).
- **Facebook Bug Bounty**
  - Facebook held an unpatched Accellion instance, and we then [hacked](https://blog.orange.tw/2016/04/bug-bounty-how-i-hacked-facebook-and-found-someones-backdoor-script.html) it!

### [2013](https://blog.orange.tw/about/index.html\#2013 "2013") 2013

- **Yahoo! Bug Bounty**
  - Several `*.login.yahoo.com` instances are vulnerable to a Struts2 vulnerability, and we [hacked](https://blog.orange.tw/2013/11/yahoo-bug-bounty-part-2-loginyahoocom.html) it!

### [2012](https://blog.orange.tw/about/index.html\#2012 "2012") 2012

- **Microsoft Internet Explorer**
  - [CVE-2012-4775](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2012/ms12-071) \- A Use-After-Free vulnerability, which is also my first CVE!