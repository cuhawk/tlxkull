---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2013-05-pycon2013-slide-django/
title: "Pycon2013 Slide - 駭客看 Django | Orange Tsai"
author: "Orange Tsai"
published: 2013-05-25T16:00:00.000Z
description: "在 Taiwan Python Conference 2013 的演講投影片 P.S. 我不是駭客，我不會寫 Django"
---

* * *

在 Taiwan Python Conference 2013 的演講投影片

_P.S. 我不是駭客，我不會寫 Django_

駭客看 Django - Speaker Deck

[![Avatar for Orange](https://secure.gravatar.com/avatar/5f7ab2ea341a883bf8572190738e864e?s=47)](https://speakerdeck.com/p8361)

[駭客看 Django](https://speakerdeck.com/p8361/hai-ke-kan-django)

by [Orange](https://speakerdeck.com/p8361)

[![Speaker Deck](https://d1eu30co0ohy4w.cloudfront.net/assets/mark-white-8d908558fe78e8efc8118c6fe9b9b1a9846b182c503bdc6902f97df4ddc9f3af.svg)](https://speakerdeck.com/)

## Slide 1

### Slide 1 text

駭客看 DJANGO

2013/05/26 @ PyCon




## Slide 2

### Slide 2 text

本場演講「四不一沒有」



## Slide 3

### Slide 3 text

四不一沒有
•  四不
– 我不是駭客
– 我不會寫 django
– 不會有 django 新漏洞（ 請洽七月台灣駭客年會 ）
– 這場演講不難，真的很簡單

•  沒有
– 這場演講沒有梗，有笑點的話拜託笑一下



## Slide 4

### Slide 4 text

About Me
•  蔡政達 aka Orange
•  2009 台灣駭客年會競賽
冠軍
•  2011, 2012 全國資安競賽
金盾獎冠軍
•  2011 東京 AVTOKYO 講師
•  2012 香港 VXRLConf 講師
•  台灣 PHPConf, WebConf 講
師

•  專精於
–  駭客攻擊手法
–  Web Security
–  Windows Vulnerability
Exploitation



## Slide 5

### Slide 5 text

About Me
•  CHROOT Security Group 成員
•  NISRA 資訊安全研究會 成員
•  Disclosed
– Windows MS12-071(CVE-2012-4775)
– Django (CVE-2013-0305)
•  Blog
– http://blog.orange.tw/



## Slide 6

### Slide 6 text

2013 年 X 月 O 日
天氣晴，今天是寒假的第一天…
幹, Rails 爆遠端執行代碼漏洞欸



## Slide 7

### Slide 7 text

No content


## Slide 8

### Slide 8 text

Django 會不會有同樣的問題呢？
學生什麼都沒有， 最多的就是時間。
來研究個 Open Source 專案很正常吧！



## Slide 9

### Slide 9 text

Vulnerabilities by Year
Django



## Slide 10

### Slide 10 text

Vulnerabilities by Year
Django
同樣情境跟 Rails 比較...



## Slide 11

### Slide 11 text

包含至少 8 個 Remote Code Execution


## Slide 12

### Slide 12 text

......




## Slide 13

### Slide 13 text

其實我今天是來推廣 Rails
開玩笑的啦我沒有要戰語言 T＿T



## Slide 14

### Slide 14 text

Django 現有的保護機制
Django Security Overview



## Slide 15

### Slide 15 text

Security Overview
•  Built-in XSS protection
•  Built-in SQL Injection protection
– ORM ( Q Object )
•  Built-in CSRF protection
– django.middleware.csrf.CsrfViewMiddleware
– Check REFERER header
– Compare CSRF token



## Slide 16

### Slide 16 text

Security Overview
•  Clickjacking protection
– django.middleware.clickjacking.XFrameOptionsMiddleware
– Optional in settings.py
– X-Frame-Options: SAMEORIGIN



## Slide 17

### Slide 17 text

Security Overview
•  Password hashing is more and more stronger
– Default is PBKDF2 hasher
– django.contrib.auth.hahsers
– 10000 iterators makes attackers say fuck …
$ time python pbkdf2.py mypassword
real
0m0.401s
user
0m0.260s
sys
0m0.074s



## Slide 18

### Slide 18 text

攻擊手法
Some Attacking Vectors



## Slide 19

### Slide 19 text

Some Attacking Vectors
•  VERY VERY BASIC attacking way
•  Weak admin password
•  Debug mode on
– Leakage URL pattern
– Leakage database password



## Slide 20

### Slide 20 text

Some Attacking Vectors
•  Cross-Site Scripting
– HttpResponse( html )
– {{ output\|safe }}
– {% autoescape off %}
•  Bad HTML style is always vulnerable
– [\# safe\\
–](https://speakerdeck.com/player/%7B%7B%20url%20%7D%7D) [\# unsafe\\
–](https://speakerdeck.com/player/%7B%7B)

## Slide 21

### Slide 21 text

Some Attacking Vectors
•  SQL Injection in Django ORM
– raw( sql ) is injectable
– extra( select=…, where=… ) is also injectable
•  String concatenate and format string are vulnerable
in any case



## Slide 22

### Slide 22 text

Some Attacking Vectors
•  Third-party module security
•  Py-bcrypt




\# CVE-2013-1895
– Authentication bypass
•  Python Image Library

\# CVE-2012-3443
– Denied-of-Service


•  Python XML.sax


\# CVE-2013-1664 & 1665
– XXE & XEE Injection



## Slide 23

### Slide 23 text

XML eXternal Entity Injection

Parsing XML Document Type Definition issue

\]>
&output;



## Slide 24

### Slide 24 text

XML Entity Expansion Injection



...
\]>
&z;



## Slide 25

### Slide 25 text

Secret Key Leakage Issue (1/3)
•  Django SECRET\_KEY use in
– get\_random\_string() using in csrf and hash generating
– Django session\_data encryption
– Django signed cookie encryption
– ……



## Slide 26

### Slide 26 text

Secret Key Leakage Issue (2/3)
•  Signed cookie store python object using Pickle
– \> HTTP\_COOKIE
– \> decode with secret\_key
– \> pickle.loads( … )




## Slide 27

### Slide 27 text

Pickle & cPickle
•  A module that serializing and De-serializing python
objects
•  Execute command
>>\> import pickle
>>\> pickle.loads( "cos\\nsystem\\n(S'/bin/sh'\\ntR." )
•  You can observe by using pickletools
>>\> import pickletools
>>\> pickletools.dis( "cos\\nsystem\\n(S'/bin/sh'\\ntR." )



## Slide 28

### Slide 28 text

Secret Key Leakage Issue (3/3)
•  Signed\_cookie is encoded by Pickle
– \> HTTP\_COOKIE

# malicious cookie
– \> decode with secret\_key
– \> pickle.loads( … )

# code execution
•  Protect your SECRET\_KEY ( ex .gitignore )



## Slide 29

### Slide 29 text

Conclusion
•  I think Django is a secure framework
•  More and more wrapper make the attack difficult
•  People is always the most dangerous things



## Slide 30

### Slide 30 text

Reference
•  Django Weblog
– https://www.djangoproject.com/weblog/
•  Security in Django
– https://docs.djangoproject.com/en/dev/topics/security/
•  CVE Details
– http://www.cvedetails.com/



## Slide 31

### Slide 31 text

Any Questions ?
Whatever can be asked



## Slide 32

### Slide 32 text

Thanks.