---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2015-05-0ctf-final-0cms/
title: "講個秘訣 - 0ctf Final 0cms | Orange Tsai"
author: "Orange Tsai"
published: 2015-04-30T16:00:00.000Z
description: "這次跟著 217 到上海參加由 0ops 舉辦的 0ctf 決賽 總體來說這次是我打過最爽的一次 Attack & Defense 比賽，尤其 0cms 這個題目滿對我胃口的，考驗快速 Code Review 找洞、快速修洞、快速寫 Exploit 打全場的能力（好在有 web 題目可以發揮，這次沒有耍廢XDDD） 靠 0cms 刷分刷到第二天幾乎所有隊伍都放棄，把 Web 服務關掉防止失"
---

* * *

這次跟著 [217](http://217.logdown.com/) 到上海參加由 [0ops](http://www.0ops.net/) 舉辦的 0ctf 決賽

總體來說這次是我打過最爽的一次 Attack & Defense 比賽，尤其 0cms 這個題目滿對我胃口的，考驗快速 Code Review 找洞、快速修洞、快速寫 Exploit 打全場的能力

（好在有 web 題目可以發揮，這次沒有耍廢XDDD）

靠 0cms 刷分刷到第二天幾乎所有隊伍都放棄，把 Web 服務關掉防止失去更多分，直到比賽結束前兩三小時 Blue-Lotus 跟 Freed0m 才把服務修補好重新開啟上線XD

當中針對一個弱點有想到比較不一樣的利用方式特此紀錄一下XD

（紅色=被入侵、深黃色=服務當掉、淺黃色=服務當掉+被入侵）

![](https://blog.orange.tw/posts/2015-05-0ctf-final-0cms/e2c98243a3f0649a-01.png)

0cms 是一題以 Webpy 寫的一個線上內容管理系統，配合 SQLite 以及許多個弱點，第一眼看到用到 Webpy 這個 Python framework 就想到烏雲的這篇 [新型任意文件读取漏洞的研究](http://drops.wooyun.org/papers/5040)，事後比較好像弱點那部分程式碼真的長得差不多XD

不過這次要講的不是它XD

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://blog.orange.tw/posts/2015-05-0ctf-final-0cms/)

|     |     |
| --- | --- |
|  | #!/usr/bin/env python |
|  | #coding=utf-8 |
|  | importweb, settings |
|  |  |
|  | urls= ( |
|  | '/uploads/(.\*)', 'download', |
|  | '(\[a-z0-9\\/\]\*)', 'dispatcher' |
|  | ) |
|  |  |
|  | classdispatcher: |
|  | def\_\_init\_\_(self): |
|  | pass |
|  | defGET(self, path): |
|  | returnself.\_\_request(path) |
|  |  |
|  | defPOST(self, path): |
|  | returnself.\_\_request(path) |
|  |  |
|  | def\_\_request(self, path=''): |
|  | try: |
|  | libName='action' |
|  | controllerName='index' |
|  | ifpath.count('/') <2: |
|  | path=settings.DEFAULT\_PATH |
|  | ifpath.count('/') ==2: |
|  | modelName, controllerName=path.strip()\[1:\].split('/', 1) |
|  | else: |
|  | libName, modelName, controllerName=path.strip()\[1:\].split('/', 2) |
|  | ifnotmodelName: |
|  | return'controller missing' |
|  | moduleList=\_\_import\_\_(libName+'.'+modelName, {}, {}, \[modelName\]) |
|  | modelObj=getattr(moduleList, modelName)() |
|  | ifhasattr(modelObj, controllerName): |
|  | result=getattr(modelObj, controllerName)() |
|  | else: |
|  | result='no such controller' |
|  | returnresult |
|  | exceptException ,e: |
|  | fromaction.baseimportbaseasbaseAction |
|  | baseObj=baseAction() |
|  | ife.message=='db not exists' : |
|  | returnbaseObj.error('To be installed',baseObj.makeUrl('install')) |
|  | returnbaseObj.error(e.message,baseObj.makeUrl('index')) |
|  | #raise Exception,e.message |
|  |  |
|  | classdownload: |
|  | defGET(self, filepath): |
|  | try: |
|  | withopen("./uploads/%s"%filepath, "rb") asf: |
|  | content=f.read() |
|  | returncontent |
|  | except: |
|  | returnweb.notfound("Sorry, the file you were looking for was not found.") |
|  |  |
|  |  |
|  | if\_\_name\_\_=="\_\_main\_\_": |
|  | app=web.application(urls, globals()) |
|  | app.run() |

[view raw](https://gist.github.com/orangetw/624b21900765665bc068/raw/c02b2644253543237db95a8064abc06bc4dad797/app.py) [app.py](https://gist.github.com/orangetw/624b21900765665bc068#file-app-py)
hosted with ❤ by [GitHub](https://github.com/)

在第 31 行 `dispatcher -> __request` 的地方有個可以任意引入已知檔案模組的功能，當 URL 是以 `/A/B/C` 開頭可以執行到類似如下的語法

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>from A.B import B<br>B.C()<br>``` |

不過如果伺服器上沒有可控檔案的話幾乎不能做什麼事情，所以大部份人的玩法都是透過 CMS 本身管理功能有提供一個任意檔案上傳，透過上傳一個 .py 檔案到 action 目錄下再透過這個漏洞去執行造成 Remote Code Execution

不過當然這麼明顯的上傳當然馬上就被很多隊伍修補了，不過任意引用的部分似乎許多隊伍認為是正常功能以及不搭配上傳無法利用所以都沒修補，所以在比賽第一天晚上花了一點時間研究這個任意引用到底還可以做到什麼樣子的利用

限制比較麻煩的是要在 A 目錄下找到 B.py 同時檔案內要有 class B 可用，而且 A B C 都限定 a-z0-9 且呼叫 C 除了 self instance 外不能指定其他參數

看到這些限制又要可以對網站有實質影響所以最後決定看一下 Webpy 的原始碼，花了一陣子後沒發現什麼，不過在 Attack & Defense 比賽中 DoS 的洞也很有利用價值

再仔細看一下後發現 `web/application.py` 下有個 `class application` 符合條件，配合裡面的 `stop()` 可以直接停止 WSGIServer 把別人服務給關閉XD

最後 PoC

> curl [http://100.64.101.154/web/application/stop](http://100.64.101.154/web/application/stop)

靠著這招在第二天狂刷所有隊伍XD 如此這般，不知道有沒有什麼其他更好利用的方式？