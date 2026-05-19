---
source: detectify
source_url: https://labs.detectify.com/how-to/set-up-docker-for-varnish-http-2-request-smuggling/
title: "How to set up Docker for Varnish HTTP/2 request smuggling - Labs Detectify"
author: "Detectify"
published: 2021-08-26T14:44:01+00:00
description: "Here a guide on how to set up a docker to test out varnish HTTP/2 request smuggling including the link to the github repo."
---

[Home](https://labs.detectify.com/)/ [How to](https://labs.detectify.com/category/how-to/)/ [How to set up Docker for Varnish HTTP/2 request smuggling](https://labs.detectify.com/how-to/set-up-docker-for-varnish-http-2-request-smuggling/)

[How to](https://labs.detectify.com/category/how-to/ "How to")

# How to set up Docker for Varnish HTTP/2 request smuggling

**Alfred Berg** Aug 26, 2021

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/set-up-docker-for-varnish-http-2-request-smuggling/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/set-up-docker-for-varnish-http-2-request-smuggling/ "Share on LinkedIn")

**If you don’t know about HTTP/2 request smuggling then what are you hacking? Alfred Berg, Security Researcher at [Detectify](https://www.detectify.com/), shows you how to set up an environment to test out HTTP/2 request smuggling.**

One of the highlights from Black Hat USA 2021 and DEFCON 29 has been James Kettle’s [**presentation about H2 (HTTP/2) request smuggling.**](https://www.youtube.com/watch?v=rHxVVeM9R-M) Inspired by this, I’ll show you how to set up a local environment that is vulnerable to HTTP/2 request smuggling [CVE-2021-36740.](https://nvd.nist.gov/vuln/detail/CVE-2021-36740) I’ll also explain how it works with a PoC for the vulnerability. The git repository to follow along with this blog post can be found [on Detectify’s Github page.](https://github.com/detectify/Varnish-H2-Request-Smuggling)

## What is H2 request smuggling?

H2 request smuggling is essentially a variant of [request smuggling](https://blog.detectify.com/2020/05/28/hiding-in-plain-sight-http-request-smuggling/), but instead of a confusion about the headers `Content-Length` and chunked encoding, H2 request smuggling takes advantage of H2 compatible proxies rewriting H2 requests into HTTP/1.1.

One of the things that can go wrong in this conversion is that the content length is not required in HTTP/2 \[ [rfc7540](https://datatracker.ietf.org/doc/html/rfc7540#:~:text=a%20request%20or%20response%20that%20includes%20a%20payload%20body%20can%20include%20a%20content-length%20header%20field)\] due to H2’s frame structure. However, if an incorrect content length is specified in the H2 request and written to the new HTTP/1.1 request without any checks, a confusion can arise between the server where a request starts and ends. This can, for example,  make it possible to add prefixes to other users’ requests. [James Kettle’s article](https://portswigger.net/research/http2) goes more in- depth and covers more techniques.

Varnish cache was vulnerable to H2 request smuggling. This vulnerability was discovered internally by Martin Blix Grydeland, and [there is now a patch and workaround out to fix it.](https://docs.varnish-software.com/security/VSV00007/%20https://nvd.nist.gov/vuln/detail/CVE-2021-36740)

## Setup

![](https://labsadmin.detectify.com/app/uploads/2021/08/diagram-http2.png)

All that is needed to set up your own vulnerable environment is to clone the repository, cd into the folder and run `docker-compose up`. The environment mainly consists of four different web servers; a varnish server running a vulnerable version, a hitch server to terminate TLS since the open source version of varnish can’t handle TLS, and two origin servers. The origin servers consist of one default HTTPd server and one ncat listener that varnish sends requests to if the authority header (similar to the Host header in HTTP/1.1).

The ncat listener makes it easy to inspect what varnish sends to the TCP socket since it echos out all data it receives. Note however that `docker-compose logs -t` and `docker-compose up` will only output complete lines, so the last line of a request will be seen only after a new request comes in.

## Let’s send some requests

When the environment set up, let’s send some requests. Open Burp and a browser that uses Burp as a proxy, and visit `https://localhost/`. Get a request similar to this into the repeater, and make sure that the protocol in the inspector is `HTTP/2` and that `Update Content-Length` is unchecked in the Repeater settings.

![](https://labsadmin.detectify.com/app/uploads/2021/08/setup-in-BURP.png)

After sending that request followed by a normal request, this is what the ncat origin receives:

![see the response in ncat origin](https://labs.detectify.com/wp-content/uploads/2021/08/response-ncat-origin.png)

`POST / HTTP/1.1

scheme: https

host: ncat

content-type: application/x-www-form-urlencoded

content-length: 1

X-Forwarded-For: 192.168.0.1

X-Varnish: 32769

`

`aSMUGGLEDGET / HTTP/1.1

Host: ncat

X-Forwarded-For: 192.168.0.1

Accept-Encoding: gzip

X-Varnish: 32772`

Due to the content length on the first request being 1, only the first byte in the body will be regarded as coming from the first request; the word SMUGGLED will instead be appended to the next request. This happens because the varnish server receives the HTTP/2 request and reads the whole body since content-length is not required in HTTP/2 \[ [rfc7540](https://datatracker.ietf.org/doc/html/rfc7540#:~:text=a%20request%20or%20response%20that%20includes%20a%20payload%20body%20can%20include%20a%20content-length%20header%20field)\] due to that H2’s frame structure. But when rewriting the request to HTTP/1.1, the incorrect content-length value is used.

When Changing the authority/host to localhost on the requests to make varnish send them to HTTPd, we can see that this is indeed the case. Note the cachebuster `nocache=1` here to make sure that the request gets sent to the origin.

![](https://labsadmin.detectify.com/app/uploads/2021/08/change-authority-host.png)

## **This is just the beginning**

This new research opens up the web app landscape and we’re expecting to see new web vulnerabilities stemming from this research.

**Resources on web browser security and secure headers:**

- [A guide to HTTP security headers for better web browser security](https://blog.detectify.com/2019/02/05/guide-http-security-headers-for-better-web-browser-security/)
- [HTTP response splitting exploitations and mitigations](https://blog.detectify.com/2019/06/14/http-response-splitting-exploitations-and-mitigations/)
- [Content Security Policy (CSP) explained including common bypasses](https://blog.detectify.com/2019/07/11/content-security-policy-csp-explained-including-common-bypasses/)
- [CORS Misconfigurations Explained](https://blog.detectify.com/2018/04/26/cors-misconfigurations-explained/)

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/set-up-docker-for-varnish-http-2-request-smuggling/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/set-up-docker-for-varnish-http-2-request-smuggling/ "Share on LinkedIn")

**Alfred Berg**

Security Researcher, Detectify

## Check out more content

External Attack Surface Management (EASM) is the continuous discovery, analysis, and monitoring of an organization’s public facing assets. A substantial part of EASM is the …

January 13, 2023

TL/DR: Web applications have both authentication and authorization as key concepts and if bypassed by an attacker, it can compromise sensitive data. With threats such …

August 05, 2022

TL/DR: It’s becoming increasingly easy to compromise sensitive information for attackers to take advantage of. In this post, Detectify security researcher Alfred Berg wrote about …

June 16, 2022

TL/DR: Web applications can be exploited to gain unauthorized access to sensitive data and web servers. Threats include SQL Injection, Code Injection, XSS, Defacement, and …

May 16, 2022