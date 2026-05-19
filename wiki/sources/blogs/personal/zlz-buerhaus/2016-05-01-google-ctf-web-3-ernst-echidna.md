---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-3-ernst-echidna
title: "Google CTF – Web 3 – Ernst Echidna | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 3 - Ernst Echidna**

Description: "Can you hack this website? The robots.txt sure looks interesting."

![](https://buer.haus/wp-content/uploads/2016/05/site1.png)

This was a pretty straightforward web challenge that involved a simple authentication check.

Because Google told us to, we take a look at robots.txt first.

https://ernst-echidna.ctfcompetition.com/robots.txt

```
Disallow: /admin
```

Alright, so we need to load /admin.

https://ernst-echidna.ctfcompetition.com/admin responds with "You are not logged in!"

The only page we have access to is **/register**. It asks for a username and password. When you submit this request, you receive a cookie "md5-hash".

![](https://buer.haus/wp-content/uploads/2016/05/pic21.png)

Registering with a simple username and password, we can do a quick check against Rainbow tables to see if it matches either.

![](https://buer.haus/wp-content/uploads/2016/05/pic31.png)

Sure enough, it's just an MD5 hash of our username. The first guess is to get the MD5 hash of "admin", replace our cookie, and see if we can load the **/admin** endpoint.

![](https://buer.haus/wp-content/uploads/2016/05/pic41.png)