---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2013-07-0-day-0-day-easy-talk-happy-fuzzing/
title: "0-Day 輕鬆談 (0-Day Easy Talk) - Happy Fuzzing Internet Explorer | Orange Tsai"
author: "Orange Tsai"
published: 2013-07-18T16:00:00.000Z
description: "這是我在台灣駭客年會 Hacks in Taiwan HITCON 2013 的演講 0-Day 怎麼來？ Fuzzing 做為一種尋找漏洞的方式，讓你連躺著都有 0-Day 進帳。 這是一場輕鬆的演講， 分享一些 Fuzzer 的設計、Fuzzing 上的心得、Fuzzing Internet Explorer 上的方向。 最後為本次 HITCON 揭露一個未公開的 0-Day。"
---

* * *

這是我在台灣駭客年會 Hacks in Taiwan HITCON 2013 的演講

* * *

0-Day 怎麼來？ Fuzzing 做為一種尋找漏洞的方式，讓你連躺著都有 0-Day 進帳。

這是一場輕鬆的演講， 分享一些 Fuzzer 的設計、Fuzzing 上的心得、Fuzzing Internet Explorer 上的方向。 最後為本次 HITCON 揭露一個未公開的 0-Day。

0-Day 輕鬆談 - Happy Fuzzing Internet Explorer - Speaker Deck

[![Avatar for Orange](https://secure.gravatar.com/avatar/5f7ab2ea341a883bf8572190738e864e?s=47)](https://speakerdeck.com/p8361)

[0-Day 輕鬆談 - Happy Fuzzing Internet Explorer](https://speakerdeck.com/p8361/0-day-qing-song-tan-happy-fuzzing-internet-explorer)

by [Orange](https://speakerdeck.com/p8361)

[![Speaker Deck](https://d1eu30co0ohy4w.cloudfront.net/assets/mark-white-8d908558fe78e8efc8118c6fe9b9b1a9846b182c503bdc6902f97df4ddc9f3af.svg)](https://speakerdeck.com/)

## Slide 1

### Slide 1 text

0-Day 輕鬆談 (0-Day Easy Talk)


## Slide 2

### Slide 2 text

0-Day 甘苦談 (0-Day WTF Talk)


## Slide 3

### Slide 3 text

這是一場簡單的演講
This is an Easy Talk



## Slide 4

### Slide 4 text

分享一些我的 Fuzzing 心得
Share Some Fuzzing Review of Mine



## Slide 5

### Slide 5 text

以及很順便的丟個 0-Day 出來
And Disclosed a 0-Day in Passing



## Slide 6

### Slide 6 text

大家好
Hello, Everyone



## Slide 7

### Slide 7 text

我是 Orange
This is Orange Speaking



## Slide 8

### Slide 8 text

現任大學生
I am a College Student, Now



## Slide 9

### Slide 9 text

CHROOT.org 成員
Member of CHROOT.org



## Slide 10

### Slide 10 text

DevCo.re 打工中
Part-Time Work at DevCo.re



## Slide 11

### Slide 11 text

揭露過一些弱點
Disclosed Some Vulnerabilities
cve 2013-0305

cve 2012-4775
(MS12-071)



## Slide 12

### Slide 12 text

About Me
•  蔡政達 aka Orange
•  2009 台灣駭客年會競賽
冠軍
•  2011, 2012 全國資安競賽
金盾獎冠軍
•  2011 東京 AVTOKYO 講師
•  2012 香港 VXRLConf 講師
•  台灣 PHPConf, WebConf,
PyConf 講師

•  專精於
–  駭客攻擊手法
–  Web Security
–  Windows Vulnerability
Exploitation



## Slide 13

### Slide 13 text

如果對我有興趣可以到
blog.orange.tw
If You are Interesting at Me. You Can Visit
blog.orange.tw



## Slide 14

### Slide 14 text

我專注於


## Slide 15

### Slide 15 text

但今天來聊聊 0-Day 以及
Fuzzing (不是我專門的領域 QQ)
But Today Let's Talk About 0-Day and Fuzzing
(I am Not Expert in This, But Just Share)



## Slide 16

### Slide 16 text

Conference-Driven 0-Day
n. 名詞

釋義: 為了研討會生 0-Day



## Slide 17

### Slide 17 text

在找 0-Day 中的一些筆記
Some Notes in Finding 0-Day



## Slide 18

### Slide 18 text

這次我們討論 IE
This Time We Talk About IE



## Slide 19

### Slide 19 text

http://www.forbes.com/sites/andygreenberg/2012/03/23/shopping-for-zero-
days-an-price-list-for-hackers-secret-software-exploits/



## Slide 20

### Slide 20 text



Hacker's Good Friend



## Slide 21

### Slide 21 text

方法

•  White Box
– Code Review (IE5.5 Source Code)
– 二話不說丟進 IDA
•  Black Box
– Fuzzing



## Slide 22

### Slide 22 text

Fuzzing

•  Garbage in Garbage out
•  理論上可以找到所有漏洞
– 前提是你有無限的時間…



## Slide 23

### Slide 23 text

「時間越多，

0-Day 越多」






 -⾙貝拉克.歐巴⾺馬








## Slide 24

### Slide 24 text

Fuzzing Model
Generator
Debugger
Result
Logger



## Slide 25

### Slide 25 text

http://youtube.com/watch?v=m7Xg-YnMisE



## Slide 26

### Slide 26 text

Debugger
•  Windows Debug API
– DebugActiveProcess
– WaitForDebugEvent
– ContinueDebugEvent
– 好麻煩…

•  快速、客制化的 Debugger



## Slide 27

### Slide 27 text

PyDBG
A Pure Python Windows Debugger
Interface



## Slide 28

### Slide 28 text

Debug a Process

>>\> import pydbg
>>\> dbg = pydbg()
>>\> dbg.load( file )

\# or dbg.attach( pid )
>>\> dbg.run()



## Slide 29

### Slide 29 text

Set Breakpoint
>>\> dbg.bp\_set( address, callback )
>>\> dbg.set\_callback( exception\_code, callback )



## Slide 30

### Slide 30 text

Memory Manipulation
>>\> dbg.read( address, length )
>>\> dbg.write( address, length )



## Slide 31

### Slide 31 text

Crash Dump Report
>>\> bin = utils.crash\_binning.crash\_binning()
>>\> bin.record\_crash( dbg )
>>\> bin.crash\_synopsis()



## Slide 32

### Slide 32 text

Logger (Filter)
•  滿山滿谷的 崩潰
•  不是所有的 Crash 能成
為 Exploit
•  九成以上是 Null Pointer
只能當 DoS 用
–  mov eax, \[ebx+0x70\]
–  ; ebx = 0
•  EIP
•  Disassemble
–  jmp reg
–  call reg
–  call \[reg + CONST\]
•  Stack
•  SHE Chain



## Slide 33

### Slide 33 text

EIP = ffffffff !!?



## Slide 34

### Slide 34 text

0x50000 = 327680 = (65535 / 2)\*10


## Slide 35

### Slide 35 text

File Generator
The Most Important Part of Fuzzing



## Slide 36

### Slide 36 text

File Generator
•  內容越機歪越好，當然還是要符合 Spec
– 熟讀 Spec 熟悉 File Structure
– 想像力是你的超能力



## Slide 37

### Slide 37 text

Fuzzing 方向
1)  找新型態弱點


(麻煩但可通用)
2)  找已知型態弱點
(快速但有針對性)



## Slide 38

### Slide 38 text

新型態弱點
•  試試比較新、或比較少人用的
– HTML5 Canvas
– SVG




– VML
•  cve-2013-2551 / VML Integer Overflow / Pwn2own / VUPEN
– WebGL
•  IE11 Begin to Support



## Slide 39

### Slide 39 text

啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec
啃 Spec



## Slide 40

### Slide 40 text

已知型態弱點
•  研究以往的弱點我們可以知道
•  Internet Explorer is Not Good at
– Parsing DOM Tree
– Parsing with &
– Parsing with •  CTreeNode & CTableLayout




## Slide 41

### Slide 41 text

Pseudo Scenario of Use-After-Free

1.
2.

3.


4.


……
5.


6.

7.
1.
2.  var x =
document.getElementById( 'x' );
3.  var y =
document.getElementById( 'y' );
4.  x.innerHTML = 'AAAA…';
5.  y.length = 100px;
6.



## Slide 42

### Slide 42 text

Ex: CVE-2011-1260 (Not Full Version)
1.
2.
3.  document.body.innerHTML += "<object …>TAG\_1</object>";
4.  document.body.innerHTML += "<aid='tag\_3' style='…'>TAG\_3</a>";
5.  document.body.innerHTML +="AAAAAAA";
6.  document.body.innerHTML += "<strong style='…'>TAG\_11</strong>";
7.
8.



## Slide 43

### Slide 43 text

Ex: CVE-2012-1876 (Heap Overflow)
1.  setTimeout("trigger();",1);
2.
3.  4.
5.

1.  function trigger() {
2.  var obj\_col =
document.getElementById("132");
3.  obj\_col.width = "42765";
4.  obj\_col.span = 1000;
5.  }



## Slide 44

### Slide 44 text

Fuzzing with DOM Tree
https://www.facebook.com/zztao
•  Using DOM Methods to
Manipulate Objects
–  CreateElement
–  removeChild appendChild
–  InnerHTML outerText
–  createRange
–  addEventListener
–  select
–  …



## Slide 45

### Slide 45 text

Putting All Together
1)  Randomize HTML Node for Initial
2)  Manipulated Nodes with DOM Method
( Can Also Play with CSS at the Same Time)



## Slide 46

### Slide 46 text

No content


## Slide 47

### Slide 47 text

「運氣不好，

是⼈人品問題」






 -⾙貝拉克.歐巴⾺馬








## Slide 48

### Slide 48 text

Generally, Single Machine Run Can
Find 1 or 2 IE 0-Day in a Month
I Have Successfully Found 0-Days from IE6 to IE9,
For IE10+ I Haven't Tried Because I am Too Lazy : (



## Slide 49

### Slide 49 text

So I Found a 0-Day For HITCON
1)  Work on Internet Explore 8
2)  Mshtml.dll 8.0.6001.23501



## Slide 50

### Slide 50 text

http://www.zdnet.com/ie8-zero-day-flaw-targets-u-s-nuke-researchers-all-versions-
of-windows-affected-7000014908/



## Slide 51

### Slide 51 text

WinXP 還能再戰十年



## Slide 52

### Slide 52 text

Proof-of-Concept



## Slide 53

### Slide 53 text

## Slide 54

### Slide 54 text

Microsoft is Our Sponsor
I Can't Say More Detail Until Patched : (



## Slide 55

### Slide 55 text

Call Stack



## Slide 56

### Slide 56 text

call edx

(e10.950): Access violation - code c0000005 (!!! second chance !!!)
eax=3dbf00a4 ebx=0019bb30 ecx=037f12c8 edx=085d8b53
esi=0172b130 edi=00000000
eip=085d8b53 esp=0172b100 ebp=0172b11c iopl=0 nv up ei pl
zr na pe nc
cs=001b ss=0023 ds=0023 es=0023 fs=003b gs=0000
efl=00000246
085d8b53 ?? ???



## Slide 57

### Slide 57 text

Writing Exploit
•  Windows Protection
– DEP
– Luckily If Windows XP We Don't Care About ASLR
– Luckily It is Not IE10+ that It Hasn't vTable Guard




## Slide 58

### Slide 58 text

So, Writing Exploit is Easy
Heap Spray + ROP Enough



## Slide 59

### Slide 59 text

Demo



## Slide 60

### Slide 60 text

http://youtube.com/watch?v=QwKkfUcq\_VA



## Slide 61

### Slide 61 text

本來故事到這有個美滿的結局
Originally, This Story Have a Happy Ending



## Slide 62

### Slide 62 text

But
人生最精彩的就是這個 But



## Slide 63

### Slide 63 text

0-Day 在 HITCON 前一週被修掉了
Silent Fixed Before a Week of HITCON



## Slide 64

### Slide 64 text

What the



## Slide 65

### Slide 65 text

Proof-of-Concept
1.
2.
3.

4.
5.
6.
7.
8.  O
9.
1.  window.onload = function(){
2.  var x =
document.getElementById('e');
3.  x.outerText = '';
4.  }



## Slide 66

### Slide 66 text

Work on
•  mshtml.dll ……





\# ……
•  mshtml.dll …...





\# 2013 / 05 / 14
•  mshtml.dll 8.0.6001.23501
\# 2013 / 06 / 11
•  mshtml.dll 8.0.6001.23507
\# 2013 / 07 / 09



## Slide 67

### Slide 67 text

Reference
•  VUEPN Blog
– http://www.vupen.com/blog/
•  Paimei
– https://github.com/OpenRCE/paimei
•  Special Thank tt & nanika



## Slide 68

### Slide 68 text

Thanks