---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2011-12-xd/
title: "一百年度全國大專院校資安技能金盾獎 XD | Orange Tsai"
author: "Orange Tsai"
published: 2011-12-09T16:00:00.000Z
description: "Ya~ 冠軍！！！！ 今年是參加的第二年，真的有比去年進步成為第一名了！！XD 隊伍名稱： [NISRA] 台科大分舵 這樣講下來好像台灣兩大資安競賽都拿過冠軍了 //flee 2009 HIT 駭客年會 2011 金盾獎 去年的隊友 Taien 碩士畢業了，今年只有我以及強者 allenown 組隊，比較起去年其實感覺人數真的有差，兩個人下去比已經快看不完 & 沒"
---

* * *

Ya~ 冠軍！！！！

今年是參加的第二年，真的有比去年進步成為第一名了！！XD

隊伍名稱： **\[ [NISRA](http://www.nisra.net/)\] 台科大分舵**

這樣講下來好像台灣兩大資安競賽都拿過冠軍了 //flee

- [2009 HIT 駭客年會](http://orange-tw.blogspot.com/2010/02/hacks-in-taiwan-conference-2009-wargame.html)
- 2011 金盾獎

去年的隊友 Taien 碩士畢業了，今年只有我以及強者 [allenown](http://allenown.blogspot.com/) 組隊，比較起去年其實感覺人數真的有差，兩個人下去比已經快看不完 & 沒有時間去解所有題目了。

戰力分配大致如

- Linux 題目交給 allenown
- Windows 題目給我XD
- Web , Forensic, Misc就一起玩XD

# [雜紀:](https://blog.orange.tw/posts/2011-12-xd/\#%E9%9B%9C%E7%B4%80 "雜紀:") 雜紀:

- 早上依然是傳統在麥當勞度過早餐時間XD
- 今年一樣在恆逸資訊教育中心十二樓，捷運南京東路站一號出口出來就到了，這邊勾起一堆回憶整個超難過Q\_\_\_\_Q

![](https://blog.orange.tw/posts/2011-12-xd/83883196ff8410e5-01.jpg)

- 今年很棒有聽到去年的牢騷，午餐是傳說中的麥當勞山！！！XDD

![](https://blog.orange.tw/posts/2011-12-xd/3ff10296a572356b-02.jpg)

- 比賽時間五個小時(12:00 ~ 17:00)，前兩個半小時完全是沒有分數掛蛋的XD

![](https://blog.orange.tw/posts/2011-12-xd/ba91ab6f5452800d-03.jpg)

- 記分板會在比賽結束前三十分鐘關閉，以增加比賽刺激性，記分板關閉前照片XD

![](https://blog.orange.tw/posts/2011-12-xd/9a6ea6ef7e7b6078-04.jpg)

- 揭曉名次整個超緊張，跟交大 DSNS lab 爭奪一二名XD
- 喔喔還有贈品很不錯我好喜歡，一個滿大的手提袋XD
- 會後依然照慣例有個慶功宴這次在 [Vegas Vegas](http://vegas.smartweb.tw/) ~

# [題目：](https://blog.orange.tw/posts/2011-12-xd/\#%E9%A1%8C%E7%9B%AE%EF%BC%9A "題目：") 題目：

- 今年總題目數共 15 題
- 今年題目感覺還是以 Forensics 為大宗
- 兩個人比真的會發現題目做不完，有許多題目是我們根本都還沒看過去解的
- 今年多了幾題關於 Android 的題目，理所當然交給強者我隊友XDD
- 今年也多了幾題類似Capture the Flag的題目，提供你 Linux server 要你上 patch 以獲得key
- 經過兩個半小時，強者 allenown 解出題目五，終於破蛋了XD
- 有分數後就開始勢如破竹，整個緊張感都沒了一題一題解出來XD
- 其實應該分數可以再更高，題目四考的是資訊隱藏 Steganography，使用 Openpuff 解出來為一個 url.txt 的檔案，裡面是一個網址
- 誰會知道那個就是 key XDDD，如果取名為 key.txt 的話我就會把那串網址當 key 送QQ
- 題目三在最後似乎沒人解出所以提示大放送，給的提示幾乎就是解題的步驟，在 PE 可執行檔內多了一個奇怪的 section 叫做 .icst ，觀察一下可以利用 PE 的特性找出解密的 key
- 不過題目三解的方式好像跟題目沒關係XDDD
- 題目八考的是 SQL Injection，之前自己寫的 [Orange Web Security Toolkit](http://orange-tw.blogspot.com/2011/05/project-web-security-toolkit.html) 派上用場超爽
- 打個廣告 Web Security Toolkit 目前 update 到1.2.6，已經修正許多穩定性以及通用性的 BUG ，有機會的話再 release 出來XD
- 題目六考的觀念與 2011駭客年會 wargame 其中一題相似，給出一個被加密起來的可執行檔，使用 repeat key 的 xor 加密。xor 的 key 不只一個 byte，所以不能使用暴力破解，但由於 PE 檔案各個 sections 都會以填 0 的方式填到固定大小，可以透過觀察的方式找出xor的key。
- 題目十二跟題目六也是同樣的觀念， 但是分兩個部分，第一部分可以透過 pdf 的 header 來發現 xor 的 key 是 “%PDF” ，接著會解出一個被內嵌 javascript 的 PDF 檔案，好在以前有玩過一些分析惡意文件的手法，經過兩三層的 Javascript 混淆可以得到 Key為~XD

![](https://blog.orange.tw/posts/2011-12-xd/0954a0ec809970c6-05.png)

- 題目十三超機車的， 脫殼完只差修復 IAT 表不過就已經浪費掉大半的時間了
- 題目十三， D\_v\_ 出來面對XDD
- 今年的題目出的還不錯，不過還是有幾題淪為到比較偏猜謎
- 感謝各位工作人員~XD

其實工具真的不用帶太多，基本有了就好

這次其實沒用到甚麼工具大部分都是透過 Python 寫幾行 code 就可以解出來。 Reversing 逆向部分也只用到經典的 OllyDbg 以及 IDA pro，剩下的也只有自己習慣的 hex editor (010 editor) 以及慣用的瀏覽器就夠了XD

YA冠軍 ^\_\_\_\_\_<

\[ 照片暫時移除XD \]