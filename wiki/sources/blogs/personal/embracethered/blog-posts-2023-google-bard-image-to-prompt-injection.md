---
source: embracethered
source_url: https://embracethered.com/blog/posts/2023/google-bard-image-to-prompt-injection/
title: "Image to Prompt Injection with Google Bard · Embrace The Red"
description: "A prompt injection scenario that I, and others, have been wondering about in the past, is the potential risk associated with chatbots being able to analyze …"
---

A prompt injection scenario that I, and others, have been wondering about in the past, is the potential risk associated with chatbots being able to analyze images.

**Could this ability open up the way for Indirect Prompt Injection attacks?**

Recently, Google added the ability to uploading and analyze images with Bard. And it turns out that it is indeed possible to add instructions to an image, and have the Bard follow those instructions.

Here is a demonstration picture doing a Rickroll:

![AI Prompt Injection - Rickroll](https://embracethered.com/blog/images/2023/aiinjection-image-joke.png)

And this is the result after asking Bard to describe the image:

![AI Prompt Injection - Rickroll](https://embracethered.com/blog/images/2023/aiinjection-image-joke-bard-response.png)

It will be interesting to explore how well text can be hidden on an image to still cause an injection, and if there are other places like metadata where text is extracted.

## References

- Base images (bot and banana pictures) generated with Bing Chat (then modified by me)
- Initial tweet showing proof-of-concept

Twitter Embed

> 👉 Image to Prompt Injection
>
> Was always wondering if this would be a thing… works better then expected at a first glance. [#llm](https://twitter.com/hashtag/llm?src=hash&ref_src=twsrc%5Etfw) [#bard](https://twitter.com/hashtag/bard?src=hash&ref_src=twsrc%5Etfw) [#infosec](https://twitter.com/hashtag/infosec?src=hash&ref_src=twsrc%5Etfw) [#promptinjection](https://twitter.com/hashtag/promptinjection?src=hash&ref_src=twsrc%5Etfw) [#ai](https://twitter.com/hashtag/ai?src=hash&ref_src=twsrc%5Etfw) [#poc](https://twitter.com/hashtag/poc?src=hash&ref_src=twsrc%5Etfw) [pic.twitter.com/taoK3MIWeV](https://t.co/taoK3MIWeV)
>
> — Johann Rehberger (@wunderwuzzi23) [July 14, 2023](https://twitter.com/wunderwuzzi23/status/1679676160341581824?ref_src=twsrc%5Etfw)

Subscribe to learn about new posts and occasional updates

Sign up

Twitter Widget Iframe