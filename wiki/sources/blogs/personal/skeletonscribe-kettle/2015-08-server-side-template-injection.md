---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2015/08/server-side-template-injection.html
title: "Skeleton Scribe: Server-Side Template Injection"
description: "I've written up a novel technique to get RCE on webservers - Server-Side Template Injection - over at http://blog.portswigger.net/2015/08/s..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Wednesday, 19 August 2015

### Server-Side Template Injection

I've written up a novel technique to get RCE on webservers - **Server-Side Template Injection** \- over at [http://blog.portswigger.net/2015/08/server-side-template-injection.html](http://blog.portswigger.net/2015/08/server-side-template-injection.html). I presented this at **Black Hat USA 2015** \- you can watch a recording at [https://www.youtube.com/watch?v=3cT0uE7Y87s](https://www.youtube.com/watch?v=3cT0uE7Y87s)

Shortly afterwards, I  presented at **44Con 2015** on **Hunting Asynchronous Vulnerabilities**. You can read a summary at [http://blog.portswigger.net/2015/09/hunting-asynchronous-vulnerabilities.html](http://blog.portswigger.net/2015/09/hunting-asynchronous-vulnerabilities.html) or watch the recording (paid only alas) at [https://vimeo.com/ondemand/44conlondon2015/141318621](https://vimeo.com/ondemand/44conlondon2015/141318621)

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[17:33](https://www.skeletonscribe.net/2015/08/server-side-template-injection.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5100474545172121970&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5100474545172121970&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5100474545172121970&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5100474545172121970&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5100474545172121970&target=pinterest "Share to Pinterest")

#### No comments:

#### Post a Comment

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

[Newer Post](https://www.skeletonscribe.net/2016/04/exploiting-uber-and-piwik-with-adapted.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2015/02/exploiting-path-relative-style-sheet.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/5100474545172121970/comments/default)

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