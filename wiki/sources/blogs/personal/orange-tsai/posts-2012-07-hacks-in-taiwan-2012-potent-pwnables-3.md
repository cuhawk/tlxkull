---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2012-07-hacks-in-taiwan-2012-potent-pwnables-3/
title: "Hacks in Taiwan 2012 Potent Pwnables 3 出題詳解 | Orange Tsai"
author: "Orange Tsai"
published: 2012-07-23T16:00:00.000Z
description: "照慣例今年還是有個經典遊戲題，皮卡丘打排球相信是許多人童年的回憶XD 這次的題目是 - Hack Ｐikachu. (Pikachu is a hacker’s name.) 檔案可以在 http://rsghost.org/backup/wargame.hitcon.org/ 下載 (感謝 RSGhost 備份)，主要考的觀念是 Poison Ivy 的 stack overflow 問題"
---

* * *

![preview](https://blog.orange.tw/posts/2012-07-hacks-in-taiwan-2012-potent-pwnables-3/3be3e2765196a836-01.jpg)

照慣例今年還是有個經典遊戲題，皮卡丘打排球相信是許多人童年的回憶XD

這次的題目是 \- Hack Ｐikachu. (Pikachu is a hacker’s name.)

檔案可以在 [http://rsghost.org/backup/wargame.hitcon.org/](http://rsghost.org/backup/wargame.hitcon.org/) 下載 (感謝 RSGhost 備份)，主要考的觀念是 Poison Ivy 的 stack overflow 問題

Poison ivy 是一套滿有名的木馬程式，其中最大的特性是木馬的 server 端可以變成 shellcode 的形式，使得木馬要加密、變形、免殺變得異常方便！ 所以在很多地方都可以看到它的蹤跡…XD

又由於 Poison ivy 目前版本( 2.3.2 ) 已不再更新，要更新的請花錢買付費版XD 並要要執行必須在關閉 DEP 的環境下，所以 Exploit 環境較單純利用起來相對容易，有興趣研究的人可以到 [http://www.poisonivy-rat.com/](http://www.poisonivy-rat.com/) 下載

主程式被 binary patch 改了一些 call function 以及加上了兩個 sections，一個是 Poison Ivy 的 shellcode，另一個是 Anti VMware, SEH 的一些 little and easy tricks，又因為主程式是 Single Thread 又自己加上 CreateThread 等

心血來潮丟到 Virustotal 上測試沒想到只有4家可以偵測到orz 都還沒出大絕招就只剩下四家這… XDD

![](https://blog.orange.tw/posts/2012-07-hacks-in-taiwan-2012-potent-pwnables-3/3bf0d8e3ae3d5499-02.jpg)

舊版 2.3.2 的 Poison Ivy 在 Windows 7 上跑不起來，原因是因為 Windows 7 在取得 ImageBase 上的方式不同，詳細原因可以參考我以前寫過的文章 [Download Exec shellcode fix & for Windows 7](http://orange-tw.blogspot.tw/2011/04/downloadexec-shellcode-fix-for-windows.html)

Patch 方法除了自己改外網路上有人已經有寫好的小程式可以直接用

[http://existence.vacau.com/PI/pi.html](http://existence.vacau.com/PI/pi.html)

將產生的 shellcode 直接貼上去就可以進行 patch ! 所以在 Windows XP or Windows 7 無論 32bits 或是 64bits 皆可以執行。

由於主程式是 Windows98/me 時代撰寫的( 1997 (C)SACHI SOFT )，跑在 Windows 7 64bits 上有點怪怪的小 BUG (會 crash)，猜測是 Heap Allocation 的問題(未證實)，解決方法是將相容性改成 Windows 98/me 就可以正常執行了!

至於如何判斷是 Poison Ivy ，除了行為外，還可以從

- Poison Ivy 預設的 port 是 3460
- Poison Ivy 預設的 mutex 是 )!VoqA.I4 等看出

接著就可以直接用 Metasploit 進行攻擊

> [http://www.metasploit.com/modules/exploit/windows/misc/poisonivy\_bof](http://www.metasploit.com/modules/exploit/windows/misc/poisonivy_bof)

![](https://blog.orange.tw/posts/2012-07-hacks-in-taiwan-2012-potent-pwnables-3/f436aeb31a2ccba2-03.jpg)

<(￣︶￣)\> 得到 key

額外補充:

駭客年會兩天約有200~300個連線(累計紀錄)連過來，忘記把盛況拍下來了 //flee

> How to hack a hacker, this is a good question. XD