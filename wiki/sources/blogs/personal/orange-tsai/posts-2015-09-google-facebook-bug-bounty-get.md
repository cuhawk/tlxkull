---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2015-09-google-facebook-bug-bounty-get/
title: "Google & Facebook Bug Bounty GET | Orange Tsai"
author: "Orange Tsai"
published: 2015-09-28T16:00:00.000Z
description: "先說這篇純粹炫耀文xD 暨 2013 年 Yahoo 開始有 Bug Bounty 那時搶個流行找了兩個漏洞回報 Yahoo 然後 Yahoo Bug Bounty Part 1 - 台灣 Yahoo Blog 任意檔案下載漏洞 Yahoo Bug Bounty Part 2 - *.login.yahoo.com 遠端代碼執行漏洞 就沒有然後了。之後就變成電競選手在打 CTF 了 直到今年年"
---

* * *

先說這篇純粹炫耀文xD

暨 2013 年 Yahoo 開始有 [Bug Bounty](http://bugbounty.yahoo.com/) 那時搶個流行找了兩個漏洞回報 Yahoo 然後

- [Yahoo Bug Bounty Part 1 - 台灣 Yahoo Blog 任意檔案下載漏洞](http://blog.orange.tw/2013/11/yahoo-bug-bounty-part-1-yahoo-blog.html)
- [Yahoo Bug Bounty Part 2 - \*.login.yahoo.com 遠端代碼執行漏洞](http://blog.orange.tw/2013/11/yahoo-bug-bounty-part-2-loginyahoocom.html)

就沒有然後了。之後就變成電競選手在打 CTF 了

直到今年年中，想說至少把幾間大公司的漏洞回報榜都留個名字就開始繼續挖洞

不過實際下去挖掘的時候發現差異滿大的，好挖好找嚴重性大的漏洞都已經被找走

感覺挖漏洞的藍海時代已經過惹

現在要當獎金獵人只能往比較前端跟設計上的小疏失挖掘，賺不到甚麼大錢XD

花了一點時間 survey 歷年出過的一些漏洞以及前端相關的一些攻擊手法

找到了個 Google 某官方的 CSRF 導致個人資訊洩漏以及 Facebook 某個子域名的 XSS

Google 那個比較有趣，利用起來比較類似 [Watering holes exploiting JSONP hijacking to track users in China](https://www.alienvault.com/open-threat-exchange/blog/watering-holes-exploiting-jsonp-hijacking-to-track-users-in-china)

順道一提，在寄信回報漏洞時的 PoC 還順便釣到 Google Security Team 的測試帳號

（很靠北的大頭貼XDD）

![](https://blog.orange.tw/posts/2015-09-google-facebook-bug-bounty-get/70a150d15f96b808-01.png)

[https://www.google.com/about/appsecurity/hall-of-fame/](https://www.google.com/about/appsecurity/hall-of-fame/)

![](https://blog.orange.tw/posts/2015-09-google-facebook-bug-bounty-get/dd2b09f7fc221bf7-02.png)

[https://www.facebook.com/whitehat/thanks/](https://www.facebook.com/whitehat/thanks/)

![](https://blog.orange.tw/posts/2015-09-google-facebook-bug-bounty-get/a5aa68b3c8c0abad-03.png)