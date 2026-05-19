---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-4-dancing-dingoes
title: "Google CTF – Web 4 – Dancing Dingoes | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 4 - Dancing Dingoes**

Description: "We're interested in finding out what information is stored on this website. We've already obtained the username "proff" and the password "strobe.c", but can't work out how to access the "admin" user. Any ideas?"

The only thing we have when we load this website is a login form. We are given a login (proff/strobe.c) in the challenge description. When we log into the site, we are given a list of documents of no importance. Going back to the login, I monitor the requests that I send when I log into the website.

![login](https://buer.haus/wp-content/uploads/2016/05/login.png)

There's a strange /api/users/login endpoint request that includes a suspicious domain GET request variable. I decided to throw a random fuzz character (') into it to see what the response is.

![step 2](https://buer.haus/wp-content/uploads/2016/05/step-21.png)

As you can see in the error response back, it's trying to load **https://\[domain\]/rest/v1/user/current**. I load the endpoint to see what the server is processing.

![step 3](https://buer.haus/wp-content/uploads/2016/05/step-32.png)

Ok, it's specifying that the current user is "proff", the user that I logged into. Because we are able to specify the domain, I create a txt file on my web server and change "proff" to "admin".

![step 4](https://buer.haus/wp-content/uploads/2016/05/step-41.png)

Now we load the following URL:

https://dancing-dingoes.ctfcompetition.com/api/users/login?domain=potatopla.net/test.txt?

We are redirected to the following:

![step 5](https://buer.haus/wp-content/uploads/2016/05/step-5.png)

We can see that admin was the right user and we now have a new document.

Loading the document:

![step 6](https://buer.haus/wp-content/uploads/2016/05/step-6.png)