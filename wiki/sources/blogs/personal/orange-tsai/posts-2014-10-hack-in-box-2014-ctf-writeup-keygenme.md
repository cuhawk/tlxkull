---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2014-10-hack-in-box-2014-ctf-writeup-keygenme/
title: "Hack in the Box 2014 CTF Writeup - KeygenMe with RSA | Orange Tsai"
author: "Orange Tsai"
published: 2014-10-18T16:00:00.000Z
description: "這次被以 HITCON 的身份邀請到馬來西亞參加 HITB 2014 CTF，照慣例來寫篇 Write Up 這次結果只有亞軍第二名有點殘念，第二天下午攻擊程式停了四小時少了幾萬分，不然應該有望第一XD 不過也是經驗，有個自動化攻擊以及送 Flag 的 Framework 真的還滿重要的，沒準備好也是失策XDRZ HITB 這次是以 Attack & Defense 加上 Jeopardy"
---

* * *

這次被以 HITCON 的身份邀請到馬來西亞參加 [HITB 2014 CTF](http://conference.hitb.org/hitbsecconf2014kul/capture-the-flag/)，照慣例來寫篇 Write Up

這次結果只有亞軍第二名有點殘念，第二天下午攻擊程式停了四小時少了幾萬分，不然應該有望第一XD

不過也是經驗，有個自動化攻擊以及送 Flag 的 Framework 真的還滿重要的，沒準備好也是失策XDRZ

HITB 這次是以 Attack & Defense 加上 Jeopardy 形式舉辦，每個隊伍有一檯實體主機，上面 run 個 Ubuntu 14.04 on VMPlayer。 隊伍要想辦法自己取得 root 以及找到服務開啟，到比賽截止前主辦方共放出了 4 個 Daemon 以及 7 個 Challenge

比賽形式是以宇宙機戰的模式進行，每回合成功 Keep 住 Daemon 獲得 100 生命值，成功攻擊其他隊伍 Daemon Flag 獲得 200 生命值，而 Challenges 則是加分項目，成功解開一個獲得 2000 - 3000 不等的生命值

![](https://blog.orange.tw/posts/2014-10-hack-in-box-2014-ctf-writeup-keygenme/c763790921f60538-01.jpg)

而雖然這次的比賽是以 Attack & Defense 型式進行，不過各 Daemon 服務比較像是 Reversing & Puzzle 的綜合，成功解開後 Daemon 會自行讀取 Flag 吐給你，所以整場比賽也都不會用到 Overflow, Shellcode, ROP… 等，另外的 Challenge 則比較偏向 Reversing 以及 Stego 的形式。

這次的 Write Up 就是本次 CTF Challenge 中的一題 Reversing 題目，雖然本身是 Web 狗、滲透狗，不過在這種對我們不友善的地方還是只能哭著下去看 T\_\_\_\_\_T

題目是一題 Keygen Me，標題是 HITB2013KUL 不知道是 Typo Error 還是去年出的題目沒有用上放到今年開XDDDDD

![](https://blog.orange.tw/posts/2014-10-hack-in-box-2014-ctf-writeup-keygenme/0ed121c0db14386e-02.png)

很直觀的就是一個驗證程式要寫出註冊碼，正確會顯示 Correct 錯誤會顯示 Wrong，理所當然使用爆破直接改跳轉點是沒有用的。 二話不說拖進 IDA!

![](https://blog.orange.tw/posts/2014-10-hack-in-box-2014-ctf-writeup-keygenme/b6dd2ca8f438a4d1-03.png)

一堆臭臭長長的 Function 沒有辨識出來，OEP 怪怪的不過不影響分析，Visual C++ 編出來的程式多了一些怪程式區段滿機車的 T\_\_\_T

使用 GetDlgItemText 可以把關鍵地方定位出來，仔細觀察發現程式有使用 MIRACL 的 C++ 大數函示庫，可以從 [這篇](http://bbs.pediy.com/showthread.php?t=35599) 文章中將各個函數作用大致識別出來，如 subtract, divide, powmod 等，如此一來分析輕鬆了許多！

接著花了幾個小時分析，把大致程式邏輯給弄懂如下

（IDA 靜態分析中雖然沒有看到對於 e 的賦值，不過可以透過動態追蹤會發現 e = 17）

看起來是對 Input 進行處理後使用 RSA 加密起來並且最後與密文進行比對，成功則是正確的 Flag！ RSA 依靠大質數保護演算法的安全，其中用到的大質數乘積為

> 7906961983747432626460011685427449111190647169309825535629493220735583689550836202522449

滿短的應該可以很快解出，丟進 [Factordb](http://www.factordb.com/) 中可以馬上分解出

> 7906961983…49 = 88899280969284710491078307117271523349979587 x 88942923919478497069248398794539034790292827

所以現在有了

> p = 88899280969284710491078307117271523349979587
>
> q = 88942923919478497069248398794539034790292827
>
> e = 17
>
> n = 7906961983…49

複習了一下好久沒碰的 RSA，當把 N 解開有了 P 跟 Q 後接下來可以求出 Private Key D 來，這邊使用 rsatool 來用

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>``` | ```<br>orange@me:~$ python rsatool.py \<br>    -p 88899280969284710491078307117271523349979587 \<br>    -q 88942923919478497069248398794539034790292827 \<br>    -e 17 \<br>    -n 7906961983747432626460011685427449111190647169309825535629493220735583689550836202522449<br>Using (p, q) to initialise RSA instance<br>n = fe6277ac25de48eedb829ad5458bc32e0dd678c80a123ecd73a54cb08eb719017cc88c751<br>e = 17 (0x11)<br>d = d17e446fa6b70ee2d2e40709fd09afcb92ec72dbe4c3614dcfb8a25b150b817622e58ae49<br>p = 3fc8381a552f012766fc3078a07f8103761c3<br>q = 3fd03c2f3c9b63f9208ee942c904d16536d5b<br>``` |

得到 D 之後就可以解上面要解的密文了！

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>orange@me:~$ echo 021abe7c17d73978e63835b0e76ad6120f5a3f8148f3de87da6e5b07bf7b76041c78aedf0c |  \<br>    xxd -r -p | python rsacrack.py \<br>        -d d17e446fa6b70ee2d2e40709fd09afcb92ec72dbe4c3614dcfb8a25b150b817622e58ae49 \<br>        fe6277ac25de48eedb829ad5458bc32e0dd678c80a123ecd73a54cb08eb719017cc88c751 | xxd -p -c 64<br>0000000000000000000000000000000000000000000001c2f3db8f478caafc84b10ed113<br>``` |

得到明文 `1c2f3db8f478caafc84b10ed113`，不過這是運算過後的結果 =\_\_\_=

所以要根據剛剛的運算弄出逆算法（數學苦手XDRZ）

最後推出

> 0x1c2f3db8f478caafc84b10ed113 \* 66772239585999913610952241123315507216972277506025821^N + 29411180916569003283374190496632319086172136623216324

出來的結果就可以以十進位五個一組五個一組推回原本的 FLAG ，又因為是 mod 的逆運算，根據 N 的值答案可以不只一組（ N=1,2,3 … ），最後得出當 N=1 的時候會有 printable 的解!

> 2385648152415111590458116323765417147676516881603229820532451315251688506013237646763

解碼後為

![](https://blog.orange.tw/posts/2014-10-hack-in-box-2014-ctf-writeup-keygenme/82b52c8df1349f80-04.png)