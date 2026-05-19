---
source: zlz-buerhaus
source_url: https://buer.haus/2016/05/01/google-ctf-web-8-global-ctf
title: "Google CTF – Web 8 – Global CTF | ziot"
---

[< Back](https://buer.haus/)

**Google CTF - Web 8 - Global CTF**

Description: Can you break into this CTF website? Features Two Factor Authentication for unbeatable security.

I was the second person to solve this challenge and I still don't understand how the vulnerability works. I don't think I solved it the way they intended either, but hey, a flag is a flag.

![site](https://buer.haus/wp-content/uploads/2016/05/site5.png)

When you go into the site, you load a CTF website using the [mellivora framework](https://github.com/Nakiami/mellivora). How meta is that? Google put a CTF inside of their CTF.

When you register a new team, you get an error. Your team is still created, so I logged into my account. It's worth noting that the error is important though.

![error](https://buer.haus/wp-content/uploads/2016/05/error.png)

I wasn't familiar with this CTF framework, so I clicked through the teams on the website. You can see all teams by team name, but you can't see their emails. The top team is "admin". I tried to create an account using the email admin@google.com, but the account already exists. This error message exists to let us know what the admin account's email is.

I downloaded the mellivora source code and went through each page. I assumed Google wasn't going to expose any 0days and I couldn't find any known vulnerabilities. The next step would be to compare the application base install to Google's CTF page to spot any glaringly obvious changes.

The obvious thing to try was to enable TOTP/2-Factor authentication in my profile because that's what the challenge is all about. I registered a few accounts and noticed that the secret\_key used for all TOTP were the same. Looking at the mellivora source code, it is supposed to generate a unique key for every account. With this knowledge, we know that the admin most likely has the same TOTP secret key that we do. With his TOTP key and email, all we need now is his password to log into his account.

Going through each page one by one, I could not find any vulnerabilities.

I filled out the /recruit page that looks like the following:

![recruit](https://buer.haus/wp-content/uploads/2016/05/recruit.png)

Nothing interesting. So I move on and eventually click on my Profile page.

I'm all of a sudden logged in as the admin and there is the flag:

![flag](https://buer.haus/wp-content/uploads/2016/05/flag.png)

I created a new account and walked through the steps again to verify. Indeed, any time you use the **/recruit** request you change your current user session logging you into a different account.

I'll have to revisit this later because it doesn't seem like the intended solution or I missed something obvious.