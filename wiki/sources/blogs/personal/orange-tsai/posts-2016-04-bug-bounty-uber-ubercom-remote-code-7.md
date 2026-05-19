---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2016-04-bug-bounty-uber-ubercom-remote-code_7/
title: "Uber 遠端代碼執行- Uber.com Remote Code Execution via Flask Jinja2 Template Injection | Orange Tsai"
author: "Orange Tsai"
published: 2016-04-06T16:00:00.000Z
description: "好久沒 po 文了XD 幾天前，Uber 公佈了 Bug Bounty 計畫，從 Hackerone 上看到獎金不低，最少的 XSS / CSRF 都有 3000 美金起就跳下來看一下有什麼好玩的XD 從官方公佈的技術細節發現 Uber 主要網站是以 Python Flask 以及 NodeJS 為架構，所以在尋找漏洞的時候自然會比較偏以測試這兩種 Framework 的漏洞為主!"
---

* * *

![preview](https://blog.orange.tw/posts/2016-04-bug-bounty-uber-ubercom-remote-code_7/43da2ae8d44965cf-01.jpg)

好久沒 po 文了XD

幾天前，Uber 公佈了 [Bug Bounty 計畫](https://eng.uber.com/bug-bounty/)，從 [Hackerone](https://hackerone.com/uber) 上看到獎金不低，最少的 XSS / CSRF 都有 3000 美金起就跳下來看一下有什麼好玩的XD

從官方公佈的技術細節發現 Uber 主要網站是以 Python Flask 以及 NodeJS 為架構，所以在尋找漏洞的時候自然會比較偏以測試這兩種 Framework 的漏洞為主!

Uber 網站在進行一些動作如修改電話、姓名時，會以寄信及簡訊的方式告知使用者帳號進行了變更，在某次動作後發現 Uber 寄過來的信如下圖，怎麼名字會多個 “2” XDDDD

![](https://blog.orange.tw/posts/2016-04-bug-bounty-uber-ubercom-remote-code_7/280a3e7ddc59927c-02.jpg)

往前追查原因才發現進入點是在 Riders.uber.com，Riders.uber.com 為修改個人資料以及顯示帳單、行程行程的地方，在修改的姓名中，使用了

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>{{ 1+1 }}<br>``` |

這個 payload 導致的，漏洞大概成因是 Python Flask 中預設使用的模板引擎是 Jinja2，在 Jinja2 中可使用些許的 Python 語法來幫助產生 HTML (當然有 Sandbox)

所以 {{ 1+1 }} 就被 Python 解析成 2 並且放置信件中寄到我的信箱，更詳細的內容可參考由 PortSwigger (BurpSuite 開發人員) 在 BlackHat 2015 發表的 [Server-Side Template Injection:RCE for the modern webapp](https://www.blackhat.com/docs/us-15/materials/us-15-Kettle-Server-Side-Template-Injection-RCE-For-The-Modern-Web-App-wp.pdf)

所以現在我可以使用 Jinja2 的語法有限度的在姓名欄位寫 Python 程式碼了! 如在姓名欄位依照 Jinja2 語法填入

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>{% for c in [1,2,3] %}{{ c,c,c }}{% endfor %}<br>``` |

利用模板引擎叫 Uber 伺服器幫我們跑個 FOR 迴圈，結果還會寄到你信箱XD

![](https://blog.orange.tw/posts/2016-04-bug-bounty-uber-ubercom-remote-code_7/1154b6733b7e40d2-03.png)

![](https://blog.orange.tw/posts/2016-04-bug-bounty-uber-ubercom-remote-code_7/56812f048d715f9c-04.png)

成功執行 FOR 迴圈! 不過在文章前面有提到，可以執行 Python Code 但並不是無限制，Jinja2 中有 Sandbox 來對危險的用法、函數進行防護。

不過這個對常玩 CTF 的人絕對不是問題，在各個比賽中很常出現 Python 的 Sandbox 繞過用到的手法可以直接拿來這裡用!

詳細技術細節可以參考

- [Exploring SSTI in Flask/Jinja2](https://nvisium.com/blog/2016/03/09/exploring-ssti-in-flask-jinja2/), [Part2](https://nvisium.com/blog/2016/03/11/exploring-ssti-in-flask-jinja2-part-ii/)
- [利用 Python 特性在 Jinja2 模板中執行任意代碼](http://blog.knownsec.com/2016/02/use-python-features-to-execute-arbitrary-codes-in-jinja2-templates/)

如使用

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>{{ [].__class__.__base__.__subclasses__() }}<br>``` |

可列出所有引用的模組， 如

![](https://blog.orange.tw/posts/2016-04-bug-bounty-uber-ubercom-remote-code_7/30a9f09949a99fab-05.png)

會顯示是空的是因為被 HTML < > 包起來了，檢視原始信件就可以看到了XD

額外一提的是在引用模組中看到 Celery，因此可以猜測網站大致架構應該是：

從 Riders.uber.com 這個進入點修改姓名後存進資料庫

不過為了寄送簡訊以及信件等耗時的工作，使用 Asynchronous Task 機制交給後方的 Worker

而當 Worker 再從資料庫抓出姓名產生模板時使用串接的方式直接將模板產生所以導致了這次遠端代碼執行 :P

寫到這，最後廢言一下，對我來說，其實玩 Bug Bounty 獎金什麼都是額外的，最主要的是可以找出別人找不出、別人發現不了的漏洞，回報並且讓別人也認同你的發現，這其中得到的成就感才是最爽的XD

![](https://blog.orange.tw/posts/2016-04-bug-bounty-uber-ubercom-remote-code_7/2d105e71683bc031-06.png)