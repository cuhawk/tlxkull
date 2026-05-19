---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2014-03-pwned-ctf-leaderboard-git/
title: "Pw3ed CTF LeaderBoard - Git Misconfiguration & SQL Injection | Orange Tsai"
author: "Orange Tsai"
published: 2014-03-30T16:00:00.000Z
description: "（前情提要） 某月某日晚上，人在外面有約正巧無法參與在週末所舉辦的 CTF，這次的這個 CTF 競賽似乎是某個國家某個實驗室第一次舉辦的對外 CTF 競賽，在 Ctftime.org 也有獨立頁面，結束回到家時競賽正好剩下最後幾個小時，在朋友的 Wargame 討論頻道內看到了一個鏈結 這次的競賽很特別的一點是，有所謂 hidden flag 的設計，會有額外的分數藏在計分板網站的各個角落，在對網"
---

* * *

（前情提要）

某月某日晚上，人在外面有約正巧無法參與在週末所舉辦的 CTF，這次的這個 CTF 競賽似乎是某個國家某個實驗室第一次舉辦的對外 CTF 競賽，在 [Ctftime.org](http://ctftime.org/) 也有獨立頁面，結束回到家時競賽正好剩下最後幾個小時，在朋友的 Wargame 討論頻道內看到了一個鏈結

這次的競賽很特別的一點是，有所謂 hidden flag 的設計，會有額外的分數藏在計分板網站的各個角落，在對網站搜索的過程中，會不會找著找著就不小心找進去計分板裡面呢？ 這篇就是再說這樣的一個故事

（目前網站漏洞已修復）

一開始看到的是這個鏈結

> http://vulnerability-leader-board/error\_log

![](https://blog.orange.tw/posts/2014-03-pwned-ctf-leaderboard-git/1eb8eb7afc01f64d-01.png)

看起來是網站開發時的 Error Log 以及 Apache 的設置沒設置好，看到這樣子的內容暴露在網路上，可以想像整個網站的防護應該不是很完整的，因此我們繼續來深入看看

整個網站是用 PHP, Apache, MySQL, Ubuntu 所架設，PHP 的部分使用了 MVC 的架構，整個網站逛了一下發現安全設定似乎沒有很嚴謹，表面上看起來很 ok 不過在一些小細節的處理上滿容易噴出錯誤訊息的

如把 ?team=foo 置換成 ?team\[\]=foo 很容易噴出如

> Warning: substr() expects parameter 1 to be string, array given in /home/deploy/vulnerability-leader-board/handlers/team\_handler.php on line 146

等錯誤訊息。

再翻翻發現了

> http://vulnerability-leader-board/phpmyadmin/
>
> http://vulnerability-leader-board/.git/

的目錄。 許多開發者會將 Git, SVN 或者 CVS clone(checkout) 到正式上線的網站上，這時如果未將權限設置好，攻擊者可以透過這些版本控管軟體所留下的資訊，取得敏感資訊。

（某些狀況甚至可以獲取原始碼）

> http://vulnerability-leader-board/.git/config
>
> http://vulnerability-leader-board/.git/index

![](https://blog.orange.tw/posts/2014-03-pwned-ctf-leaderboard-git/0fd8cebaae3ca4d6-02.png)

從 config 可以看到，使用了 [github.com](http://github.com/) 的平台，以及哪個 Repository 以及 Github 帳號資訊等（不過在那個時候無法從 Github 存取到，似乎那個 repo 是 private 的或者已經移除）

從 index 可以取得網站目錄結構，懶人可以直接 `curl http://vulnerability-leader-board/.git/index | strings` 快速爬出

![](https://blog.orange.tw/posts/2014-03-pwned-ctf-leaderboard-git/69fb09e8df48e1a2-03.png)

從目錄結構已經可以發現些有趣的東西了，已經可以看到一些題目的 FLAG 了，因為某些題目的 FLAG 是以檔案形式放在網站上，也可以發現一些 Hidden Flags。 接著再依照剛剛的目錄結構對現有檔案做一次觀察，發現了開發者留下的測試頁面

> http://vulnerability-leader-board/nemoscript.php

點進去會發現

![](https://blog.orange.tw/posts/2014-03-pwned-ctf-leaderboard-git/8748b0e3fcc2d1af-04.png)

> 「 pass a team 」

恩，好，你要隊伍名稱我就給你嘛 ʅ（´◔౪◔）ʃ 我的隊伍名稱叫做 「 a’ 」

> http://vulnerability-leader-board/nemoscript.php?team=a’

![](https://blog.orange.tw/posts/2014-03-pwned-ctf-leaderboard-git/3e2862d871f22a7d-05.png)

看來是 SQL Injection，而且還是個 Error Based 的 SQL Injection … 再來看看一下權限高不高，

> http://vulnerability-leader-board/nemoscript.php?team=a’ and exists (select \* from mysql.user)%23

恩… 可以存取 mysql.user 以及又跑在 localhost 以及又存在 phpmyadmin，這麼完美的組合好久沒遇到了

接著就是丟到 [owst](http://blog.orange.tw/2011/05/project-web-security-toolkit.html) … 可以讀取檔案（/etc/passwd）

![](https://blog.orange.tw/posts/2014-03-pwned-ctf-leaderboard-git/d4341906384db031-06.png)

所有的註冊隊伍使用者（ [#plainpass](http://plainpass.com/)）

![](https://blog.orange.tw/posts/2014-03-pwned-ctf-leaderboard-git/1410131cd1e3e1f4-07.png)

接下來就是最 High 的，所有題目的 Flags

![](https://blog.orange.tw/posts/2014-03-pwned-ctf-leaderboard-git/1efc33b093331bfa-08.png)

到這裡囉，舉辦一次 CTF 競賽也是很辛苦的！

總而言之這是一次很有趣的體驗 :P