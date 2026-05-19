---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-15-horton-hears-a-who
title: "Google CTF – Web 15 – Horton Hears a Who! | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 15 - Horton Hears a Who!**

This was a nifty little challenge that I actually tried a bunch of really stupid things on.

![site](https://buer.haus/wp-content/uploads/2016/05/site6.png)

You're given a website with three links:

- Register
- Login
- Logout

If you register an account and log into it, you get a session cookie like so:

Username: ziot

Cookie: sessdata=ziot:0:1462103510:JtfZmpH\_I9e-RMj9UdyOl2rOZQDnrRlPdmBLZedg1MQ=

It redirects you to a **/flag** endpoint that says "Access Denied. Must be an admin." The first idea I had is that you need to be username admin but the account already exists. Minds will immediately jump to simply modifying the cookie, finding out the sessdata format, or SQL injection, but those were all ruled out immediately.

For some people the answer is immediately obvious, but it took me awhile before it clicked. The website is parsing the sessdata cookie based on a : character. If it's splitting it and checking by array index, we can fake any username that we want.

Username: admin:1:1462103278:null

Cookie: admin:1:1462103278:null:0:1462103350:foBi7Ry8pam5Jopb3FvKV\_fulUHFPpn4NqIrowNwu7c=

Result:

![flag](https://buer.haus/wp-content/uploads/2016/05/flag1.png)