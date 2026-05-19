---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html
title: "Skeleton Scribe: Hackxor hacking game beta"
description: "EDIT: the final version of hackxor is out at http://hackxor.sourceforge.net I've just released a public beta of hackxor at http://sourcef..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Tuesday, 1 February 2011

### Hackxor hacking game beta

EDIT: the final version of hackxor is out at [http://hackxor.sourceforge.net](http://hackxor.sourceforge.net/)

I've just released a public beta of hackxor at [http://sourceforge.net/projects/hackxor](http://sourceforge.net/projects/hackxor/)

Hackxor is a webapp hacking game where players must locate and exploit vulnerabilities to progress through the story. Think WebGoat/DVWA but with a plot and a focus on realism&difficulty. Contains XSS, CSRF, SQLi, ReDoS, DOR, command injection, and many other vulnerabilities. Hackxor uses HTMLUnit to simulate victims loading emails you've sent them, so you need carefully crafted XSS payloads; not an alert('xss') in sight. The second half of the game is much much more difficult than webgoat/DVWA, and should even make the pros pause to think.

**This is a beta.** Unless you want to try it out and give some feedback, you might as well wait for the final release. It is complete in terms of the exploits and how they fit together, but the websites need polish. The final release will be in ~~May~~ April, and will have a few extra features such as a 'stealth' ranking based on how many triggers you set off, bruteforce prevention, and social engineering attacks on the player. Hopefully it will also be easier to install :)

**Feedback feedback feedback**

I'd like to know if you think any of the sites are too hard/easy, or illogical.

Please tell me if you find a way of gaining a shell on the server without using the final website (utrack). Any such vulnerability is intentional and needs to be fixed. People who report such vulnerabilities will appear in the credits (heh).

**Installation**

Download [hackxor](http://sourceforge.net/projects/hackxor/)

Install [VMWare player](https://www.vmware.com/tryvmware/?p=player).

Open the image in hackxor using VMware player.

Work out what the IP of hackxor is (try logging in with username:root pass:hackxor1 and typing ifconfig)

Configure your hosts file (/etc/hosts on linux) to redirect the following domains to the IP of hackxor: wraithmail, wraithbox, cloaknet, GGHB, rentnet, utrack.

Browse to wraithmail:8080 and login with username:algo password:smurf

**Game Rules**

You are free to use any webapp hacking technique, except bruteforcing passwords. This is simply because I haven't written the anti-password guessing code yet. The final version will have no rules.

I'll post updates [on twitter](http://twitter.com/albinowax)

Enjoy.

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[19:05](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6793557918502568622&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6793557918502568622&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6793557918502568622&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6793557918502568622&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6793557918502568622&target=pinterest "Share to Pinterest")

#### 8 comments:

1. ![](https://2.bp.blogspot.com/_mGvG5n_XWEU/S6v1juGeVUI/AAAAAAAAAAs/nT21Vd5zzx8/S45-s35/Picture%2B022.jpg)



[Abhisek Sanyal](https://www.blogger.com/profile/03484181296246017591)[2 February 2011 at 16:58](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html?showComment=1296665908909#c1112812359353542778)



Nice !

I have started the download, this should be fun.

It is high time I learned something new.

Thanks albino

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/1112812359353542778)



Replies







Reply

2. ![](https://resources.blogblog.com/img/blank.gif)



Anonymous[6 February 2011 at 12:08](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html?showComment=1296994118656#c1499001146475150961)



Any hint to get started?

I'm not an expert and I'm stuck right at the beginning :-)



Thanks for this hacking game, I have a lot of exercise to do.

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/1499001146475150961)



Replies







Reply

3. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



[James Kettle](https://www.blogger.com/profile/03270155456684307605)[6 February 2011 at 15:14](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html?showComment=1297005265256#c5019785892979273158)



The attack log you're provided with has several useful pieces of information in it. Try looking up information on HTTP request headers, particularly the Referrer header.

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/5019785892979273158)



Replies







Reply

4. ![](https://resources.blogblog.com/img/blank.gif)



Anonymous[5 March 2011 at 17:29](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html?showComment=1299346183265#c56185933716347808)



An hint document or walkthrough would be nice, I realized that this game is too hard for me but I still want to learn something.



Thank you albino

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/56185933716347808)



Replies







Reply

5. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



[James Kettle](https://www.blogger.com/profile/03270155456684307605)[7 March 2011 at 16:13](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html?showComment=1299514381999#c4540039036140713397)



I will release a hint document with the final version of hackxor (in a month or two). No walkthroughs :)



If you haven't already tried it I recommend the OWASP ; [broken web apps collection](http://www.owaspbwa.org/)



It's similar to hackxor but much easier to learn from.

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/4540039036140713397)



Replies







Reply

6. ![](https://resources.blogblog.com/img/blank.gif)



Anonymous[7 March 2011 at 17:38](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html?showComment=1299519533100#c4705623489247865493)



Thank you, I will give it a try while waiting for your hint document ;-)

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/4705623489247865493)



Replies







Reply

7. ![](https://resources.blogblog.com/img/blank.gif)



Anonymous[31 March 2011 at 20:59](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html?showComment=1301601573169#c5787663958813911377)



Hackxor. HACKXOR? Will the sequel be called Chainxor?

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/5787663958813911377)



Replies







Reply

8. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



[James Kettle](https://www.blogger.com/profile/03270155456684307605)[1 April 2011 at 10:29](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html?showComment=1301650172968#c70779437175450250)



I was thinking dinoxor

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/70779437175450250)



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

[Newer Post](https://www.skeletonscribe.net/2011/05/simulating-targets-for-xsscsrf-attacks.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2010/12/chronofeit-phishing.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/6793557918502568622/comments/default)

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