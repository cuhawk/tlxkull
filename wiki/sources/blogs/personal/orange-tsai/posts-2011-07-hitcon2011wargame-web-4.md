---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-4/
title: "台灣駭客年會 HITCON2011，Wargame Web 4出題心得 & 解法 | Orange Tsai"
author: "Orange Tsai"
published: 2011-07-23T16:00:00.000Z
description: "DEBUG 心得是現在大多數的人對於SQL injection (Mysql)都是union加上information_schema取得資料，但是並不是那麼的簡單，SQL injection其實是一門非常深的學問，就出了這題XD 這個方法最早是在大陸的文章看到，後來有分析到國外的一套SQL自動化攻擊工具havij，裡面也有用到類似的方式。 一個登入介面，題目是 If you can login,"
---

* * *

[DEBUG](https://blog.orange.tw//2011/07/hitcon2011wargame-web-4.html)

心得是現在大多數的人對於SQL injection (Mysql)都是union加上information\_schema取得資料，但是並不是那麼的簡單，SQL injection其實是一門非常深的學問，就出了這題XD

這個方法最早是在大陸的文章看到，後來有分析到國外的一套SQL自動化攻擊工具havij，裡面也有用到類似的方式。

一個登入介面，題目是

> If you can login, You can get the key.

登入畫面

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-4/96ac50d31b1ce6f3-01.png)

可以明顯發現確認使用者的頁面存在SQL injection

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-4/33b64799b36b3a52-02.png)

也可以發現

- 不能使用 `union` –\> 因為只會顯示 True or False，不可能列出任何資訊
- 不能使用 `Information_schema` –\> 假想環境是在mysql4上面運行，在Mysql4以前沒有這個資料庫，這題是我自己patch mysql主程式所以使用不了`information_schema`查table name以及column name
- 不能使用blind injection or time base injection –> 因為無法取得column name不能取得資料

但是，發現他是Error base的Injection。 可以利用Duplicate column name的方式來注入

Example:

在Mysql Commandline下輸入：

> Select \* from (Select 1,1) as a

會顯示

> ERROR 1060 (42S21): Duplicate column name ‘1’

利用Error base的方式像SQL server一樣可以把想要的資料出現在錯誤訊息中。 但是要利用這個爆出非CONST以外的還需要配合`NAME_CONST`這個函數來達成

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-4/02769224b3473ada-03.png)

但是`NAME_CONST`在Mysql 5.1後被Update了不能使用非常量CONST以外的參數，但是還是有其他的方法的，有興趣可以自己去Google這裡就不詳談了 :P

所以可以利用以下的方式爆出 Column name

> id=test’ and (Select \* from (Select \* from users as a join users as b) as c) and ‘’=’

> id=test’ and (Select \* from (Select \* from users as a join users as b using(column name)) as c) and ‘’=’

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-4/14993b5a740d538e-04.png)

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-4/480ed4d60e1eefe5-05.png)

可以得到Column name

> wpw\_d7862549d4ed8f82

繼續利用`NAME_CONST`爆出其中的資料

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-4/8b2d7173f5e02dd5-06.png)

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-4/73e2f421d19ba1bf-07.png)

可以取得

> admin / 0b79f46808458afb

在登入頁面的地方也可以發現輸入單引號也會顯示SQL error，仔細觀察會發現是使用Mysql的`old_password`來對密碼進行加密。

![](https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-4/03157dc04a3e4907-08.png)

在Mysql4以前password儲存的方式是透過old\_password這個函數進行加密的，實際上這個加密方式存在弱點能被很快速的碰撞(Collision)出來，網路上可以找到現成的工具，約20~30分鐘可以撞出一組hash值與上面一樣的密碼

我自己碰撞的結果是這組

> Select old\_password(‘!H6~a\`”~H\\DN>’);

出來的結果與上面的hash值是一樣的，所以使用 admin / !H6~a\`"~H\\DN> 即可登入取得Key。

:P 解題愉快XD 沒解出來至少有學到新東西吧 :P

有機會再把出的另外一題Web以及Windows Binary解題過程寫出XD