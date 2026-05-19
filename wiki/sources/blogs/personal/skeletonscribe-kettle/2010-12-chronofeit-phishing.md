---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2010/12/chronofeit-phishing.html
title: "Skeleton Scribe: Chronofeit Phishing"
description: "This combines RSnake's Popup & Focus URL Hijacking * with Paul Stone's login detection to enhance phishing attacks. The basic concept ..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Saturday, 18 December 2010

### Chronofeit Phishing

This combines RSnake's [Popup & Focus URL Hijacking](https://web.archive.org/web/20150320023006/http://ha.ckers.org/blog/20091228/popup-focus-url-hijacking/)\\* with Paul Stone's

[login detection](http://contextis.co.uk/resources/white-papers/clickjacking/) to enhance [phishing](http://www.owasp.org/index.php/Phishing) attacks.

The basic concept behind this attack is to use URL hijacking to change a legitimate login page to a fake one in the gap between when the user checks the URL and when they enter their username/password.

This implementation uses polling to detect the moment the user logs in, then redirects them to a classic phishing page saying their password was incorrect, and hopes that they don't re-check the URL.

To view the demo, visit the link. You will need javascript, iframes and a legitimate Google account username/password for this to work. Note: This is not the most subtle browser based attack in the book. It may well be the least. As such, your browser could just freeze. The page will automatically stop polling after 60 seconds to avoid unnecessary grief.

[View the demo](http://justademo.110mb.com/chronofeitdemo.html) (Tested in Firefox 3.x, probably doesn't work in IE)

I have left the iframes visible for clarity. Obviously, in a real attack they'd be invisible and the phishing URL would be a nice reassuring shade of green along the lines of https://google.evildomain.com/account

**Scope for improvement**

As you've probably noticed if you tried the demo, there is a clear delay between clicking login and getting redirected. This delay could be significantly reduced by using the login detection with a page that doesn't send a redirect (and isn't encrypted). That said, there are probably completely different approaches to identifying this moment that have less delay anyway.

**Countermeasures:**

Website owners could prevent framing by using frame-busting code/X-Frame-Options etc. They ought already be doing to this protect against (the much more severe attack) clickjacking. Users should just check the URL _every_ time they enter their password, I guess.

Comments&Feedback appreciated :)

\*If server is still down try [the cached version](http://webcache.googleusercontent.com/search?q=cache:0na-80s-ligJ:ha.ckers.org/blog/20091228/popup-focus-url-hijacking/+glfixingItid&cd=1&hl=en&client=nicetry)

**EDIT October 2011: This demo no longer works, as Google has prevented the login-detection by using X-Frame-Options. I have no plans to fix it.**

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[23:31](https://www.skeletonscribe.net/2010/12/chronofeit-phishing.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6003551970281283049&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6003551970281283049&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6003551970281283049&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6003551970281283049&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6003551970281283049&target=pinterest "Share to Pinterest")

Labels:
[phishing](https://www.skeletonscribe.net/search/label/phishing)

#### 1 comment:

1. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



[James Kettle](https://www.blogger.com/profile/03270155456684307605)[10 February 2011 at 10:51](https://www.skeletonscribe.net/2010/12/chronofeit-phishing.html?showComment=1297335060824#c3040794793292056482)



Wow, I love the speed on that. Thanks for sharing it.

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/3040794793292056482)



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

[Newer Post](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html "Newer Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/6003551970281283049/comments/default)

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