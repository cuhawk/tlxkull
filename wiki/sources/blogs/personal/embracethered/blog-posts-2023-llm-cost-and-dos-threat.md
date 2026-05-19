---
source: embracethered
source_url: https://embracethered.com/blog/posts/2023/llm-cost-and-dos-threat/
title: "LLM Apps: Don't Get Stuck in an Infinite Loop! 💵💰 · Embrace The Red"
description: "What happens if an attacker calls an LLM tool or plugin recursively during an Indirect Prompt Injection? Could this be an issue and drive up costs, or DoS a …"
---

What happens if an attacker calls an LLM tool or plugin recursively during an Indirect Prompt Injection? Could this be an issue and drive up costs, or DoS a system?

I tried it with ChatGPT, and it indeed works and the Chatbot enters a loop! 😊

![llm-dos-loop](https://embracethered.com/blog/images/2023/llm-plugin-loop-2.png)

**However, for ChatGPT users this isn’t really a threat, because:**

1. It’s subscription based, so OpenAI would pay the bill.
2. There seems to be a call limit of 10 times in a single conversation turn (I tried a few times).
3. Lastly, one can click “Stop Generating” if the loop keeps ongoing.

**BUT**

Other applications might be vulnerable to this threat, especially if there is backend automation service consuming untrusted data and calling tools.

**Things could become costly quickly!**

[@wunderwuzzi23](https://twitter.com/wunderwuzzi23)

Here is a short video:

LLM Threat: Infinite Loop Attempt with ChatGPT (unlisted) - YouTube

Tap to unmute

[LLM Threat: Infinite Loop Attempt with ChatGPT (unlisted)](https://www.youtube.com/watch?v=HjHWN7kGBC8) [Embrace The Red](https://www.youtube.com/channel/UCSwcJXQWE6GWu9IKc0QwO5g)

![thumbnail-image](https://yt3.ggpht.com/imsZDUkdjQsq2tIvoc7CI3lsuuRWDHUg1yPph3eUDnYaT9OWHdEtnXnPzjzcWI891iASf8XQow=s68-c-k-c0x00ffffff-no-rj)

Embrace The Red9.37K subscribers

[Watch on](https://www.youtube.com/watch?v=HjHWN7kGBC8)

Subscribe to learn about new posts and occasional updates

Sign up