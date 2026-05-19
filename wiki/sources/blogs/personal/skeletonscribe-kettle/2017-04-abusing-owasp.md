---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2017/04/abusing-owasp.html
title: "Skeleton Scribe: Abusing OWASP with 'Insufficient Attack Protection'"
description: "I have no love for drama but over the last couple of years I’ve witnessed some shameless abuse of OWASP by commercial interests and feel it..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Monday, 24 April 2017

### Abusing OWASP with 'Insufficient Attack Protection'

I have no love for drama but over the last couple of years I’ve witnessed some shameless abuse of OWASP by commercial interests and feel it's important to call this out.

The latest draft of the [OWASP TOP 10](https://github.com/OWASP/Top10/raw/master/2017/OWASP%20Top%2010%20-%202017%20RC1-English.pdf) ‘Most Critical Web Application Security Risks’ added a new entry at A7, titled ‘Insufficient Attack Protection’. It claims that failing to detect and respond to attacks is a critical risk.

This is a surprising and distinctly out of place addition to the top 10; every other entry is a serious vulnerability that poses a notable risk by itself, whereas failure to detect attacks is only hazardous when combined with a real vulnerability.

Furthermore, addressing any other entry in the top 10 provides a clear net positive to a webapp’s security posture, whereas complying with A7 can easily cause a net harm. Complying with A7 makes it extremely awkward to run an accessible bug bounty program, since it will hinder researchers trying to help you out. It also increases your attack surface (much like antivirus software) and introduces the risk of denial of service attacks by spoofing attacks from other users.

I’m [not](https://twitter.com/sirdarckcat/status/855860484377063424) the [only](https://twitter.com/kkotowicz/status/851753428107898880) one [in](https://twitter.com/strawp/status/851764135704571904) the [community](https://twitter.com/slekies/status/851757526139973634) who thinks Insufficient Attack Protection has no place in the top 10 - [a poll by @thornmaker](https://twitter.com/thornmaker/status/852263747267710977) found 80% of 110 respondents thought it should be removed.

At this point, you might be wondering where A7 came from. According to a contributer, it was ["](http://lists.owasp.org/pipermail/owasp-topten/2017-April/001422.html) [suggested by Contrast Security and \*only\* by Contrast Security"](http://lists.owasp.org/pipermail/owasp-topten/2017-April/001422.html).

I wonder why Contrast Security made this suggestion? Well, we can find a clue on their website - they’ve already started using A7 to flog ‘Contrast Protect’, their shiny attack protection solution:

> A7: Insufficient Attack Protection. This new requirement means that applications need to detect, prevent, and respond to both manual and automated attacks. \[…\] [Contrast Protect effectively blocks attacks](https://www.contrastsecurity.com/runtime-application-self-protection-rasp) by injecting the protection directly into the application where it can take advantage of the full application context.

[https://www.contrastsecurity.com/security-influencers/two-new-vulnerabilites-added-to-the-owasp-top-10](https://www.contrastsecurity.com/security-influencers/two-new-vulnerabilites-added-to-the-owasp-top-10)

Still, perhaps I shouldn’t rush to assume Contrast Security is acting in bad faith and abusing the OWASP brand name to sell a product. It’s not like they’ve done anything like this before is it?

In 2015 [Contrast/Aspect](http://www.aspectsecurity.com/contrast-security) released a tool to evaluate vulnerability scanners dubbed “ [OWASP Benchmark](https://www.owasp.org/index.php/Benchmark)”. This is much lower profile than the OWASP Top 10, but I work for a web scanner vendor myself so it caught my attention. Just like the new OWASP Top 10, there was something a bit odd about it - it ranked Contrast’s scanner vastly higher than all the competition, something they [made sure to point out](https://www.contrastsecurity.com/owasp-benchmark) in marketing materials.

Here’s what Simon Bennets, the OWASP project leader for ZAP had to say:

> Here we have a company that leads an OWASP project that just happens to show that their offering in this area appears to be \_significantly\_ better than any of the competition. Their recent press release stresses that its an OWASP project, make the most of the fact that the US DHS helped fund it but make no mention of their role in developing it.

[http://lists.owasp.org/pipermail/owasp-leaders/2015-September/015120.html](http://lists.owasp.org/pipermail/owasp-leaders/2015-September/015120.html)

Simon's post caused extensive discussion on the OWASP leaders mailing list, eventually leading to Jim Manico (an OWASP board member at the time) [calling for the project to be demoted to 'incubator' status](https://lists.owasp.org/pipermail/owasp-board/2015-December/016724.html), in order to reflect the project's immaturity. The project is still in the incubator status. This hasn’t stopped Gartner from using it to compare scanning vendors, so I guess Contrast still got their money’s worth.

All in all I think it’s pretty clear why Insufficient Attack Protection has suddenly appeared. Perhaps the OWASP Top 10 should be demoted to incubator status too :-)

\- [albinowax](http://skeletonscribe.net/)

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[14:31](https://www.skeletonscribe.net/2017/04/abusing-owasp.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=98773771505067224&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=98773771505067224&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=98773771505067224&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=98773771505067224&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=98773771505067224&target=pinterest "Share to Pinterest")

#### 9 comments:

1. ![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjs8RC6ol0w7c11jTZEF3wzfEkT0MsWVRPJEIBMabusYP0G7hJWvDrE_P-eXQ2KQhxArf09WqfL9loU6EEFj2SYDLvG6-59WsSV0faPmSYEgGvifM-CP7U6rPRrv1e81pE/s45-c/McCuneMain.jpg)



[Rory McCune](https://www.blogger.com/profile/02041778936182391744)[24 April 2017 at 17:18](https://www.skeletonscribe.net/2017/04/abusing-owasp.html?showComment=1493050734691#c8301825674430989884)



I think it's important that this point gets debated as obviously changing something like the OWASP top 10 can have quite a big impact given the number of standards that rely on it.



That said I'm not sure I see the concept of having applications actively protect themselves (which I think is the core of what A7 suggests) as a wholly negative point.



We already have some level of active protection with things like account lockout, greylisting etc, so it's not really a new paradigm.



On the points you mention, well bug bounty participants are, like pentesters, pseudo bad guys, so if we're saying it makes our lives more difficult, surely that's a good thing?



And whilst it's definitely true to say that badly designed active defence mechanisms could pose a risk to availability, that to me is more an argument for well designed controls than an argument to scrap the concept entirely.



Same with increased attack surface, when companies started introducing 2FA onto their sites, that increased the attack surface of their authentication stacks and bugs were found in those implementations, but that's not necessarily an argument against 2FA (or at least not one I came across often).



Overall the reason I think that having some focus on this would be good, is that it seems daft to me that applcations, which have good contextual information about what attack traffic looks like (far better context than a WAF or IPS could have), don't defend themselves against obvious attacks. I test web apps. week in week out and it seems like a missed opportunity for the application not to take action against what is obviously attack traffic, providing useful data to defenders and slowing down the rate of attack.

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8301825674430989884)



Replies



![](https://www.blogger.com/img/blogger_logo_round_35.png)



[buherator](https://www.blogger.com/profile/07014603847076182569)[25 April 2017 at 08:37](https://www.skeletonscribe.net/2017/04/abusing-owasp.html?showComment=1493105858845#c4087063968426272674)



Another reason A7 is awful is that it mixes different concepts, like rate limiting/account lockout (which can be good practices as you note) with magic software unicorns that can detect "atypical input" and "unusual usage patterns". (Such inconsistencies are there in other points too, which is a weakness of the project in general, but A7 bring this to a new, harmful level)

[Delete](https://www.blogger.com/comment/delete/8601133831815091251/4087063968426272674)



Replies







Reply

![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjs8RC6ol0w7c11jTZEF3wzfEkT0MsWVRPJEIBMabusYP0G7hJWvDrE_P-eXQ2KQhxArf09WqfL9loU6EEFj2SYDLvG6-59WsSV0faPmSYEgGvifM-CP7U6rPRrv1e81pE/s45-c/McCuneMain.jpg)



[Rory McCune](https://www.blogger.com/profile/02041778936182391744)[25 April 2017 at 12:45](https://www.skeletonscribe.net/2017/04/abusing-owasp.html?showComment=1493120746440#c8986966918914393583)



I'd agree that consistency in recommendations is important for people to be able to apply a standard, but I'm not sure I'd call recognizing "atypical input" as a magic software unicorn. In many cases it's relatively easy for an application to define expected/acceptable input and therefore to define what atypical input looks like.



For example for an application which is used by UK consumers and has name fields, certain character classes are valid and certain ones are not. If a user starts filling name fields with HTML/JavaScript code, it's a fair bet that their input is atypical, and an application could defend itself by reacting to that atypical input.

[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8986966918914393583)



Replies







Reply

![](https://www.blogger.com/img/blogger_logo_round_35.png)



[Unknown](https://www.blogger.com/profile/17142689664870724538)[30 April 2017 at 22:59](https://www.skeletonscribe.net/2017/04/abusing-owasp.html?showComment=1493589548156#c2558222699961260125)



Yes, and those input validation protections would be covered by the "Injection" or the "XSS" OWASP TOP 10 points (which, btw, are both the exact same and should have been collapsed into the same, imho).

"Insufficient Attack Protection" is true and applicable for every possible attack vector if you think of it.

A7 reads A LOT like OWASP was being lazy and ends up recommending something like "do things securely (tm)" which doesn't really say anything. Actually, why don't we replace all of the TOP10 by exactly that? "A\* Do it well!".



Also, wasn't OWASP's TOP10 supposed to be a rundown of the most commonly found vulnerabilities so that you could protect against most the the attacks and not an attempt to cover everything that exists? This shift in focus says one thing: it's gone $political$. As such, should no longer be trusted.

[Delete](https://www.blogger.com/comment/delete/8601133831815091251/2558222699961260125)



Replies







Reply





Reply

2. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



[Eduardo](https://www.blogger.com/profile/15516448229822283514)[24 April 2017 at 19:03](https://www.skeletonscribe.net/2017/04/abusing-owasp.html?showComment=1493056982164#c545081626643183581)



Here is the net negative from "automatic protection" or pretty much just any WAF. They make finding the vulnerabilities harder for the good guys.



This means:

1\. Mitigations are imperfect and bypassable by definition.

2\. It will be harder for "good guys" to find vulnerabilities.

3\. Less vulnerabilities will be fixed in the absolute.



As a result, applications will end up worse and all that while profiting vendors. FFS..

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/545081626643183581)



Replies



![](https://resources.blogblog.com/img/blank.gif)



[albinowax](http://skeletonscribe.net/)[25 April 2017 at 11:09](https://www.skeletonscribe.net/2017/04/abusing-owasp.html?showComment=1493114940236#c9124366277033054666)



Well put, I absolutely agree. This is a core reason why A7 is such a terrible recommendation.

[Delete](https://www.blogger.com/comment/delete/8601133831815091251/9124366277033054666)



Replies







Reply

![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjs8RC6ol0w7c11jTZEF3wzfEkT0MsWVRPJEIBMabusYP0G7hJWvDrE_P-eXQ2KQhxArf09WqfL9loU6EEFj2SYDLvG6-59WsSV0faPmSYEgGvifM-CP7U6rPRrv1e81pE/s45-c/McCuneMain.jpg)



[Rory McCune](https://www.blogger.com/profile/02041778936182391744)[25 April 2017 at 12:42](https://www.skeletonscribe.net/2017/04/abusing-owasp.html?showComment=1493120557886#c300631620700476518)



For finding vulnerabilities for the "good guys" I've long recommended reviewing applications in test environments where protections can be disabled to allow for the use of automated scanning tools.



Testing in live is rarely optimal and, you'd hope, that most companies are capable of standing up a representative test enviornment, to allow for unfettered testing to be completed.



On your point about mitigations being imperfect, well all security controls are in some way imperfect, but that doesn't mean that we don't apply them, does it?



And the bit around vendors I don't really get. The intention is for applications to defend themselves, that's the way it reads (to me) and that is, as far as I'm aware, the intent.

[Delete](https://www.blogger.com/comment/delete/8601133831815091251/300631620700476518)



Replies







Reply

![](https://www.blogger.com/img/blogger_logo_round_35.png)



[Eduardo](https://www.blogger.com/profile/15516448229822283514)[28 April 2017 at 05:00](https://www.skeletonscribe.net/2017/04/abusing-owasp.html?showComment=1493352049059#c1407046586992929778)



Look, the simplest way of looking at this is that no matter what is said, as soon as you install a WAF, you will immediately see less vulnerabilities, and you will stop learning how to make your software safer.



Of course you could disable the WAF from some IPs, you could give trusted researchers access to WAFless test versions, but in reality that doesn't effectively happen even for pentesters and auditors.



As a result, the 100 hours the pentesters bill you for, are used bypassing dumb mitigations that make no difference to an attacker but consume time from the pentest instead of analyzing other parts of the application. No matter how you think about it, finding vulnerabilities becomes more expensive. Exploiting them too, but still faaaar within the attackers budget. But faaaar below the pentesters'.



We know that fixing vulnerabilities one by one doesn't work. But we know that learning from them once they happen twice or more and then preventing them for ever in the framework/library works and scales.



But instead, WAFs/RASPs/etc are going the route of hiding the sickness by catching and treating the symptoms. Leaving the application sicker, weaker and more complex, just there waiting for it to be attacked by the next guy that knows how, and had the motivation to step over these silly mitigations.



No matter how smart the attacker is, if there are 10 times less bugs, it will be 10 times harder to find a bug that the attacker needs. With a strategy that depends on mitigations the difficulty is constant independent of the application intrinsic security. It won't get better, it will only get worse over time.

[Delete](https://www.blogger.com/comment/delete/8601133831815091251/1407046586992929778)



Replies







Reply





Reply

3. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



[Unknown](https://www.blogger.com/profile/01927428147246609281)[26 June 2017 at 15:27](https://www.skeletonscribe.net/2017/04/abusing-owasp.html?showComment=1498487237164#c8893744275355219646)



I know this is an "old" thread, but in my very recent past life working for a pure-play application security vendor (SAST and DAST testing), we regularly tested apps while being whitelisted or in a test environment with no network-based protection mechanisms (WAF, IPS, etc). Our line to the customer was that we want to test the security of the app, not the tools surrounding the app. It is definitely something that can be accomplished.



I understand the issue around bug bounty programs, however, because those are definitely less conducive to whitelisting and/or removing protective mechanisms.

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8893744275355219646)



Replies







Reply


Add comment

Post a comment

Comment with your Google Account if you’d like to be able to manage your comments in the future. If you comment anonymously, you won’t be able to edit or delete your comment. [Learn more](https://www.blogger.com/go/anonymouscommentshelp)

![User Avatar](https://resources.blogblog.com/img/anon36.png)

Comment as:

Select profile:

Google Account

Anonymous

Name/URL



Edit

Enter comment

Publish

This site is protected by reCAPTCHA and the Google [privacy policy](https://policies.google.com/privacy) and [Terms of Service](https://policies.google.com/terms) apply.

Load more...

[Newer Post](https://www.skeletonscribe.net/2017/11/h1-212-ctf-writeup.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2016/08/reviewing-bug-bounties-hackers.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/98773771505067224/comments/default)

**Who**

- [James Kettle](http://skeletonscribe.net/)

**Contact**

- [@albinowax](https://twitter.com/albinowax)
- xawonibla@gmail.com (personal)

- elttek.semaj@portswigger.net (work)

- albinowax on [freenode](https://webchat.freenode.net/?randomnick=0&channels=#slackers)

## Quality content

- [magic mac's blog](https://www.brokenbrowser.com/)
- [lcamtuf's blog](http://lcamtuf.blogspot.co.uk/)
- [.mario's slides](http://www.slideshare.net/x00mario/presentations)
- [sirdarckcat's blog](https://sirdarckcat.blogspot.co.uk/)
- [irsdl's blog](https://soroush.secproject.com/blog/)
- [Gareth Heyes' blog](http://www.thespanner.co.uk/)
- [kuza's blog](http://kuza55.blogspot.co.uk/)
- [Shared Fuzzer](http://shazzer.co.uk/)
- [HTML5 Security Cheat Sheet](http://html5sec.org/)
- [unexpected theology](http://davidkettle.org.uk/)

## Archive

- [Practical HTTP Host header attacks](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html)
- [Phrack ebook](https://www.skeletonscribe.net/2011/12/phrack-ebook.html)
- [Reviewing bug bounties - a hacker's perspective](https://www.skeletonscribe.net/2016/08/reviewing-bug-bounties-hackers.html)
- [h1-212 CTF Writeup](https://www.skeletonscribe.net/2017/11/h1-212-ctf-writeup.html)
- [Abusing OWASP with 'Insufficient Attack Protection'](https://www.skeletonscribe.net/2017/04/abusing-owasp.html)
- [X-Frame-Options gotcha](https://www.skeletonscribe.net/2012/06/x-frame-options-sameorigin-warning.html)
- [Hackxor hacking game beta](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html)
- [Simulating targets for XSS/CSRF attacks in hacking games](https://www.skeletonscribe.net/2011/05/simulating-targets-for-xsscsrf-attacks.html)
- [Sparse Bruteforce Addon Detection](https://www.skeletonscribe.net/2011/07/sparse-bruteforce-addon-scanner.html)
- [Chronofeit Phishing](https://www.skeletonscribe.net/2010/12/chronofeit-phishing.html)

|     |     |
| --- | --- |
|  |  |

|     |     |
| --- | --- |
|  |  |

Powered by [Blogger](https://www.blogger.com/).