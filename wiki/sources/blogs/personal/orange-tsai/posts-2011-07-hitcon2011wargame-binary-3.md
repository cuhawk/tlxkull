---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2011-07-hitcon2011wargame-binary-3/
title: "台灣駭客年會 HITCON2011，Wargame Binary 3出題心得 & 解法 | Orange Tsai"
author: "Orange Tsai"
published: 2011-07-23T16:00:00.000Z
description: "心得：很久以前就想出一題類似要輸入↑ ↑ ↓ ↓ ← → ← → B A會跳key的題目了XD 題目下載點 from rsghost ，小時候的回憶，特訓99 XD 用UPX加殼過後有改過OEP，For fun，讓檢測殼軟體(Ex: Peid)混淆XD 很簡單的殼，脫殼可以靠ESP定律，或者看得出是UPX直接bp popad可以找到最原始的OEP 這個遊戲其實有DEBUG MO"
---

* * *

![preview](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-binary-3/fa2b1941dfa36b22-01.png)

心得：很久以前就想出一題類似要輸入↑ ↑ ↓ ↓ ← → ← → B A會跳key的題目了XD

題目 [下載點](http://rsghost.web.fc2.com/HIT201_wargame/10.0.15.1/files/BINARY/Orange.EXE) from [rsghost](http://rsghost.web.fc2.com/HIT201_wargame/10.0.15.1/) ，小時候的回憶，特訓99 XD

用UPX加殼過後有改過OEP，For fun，讓檢測殼軟體(Ex: Peid)混淆XD

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-binary-3/21e48af603ea762d-02.png)

很簡單的殼，脫殼可以靠ESP定律，或者看得出是UPX直接bp popad可以找到最原始的OEP

這個遊戲其實有DEBUG MODE的，開啟原始遊戲後可以用Winhex或者Dump memory觀察到

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-binary-3/0e6925d82667a78d-03.png)

- reset
- another
- omitback
- simpleback
- fullback
- chicken
- quit
- butterfly
- maniac
- paranoia
- booston
- off
- paranoiamax
- hequil
- basia
- quti
- version
- test
- slow
- love
- desu?

有這些指令可以使用，這題透過修改其中一個的字串以前對應的函數來出題

只要在遊戲開始輸入

> c (倒退鍵) a (倒退鍵) (倒退鍵) b (倒退鍵) (倒退鍵) (倒退鍵)

就可以取得Key

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-binary-3/9167086ec9e8c92c-04.png)

開啟遊戲時會將DEBUG String xor解碼，所以未執行直接觀察原始檔會找不到有甚麼有意義的字串 ，位置在 0x00401242，xor的key是0xff

這題的解法當初是設想需要Condition BreakPoint Message Queue的 KeyDown Event來進行Trace ，追的過程中會發現修改了0x0040394A改成了一個長jmp

這題還滿多人解出來的XD 不過應該都不是用靠輸入key的方式 :P