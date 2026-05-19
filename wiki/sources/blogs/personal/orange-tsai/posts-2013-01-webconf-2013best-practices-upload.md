---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2013-01-webconf-2013best-practices-upload/
title: "WebConf 2013「Best Practices - The Upload」投影片 | Orange Tsai"
author: "Orange Tsai"
published: 2013-01-12T16:00:00.000Z
description: "很榮幸被邀請到 WebConf 2013 分享關於 Web Security 上相關的議題 WebConf 2013 網站 第一在六、七百人的場子演講，還是在兩天最後一場議程的主會議廳，所幸迴響還不錯，梗幾乎都有人懂發問也算踴躍太棒了 xD (超怕會在上面沒梗自嗨>///<) 下面是這次演講的投影片(刪掉了一張不能洩漏出來的投影片:P) 主要講了上傳相關的"
---

* * *

很榮幸被邀請到 WebConf 2013 分享關於 Web Security 上相關的議題 [WebConf 2013 網站](http://www.webconf.tw/)

第一在六、七百人的場子演講，還是在兩天最後一場議程的主會議廳，所幸迴響還不錯，梗幾乎都有人懂發問也算踴躍太棒了 xD (超怕會在上面沒梗自嗨>///<)

下面是這次演講的投影片(刪掉了一張不能洩漏出來的投影片:P)

主要講了上傳相關的問題

1. 黑名單? 白名單?
2. 文件解析漏洞
3. 程式設計師檢測檔案類型的方法以及繞過

其實還可以在把一些相關現成 editor 的安全性放進去不過來不及XD

Best Practices - The Upload - Speaker Deck

[![Avatar for Orange](https://secure.gravatar.com/avatar/5f7ab2ea341a883bf8572190738e864e?s=47)](https://speakerdeck.com/p8361)

[Best Practices - The Upload](https://speakerdeck.com/p8361/best-practices-the-upload)

by [Orange](https://speakerdeck.com/p8361)

[![Speaker Deck](https://d1eu30co0ohy4w.cloudfront.net/assets/mark-white-8d908558fe78e8efc8118c6fe9b9b1a9846b182c503bdc6902f97df4ddc9f3af.svg)](https://speakerdeck.com/)

## Slide 1

### Slide 1 text

2013/01/13 @ WebConf




## Slide 2

### Slide 2 text

• aka Orange
• 2009
• 2011, 2012
• 2011 AVTOKYO
• 2012 PHP Conf
• 2012 VXRLConf
•
–
– Web Security
– Windows Vulnerability
Exploitation



## Slide 3

### Slide 3 text

• CHROOT Security Group
• NISRA
• Disclosed
– MS12-071 / CVE-2012-4775
• http://blog.orange.tw/



## Slide 4

### Slide 4 text

No content


## Slide 5

### Slide 5 text

No content


## Slide 6

### Slide 6 text

1\. Reconnaissance
– Google Hacking, Reversed Whois, AXFR ……
2\. Scanning
– SYN/ACK Scan, TCP NULL/FIN/Xmas/Mainmon/Window
Scan, SCTP INIT Scan, Hydra, Nessus ……
3\. Gaining Access
– Heap/Stack/V-table Overflow, ROP, Heap Spray, System
Misconfiguration, Metasploit, Exploit Database ……
4\. Maintaining Access
– Privilege Escalation, Trojan, Backdoor, Rootkit, Code/DLL
Injection, API Hook, LD\_PRELOAD, Anti AV/Debugger ……
5\. Clearing Tracks
– Syslog, WTMP/UTMP, Event Log, Shell(Bash/Explorer) ……



## Slide 7

### Slide 7 text

No content


## Slide 8

### Slide 8 text

– Upload?
– Web log? Dabase log?



## Slide 9

### Slide 9 text

•
•
–
– Runtime.getRuntime().exec( cmd )
– <%eval request("cmd") %>
– \_\_import\_\_('os').system(cmd)



## Slide 10

### Slide 10 text

https://github.com/evilcos/python-webshell/



## Slide 11

### Slide 11 text

No content


## Slide 12

### Slide 12 text

No content


## Slide 13

### Slide 13 text

No content


## Slide 14

### Slide 14 text

No content


## Slide 15

### Slide 15 text

No content


## Slide 16

### Slide 16 text

No content


## Slide 17

### Slide 17 text

No content


## Slide 18

### Slide 18 text

http://www.lu-chen.com/



## Slide 19

### Slide 19 text

No content


## Slide 20

### Slide 20 text

No content


## Slide 21

### Slide 21 text

•
– PHP CGI PATH\_INFO
•
– /index.php/module/login
– /index/module/login
•
– /userfiles/mypic.jpg
– /userfiles/mypic.jpg/nihao.php



## Slide 22

### Slide 22 text

•
– Huffman table
– EXIF
•
– copy /b rst.jpg+backdoor.php dst.jpg
•
– http://orange.tw/exif.jpg



## Slide 23

### Slide 23 text

No content


## Slide 24

### Slide 24 text

No content


## Slide 25

### Slide 25 text

•
•
•
•



## Slide 26

### Slide 26 text

•
–
–
–
•
– php phtml php3 php4 php5
– asp asa cer cdx shtml
– aspx asax ascx ashx asmx
http://www.hitcon.org/download/2010/5\_Flash Exploit.pdf#Page.20



## Slide 27

### Slide 27 text

No content


## Slide 28

### Slide 28 text

– AddHandler application/x-httpd-php .jpg
•
– .php\*



## Slide 29

### Slide 29 text

No content


## Slide 30

### Slide 30 text

https://speakerdeck.com/allenown/the-internet-is-not-safe-webconf-taiwan-2013



## Slide 31

### Slide 31 text

https://www.facebook.com/TWWDB



## Slide 32

### Slide 32 text

(htaccess ^ ^)



## Slide 33

### Slide 33 text

•
•
– user.jpg  .jpg
– user.php.jpg  .jpg
– user.php.xxx  .php
– user.php.xxx.ooo  .php



## Slide 34

### Slide 34 text

No content


## Slide 35

### Slide 35 text

•
– IIS < 7
– Asp.net ^\_\_<
•
– http://webconf.orange.tw/files/a.asp/user.jpg
•
– http://webconf.orange.tw/files/user.asp;aa.jpg
user.asp;aa.jpg



## Slide 36

### Slide 36 text

No content


## Slide 37

### Slide 37 text

No content


## Slide 38

### Slide 38 text

filename
Content-Type
File header



## Slide 39

### Slide 39 text

No content


## Slide 40

### Slide 40 text

• Update your sense and software.
• User controlled filename is always dangerous.
– Whatever filename, extension or temporary
filename.
• Use Image library to valid or strip the image.
• Disabled the directory’s execution permission
you uploaded to.



## Slide 41

### Slide 41 text

•
•
– htaccess
•
– Apache
– IIS
•
•



## Slide 42

### Slide 42 text

No content


## Slide 43

### Slide 43 text

Q & A



## Slide 44

### Slide 44 text

Orange@chroot.org