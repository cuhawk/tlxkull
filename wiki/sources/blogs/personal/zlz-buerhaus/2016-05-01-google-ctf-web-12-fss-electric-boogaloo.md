---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-12-fss-electric-boogaloo
title: "Google CTF – Web 12 – FSS – Electric Boogaloo | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 12 - FSS - Electric Boogaloo**

This continues off of [Web 11 Flag Storage Service](https://buer.haus/2016/05/01/google-ctf-web-11-flag-storage-service/).

Two important discoveries were made in the previous challenge. I'll re-post them here:

[https://next-bitter-flag.ctfcompetition.com/robots.txt](https://next-bitter-flag.ctfcompetition.com/robots.txt)

`

    User-agent: hackers

    Disallow: /README.txt

    Disallow: /sync

`

[https://next-bitter-flag.ctfcompetition.com/README.txt](https://next-bitter-flag.ctfcompetition.com/README.txt)

`

    FlagService 0.01`

`
    == Authentication ==

    Authentication via username/password is the default.  If another authentication

    mechanism is configured, then the password field must *not* be sent to avoid

    including it in the backend query.  The default username is 'manager', but this

    may be customized to suit your needs.

    == Synchronization ==

`

`    In order to sync between multiple instances, there is a config page at

    /sync that is only available to authorized applications that send the

    appropriate X-FlagStore header.  This header is automatically added

    to all HTTP requests to partner instances.

`

Because we were able to solve the first challenge with Authentication, we are assuming that Synchronization is for the second challenge. When we attempt to load the **/sync** endpoint, we get an error. This is presumably because it requires a "X-FlagStore" header with a valid value.

After solving the first challenge, we are now authenticated and have access to two new pages. The flag page simply tells you that the flag is the password, so that is no use to us. The profile page is the interesting one that we probably need to solve this challenge.

There's a form for uploading GnuPG keys based on a remote URL. The immediate thing that jumps to mind is Server-Side Request Forgery. I tried to put my own website in this input and sure enough, it loaded the contents of my website and displayed it back. I put the **/sync** endpoint into the input and got the following:

![Step 2](https://buer.haus/wp-content/uploads/2016/05/Step-21.png)