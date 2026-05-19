---
source: detectify
source_url: https://labs.detectify.com/security-guidance/ssrf-vulnerabilities-and-where-to-find-them/
title: "SSRF vulnerabilities and where to find them - Labs Detectify"
author: "Detectify"
published: 2022-09-23T09:21:02+00:00
description: "SSRF vulnerabilities aren't a new threat vector but they're often misunderstood. Here are details about what it is and where it can be found."
---

[Home](https://labs.detectify.com/)/ [Security guidance](https://labs.detectify.com/category/security-guidance/)/ [SSRF vulnerabilities and where to find them](https://labs.detectify.com/security-guidance/ssrf-vulnerabilities-and-where-to-find-them/)

[Security guidance](https://labs.detectify.com/category/security-guidance/ "Security guidance")

# SSRF vulnerabilities and where to find them

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2021%2F08%2Fhakluke.jpg&w=128&q=75)

**Hakluke** Sep 23, 2022

[hakluke](https://labs.detectify.com/tag/hakluke/ "hakluke")

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/ssrf-vulnerabilities-and-where-to-find-them/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/ssrf-vulnerabilities-and-where-to-find-them/ "Share on LinkedIn")

![SSRF vulnerabilities and where to find them](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2022%2F09%2Fimage2-4.png&w=3840&q=75)

**It’s no secret that c** **loud architectures have several characteristics that make SSRF attacks challenging to defend against.** **While [SSRFs](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery) are not a new threat vector, they are often misunderstood and confused with CSRFs.**

In this article, ethical hacker Luke Stephens outlines [what the vulnerability is](https://cwe.mitre.org/data/definitions/918.html), the places that they are most commonly found and how you can bypass SSRF protections _._

## **SSRF explained**

[Server-Side Request Forgery (SSRF)](https://blog.detectify.com/2019/01/10/what-is-server-side-request-forgery-ssrf/?_gl=1*506b1s*_ga*NzYxMDI2NjgzLjE2NTg5MDIyMjM.*_ga_F9HDKDJVKN*MTY2MzY4NjQ2Mi41MC4xLjE2NjM2ODY4NTUuNTQuMC4w*_fplc*TlhXbTIydEFxQXdwMjBqbFkydFQlMkZ5cnlYOHFja25oUkQlMkZGUTNCQnk2VjBBSnJDcXBLajRTNFpTZm5HOFF5Q2V4WTZpSVhKZDVTSEEwSDY4djFUSnlIa0h1ZkFEVXhKMU5QbWhRR2ZyTTRCZ3RiU3BQSXlUVEM2aEVscEVBUSUzRCUzRA..) occurs when an application accepts a URL (or partial URL) from the user, then accesses that URL from the server. It’s important to note that SSRF is only a vulnerability if there is some _security impact_. Accessing URLs from the server is a common task that is required in many cases and can be completely safe. It becomes an issue when this request compromises security. For example:

- You can make requests to an internal endpoint that leaks sensitive information, and the response can be viewed by the attacker
- You can make requests to the internal network that allow you to perform unauthorized actions or exploit internal systems
- You are able to map out the internal network by spraying requests through it, using the vulnerable web application as a proxy

## ![](https://labsadmin.detectify.com/app/uploads/2022/09/image1-6.png)

## **Blind vs. Partial-blind vs. Non-blind**

It’s important to make this distinction.

- In a **_blind_** SSRF, no part of the response can be seen. This makes it difficult (but not always impossible) to exploit.
- In a **_non-blind_** SSRF, the response to the request from the server can be viewed by the attacker in full.
- In a **_partial-blind_** SSRF, some part of the response can be seen (maybe a status code or some specific section of the response).

## **Where to Find SSRF Vulnerabilities**

### **Common Vulnerable Parameter Names**

When security testing applications in the wild, we will typically be analyzing thousands of requests and parameters. It pays to know what parameter names are most likely to be [vulnerable to SSRF](https://labs.detectify.com/2021/09/30/10-types-web-vulnerabilities-often-missed/) so that we can pay extra attention to them.

Thankfully, this data has already been collated in the [HUNT Burp Suite extension](https://github.com/bugcrowd/HUNT/). This tool was originally created by Jason Haddix when he worked at Bugcrowd, so I believe that these parameter names were collated from Bugcrowd’s bug bounty submissions. Here are the parameter names:

- dest
- redirect
- uri
- path
- continue
- url
- window
- next
- data
- reference
- site
- html
- val
- validate
- domain
- callback
- return
- page
- feed
- host
- port
- to
- out
- view
- dir
- show
- navigation

Unsurprisingly, these parameter names all refer to an object type that could be fetched from a remote resource.

### **Webhook Integrations**

Applications that wish to integrate with other applications will often do so by implementing outgoing webhooks. The best way to explain this is with an example.

Let’s say we are testing a web application that handles invoices. The developers wanted to provide a generic solution for integrating with other services, so they implemented webhooks. The application can be set up so that when an invoice is created, it will send an HTTP request (webhook) out to an arbitrary server, chosen by the user, containing the details of the invoice that was just created.

This allows users of the application to catch the webhook on their own server and use the invoice details as they wish. For example, they may want to post the invoice details to Slack, push it to their CRM or send an email to their accounts team.

Most applications that have webhook functionality will also have some type of functionality for _testing_ the webhooks. Typically you provide the application with the details of the request you wish to make, such as the URL, and then the webhook test will show you the response. I’ve even seen some applications even allow you to specify HTTP verbs and custom headers. It’s like your own little SSRF testing station.

### **File Imports**

Many applications require the need to import files. For example, a social media application requires the need to upload a profile picture. In some cases, applications allow the file to be imported from a URL instead of being uploaded directly.

Cases like these can often result in SSRF. To test, simply specify a sensitive internal URL, such as [http://169.254.169.254](http://169.254.169.254/), then download the resulting profile picture and view it with a text editor. If you’re lucky, it will contain a response from the cloud metadata endpoint.

### **PDF Generators**

A while back, [Nahamsec](https://twitter.com/nahamsec) and [Cody Brocious](https://twitter.com/daeken) did an excellent DEFCON talk about performing SSRF attacks through PDF generators, titled “ [Owning the cloud through SSRF and PDF generators](https://docs.google.com/presentation/d/1JdIjHHPsFSgLbaJcHmMkE904jmwPM4xdhEuwhy2ebvo/htmlpresent)“.

In this presentation, they present an idea for performing SSRF through PDF generators. You see, most PDF generators nowadays simply render HTML in a headless browser and then print the resulting webpage as a PDF in order to generate it. If any user-defined content is pushed to that PDF, it will potentially be vulnerable to XSS, which means that the user is able to embed an iframe within the PDF. That iframe could load any internal resource, and then the response from that internal resource would show on the resulting PDF.

The full details are out of the scope of this blog, but I’d encourage you to check out the [slides](https://docs.google.com/presentation/u/0/d/1JdIjHHPsFSgLbaJcHmMkE904jmwPM4xdhEuwhy2ebvo/edit).

[_How secure is the PDF file? Check out this write-up and its flaws on Detectify Blog._](https://blog.detectify.com/2020/08/27/how-secure-is-the-pdf-file/)

## **Common Bypasses**

If your SSRF attempts don’t work on the first try, all is not lost. Here are some quick, common bypasses to try.

### **Use Hostnames Instead of IPs**

Sometimes, the developers just banned the use of 169.254.169.254 directly. In that case, we can simply use hostnames that resolve to the same IP address. Nip.io allows simple wildcard DNS for any IP address; here are some examples. All of these resolve to 169.254.169.254.

- 169.254.169.254.nip.io
- 169-254-169-254.nip.io
- a9fea9fe.nip.io (hexadecimal IP notation)
- Something.google.com.169.254.169.254.nip.io

### **HTTP Redirects**

Sometimes, bypassing SSRF protection is as easy as using an HTTP redirect.

Let’s say we can make a request to customdomain.com, but not 169.254.169.254.

We can host a simple script on customdomain.com to 302 redirect to 169.254.169.254. If the vulnerable endpoint follows redirects but doesn’t check them, we have SSRF!

Here’s a simple PHP script to perform the redirect.

|     |
| --- |
| <?php header(“Location: http://169.254.169.254/”) ?> |

### **DNS Rebinding**

Many applications attempt to thwart SSRF attempts with a code pattern that looks like this:

|     |
| --- |
| funcfetch\_if\_allowed(url string){<br>if ip\_is\_blocked(resolve($url)){<br>returnfalse<br>    } else {<br>        fetch($url)<br>    }<br>} |

This code is vulnerable to a form of TOCTOU (time-of-check, time-of-use) vulnerability called DNS rebinding. An attacker can set up a DNS server that responds with two different IP addresses on alternating requests, one is allowed through the ip\_is\_blocked() function, and the other is not.

In this case, we could set up a DNS rebinding service such as [Taviso’s rbndr](https://github.com/taviso/rbndr) to resolve to 1.1.1.1 every second time, and 169.254.169.254 every other time. When the domain is resolved the first time, the application sees that it resolves to 1.1.1.1, and allows the code to flow into the else statement, where the domain is resolved again – this time to 169.254.169.254.

### **Non-Standard IP Notations**

Sometimes, specific IP addresses are blocked, such as 169.254.169.254. In this case, we may be able to bypass it by simply using different IP notation. For example, all of these will be interpreted as 169.254.169.254. Don’t believe me? Try pinging them!:

- 025177524776 (octal)
- 0xa9fea9fe (hexadecimal)
- 2852039166 (integer)
- ::ffff:a9fe:a9fe (IPv6)

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/ssrf-vulnerabilities-and-where-to-find-them/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/ssrf-vulnerabilities-and-where-to-find-them/ "Share on LinkedIn")

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2021%2F08%2Fhakluke.jpg&w=128&q=75)

**Hakluke**

Founder, Haksec

## Check out more content

The smaller our attack surface, the fewer things we need to worry about. An excellent way of reducing the attack surface (and our cognitive load) is using AWS Service Control Policies (SCPs.) In this post, I’ll describe how we approached it.

March 26, 2024

TL/DR: AWS QuickSight makes it easy to build visualizations, perform ad-hoc analysis, and quickly get business insights from their data, anytime, on any device. Hacker …

May 30, 2022

TL/DR: On December 2, open-source analytics solution Grafana released an emergency security patch for critical zero-day Path Traversal vulnerability CVE-2021-43798, after proof-of-concept code to exploit …

December 15, 2021

Crowdsource hackers Hakluke and Farah Hawa share the top web vulnerabilities that are often missed during security testing. When hunting for bugs, especially on competitive bug bounty …

September 30, 2021