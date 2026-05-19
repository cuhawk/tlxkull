---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2014-05-defcon-ctf-quals-2014-nonameyet-write-up/
title: "Defcon CTF Quals 2014 - Nonameyet write up | Orange Tsai"
author: "Orange Tsai"
published: 2014-05-18T16:00:00.000Z
description: "記錄一下，Defcon 是世界駭客 CTF 比賽最盛大的賽事，每年都是每個國家資安社群比拼較勁的地方，前十二強可以進入八月在 Las Vegas 拉斯維加斯舉辦的決賽，在現場進行實際網路攻防的 Attack & Defense CTF 的比賽！ 在今年，終於湊齊台灣各方戰力順利打入決賽！ 計分板： 這次解了三、四題左右，這次感想有隊友可以 Cover 真的滿不錯的，討論時可以互相發現對"
---

* * *

記錄一下，Defcon 是世界駭客 CTF 比賽最盛大的賽事，每年都是每個國家資安社群比拼較勁的地方，前十二強可以進入八月在 Las Vegas 拉斯維加斯舉辦的決賽，在現場進行實際網路攻防的 Attack & Defense CTF 的比賽！

在今年，終於湊齊台灣各方戰力順利打入決賽！

計分板：

![](https://blog.orange.tw/posts/2014-05-defcon-ctf-quals-2014-nonameyet-write-up/f2109f9503bf8157-01.png)

這次解了三、四題左右，這次感想有隊友可以 Cover 真的滿不錯的，討論時可以互相發現對方沒有想到的盲點等

然後第一次嘗試吃 B 群，超有用的 xDDDD 另外這次與以往不同的是，

1. 題目的分類不像以往依 Web, Forensics, Recon, Binary … 等分類，而是依作者分類

2. 這次比賽共 24 題，幾乎七成都是 PWN 的題目

    這讓所有隊伍從一開始壓力就很大，整個 48 小時比賽節奏很慢

    （由於第一個解開題目的人有下一道題目的開題權，而 PWN 考驗的是細心的分析以及漏洞精準的利用，因此就算到了最後 12 小時還有約 1/3 的題目沒開）

3. 剩下的題目只有 Protocol 分析、純 Binary 逆向等，並沒有 Forensics

4. Web 題目只有兩題。

    （正確來說只有一題，另外一題是看起來是 Web 其實是 PWN ）

    （不過身為 Web Security 的愛好者，所以就算是扯到 PWN 還是要把它給解出來，因此特地把這篇寫出來記錄一下！）


這次的題目是 “Nonameyet”，這題約在倒數十二小時時出現，題目敘述是這樣的

> I claim no responsibility for the things posted here. nonameyet\_27d88d682935932a8b3618ad3c2772ac.2014.shallweplayaga.me:80

網址進去是一個 PHP 寫的照片分享以及上傳網站，很容易不難發現任意檔案下載的漏洞，可以從

> http://nonameyet\_27d88d682935932a8b3618ad3c2772ac.2014.shallweplayaga.me/index.php?page=./../../../../../../../../../../../../../etc/passwd

下載任意檔案。 雖然大部份功能都是 PHP 撰寫，但是上傳相片的部份卻是放在

> http://nonameyet\_27d88d682935932a8b3618ad3c2772ac.2014.shallweplayaga.me/cgi-bin/nonameyet.cgi

這是一個 C 語言所撰寫並編譯成 32 位元 ELF Linux Binary 的可執行檔 （檔案可從 [這裡下載](https://trello-attachments.s3.amazonaws.com/53678e28f6b188db76a0e640/5378a4c4f75d1d7626635f65/c6e927cd86ed0199fff8d7fb5aa56c3e/nonameyet.cgi)）

整個網站要入侵從 PHP 的視野來看無法拿到寫入的權限以及執行命令的權限，所能做的只能讀檔，但為了 PWN 他光讀檔是沒有用的，至少要可以執行指令！

所以從純 Web 的路下不了手只好從 cgi-bin 下的那個 nonameyet.cgi下手尋找看看是否有可利用的地方，仔細觀察了 一段 不只一段時間，發現

1. 程式會將從 multipart/form-data POST base 的值當作檔案名稱上傳至 cgi-bin/photos 資料夾下，但是 open 時權限為 420 無法執行
2. 無法直接寫入 PHP 木馬到目錄下
3. 會將上傳後的 POST base 檔名經過 base64 編碼後放在 Cookie 上，其中 base 的內容經過設計後可以 leak memory 洩漏記憶體內容
4. base 的值太長會發生 Heap Overflow 但初步看下去沒有可控之處
5. 有段程式邏輯再處理 base 的內容，尋找他所定義的 TAGS (ex: %Time%, %Date%, %Genr%) 等並取代成相對應於 POST 值的內容

發現有 Heap Overflow 後就一直再 Fuzz 有沒有方法可以控制 EIP 的（要去追有點累…XDrz）

嘗試了滿久都失敗最後發現在處理 TAG 時程式去引用時可以去控制一些暫存器內容，經過設計後可以使它產生 Stack Overflow

![](https://blog.orange.tw/posts/2014-05-defcon-ctf-quals-2014-nonameyet-write-up/475e2ea1ba4da1b7-02.png)

所以控制好 ecx 以及 esi 接下來讓 mov \[ebx\], eax 的 ebx 為一個合法的值就可以來到 ret

![](https://blog.orange.tw/posts/2014-05-defcon-ctf-quals-2014-nonameyet-write-up/5d51124eb693e877-03.png)

證明 EIP 可控，接下來就是構造 Exploit 的部份，由於 Stack 可寫，讓整個 Exploit 撰寫變得簡單許多，剩下比較機歪的的就是 ASLR 的部份，所以利用 ROP 的手法將 shellcode 放置在 Cookie 的部份，在利用原本程式中的 getenv 執行後結果 eax 會是我們的 shellcode

最後再找個 call eax 就可以成功執行 shellcode，所以最後構造的 ROP Chain 類似

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>``` | ```<br>AAAAAAA... # junk<br>0x00000000 #  要賦予給 n 的值<br>AAAAAAA... # junk<br>0x0804af93 # [ pop ebp / ret ]<br>0x0804f02c # 可寫的地方，會被設為 ebx 的值<br>0x08048a80 # .GOT getenv<br>0x08048cff # [call eax]<br>0x0804d55a # .RODATA 字串 HTTP_COOKIE<br>``` |

送出如下的 Request

![](https://blog.orange.tw/posts/2014-05-defcon-ctf-quals-2014-nonameyet-write-up/cf9130fe77677630-04.png)

即可拿到反連 shell

> The flag is: Angry Rhinoceros. And then I found five dollars.

![](https://blog.orange.tw/posts/2014-05-defcon-ctf-quals-2014-nonameyet-write-up/c435fc204997de62-05.png)