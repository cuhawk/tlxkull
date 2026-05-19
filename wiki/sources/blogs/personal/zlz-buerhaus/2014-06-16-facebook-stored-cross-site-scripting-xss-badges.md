---
source: zlz-buerhaus
source_url: https://buer.haus/2014/06/16/facebook-stored-cross-site-scripting-xss-badges/
title: "Facebook – Stored Cross-Site Scripting (XSS) – Badges | ziot"
---

[< Back](https://buer.haus/)

The Facebook badges page was vulnerable to stored Cross-Site Scripting (XSS). This was initially reported back in August 2013, but due to communication problems over e-mail it wasn't fixed until early January. Neither party is to blame, but this shows some of the difficulties that companies can face communicating with security researchers.

This [problem](http://techcrunch.com/2013/08/18/security-researcher-hacks-mark-zuckerbergs-wall-to-prove-his-exploit-works/) hit the media earlier this year when a Facebook security report was not clearly understood and led to the exploit being abused on Mark Zuckerberg's wall.

Facebook recently moved their Whitehat communication to their support dashboard instead of over e-mail which is going to help the company and security testers tremendously.

**The Exploit**

Sample request:

URL: [https://www.facebook.com/badges/profile.php](https://www.facebook.com/badges/profile.php)

POST:

fb\_dtsg=& **layout=horiz**&items%5B%5D=badge\_profile\_pic&items%5B%5D=badge\_test&items%5B%5D=badge\_hometown&items%5B%5D=badge\_email&items%5B%5D=badge\_mobile\_status&save=Save&bid=2421&badge\_type=0&wizard=badges&owner\_id=4

When this request is sent, it would return the following source:

Source: <div class="badge\_holder bh\_ **horiz**">

The layout request variable was being saved to a database and pulled into the <div>'s class. Because the input was not encoded, it allowed you to break out of the div and inject HTML.

**Example**

URL: [https://www.facebook.com/badges/profile.php](https://www.facebook.com/badges/profile.php)

POST:

fb\_dtsg=&layout= **"><b>**&items%5B%5D=badge\_profile\_pic&items%5B%5D=badge\_test&items%5B%5D=badge\_hometown&items%5B%5D=badge\_email&items%5B%5D=badge\_mobile\_status&save=Save&bid=2421&badge\_type=0&wizard=badges&owner\_id=4

Screenshot:

**![image](https://31.media.tumblr.com/afc76c1b52d30d8fd74fa417ad2e26da/tumblr_inline_n7a2jaWevf1svukax.png)**

Normally I would show an iframe or script alert as an example, but this is the only screenshot I still have of this. The entire badge page has since been completely overhauled and no longer functions in a way that a string is passed by the client to a database to be saved.

**The Danger**

Although this could force you to save JavaScript/HTML on your badges page, the impact of it is quite small. This request is protected by fb\_dtsg which is a csrftoken and Facebook has X-Frame-Options preventing clickjacking.

That means no one can force you to make this request, you would have to damage yourself or the attacker would have to already have access to your Facebook. Even still, you would have to visit the badge page in order for it to execute.

I'm going to bet a lot of you haven't even heard of the badge page until you read this.

Regardless, XSS is XSS! It can force you to execute any action protected by a csrftoken and extract information from your Facebook. That means forcing you to make Facebook posts or stealing private data that you didn't want public.

**The Bug**

Submitted: August 2013

Fixed: January 2014