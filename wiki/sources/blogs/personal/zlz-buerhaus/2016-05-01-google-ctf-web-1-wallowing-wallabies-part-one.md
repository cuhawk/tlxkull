---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-1-wallowing-wallabies-part-one
title: "Google CTF – Web 1 – Wallowing Wallabies – Part One | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 1 - Wallowing Wallabies - Part One**

The first web challenge you visit a website that appears to have no links or pages.

![](https://buer.haus/wp-content/uploads/2016/05/site.png)

One of the first things you look for when you have nothing else is robots.txt. This may give you some insight into the website such as other pages that exist or a framework that the website might be using.

```
User-agent: *
Disallow: /deep-blue-sea/
Disallow: /deep-blue-sea/team/
# Yes, these are alphabet puns :)
Disallow: /deep-blue-sea/team/characters
Disallow: /deep-blue-sea/team/paragraphs
Disallow: /deep-blue-sea/team/lines
Disallow: /deep-blue-sea/team/runes
Disallow: /deep-blue-sea/team/vendors
```

Now we have a bunch of different endpoints we can test. Going through them each one by one you'll eventually realize you cannot access any of them except /deep-blue-sea/team/vendors.

It's a small form that takes your name and a textbox asking justification for access. When you submit the form, you can see the details you entered displayed back to you. I quickly noticed that it's vulnerable to XSS and assumed there is a bot reading our submissions based on the sentence "an admin will review your application as soon as possible."

![](https://buer.haus/wp-content/uploads/2016/05/pic2.png)

I used a pretty standard XSS payload to cause the browser to load an image to an endpoint with the cookies in the request vars. On my server I checked my access logs and found the following:

![](https://buer.haus/wp-content/uploads/2016/05/pic3.png)

The bot executed the payload and gave me a new cookie "green-mountains". e.g.

```
cookie=green-mountains=eyJub25jZSI6IjU4MzYwMzIyZmFhYjVmZGQiLCJhbGxvd2VkIjoiXi9kZWVwLWJsdWUtc2VhL3RlYW0vdmVuZG9ycy4qJCIsImV4cGlyeSI6MTQ2MTk3NjMwNX0=|1461976302|774b68429266fe1b836e57294299dab27d5481e6
```

If you base64 decode the first part of this cookie, you get the following:

"allowed":"^/deep-blue-sea/team/vendors.\*$"

We know there are 3 flags on this website by looking at the Google CTF web challenge list. We also know there are 6 different endpoints in robots.txt. We can make a safe assumption that this cookie only gets us access to the /vendors/ endpoint and not the others.

Setting that cookie in my request on /vendors/, this is what we get:

![](https://buer.haus/wp-content/uploads/2016/05/pic4.png)

Success! We have our first flag. We can also see a new link opened at the top of the navigation "Messaging".

This most likely leads to the next CTF challenge for this website.