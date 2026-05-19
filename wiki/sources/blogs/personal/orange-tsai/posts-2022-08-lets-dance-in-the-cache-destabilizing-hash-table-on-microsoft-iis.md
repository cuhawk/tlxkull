---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2022-08-lets-dance-in-the-cache-destabilizing-hash-table-on-microsoft-iis/
title: "Let's Dance in the Cache - Destabilizing Hash Table on Microsoft IIS! | Orange Tsai"
author: "Orange Tsai"
published: 2022-08-17T16:00:00.000Z
description: "Hi, this is my fifth time speaking at Black Hat USA and DEFCON. You can get the slide copy and video there: Let’s Dance in the Cache - Destabilizing Hash Table on Microsoft IIS (slides) Let’s Dan"
---

* * *

![preview](https://blog.orange.tw/posts/2022-08-lets-dance-in-the-cache-destabilizing-hash-table-on-microsoft-iis/d9a302d219bb7c0e-01.png)

Hi, this is my fifth time speaking at [Black Hat USA](https://www.blackhat.com/us-22/briefings/schedule/index.html#lets-dance-in-the-cache---destabilizing-hash-table-on-microsoft-iis-27199) and [DEFCON](https://forum.defcon.org/node/241837). You can get the slide copy and video there:

- [Let’s Dance in the Cache - Destabilizing Hash Table on Microsoft IIS (slides)](https://i.blackhat.com/USA-22/Wednesday/US-22-Tsai-Lets-Dance-in-the-Cache-Destabilizing-Hash-Table-on-Microsoft-IIS.pdf)
- [Let’s Dance in the Cache - Destabilizing Hash Table on Microsoft IIS (video - TBD)](https://blog.orange.tw/posts/2022-08-lets-dance-in-the-cache-destabilizing-hash-table-on-microsoft-iis/#TBD)

As the most fundamental Data Structure in Computer Science, Hash Table is extensively used in Computer Infrastructures, such as Operating Systems, Programming Languages, Databases, and Web Servers. Also, because of its importance, Microsoft has designed its own Hash Table algorithm from a very early stage, and applied it heavily to its web server, IIS.

Since IIS does not release its source code, I guess the algorithm implementation details should be an unexplored area to discover bugs. Therefore, **this research mainly focuses on the Hash Table implementation and its usage**. We also look into the Cache mechanism because most of the Hash Table usages in IIS are Cache-Related!

Because most of the details are in the slides, please forgive me this time for this brief write-ups instead of a full blog.

- [CVE-2022-22025](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-22025) \- Microsoft IIS Hash-Flooding DoS
- [CVE-2022-22040](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-22040) \- Microsoft IIS Cache Poisoning Attack
- [CVE-2022-30209](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-30209) \- Microsoft IIS Authentication Bypass

_P.S. All vulnerabilities addressed in this blog have been reported responsibly to Microsoft and patched in July 2022._

# [1. IIS Hash-Flooding DoS](https://blog.orange.tw/posts/2022-08-lets-dance-in-the-cache-destabilizing-hash-table-on-microsoft-iis/\#1-IIS-Hash-Flooding-DoS "1. IIS Hash-Flooding DoS") 1\. IIS Hash-Flooding DoS

It’s hard to imagine that we can still see such a classic Algorithmic Complexity Attack as Hash-Flooding Attack in IIS in 2022. Although Microsoft has configured a thread deleting outdated records every 30 seconds to mitigate the attack, we still found a key-splitting bug in the implementation to **amplify our power by over 10 times to defeat the guardian by zero hashes**. Through this bug we can **make a default installed IIS Server unresponsive** with about 30 connections per second!

Because this bug also qualifies for the [Windows Insider Preview Bounty Program](https://www.microsoft.com/en-us/msrc/bounty-windows-insider-preview), we also rewarded $30,000 for this DoS. This is the maximum bounty for the category of Denial-of-Service!

You can check the full demo video here:

YouTube

# [2. IIS Cache Poisoning Attack](https://blog.orange.tw/posts/2022-08-lets-dance-in-the-cache-destabilizing-hash-table-on-microsoft-iis/\#2-IIS-Cache-Poisoning-Attack "2. IIS Cache Poisoning Attack") 2\. IIS Cache Poisoning Attack

Compared with other [marvelous Cache Poisoning research](https://portswigger.net/research/practical-web-cache-poisoning), this one is relatively plain. The bug is found in the component of Output Caching, the module responsible for caching dynamic responses to reduce expensive database or filesystem access on web stacks.

Output Caching uses a bad Query String parser that only takes the first occurrence as the Cache-Key when Query String keys are duplicated. This behavior is actually not a problem independently. However, it’s a trouble in the view of the whole architecture with the backend, [ASP.NET](http://asp.net/). The backend concatenates the value of all repeated keys together, which leads to an inconsistency between parser behaviors. Therefore, **a classic HTTP Parameter Pollution can make IIS cache the wrong result**!

# [3. IIS Authentication Bypass](https://blog.orange.tw/posts/2022-08-lets-dance-in-the-cache-destabilizing-hash-table-on-microsoft-iis/\#3-IIS-Authentication-Bypass "3. IIS Authentication Bypass") 3\. IIS Authentication Bypass

This may be the most interesting bug of this talk. LKRHash is a Hash Table algorithm designed and [patented](https://patents.google.com/patent/US6578131) by Microsoft in 1997. It’s based on [Linear Hashing](https://en.wikipedia.org/wiki/Linear_hashing) and created by [Paul Larson](https://en.wikipedia.org/wiki/Paul_Larson) of Microsoft Research, Murali Krishnan and George Reilly of the IIS team.

LKRHash aims to build a scalable and high-concurrent Hash Table under the multithreading and multi-core environment. The creators put a lot of effort into making this implementation portable, flexible and customizable to adapt to multiple products across Microsoft. An application can define its own Table-Related functions, such as the Hash Function, the Key Extracting Function, or the Key Comparing Function. This kind of extensibility creates a bunch of opportunities for vulnerability mining. So, under this context, we cares more about the relationship between the records, the keys, and the functions.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>``` | ```<br>CLKRHashTable::CLKRHashTable(<br>    this,<br>    "TOKEN_CACHE",   // An identifier for debugging<br>    pfnExtractKey,   // Extract key from record<br>    pfnCalcKeyHash,  // Calculate hash signature of key<br>    pfnEqualKeys,    // Compare two keys<br>    pfnAddRefRecord, // AddRef in FindKey, etc<br>    4.0,             // Bound on the average chain length.<br>    1,               // Initial size of hash table.<br>    0,               // Number of subordinate hash tables.<br>    0                // Allow multiple identical keys?<br>);<br>``` |

Because “Logon” is an expensive operation, to improve the performance, IIS cached all tokens for password-based authentications, such as Basic Authentication by default, and the bug we found this time is located in the logic of the key-comparing function when a collision occurs.

If a login attempt whose hash hits a key that is already in the cache, LKRHash enters the application-specific `pfnEqualKeys` function to determine whether the key is correct or not. The application-specific logic of `TokenCacheModule` is as follows:

Twitter Embed

> My favorite bug among the vulnerabilities I presented today! 😆
>
> The original intent was to compare the password. However, the developer copy-and-pasted the code but forgot to replace the variable name. That leads to the Authentication Bypass on IIS. [pic.twitter.com/NLDDLQNYX2](https://t.co/NLDDLQNYX2)
>
> — Orange Tsai 🍊 (@orange\_8361) [August 10, 2022](https://twitter.com/orange_8361/status/1557504677050478594?ref_src=twsrc%5Etfw)

As the logic compares several parts to make the decision, it’s weird why IIS compares the username twice.

I guess the original intent was to compare the password. However, the developer copy-and-pasted the code but forgot to replace the variable name. That leads to that **an attacker can reuse another user’s logged-in token with random passwords**.

To build the smallest PoC to test your own, you can create a testing account and configure the Basic Authentication on your IIS.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br># add a test account, please ensure to remove that after testing<br>> net user orange test-for-CVE-2022-30209-auth-bypass /add<br># the source of login is not important, this can be done outside IIS.<br>> curl -I -su 'orange:test-for-CVE-2022-30209-auth-bypass' 'http://<iis>/protected/' | findstr HTTP<br>HTTP/1.1 200 OK<br>``` |

Under the attacker’s terminal:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>``` | ```<br># script for sanity check<br>> type test.py<br>def HashString(password):<br>    j = 0    <br>    for c in map(ord, password):<br>        j = c + (101*j)&0xffffffff<br>    return j<br>assert HashString('test-for-CVE-2022-30209-auth-bypass') == HashString('ZeeiJT')<br># before the successful login<br>> curl -I -su 'orange:ZeeiJT' 'http://<iis>/protected/' | findstr HTTP<br>HTTP/1.1 401 Unauthorized<br># after the successful login<br>> curl -I -su 'orange:ZeeiJT' 'http://<iis>/protected/' | findstr HTTP<br>HTTP/1.1 200 OK<br>``` |

As you can see, the attacker can log into the user `orange` with another password whose hash is the same as the original one.

However, it’s not easy to collide the hash. The probability of each attempt is only worth 1/2^32 because the hash is a 32-Bit Integer, and the attacker has no way to know the hash of existing cache keys. It’s a ridiculous number to make exploiting this bug like playing a lottery. The only pro is that the attempt costs nothing, and you have unlimited tries!

To make this bug more practical, we proposed several ways to win the lottery, such as:

1. Increase the odds of the collision - LKRHash combined LCGs to scramble the result to make the hash more random. However, we can lower the key space because the LCG is not one-to-one mapping under the 32-Bit Integer. There must be results that will never appear so that we can pre-compute a dictionary that excludes the password whose hash is not in the results and **increase the success rate by 13% at least**!
2. Regain the initiative - By understanding the root cause, we brainstorm several use cases that **can cache the token in memory forever and no longer wait for user interaction**, such as the IIS feature [Connect As](https://docs.microsoft.com/en-us/troubleshoot/developer/webapps/iis/www-authentication-authorization/understanding-identities) or leveraging software design patterns.

We have also proved this attack works naturally on Microsoft Exchange Server. By leveraging the default activated `Exchange Active Monitoring` service, we can enter `HealthMailbox`‘s mailbox without passwords! This authentication-less account hijacking is useful for further exploitations such as phishing or chaining another post-auth RCE together!

![](https://blog.orange.tw/posts/2022-08-lets-dance-in-the-cache-destabilizing-hash-table-on-microsoft-iis/e094d7f42a2fd662-02.png)

# [Timeline](https://blog.orange.tw/posts/2022-08-lets-dance-in-the-cache-destabilizing-hash-table-on-microsoft-iis/\#Timeline "Timeline") Timeline

- Mar 16, 2022 - We reported the IIS Cache Poisoning to Microsoft through the MSRC portal.
- Apr 09, 2022 - We reported the IIS Hash-Flooding DoS to Microsoft through the MSRC portal.
- Apr 10, 2022 - We reported the IIS Authentication Bypass to Microsoft through the MSRC portal.
- Jul 12, 2022 - Microsoft fixed everything at July’s Patch Tuesday.

Twitter Widget Iframe