---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2013-07-hitcon-2013-wargame-web-500/
title: "HITCON 2013 Wargame - Web 500 詳解 | Orange Tsai"
author: "Orange Tsai"
published: 2013-07-20T16:00:00.000Z
description: "Web 500 是一題 PHP source code review 找 vuln 的題目 1234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556<?php/* * * Written by Orange@chroot.org *"
---

* * *

Web 500 是一題 PHP source code review 找 vuln 的題目

![](https://blog.orange.tw/posts/2013-07-hitcon-2013-wargame-web-500/a8020f5c156d8aa1-01.png)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>``` | ```<br><?php<br>/*<br> *<br> *     Written by Orange@chroot.org<br> *<br> */<br> $cookie_key  =  "◢▆▅▄▃崩╰(〒皿〒)╯潰▃▄▅▇◣";<br> $iv          =  "00000000";<br>function safe( $s ) {<br>    if ( is_string( $s ) && strpos( $s, "\0" ) === false ) {<br>        if ( strpos( $s, 'O:' ) === false ) {<br>            return true;<br>        } else if ( ! preg_match('/(^|;|})s:[+\-0-9]+:"/', $s ) ) {<br>            return true;<br>        }<br>    }<br>    return false;<br>}<br>class qoo{<br>    var $key_var = "FakeKey";<br>    function __construct(){}<br>    function __destruct(){<br>        $keyfile = $this->key_var . ".php";<br>        $keyfile = basename( $keyfile );<br>        include( $keyfile );<br>        print $key;<br>    }<br>}<br>$checksum = $_COOKIE['checksum'];<br>if ( @md5($checksum) == '' ) {<br>    $auth_str = $_COOKIE['auth_str'];<br>    $auth_str = base64_decode( $auth_str );<br>    $auth_str = mcrypt_decrypt( MCRYPT_BLOWFISH,<br>                                $cookie_key,<br>                                $auth_str,<br>                                MCRYPT_MODE_ECB,<br>                                $iv );<br>    $auth_str = trim( $auth_str );<br>    if ( safe($auth_str) )<br>        unserialize( $auth_str );<br>    else<br>        die( 'Auth string is not safe' );<br>} else {<br>    new qoo();<br>}<br>?><br>``` |

其實考的滿簡單的，如果對 PHP Sec 有概念的話直覺會想到 unserialize 的 object inj

1. 利用 object inj 覆蓋 magic method(`__destruct`) 的 `key_var` 變量
2. 繞過 `md5() == ''` 可以用 `checksum[]=bla`
3. 繞過 safe 函數的話我不小心少寫一個 byte 所以可以用 s 大小寫置換來繞過，

不過我既然題目都已經出來了就算了XD 給你們簡單解吧!

原本繞過的方式是利用 PHP 對於 unserialize 實作的不一致來繞過

> O:3:”qoo”:1:{s:7:”key\_var”ts:3:”Key”;}

注意的 `ts:3` 這樣的形式 PHP unserialize 是可以接受的，有多少人是這樣解的給我說說看XDDD

這個問題有在 2012 年 12 月底的時候 ipb 漏洞出來被人探討過。

Invision Power Board 是一款滿流行的 PHP 討論版，由於在程式碼實作上會用到 unserialize，所以 ipb 寫了一個 check function 去檢查 unserialize 是否為惡意的，但由於 PHP 對 unserialize 上的實作缺陷，讓 check function 可被繞過(這點 PHP 後來有做 bug fix掉了(待確認中))

詳細細節可參考 80vul 寫的文章

> [http://www.80vul.com/pch/pch-010.txt](http://www.80vul.com/pch/pch-010.txt)