---
source: corben-leo
source_url: https://corben.io/blog/17-01-09-aol-xss
title: "XSS in mail.aol.com"
description: "A cross-site scripting vulnerability in AOL Mail"
---

I got bored one day and somehow thought of AOL for some reason, so I decided to see if I could find any vulnerabilities in mail.aol.com.

Initially I tried looking in the signature, since it allowed HTML. I did find an XSS there, but it was self-xss, because when you sent an email with the malicious signature, the javascript was filtered out.

I looked at all the other parameters shown in an email to see if I could bypass filtering but came up empty.

Then another potential place for an XSS came to me: the **reply-to** parameter! I opened up Apple Mail on my Mac Book, created a new email and eventually came up with this payload:

`<<h1/onmouseover=javascript:confirm(document.cookie) width=800 height=800 style=@aol.com>`


I added that as the reply-to email and sent it to the AOL I had created. When I tried to reply to the email, my payload triggered!

Here's the proof of concept [video](https://drive.google.com/file/d/0B8sZyyQEiBRpZmd2MGZiY0M5ZVE/view)

I was thanked and added to their Hall of Fame for 2017 as "CDL": [https://contact.security.aol.com/hof/](https://contact.security.aol.com/hof/).

Thanks for reading,

**Corben Leo**