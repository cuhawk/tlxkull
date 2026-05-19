---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/
title: "HITCON Won the 2nd in DEFCON 22 CTF Final | Orange Tsai"
author: "Orange Tsai"
published: 2014-08-25T16:00:00.000Z
description: "HITCON 周結束，終於有個時間可以來寫寫個日記，順便記錄一下今年出征的一些記錄 ，這種感覺有點像是電競選手（ 不過比的是駭客技巧就是了XD ） 感謝所有參與的隊友們、以及提供幫助的各位朋友、前輩，以及全額贊助 HITCON 去 Las Vegas 比賽的趨勢科技 （ 幾十個人來回的 Las Vegas 機票真的不便宜… ）。 這邊讓我一一感謝一下強者我隊友們！（排名不分先後xD）"
---

* * *

![preview](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/a8eda9c1952b5e35-01.png)

[HITCON](http://hitcon.org/) 周結束，終於有個時間可以來寫寫個日記，順便記錄一下今年出征的一些記錄 ，這種感覺有點像是電競選手（ 不過比的是駭客技巧就是了XD ）

感謝所有參與的隊友們、以及提供幫助的各位朋友、前輩，以及全額贊助 HITCON 去 Las Vegas 比賽的 [趨勢科技](http://blog.trendmicro.com.tw/?p=9116) （ 幾十個人來回的 Las Vegas 機票真的不便宜… ）。 這邊讓我一一感謝一下強者我隊友們！（排名不分先後xD）

- Sean, Jeffxx, Atdog, Ddaa, Lucas 隊伍中的最主要負責找漏洞的神手，沒有他們我們的攻擊能力絕對不可能那麼強
- Jerry 隊伍的防護全部靠他了，甚至強到只要看到攻擊形式就可以把未知的漏洞給修補起來！（順道一提這位強者現在才大二喲！）
- Shik, Peter 兩位 ACM World Final 神手，除了分析外，比賽中只要把攻擊代碼給他們，接下來就可以自動得分了，另外這次 DEFCON 的比賽有道題目是必須要跟演算法有關，有個他們兩個根本就 OP！
- DM4 比賽主機的狀況幾乎都是他在顧的，他寫 script 程式的質量速度真的讓人驚歎！（ 可惡是 Ruby 派XD ）

當然並不是所有隊員只做一件事，大部份的狀況都是一個隊員要身兼多職，分析 pcap 啦、顧主機、找洞啦等

HITCON 隊伍從初賽的臨時抱佛腳賽進決賽名單，到最後成功獲得世界最大比賽 DEFCON CTF 的亞軍，到現在還是很難以相信。

![](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/0cfaf5a6b28a6e72-02.png)

相關比賽紀錄可以參考：

- [Defcon 22 Quals Baby’s First heap](http://ddaa.logdown.com/posts/200443-defcon-22-quals-babys-first-heap) by Ddaa
- [Defcon CTF Quals 2014 - Nonameyet write up](http://blog.orange.tw/2014/05/defcon-ctf-quals-2014-nonameyet-write-up.html) by Orange
- [Defcon 22 Qual Sick Writeup](http://www.jeffxx.com/blog/2014/05/19/defcon-ctf-22-qual-sick-writeup/) by Jeffxx （ 也為最後一小時打入決賽驚險記錄 ）

# [百度 BCTF](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/\#%E7%99%BE%E5%BA%A6-BCTF "百度 BCTF") 百度 BCTF

出征的第一場，是參加由中國百度所主辦的 [BCTF](http://bctf.cn/) 為 HITCON （ 原 HITCON 217 ）的前哨戰，做為第一次參加的正式 Attack & Defense 比賽，很大程度上讓我們體驗了 DEFCON CTF 的規則，驗證了許多原本的猜想，也在此場戰役中發想出了許多 Idea 在後面的 DEFCON CTF 都有被我們給用上，也可以說是「如果沒有這場比賽的熟悉，直接到了 DEFCON CTF 現場應該會手忙腳亂吧XD」

（ 主辦方技術支持 Blue Lotus，picture from [Alan](https://www.facebook.com/alan2nala) ）

![](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/dff7085c6d41f137-03.jpg)

比賽間，在第一天我們順利找出 secret-guard 題目的 0day 造成分數爬升的差距使得後面隊伍無法追趕，也因為有了先手優勢使我們可以在此場戰役中取得冠軍！

在最後一天有個隊伍試圖想對我們使用 fork bomb 來個奮力一搏，不過我們在他們要使用前修補了漏洞XD

以及由於第二天分數相差懸殊，使得我們可以在多餘的時間去實作以及分析其他的技巧的可行性，例如

1. 分析其他隊伍的修補是否完整，是否有可以繞過的地方。
2. 在其他隊伍的 Gamebox 上架 socks server
3. 分析其他隊伍如何防護等

在此也認識了些聊得來的中國朋友，算是意外的收獲～

# [SECUINSIDE CTF FINAL](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/\#SECUINSIDE-CTF-FINAL "SECUINSIDE CTF FINAL") SECUINSIDE CTF FINAL

出征的第二場，是由韓國 [ASRT](http://ls-al.org/) 所主辦的 [SECUINSIDE](http://secuinside.com/2014/) CTF Final，在韓國首爾所舉辦，採用的是 Jeopardy 解題形的方式，作為資安大國的韓國，SECUINSIDE 獎金也是世界最多，第一名可得 88 萬台幣，也開始在韓國知道、認識到世界上的一些強隊，如 9447 是 Australia 的一個學校社團，隊員中竟然還有女生（ 連 DEFCON CTF Final 都有出現，好像真的滿厲害的xD ），韓國 BOB 計劃培養出來的隊伍，看到老外跟老外之前好像都是認識的一樣，有點反省自己的英文水平還是不好

決賽共十隊參賽，在這次的比賽中 HITCON 隊伍表現並不如預期，尋找弱點的速度輸其他隊伍、相關的平台也沒準備好，如

1. IOS App Reversing
2. Windows 8 App Reversing
3. SPARC pwn
4. …

題目中還看到李家同教授的 DNA Crypto 理論，在比賽途中沒人解出時主辦單位還直接貼 [論文](http://algo2006.csie.dyu.edu.tw/paper/2/A21.pdf) 上來，不過總體來說從這場戰役中體驗到我們的差距仍然距離世界等級有一段差距，如

1. 此場比賽中的冠軍，是由天才駭客 Geohot 一個人所組的隊伍 tomcr00se 抱走 88 萬
2. 日本隊伍 Binja 在此場戰役中取得了進入之前在 DEFCON CTF 初賽無法取得的決賽門票，有題我們一直無法解出的 300 分 pwn 題目，還是由一名日本天才高中生解出
3. 也有看到某隊伍 Skype 視窗好多人啦XD

比賽途中也有一些趣事如 BalalaikaCr3w 這個隊伍在嘗試送 Key 時送太快造成主辦單位 Race Condition 所以 200 分的題目可以送兩次變 400 分XD 以及主辦單位特地幫各個國家準備隊伍名稱配上國旗的大帆布看到也真是太感動！

![](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/bd64d9733871d066-04.jpg)

相關比賽紀錄可以參考：

- [SECUINSIDE CTF Finals 2014 Writeup - Reversing 100](http://blog.dm4.tw/blog/2014/07/13/secuinside-2014-final-writeup-reversing-100/) by DM4

# [DEFCON CTF FINAL](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/\#DEFCON-CTF-FINAL "DEFCON CTF FINAL") DEFCON CTF FINAL

由美國 [LEGITBS](http://legitbs.net/) 所主辦的 DEFCON CTF ，也是世界上相關比賽中最出名的一個，被喻為是駭客界的奧林匹克，由

- DEFCON 初賽選出前十二名隊伍
- 世界上各區域種子賽的冠軍共八隊

共 20 隊，比賽也是採取 Attack & Defense 形式，共三天。 在比賽中，我們一直無法搞定網路環境

（ 需要可以支援 VLAN tag 999 的機器 ）

後來跟其他隊伍交流，聽說 Blue Lotus 還特地去買了個 Switch 還不能用XD，另外個隊伍就比較土豪說他們直接用 Mac Mini 當 Router 來用xDDD

這就是我們這三天要拼死要保護的主機，並且要想盡辦法入侵同樣別人的這台主機

（ picture from [Alan](https://www.facebook.com/alan2nala) ）

![](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/8441ac4daa3f6aab-05.jpg)

DEFCON 同時也會世界最大知名駭客研討會，三、四天的行程吸引了萬人以上不論駭客、鎖匠、教授、資安專家等齊聚 Las Vegas，下面則是入場門牌，一張 200 還 220 美金XD

「DO NOT OBEY」也是這次這次 Badge 的標語，整個也很符合駭客的習性xD

![](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/eef4fbef1731ca2f-06.jpg)

比賽中有幾個特別的成就我這邊列一下，

## [1. HITCON 隊伍為全場三天內第一個取得分數的隊伍，主辦單位為此顯示 First Blood 於螢幕上](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/\#1-HITCON-%E9%9A%8A%E4%BC%8D%E7%82%BA%E5%85%A8%E5%A0%B4%E4%B8%89%E5%A4%A9%E5%85%A7%E7%AC%AC%E4%B8%80%E5%80%8B%E5%8F%96%E5%BE%97%E5%88%86%E6%95%B8%E7%9A%84%E9%9A%8A%E4%BC%8D%EF%BC%8C%E4%B8%BB%E8%BE%A6%E5%96%AE%E4%BD%8D%E7%82%BA%E6%AD%A4%E9%A1%AF%E7%A4%BA-First-Blood-%E6%96%BC%E8%9E%A2%E5%B9%95%E4%B8%8A "1. HITCON 隊伍為全場三天內第一個取得分數的隊伍，主辦單位為此顯示 First Blood 於螢幕上") 1\. HITCON 隊伍為全場三天內第一個取得分數的隊伍，主辦單位為此顯示 First Blood 於螢幕上

![](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/db7ef27de32fdce8-07.jpg)

## [2. 結束時被冠軍 PPP 過來除了詢問 Eliza 的 exploit 如何撰寫外，使用的後門形式還被稱讚「Your crontab is so cute.」](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/\#2-%E7%B5%90%E6%9D%9F%E6%99%82%E8%A2%AB%E5%86%A0%E8%BB%8D-PPP-%E9%81%8E%E4%BE%86%E9%99%A4%E4%BA%86%E8%A9%A2%E5%95%8F-Eliza-%E7%9A%84-exploit-%E5%A6%82%E4%BD%95%E6%92%B0%E5%AF%AB%E5%A4%96%EF%BC%8C%E4%BD%BF%E7%94%A8%E7%9A%84%E5%BE%8C%E9%96%80%E5%BD%A2%E5%BC%8F%E9%82%84%E8%A2%AB%E7%A8%B1%E8%AE%9A%E3%80%8CYour-crontab-is-so-cute-%E3%80%8D "2. 結束時被冠軍 PPP 過來除了詢問 Eliza 的 exploit 如何撰寫外，使用的後門形式還被稱讚「Your crontab is so cute.」") 2\. 結束時被冠軍 PPP 過來除了詢問 Eliza 的 exploit 如何撰寫外，使用的後門形式還被稱讚「Your crontab is so cute.」

## [3. 從 Youtube 可以看出在這段時間內，我們 HITCON 是唯一可以吃到 PPP 分數的一隊](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/\#3-%E5%BE%9E-Youtube-%E5%8F%AF%E4%BB%A5%E7%9C%8B%E5%87%BA%E5%9C%A8%E9%80%99%E6%AE%B5%E6%99%82%E9%96%93%E5%85%A7%EF%BC%8C%E6%88%91%E5%80%91-HITCON-%E6%98%AF%E5%94%AF%E4%B8%80%E5%8F%AF%E4%BB%A5%E5%90%83%E5%88%B0-PPP-%E5%88%86%E6%95%B8%E7%9A%84%E4%B8%80%E9%9A%8A "3. 從 Youtube 可以看出在這段時間內，我們 HITCON 是唯一可以吃到 PPP 分數的一隊") 3\. 從 Youtube 可以看出在這段時間內，我們 HITCON 是唯一可以吃到 PPP 分數的一隊

legitbs flag capture video - YouTube

Tap to unmute

[legitbs flag capture video](https://www.youtube.com/watch?v=1UT3qXHduts) [hawaii john](https://www.youtube.com/channel/UCW56IP5xpxxkxFANxV_tWuw)

hawaii john5 subscribers

[Watch on](https://www.youtube.com/watch?v=1UT3qXHduts)

## [最後是所有隊友的合作無間!](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/\#%E6%9C%80%E5%BE%8C%E6%98%AF%E6%89%80%E6%9C%89%E9%9A%8A%E5%8F%8B%E7%9A%84%E5%90%88%E4%BD%9C%E7%84%A1%E9%96%93 "最後是所有隊友的合作無間!") 最後是所有隊友的合作無間!

在比賽第二天的下午到最後一天結束，在被冠軍 PPP 強力猛攻的時期培養出了一個 SOP 流程

1. 發現被攻擊，立即記錄下何時於哪個服務失分
2. 立即有人馬分析封包流量，找出其他隊伍所使用的 exploit 並嘗試 Replay
3. 如無法成功則送至另外一組人馬手上分析，
4. 從 exploit 大致分析為何種攻擊方式，並且交給負責的人為自己的服務上 Patch
5. 將此 exploit 寫成自動化攻擊程式

所以在比賽後半場，大家都在緊張兮兮深怕 Skype 有訊息跳出來，因為只要一有訊息跳出來則可能代表，又被其他隊伍攻擊成功了，這兩天所消耗的精神真得滿可觀的。

PPP 為冠軍真的當之無愧，除了第二天下午發現的 justify 0day 外，還有 wdub, imap 一直連打（ 雖可以 justify replay ，但目測有 ASLR 約 200 ~ 300 次約才有一次成功 ）

連唯一的 Badge 題，雖然在比賽中 PPP 沒有成功利用，但事後 [LegitBS](https://legitbs.net/2014/) 敘述 PPP 是有成功做出這題的 exploit 的，但是由於他們設計 Badge 題目的錯誤使得 IP 網段在 10.5.0.??? 的 PPP 無法成功取得分數（ 估計是 Null byte 問題 XD ）

事後想想，第三天快結束時， 由於 HITCON 隊伍剛好是以四強的身分坐在 PPP 對面，我的正對面就是 Geohot，那時他突然大吼了一聲，現在想起來也許就是完成 Badger exploit 的感覺，真的是 Never Give Up。

（ picture from [Legitbs](https://legitbs.net/2014/) ）

![](https://blog.orange.tw/posts/2014-08-hitcon-win-2nd-in-defcon-22-ctf-final/cd306c14973df1ad-08.jpg)

比賽最後五分鐘，主辦單位放起了 Europe 的 [The Final Countdown](https://www.youtube.com/watch?v=9jK-NcRmVcw)，除了歌曲剛好倒數五分鐘外，最後結束全場的歡呼拍手有了個努力三天有個完美 Ending 的感覺。

比賽的冠軍根據傳統會得到八張黑色 DEFCON Badge，也就是傳說中的 DEFCON 黑卡，憑此卡可以每年免費進入 DEFCON 會場，亞軍以下就沒有什麼獎品了，純粹是知名度！

（去年亞軍還有比賽用的 ARM 開發版的說xDD）

其他關於 DEFCON CTF Final 心得可以參考：

- [Defcon 22 Final HITCON 參賽心得 (上)](http://www.jeffxx.com/blog/2014/08/13/2014-defcon-22-final-can-sai-xin-de-shang/) by Jeffxx
- [defcon 22 CTF final diaries](http://ddaa.logdown.com/posts/220500-defcon-22-ctf-diaries) by Ddaa

* * *

最後的結語，來點感嘆

在 HITCON ENT 跟中國朋友聊到，有個現象，做二進制 Binary 的看不起做 Web、做滲透的，做 Web、滲透的覺得看到做二進制的就很屌。

做 Web、滲透除了技能是基本功必要具備外，更多的是技巧（Trick）的了解、想像力以及對於資訊的敏感度，但很多的人以為技巧就是技巧，沒什麼

引用一下 「 [中國黑客傳說：我是超級黑](http://taosay.net/index.php/2013/02/27/%E4%B8%AD%E5%9B%BD%E9%BB%91%E5%AE%A2%E4%BC%A0%E8%AF%B4%EF%BC%9A%E6%88%91%E6%98%AF%E8%B6%85%E7%BA%A7%E9%BB%91/)」中的文句如是說，

> 「技巧也要點一下你才會通啊，不點你可能永遠也通不了」

以同樣難度的題目為例，Binary 可能要花時間分析就可以有結果，Web 只要懂個比較少人懂的 Trick 就可以馬上得分，而且往往有更多的Web 技巧、滲透技巧是無法以 CTF 題目的方式呈現的的，但這樣看下來，好像做 Binary 的就比較厲害，做 Web 或是滲透的就因為花的時間少比較不受重視 :(

不可否認的，如果是從資安要入門很多人會推薦從 Web Security 入門，因為是簡單快速能有成就感的一門科目，我也這麼推薦，比起如 Pwnable 或是 Reversing 等需要大量基礎知識的學科，Web 這方便真的相對好入門，以學習曲線舉例會如

Web Security、滲透一開始的學期曲線低，但後期的曲線相對是直線攀升的

（所以很多人會覺得自己做 Web 或是滲透卡在高不成、低不就的階段）

Binary 相關一開始的學習難度高、曲線高，但後期只要努力便可以穩定爬升

但很多人只看到好入門這邊做文章，與簡單沒技術畫上等號，然後看到 Kernel、Ring0、組語等就高潮了。

（好像在某些地方也有這種現象…）

最後 HITCON 隊伍需要各方好手加入，歡迎你們！

附上此次 [亮相館](http://imagingimage.blogspot.tw/) 為本次比賽所拍的紀錄片

HITCON in DEFCON 22 CTF Final 紀錄片 - YouTube

Tap to unmute

[HITCON in DEFCON 22 CTF Final 紀錄片](https://www.youtube.com/watch?v=XcneHvq1hbY) [Orange Tsai](https://www.youtube.com/channel/UCnweRFxfA-xpTbkb83yfBog)

Orange Tsai3.75K subscribers

[Watch on](https://www.youtube.com/watch?v=XcneHvq1hbY)