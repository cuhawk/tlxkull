---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/
title: "你用它上網，我用它進你內網! 中華電信數據機遠端代碼執行漏洞 | Orange Tsai"
author: "Orange Tsai"
published: 2019-11-10T16:00:00.000Z
description: "For non-native readers, this is a writeup of my DEVCORE Conference 2019 talk. Describe a misconfiguration that exposed a magic service on port 3097 on our country’s largest ISP, and how we find RCE o"
---

* * *

![preview](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/8af98f4ac35d5432-01.png)

For non-native readers, this is a writeup of my [DEVCORE Conference 2019](https://devco.re/conf/2019/) talk. Describe a misconfiguration that exposed a magic service on port 3097 on our country’s largest ISP, and how we find RCE on that to affect more than 250,000 modems :P

大家好，我是 Orange! 這次的文章，是我在 [DEVCORE Conference 2019](https://devco.re/conf/2019/) 上所分享的議題，講述如何從中華電信的一個設定疏失，到串出可以掌控數十萬、甚至數百萬台的家用數據機漏洞!

# [前言](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/\#%E5%89%8D%E8%A8%80 "前言") 前言

身為 DEVCORE 的研究團隊，我們的工作就是研究最新的攻擊趨勢、挖掘最新的弱點、找出可以影響整個世界的漏洞，回報給廠商避免這些漏洞流至地下黑市被黑帽駭客甚至國家級駭客組織利用，讓這個世界變得更加安全!

把「漏洞研究」當成工作，一直以來是許多資訊安全技術狂熱份子的夢想，但大部分的人只看到發表漏洞、或站上研討會時的光鮮亮麗，注意到背後所下的苦工，事實上，「漏洞研究」往往是一個非常樸實無華，且枯燥的過程。

漏洞挖掘並不像 [Capture the Flag (CTF)](https://ctf-wiki.github.io/ctf-wiki/)，一定存在著漏洞以及一個正確的解法等著你去解出，在題目的限定範圍下，只要根據現有的條件、線索去推敲出題者的意圖，十之八九可以找出問題點。 雖然還是有那種清新、優質、難到靠北的比賽例如 [HITCON CTF](https://ctf.hitcon.org/) 或是 [Plaid CTF](https://plaidctf.com/)，不過 「找出漏洞」 與 「如何利用漏洞」在本質上已經是兩件不同的事情了!

CTF 很適合有一定程度的人精進自己的能力，但缺點也是如果經常在限制住的小框框內，思路及眼界容易被侷限住，真實世界的攻防往往更複雜、維度也更大! 要在一個成熟、已使用多年，且全世界資安人員都在關注的產品上挖掘出新弱點，可想而知絕對不是簡單的事! 一場 CTF 競賽頂多也就 48 小時，但在無法知道目標是否有漏洞的前提下，你能堅持多久?

[在我們上一個研究中](https://devco.re/blog/2019/09/02/attacking-ssl-vpn-part-3-the-golden-Pulse-Secure-ssl-vpn-rce-chain-with-Twitter-as-case-study/)，發現了三個知名 SSL VPN 廠商中不用認證的遠端代碼執行漏洞，雖然成果豐碩，但也是花了整個研究組半年的時間(加上後續處理甚至可到一年)，甚至在前兩個月完全是零產出、找不到漏洞下持續完成的。 所以對於一個好的漏洞研究人員，除了綜合能力、見識多寡以及能否深度挖掘外，還需要具備能夠獨立思考，以及興趣濃厚到耐得住寂寞等等特質，才有辦法在高難度的挑戰中殺出一條血路!

漏洞研究往往不是一間公司賺錢的項目，卻又是無法不投資的部門，有多少公司能夠允許員工半年、甚至一年去做一件不一定有產出的研究? 更何況是將研究成果無條件的回報廠商只是為了讓世界更加安全? 這也就是我們 DEVCORE 不論在 [滲透測試](https://devco.re/services/penetration-test) 或是 [紅隊演練](https://devco.re/services/red-team) 上比別人來的優秀的緣故，除了平日軍火庫的累積外，當遇到漏洞時，也會想盡辦法將這個漏洞的危害最大化，利用駭客思維、透過各種不同組合利用，將一個低風險漏洞利用到極致，這也才符合真實世界駭客對你的攻擊方式!

# [影響範圍](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/\#%E5%BD%B1%E9%9F%BF%E7%AF%84%E5%9C%8D "影響範圍") 影響範圍

故事回到今年初的某天，我們 DEVCORE 的情資中心監控到全台灣有大量的網路地址開著 3097 連接埠，而且有趣的是，這些地址並不是什麼伺服器的地址，而是普通的家用電腦。 一般來說，家用電腦透過數據機連接上網際網路，對外絕不會開放任何服務，就算是數據機的 SSH 及 HTTP 管理介面，也只有內部網路才能訪問到，因此我們懷疑這與 ISP 的配置失誤有關! 我們也成功的在這個連接埠上挖掘出一個不用認證的遠端代碼執行漏洞! 打個比喻，就是駭客已經睡在你家客廳沙發的感覺!

透過這個漏洞我們可以完成:

1. 竊聽網路流量，竊取網路身分、PTT 密碼，甚至你的信用卡資料
2. 更新劫持、水坑式攻擊、內網中繼攻擊去控制你的電腦甚至個人手機
3. 結合紅隊演練去繞過各種開發者的白名單政策
4. 更多更多…

而相關的 CVE 漏洞編號為:

- [CVE-2019-13411](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-13411)
- [CVE-2019-13412](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-13412)
- [CVE-2019-15064](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-15064)
- [CVE-2019-15065](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-15065)
- [CVE-2019-15066](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-15066)

相較於以往對家用數據機的攻擊，這次的影響是更嚴重的! 以往就算漏洞再嚴重，只要家用數據機對外不開放任何連接埠，攻擊者也無法利用，但這次的漏洞包含中華電信的配置失誤，導致你家的數據機在網路上裸奔，攻擊者僅僅 **「只要知道你的 IP 便可不需任何條件，直接進入你家內網」**，而且，由於沒有數據機的控制權，所以這個攻擊一般用戶是無法防禦及修補的!

經過全網 IPv4 的掃瞄，全台灣約有 25 萬台的數據機存在此問題， **「代表至少 25 萬個家庭受影響」**，不過這個結果只在 **「掃描當下有連上網路的數據機才被納入統計」**，所以實際受害用戶一定大於這個數字!

而透過網路地址的反查，有高達九成的受害用戶是中華電信的動態 IP，而剩下的一成則包含固定制 IP 及其他電信公司，至於為何會有其他電信公司呢? 我們的理解是中華電信作為台灣最大電信商，所持有的資源以及硬體設施也是其他電信商遠遠不及的，因此在一些比較偏僻的地段可能其他電信商到使用者的最後一哩路也還是中華電信的設備! 由於我們不是廠商，無法得知完整受影響的數據機型號列表，但筆者也是受害者 ╮(╯\_╰)╭，所以可以確定最多人使用的 [中華電信光世代 GPON 數據機](https://broadband.hinet.net/rate.do) 也在受影響範圍內!

![](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/1945ab1892d3cd96-02.png)

( [圖片擷自網路](https://www.hungry.tw/2014/12/MiWifi.html))

# [漏洞挖掘](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/\#%E6%BC%8F%E6%B4%9E%E6%8C%96%E6%8E%98 "漏洞挖掘") 漏洞挖掘

只是一個配置失誤並不能說是什麼大問題，所以接下來我們希望能在這個服務上挖掘出更嚴重的漏洞! 軟體漏洞的挖掘，根據原始碼、執行檔以及 API 文件的有無可依序分為:

- 黑箱測試
- 灰箱測試
- 白箱測試

在什麼都沒有的的狀況下，只能依靠經驗以及對系統的了解去猜測每個指令背後的實作、並找出漏洞。

## [黑箱測試](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/\#%E9%BB%91%E7%AE%B1%E6%B8%AC%E8%A9%A6 "黑箱測試") 黑箱測試

3097 連接埠提供了許多跟電信網路相關的指令，推測是中華電信給工程師遠端對數據機進行各種網路設定的除錯介面!

![](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/6bb927bedccb69e6-03.png)

其中，可以透過 `HELP` 指令列出所有功能，其中我們發現了一個指令叫做 `MISC` ，看名字感覺就是把一堆不知道怎麼分類的指令歸類在這，而其中一個叫做 `SCRIPT` 吸引了我們! 它的參數為一個檔案名稱，執行後像是會把檔案當成 Shell Script 來執行，但在無法在遠端機器留下一個可控檔案的前提下，也無法透過這個指令取得任意代碼執行。 不過有趣的是，`MISC SCRIPT` 這個指令會將 `STDERR` 給顯示出來，因此可以透過這個特性去完成任意檔案讀取!

## [從黑箱進化成灰箱](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/\#%E5%BE%9E%E9%BB%91%E7%AE%B1%E9%80%B2%E5%8C%96%E6%88%90%E7%81%B0%E7%AE%B1 "從黑箱進化成灰箱") 從黑箱進化成灰箱

在漏洞的利用上，無論是記憶體的利用、或是網路的滲透，不外乎都圍繞著對目標的讀(Read)、 寫(Write) 以及代碼執行(eXecute) 三個權限的取得，現在我們取得了第一個讀的權限，接下來呢?

除錯介面貌似跑在高權限使用者下，所以可以直接透過讀取系統密碼檔得到系統使用者管理登入的密碼雜湊!

![](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/3b3df7f5e18f2e7b-04.png)

透過對 `root` 使用者密碼雜湊的破解，我們成功的登入數據機 SSH 將「黑箱」轉化成「灰箱」! 雖然現在可以成功控制自己的數據機，但一般家用數據機對外是不會開放 SSH 服務的，為了達到可以「遠端」控制別人的數據機，我們還是得想辦法從 3097 這個服務拿到代碼的執行權限。

![](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/8d28a1c889b1eda7-05.png)

整個中華電信的數據機是一個跑在 MIPS 處理器架構上的嵌入式 Linux 系統，而 3097 服務則是由一個在 `/usr/bin/omcimain` 的二進位檔案來處理，整個檔案大小有將近 5MB，對逆向工程來說並不是一個小數目，但與黑箱測試相較之下，至少有了東西可以分析了，真棒!

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>``` | ```<br>$ uname -a<br>Linux I-040GW.cht.com.tw 2.6.30.9-5VT #1 PREEMPT Wed Jul 31 15:40:34 CST 2019<br>[luna SDK V1.8.0] rlx GNU/Linux<br>$ netstat -anp | grep 3097<br>tcp        0      0 127.0.0.1:3097          0.0.0.0:*               LISTEN<br>$ ls -lh /usr/bin/omcimain<br>-rwxr-xr-x    1 root   root        4.6M Aug  1 13:40 /usr/bin/omcimain<br>$ file /usr/bin/omcimain<br>ELF 32-bit MSB executable, MIPS, MIPS-I version 1 (SYSV), dynamically linked<br>``` |

## [從灰箱進化成白箱](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/\#%E5%BE%9E%E7%81%B0%E7%AE%B1%E9%80%B2%E5%8C%96%E6%88%90%E7%99%BD%E7%AE%B1 "從灰箱進化成白箱") 從灰箱進化成白箱

現在，我們可以透過逆向工程了解每個指令背後的原理及實作了! 不過首先，逆向工程是一個痛苦且煩悶的經過，一個小小的程式可能就包含幾萬、甚至十幾萬行的組合語言代碼，因此這時挖洞的策略就變得很重要! 從功能面來看，感覺會存在命令注入相關的漏洞，因此先以功能實作為出發點開始挖掘!

整個 3097 服務的處理核心其實就是一個多層的 IF-ELSE 選項，每一個小框框對應的一個功能的實作，例如 `cli_config_cmdline` 就是對應 `CONFIG` 這條指令，因此我們搭配著 `HELP` 指令的提示一一往每個功能實作挖掘!

![](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/856dfa42a901ff31-06.png)

研究了一段時間，並沒有發現到什麼嚴重漏洞 :( 不過我們注意到，當所有指命都匹配失敗時，會進入到了一個 `with_fallback` 的函數，這個函數的主要目的是把匹配失敗的指令接到 `/usr/bin/diag` 後繼續執行!

![](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/998c266474f8b271-07.png)

`with_fallback` 大致邏輯如下，由於當時 Ghidra 尚未出現，所以這份原始碼是從閱讀 MIPS 組合語言慢慢還原回來的! 其中 `s1` 為輸入的指令，如果指令不在定義好的列表內以及指令中出現問號的話，就與 `/usr/bin/diag` 拼湊起來丟入 `system` 執行! 理所當然，為了防止命令注入等相關弱點，在丟入 `system` 前會先根據 `BLACKLISTS` 的列表檢查是否存在有害字元。

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>``` | ```<br>char *input = util_trim(s1);<br>if (input[0] == '\0' || input[0] == '#')<br>    return 0;<br>while (SUB_COMMAND_LIST[i] != 0) {<br>    sub_cmd = SUB_COMMAND_LIST[i++];<br>    if (strncmp(input, sub_cmd, strlen(sub_cmd)) == 0)<br>        break;<br>}<br>if (SUB_COMMAND_LIST[i] == 0 && strchr(input, '?') == 0)<br>    return -10;<br>// ...<br>while (BLACKLISTS[i] != 0) {<br>    if (strchr(input, BLACKLISTS[i]) != 0) {<br>        util_fdprintf(fd, "invalid char '%c' in command\n", BLACKLISTS[i]);<br>        return -1;<br>    }<br>    i++;<br>}<br>snprintf(file_buf,  64, "/tmp/tmpfile.%d.%06ld", getpid(), random() % 1000000);<br>snprintf(cmd_buf, 1024, "/usr/bin/diag %s > %s 2>/dev/null", input, file_buf);<br>system(cmd_buf);<br>``` |

而 `BLACKLISTS` 定義如下:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>char *BLACKLISTS = "|<>(){}`;";<br>``` |

如果是你的話，能想到如何繞過嗎?

答案很簡單! 命令注入往往就是這麼的簡單且樸實無華!

![](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/5dcfe9b6c80ad3e9-08.png)

這裡我們示範了如何從 PTT 知道受害者 IP 地址，到進入它數據機實現真正意義上的「指哪打哪」!

中華電信光世代 GPON 數據機遠端代碼執行 - YouTube

Tap to unmute

[中華電信光世代 GPON 數據機遠端代碼執行](https://www.youtube.com/watch?v=Pq00YUoBOsQ) [Orange Tsai](https://www.youtube.com/channel/UCnweRFxfA-xpTbkb83yfBog)

Orange Tsai3.75K subscribers

[Watch on](https://www.youtube.com/watch?v=Pq00YUoBOsQ)

# [後記](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/\#%E5%BE%8C%E8%A8%98 "後記") 後記

故事到這邊差不多進入尾聲，整篇文章看似輕描淡寫，描述一個漏洞從發現到利用的整個經過，從結果論來說也許只是一個簡單的命令注入，但實際上中間所花的時間、走過的歪路是正在讀文章的你無法想像的，就像是在黑暗中走迷宮，在沒有走出迷宮前永遠不會知道自己正在走的這條路是不是通往目的正確道路!

挖掘出新的漏洞，並不是一件容易的事，尤其是在各式攻擊手法又已趨於成熟的今天，要想出全新的攻擊手法更是難上加難! 在漏洞研究的領域上，台灣尚未擁有足夠的能量，如果平常的挑戰已經滿足不了你，想體驗真實世界的攻防，歡迎加入與我們一起交流蕉流 :D

# [通報時程](https://blog.orange.tw/posts/2019-11-HiNet-GPON-Modem-RCE/\#%E9%80%9A%E5%A0%B1%E6%99%82%E7%A8%8B "通報時程") 通報時程

- 2019 年 07 月 28 日 - 透過 TWCERT/CC 回報中華電信
- 2019 年 08 月 14 日 - 廠商回覆清查並修補設備中
- 2019 年 08 月 27 日 - 廠商回覆九月初修補完畢
- 2019 年 08 月 30 日 - 廠商回覆已完成受影響設備的韌體更新
- 2019 年 09 月 11 日 - 廠商回覆部分用戶需派員更新, 延後公開時間
- 2019 年 09 月 23 日 - 與 TWCERT/CC 確認可公開
- 2019 年 09 月 25 日 - 發表至 DEVCORE Conference 2019
- 2019 年 11 月 11 日 - 部落格文章釋出