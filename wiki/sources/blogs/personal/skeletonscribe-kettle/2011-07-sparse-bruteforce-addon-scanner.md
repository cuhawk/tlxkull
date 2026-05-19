---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2011/07/sparse-bruteforce-addon-scanner.html
title: "Skeleton Scribe: Sparse Bruteforce Addon Detection"
description: "This post demonstrates a technique for discovering which browser addons/extensions people who visit your website have installed. This could ..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Friday, 1 July 2011

### Sparse Bruteforce Addon Detection

This post demonstrates a technique for discovering which browser addons/extensions people who visit your website have installed. This could be used for fingerprinting, compatibility purposes or pre-exploit reconnaissance.

[Chrome demo](http://albinowax.users.sourceforge.net/sbad.html) (Detects top 1000 extensions)

[Backing script](http://albinowax.users.sourceforge.net/sbad.py)

[Firefox demo](http://albinowax.users.sourceforge.net/sbas.html)(Detects ~10% of top 1000 addons)

[Backing script](http://albinowax.users.sourceforge.net/sbas.py)

Both demos use the [well known technique](http://ha.ckers.org/blog/20060823/detecting-firefox-extentions/) of:

<img/script src='chrome://\[imageFromAddon\]' onload='addonExists=true' onerror='addonExists=false'>

The Firefox demo was generated using a python script that inspects the chrome.manifest of each addon for 'contentaccessible=yes', then loads the addon's install.rdf and extracts the chrome:// URI of the addon's icon. The Chrome script is extremely simple; it merely detects the manifest.json that all Chrome extensions have. Both scripts can also be used to generate detection code for addons by search keyword.

**Update:** For a technical explanation & more elegant implementation see
[http://blog.kotowicz.net/2012/02/intro-to-chrome-addons-hacking.html](http://blog.kotowicz.net/2012/02/intro-to-chrome-addons-hacking.html)

**Update #2**: Firefox addons can also be detected without javascript; see [http://kuza55.blogspot.co.uk/2007/10/detecting-firefox-extension-without.html](http://kuza55.blogspot.co.uk/2007/10/detecting-firefox-extension-without.html)

The poc on that page longer works, here's one that does: [http://albinowax.users.sourceforge.net/scriptlessAddonDetect.html](http://albinowax.users.sourceforge.net/scriptlessAddonDetect.html)

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[13:20](https://www.skeletonscribe.net/2011/07/sparse-bruteforce-addon-scanner.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6774329224935148238&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6774329224935148238&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6774329224935148238&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6774329224935148238&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=6774329224935148238&target=pinterest "Share to Pinterest")

Labels:
[chrome firefox extension detection](https://www.skeletonscribe.net/search/label/chrome%20firefox%20extension%20detection)

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

[Newer Post](https://www.skeletonscribe.net/2011/12/phrack-ebook.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2011/05/js-less-xss.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/6774329224935148238/comments/default)

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