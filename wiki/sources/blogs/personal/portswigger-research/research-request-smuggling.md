---
source: portswigger-research
source_url: https://portswigger.net/research/request-smuggling
title: "HTTP Request Smuggling Research | PortSwigger Research"
description: "View the latest HTTP request smuggling research papers, tools, and techniques, from PortSwigger Research. Includes introductory and advanced content."
---

# HTTP Request Smuggling Research

HTTP Request Smuggling is an advanced technique for attacking websites that have one or more front-end servers. An attack is launched by sending ambiguous HTTP requests that get interpreted as different lengths by the servers. This causes them to desynchronize, and merge requests and responses from attackers and legitimate users.

This can ultimately lead to a wide range of serious effects. These include letting attackers steal plaintext passwords, and poison caches to persistently compromise critical functionality like login pages. It was first documented in 2004, but largely forgotten until we revisited it in 2019. We built on the existing request smuggling research with modern techniques and tooling, earning six figures in bug bounties along the way.

### HTTP Request Smuggling Research

We presented [HTTP Desync Attacks: Request Smuggling Reborn](https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn) at both Black Hat USA and DEF CON. This repopularized the technique, and has since led to a wave of discoveries and patches.

In subsequent years we presented [HTTP/2: The Sequel is Always Worse](https://portswigger.net/research/http2) followed by [Browser-Powered Desync Attacks](https://portswigger.net/research/browser-powered-desync-attacks). The next major installment will be [HTTP/1.1 Must Die! The Desync Endgame](https://portswigger.net/research/talks?talkId=32).

We also released a collection of [interactive labs](https://portswigger.net/web-security/request-smuggling) as part of our Web Security Academy, so you can practise applying the techniques to real systems.

## HTTP Request Smuggling Research Articles

[**How to distinguish HTTP pipelining from request smuggling** 19 August 2025How to distinguish HTTP pipelining from request smuggling](https://portswigger.net/research/how-to-distinguish-http-pipelining-from-request-smuggling) [06 August 2025](https://portswigger.net/research/http1-must-die) [**Making desync attacks easy with TRACE** 19 March 2024Making desync attacks easy with TRACE](https://portswigger.net/research/trace-desync-attack) [**Making HTTP header injection critical via response queue poisoning** 22 September 2022Making HTTP header injection critical via response queue poisoning](https://portswigger.net/research/making-http-header-injection-critical-via-response-queue-poisoning) [**How to turn security research into profit** 06 September 2022How to turn security research into profit](https://portswigger.net/research/how-to-turn-security-research-into-profit) [**Browser-Powered Desync Attacks** 10 August 2022Browser-Powered Desync Attacks](https://portswigger.net/research/browser-powered-desync-attacks) [**HTTP/2: The Sequel is Always Worse** 05 August 2021HTTP/2: The Sequel is Always Worse](https://portswigger.net/research/http2) [**Breaking the chains on HTTP Request Smuggler** 09 December 2019Breaking the chains on HTTP Request Smuggler](https://portswigger.net/research/breaking-the-chains-on-http-request-smuggler) [**HTTP Desync Attacks: what happened next** 03 October 2019HTTP Desync Attacks: what happened next](https://portswigger.net/research/http-desync-attacks-what-happened-next) [**HTTP Desync Attacks: Request Smuggling Reborn** 07 August 2019HTTP Desync Attacks: Request Smuggling Reborn](https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn)