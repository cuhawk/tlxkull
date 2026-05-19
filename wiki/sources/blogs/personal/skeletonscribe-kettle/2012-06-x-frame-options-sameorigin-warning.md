---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2012/06/x-frame-options-sameorigin-warning.html
title: "Skeleton Scribe: X-Frame-Options gotcha"
description: "Summary: X-Frame-Options: SAMEORIGIN validates window.top not window.parent. This is bad news for sites that frame untrusted content. UI..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Saturday, 2 June 2012

### X-Frame-Options gotcha

**Summary:** X-Frame-Options: SAMEORIGIN validates window.top not window.parent. This is bad
news for sites that frame untrusted content.

[UI-Redressing or 'Clickjacking'](https://www.owasp.org/index.php/Clickjacking) attacks rely on loading the target page in an iframe. The standard defence against them is to deny framing by using the [X-Frame-Options](http://michael-coates.blogspot.co.uk/2010/08/x-frame-option-support-in-firefox.html) (XFO) server header. Unfortunately there is a slight quirk in this feature's implementation which has left some sites vulnerable to clickjacking in spite of their use of XFO.

The problem is with the SAMEORIGIN flag. Intuitively, it sounds like it means 'Only pages from the same origin can frame this'. What it actually means is 'This page can only be framed when window.top is of the same origin'. **window.parent does not have to be of the same origin**. This is significant if your website frames untrusted/external pages. Let's use an example:

[https://skeletonpocs.appspot.com/iframepreview?src=example.com](https://skeletonpocs.appspot.com/iframepreview?src=example.com) uses X-Frame-Options: SAMEORIGIN to protect itself. It also loads a page in a sandboxed iframe.

[http://albinowax.users.sourceforge.net/clickjack.html](http://albinowax.users.sourceforge.net/clickjack.html) tries to perform a clickjacking attack but is thwarted by the XFO header. Web browsers will see the flag refuse to load the iframe, so clicking the green circle will have no effect.

However, if the target site can be cajoled into iframing the attack page, we have a problem:

[https://skeletonpocs.appspot.com/iframepreview?src=albinowax.users.sourceforge.net/clickjack.html](https://skeletonpocs.appspot.com/iframepreview?src=albinowax.users.sourceforge.net/clickjack.html)

The fix is simple: if you must iframe untrusted content, use the DENY flag instead of SAMEORIGIN

Update: see [clickjacking google](http://webstersprodigy.net/2012/09/13/clickjacking-google/) for a couple of real attacks using this technique.

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[17:56](https://www.skeletonscribe.net/2012/06/x-frame-options-sameorigin-warning.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5095657066664034620&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5095657066664034620&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5095657066664034620&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5095657066664034620&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5095657066664034620&target=pinterest "Share to Pinterest")

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

[Newer Post](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2011/12/phrack-ebook.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/5095657066664034620/comments/default)

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