---
source: kevin-mizu
source_url: https://mizu.re/post/welcome_to_kara_org
title: "Welcome to Kara Org | mizu.re"
description: "Welcome to Kara Org"
---

_keyboard\_arrow\_up_

title: Welcome to Kara Org

date: Dec 25, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [YogoshaChristmas\_2022](https://mizu.re/tag/YogoshaChristmas_2022) [Web](https://mizu.re/tag/Web)

# Welcome to Kara Org

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/welcome_to_kara_org/images/yogosha.svg)

* * *

Difficulty: 500 points \| 92 solves

Description: Welcome To Kara Organization! It's the Christmas so Konoha will let its guards down and we can take down the big threat Boruto! For that we need to prepare our forbidden jutsus. In Kara organization we are well secure, we have hidden some clues in this dockueru image shisuiyogo/christmas, can you retrieve them as your first mission ?

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/welcome_to_kara_org#%EF%B8%8F-recon)
- [🐳 Docker analysis](https://mizu.re/post/welcome_to_kara_org#-docker-analysis)
- [🎉 Flag](https://mizu.re/post/welcome_to_kara_org#-flag)

## 🕵️ Recon

This challenge was the 1st step of the CTF. From the description, we know that we have to find a docker image. To do so, we can go to: `https://hub.docker.com/r/<maintainer>/<image-name>` or directly pull `shisuiyogo/christmas`.

```sh
docker pull shisuiyogo/christmas
```

## 🐳 Docker analysis

Now that we have the docker image locally, it is possible to investigate into different layers using [dive](https://github.com/wagoodman/dive) to dig into all the different layers.

What are docker layers?

Layers in docker context represent all the different step that the docker engine will make to generate a docker image based on a Dockerfile.

In order to go faster, I've just used the following command to retrieve all the layers data into one `.tar` file:

```sh
docker save shisuiyogo/christmas -o yogo_christmas.tar
```

## 🎉 Flag

From this, the flag could be retrieved in the following file:

```
yogo_christmas.tar/26ca41e311fdd9587039634cc34f9876d781fe386c05ff21fca606d6673ca6ee/layer.tar/data/secret_note.txt
```

Flag: `FLAG{Welcome_T0-The_XmAs_Chall}` 🎉

[_keyboard\_arrow\_left_ Secret Hideout](https://mizu.re/post/secret_hideout)

[Perfect Notes _keyboard\_arrow\_right_](https://mizu.re/post/perfect_notes)