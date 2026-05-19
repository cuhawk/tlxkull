---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/
title: "Olympic CTF 2014 CURLing 400 write up | Orange Tsai"
author: "Orange Tsai"
published: 2014-02-09T16:00:00.000Z
description: "Olympic CTF CURLing 400 的 write up，前言可以參考 Olympic CTF 2014 CURLing 200 write up 這題也是個人覺得出的非常不錯的題目之一，要解開必須很熟悉 PHP 的特性以及攻擊手法才能解開這道題目，網址打開是一個白畫面，有個 PHP 的錯誤訊息 Notice: Undefined index: rpc_json_call in &#"
---

* * *

[Olympic CTF](https://olympic-ctf.ru/) CURLing 400 的 write up，前言可以參考 [Olympic CTF 2014 CURLing 200 write up](http://blog.orange.tw/2014/02/olympic-ctf-2014-curling-200-write-up.html)

這題也是個人覺得出的非常不錯的題目之一，要解開必須很熟悉 PHP 的特性以及攻擊手法才能解開這道題目，網址打開是一個白畫面，有個 PHP 的錯誤訊息

> Notice: Undefined index: rpc\_json\_call in /var/www/index.php on line 27

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/aa07e4c85c65730a-01.png)

有再寫 PHP 的同學應該馬上可以知道這個 Notice 這是少了一個 GPC 參數的警告，所以我們可以自己補上 POST

> rpc\_json\_call=blablalba

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/bf9dd46ffd4a2516-02.png)

哦，會發現錯誤訊息變了，Google 搜尋一下 [JSON RPC](http://en.wikipedia.org/wiki/JSON-RPC) 的標準，照著標準送出

> rpc\_json\_call={“jsonrpc”: “2.0”, “method”: “subtract”, “params”: \[42, 23\], “id”: 1}

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/9c334d5ef660c42f-03.png)

會發現錯誤訊息又變了。 哦？不正確的 method 名稱？ 這時候可以猜測 method 名稱，不過笨蛋才會亂猜 :p 有範圍的猜測會比盲目的亂猜好太多，如果對 PHP 夠了解，會知道 PHP class 上都會有一些 [Magic Method](http://www.php.net/manual/en/language.oop5.magic.php) 存在，經過測試會發現 `__construct` 以及 `__wakeup` 是可以使用的！

送出:

> rpc\_json\_call={“jsonrpc”: “2.0”, “method”: “\_\_construct”, “params”:\[1,2\], “id”: 1}

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/e69539db2827ede9-04.png)

錯誤訊息又變了！ 不過從這次的錯誤訊息中可以得到資訊，知道了 `__construct` 的參數有三個，`log_dir`, `debug`, 以及 `state`，一樣偽造這三個參數的值後送出

> rpc\_json\_call={“jsonrpc”: “2.0”, “method”: “\_\_construct”, “params”:{“log\_dir”:”aa”, “debug”:true, “state”: “foo”}, “id”: 1}

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/038d4cfe7851d0fb-05.png)

發現是白畫面Ｔ＿＿＿＿Ｔ

到這邊卡住了一下，也許 `__construct` 只是去設定了 `log_dir`, `debug` 以及 `state` 這三個參數並沒有其他動作，所以是不是能在一個 reuqest 內執行兩次 JSON RPC CALL 呢（？

沒有翻得很勤勞不過猜測在一個 array 內送兩個 json hash 竟然可以XDDD

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>rpc\_json\_call=[<br>    {"jsonrpc": "2.0", "method": "__construct", "params":{"log_dir":"aa", "debug":true, "state": "foo"}, "id": 1},<br>    {"jsonrpc": "2.0", "method": "__wakeup", "params":{}, "id": 1}<br>]<br>``` |

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/88652366ab818572-06.png)

哦，loged ？ 啊是 log 三小XDDDD 把 `log_dir` 參數改一下改成 `/var/www` 看看

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/e3b0a31103f5ae03-07.png)

竟然說 permission denied XD 那嘗試 `/tmp/` 呢？

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/b67f0de80c3376d5-08.png)

看來是真的可以寫檔，那它寫了什麼呢？ 可以用 out-of-bound 的方法利用 PHP 支援的 [wrapper](http://www.php.net/manual/en/wrappers.php) 把內容給寫出來（PHP 支援的話甚至可以用 `except://ls` 執行指令）。 利用 `php://output` 可以把內容寫到網頁上:

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/ee915cfcc7ed1ea4-09.png)

原來寫了一個 serialize 過後的 PHP Object 進去，難怪會用到 `__wakeup` 的 magic method，所以我們可以嘗試把 webshell 寫到 /var/www/ 內

不過因為 server 的設定，似乎每隔一秒會定時把 `/var/www` 的檔案清掉，所以如果手速不夠快會一直以為自己沒有寫成功 （哭哭Ｔ＿＿＿Ｔ）

所以寫個 script 搞定！

執行 `ls -alh`

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/109bf4007fc40d72-10.png)

執行 `cat /FLAG`

> CTF{b15ffee30a117f418d1cede6faa57778}

![](https://blog.orange.tw/posts/2014-02-olympic-ctf-2014-curling-400-write-up/b134bdcbe7073444-11.png)

<(￣︶￣)>