---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-6-purple-wombats
title: "Google CTF – Web 6 – Purple Wombats | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 6 - Purple Wombats**

![site](https://buer.haus/wp-content/uploads/2016/05/site2.png)

We get a particularly plain and strange website to test that contains only an index and login page.

Trying to log into the website with any username or password, we get the following error:

"Undergoing emergency maintenance, sorry for any inconvenience caused"

Viewing the source code, something immediately catches my eye. There is an HTML comment with a link to a github repository:

![step 1](https://buer.haus/wp-content/uploads/2016/05/step-1.png)

[http://github.com/mannequin-moments/](http://github.com/mannequin-moments/)

After a quick look through the github repository, we can tell that this is indeed the source code for the challenge website. Our goal is to figure out how the authentication process works and if we can bypass the login.

![step 2](https://buer.haus/wp-content/uploads/2016/05/step-23.png)

Here we can see that they committed the secret\_key used for generating sessions. If we use this secret\_key to generate a session cookie in a local environment, we should be able to use this cookie on the challenge website.

Booting up the website in Google Appengine in a local environment, all I did was comment out the line that caused the "emergency maintenance" error so it would generate a session cookie for me.

![step 4](https://buer.haus/wp-content/uploads/2016/05/step-42.png)

This is what the cookie looks like for the "admin" user:

![step 5](https://buer.haus/wp-content/uploads/2016/05/step-51.png)

Using the cookie on the CTF website:

![step 6](https://buer.haus/wp-content/uploads/2016/05/step-61.png)