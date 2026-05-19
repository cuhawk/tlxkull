---
source: embracethered
source_url: https://embracethered.com/blog/posts/2024/ascii-smuggling-and-hidden-prompt-instructions/
title: "Video: ASCII Smuggling and Hidden Prompt Instructions · Embrace The Red"
description: "A couple of weeks ago hidden prompt injections were discovered and we covered it at the time. This video explains it in more detail, and also highlights …"
---

A couple of weeks ago hidden prompt injections were discovered and [we covered it at the time](https://embracethered.com/blog/posts/2024/hiding-and-finding-text-with-unicode-tags/).

This video explains it in more detail, and also highlights implications beyond hiding instructions, including what I call `ASCII Smuggling`. This is the usage of [Unicode Tags Block characters](https://en.wikipedia.org/wiki/Tags_(Unicode_block)) to both craft and deciper hidden messages in plain sight.

ASCII Smuggling: Crafting Invisible Text and Decoding Hidden Secrets -New Threat for LLMs and beyond - YouTube

Tap to unmute

[ASCII Smuggling: Crafting Invisible Text and Decoding Hidden Secrets -New Threat for LLMs and beyond](https://www.youtube.com/watch?v=7z8weQnEbsc) [Embrace The Red](https://www.youtube.com/channel/UCSwcJXQWE6GWu9IKc0QwO5g)

![thumbnail-image](https://yt3.ggpht.com/imsZDUkdjQsq2tIvoc7CI3lsuuRWDHUg1yPph3eUDnYaT9OWHdEtnXnPzjzcWI891iASf8XQow=s68-c-k-c0x00ffffff-no-rj)

Embrace The Red9.37K subscribers

[Watch on](https://www.youtube.com/watch?v=7z8weQnEbsc)

Using Unicode encoding to bypass security features or execute code (XSS, SSRF,..) has been in use for a while, however this new TTP enables more sophisticated attack scenarios.

This is because Unicode Tags Code Point mirror the entire ASCII set, but are often not visible in UI elements. For Large Language Models this is interesting because LLMs often interpret this hidden text as ASCII, and they can also craft such hidden text when replying to user queries.

### Take-aways

Couple of things come to mind and I touch on those in the video in more detail:

- Test your own LLM apps for this new attack vector
- As developer a possible mitigations is to remove Unicode Tags Block text on the way in and out
- Consider implications beyond LLM applications and Chatbots


### The ASCII Smuggler Tool is here by the way

[![ASCII Smuggler Tool](https://embracethered.com/blog/images/2024/ascii-smuggler-qr-clean.png)](https://embracethered.com/blog/ascii-smuggler.html)

Subscribe to learn about new posts and occasional updates

Sign up