---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2011/05/simulating-targets-for-xsscsrf-attacks.html
title: "Skeleton Scribe: Simulating targets for XSS/CSRF attacks in hacking games"
description: "Many web application hacking techniques require a victim as well as a vulnerable website. Such techniques include XSS, CSRF, XST, HTTP respo..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Wednesday, 11 May 2011

### Simulating targets for XSS/CSRF attacks in hacking games

Many web application hacking techniques require a victim as well as a vulnerable website. Such techniques include XSS, CSRF, XST, HTTP response splitting, session fixation, and various others. While it is possible to _find_ these without a victim, to truly understand them it helps to _exploit_ them. And you can't exploit them without a victim. This post explains how to simulate victims using [HtmlUnit](https://sourceforge.net/projects/htmlunit/), the technique I used in the hacking game [hackxor](http://hackxor.sourceforge.net/). HtmlUnit is "A java GUI-Less browser, which allows high-level manipulation of web pages, such as filling forms and clicking links". Here's a brief set of instructions:

Create accounts for your victim on _all_ websites you want them to use. Ask questions like How strong is their password? Do they re-use it across multiple websites? Do they have the same username on each site? etc.

Create a database table that contains what your victim knows. This should at least contain website/username/password sets. This is necessary because it ensures that if the player/attacker changes the victim's password on a website, the victim cannot log in.

Write some code that uses the HtmlUnit library to log the victim into each website they have an account on with their username and password. Hackxor's code looks something like:

WebClient browser = new WebClient(BrowserVersion.FIREFOX\_3\_6);

for(each website the user has an account on){

final HtmlPage login = browser.getPage(website);

final HtmlForm form = login.getFormByName("login");

form.getInputByName("user").setValueAttribute(user);

form.getInputByName("pass").setValueAttribute(pass);

form.getInputByName("submit").click();

}

Finally, create a way for the player to contact the victim. Hackxor uses a fake webmail system that checks the 'to' address to see if it matches a victim's, then uses the above code to log the victim into all their accounts, then finally calls

browser.getPage("thepagewherethemessagebodyis");

That's it. Hopefully you can see the advantage of simulating victims, and that this is a robust and easily extendible way of doing it.

**Update:** See also [https://blog.gregbrockman.com/2012/08/system-design-stripe-capture-the-flag/](https://blog.gregbrockman.com/2012/08/system-design-stripe-capture-the-flag/)

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[15:44](https://www.skeletonscribe.net/2011/05/simulating-targets-for-xsscsrf-attacks.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=9216244036997872967&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=9216244036997872967&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=9216244036997872967&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=9216244036997872967&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=9216244036997872967&target=pinterest "Share to Pinterest")

Labels:
[XSS CSRF simulate hacking games](https://www.skeletonscribe.net/search/label/XSS%20CSRF%20simulate%20hacking%20games)

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

[Newer Post](https://www.skeletonscribe.net/2011/05/js-less-xss.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/9216244036997872967/comments/default)

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