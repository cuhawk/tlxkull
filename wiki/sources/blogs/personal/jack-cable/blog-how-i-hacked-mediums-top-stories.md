---
source: jack-cable
source_url: https://cablej.io/blog/how-i-hacked-mediums-top-stories
title: "How I Hacked Medium’s Top Stories"
description: "How I Hacked Medium’s Top Stories"
---

Note: This is being published with the permission of Medium under the responsible disclosure policy. The vulnerability is now fixed.

If you’re familiar with Medium, you’ll know that any user can recommend a post as a way of “liking” it. Top stories, sorted by the number of recommendations, are then shown in Medium’s [“top stories”](https://medium.com/top-stories) section.

![](https://cdn-images-1.medium.com/max/800/1*cTu7Gt_PBD5DoOfsL7B83A.png)

I discovered Medium’s [Bug Bounty Program](https://medium.com/policy/mediums-bug-bounty-disclosure-program-34b1c80764c2#.9d0bn1jkd) and decided that I’d take a look around. One common issue in websites is known as a race condition, which allows users to perform actions more than allowed. Race conditions can be a huge problem for services dealing with money, and even affected [Starbucks](http://sakurity.com/blog/2015/05/21/starbucks.html) to add an infinite balance to a gift card. It works like this:

1. A user makes, say, 10 requests to a website to perform an action at the same exact time. In the context of a bank account, let’s say this user sends $10 10 times to User B, while they only have $10 in their bank account.
2. The bank receives these requests, and checks if the user has enough money in their account. As these requests were made at the same time, the bank returns that the user does have enough money for all 10 transactions.
3. The user has now sent 10 $10 transactions, which means that they have -$90 in their account. User B, then has $100 in their account, even though there was only $10 to start with.

I discovered the same vulnerability in Medium. After concurrently recommending a comment 10 times, I noticed that Medium didn’t check for other requests at the same time:

![](https://cdn-images-1.medium.com/max/800/1*s6yybl3mkHoLnceOh9x0MA.png)

Given that Medium sorts top stories by total number of recommendations, I was able to boost my story to one of the top spots.

![](https://cdn-images-1.medium.com/max/800/1*E9DLpZmwgoKBL7AbkaCW0g.png)

Internet fame forever!

* * *

### Timeline:

12/19/15 — Reported to Medium

1/4/16 — Response from Medium acknowledging vulnerability and bounty rewarded

1/13/16 — Disclosure requested

1/14/16 — Disclosure accepted

* * *

Overall, great experience with Medium with timely responses.

X Follow Button

[Jack Cable - Blog](https://cablej.io/)

Twitter Widget Iframe