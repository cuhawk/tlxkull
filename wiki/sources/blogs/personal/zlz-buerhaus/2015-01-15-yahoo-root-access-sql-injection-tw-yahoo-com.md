---
source: zlz-buerhaus
source_url: https://buer.haus/2015/01/15/yahoo-root-access-sql-injection-tw-yahoo-com/
title: "Yahoo – Root Access SQL Injection – tw.yahoo.com | ziot"
---

[< Back](https://buer.haus/)

![](https://31.media.tumblr.com/a18fe56326d350480f6bca491a1d216d/tumblr_inline_ni8nrw1tMB1svukax.png)

I'll keep this one simple and sweet because anyone reading this blog probably knows what [SQL Injection](https://www.owasp.org/index.php/SQL_Injection) is. I discovered a root access SQL injection on tw.yahoo.com.

The vulnerability here is an old TW Yahoo page that delivers json content based on an ID specified.

Legitimate URL: https://tw.stock.yahoo.com/q/getjson.php?s=22301

Return:

```
{"id":"22301","type":"stock","relation":[]}
```

After messing with the **s** request variable **,** I noticed that it was not typecasted as integer and allowed any special character. First I checked special characters such as a single-quote - it allowed special characters, but it did not cause any server-side errors. A trick that I have picked up over the years is that sometimes websites will accidentally [**double decode**](https://www.owasp.org/index.php/Double_Encoding) user input.

By passing in the value %2527, it would decode into % and 27, and decode an additional time into a single-quote. The problem is that they were stripping single quotes after the first decode and not the second. This allows all special characters unescaped in the SQL query, including an unescaped single-quote.

Full injection URL: https://tw.stock.yahoo.com/q/getjson.php?s=%2527 union select user(),schema(),4,5,6,7,%25278

Return:

```
{"id":"' union select user(),schema(),4,5,6,7,'8","type":"stock","relation":[{"id":"root@localhost","[redacted]":"Quote","ud":"7"}]}
```

With root select access to a database, you can pull any information you want including the MySQL user password hashes. I opted not to check what databases it had access to in case it contained sensitive information.

- Reported on: 6/15/2014
- Validated the fix: 6/19/2014