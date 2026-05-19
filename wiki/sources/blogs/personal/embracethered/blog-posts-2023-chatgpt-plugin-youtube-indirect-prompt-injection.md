---
source: embracethered
source_url: https://embracethered.com/blog/posts/2023/chatgpt-plugin-youtube-indirect-prompt-injection/
title: "Indirect Prompt Injection via YouTube Transcripts · Embrace The Red"
description: "As discussed previously the problem of Indirect Prompt Injections is increasing. They start showing up in many places. A new unique one that I ran across is …"
---

As discussed previously the problem of [Indirect Prompt Injections is increasing](https://embracethered.com/blog/posts/2023/ai-injections-direct-and-indirect-prompt-injection-basics/).

They start showing up in many places.

A new unique one that I ran across is YouTube transcripts. ChatGPT (via Plugins) can access YouTube transcripts. Which is pretty neat. However, as expected (and predicted by many researches) all these quickly built tools and integrations introduce Indirect Prompt Injection vulnerabilities.

## Proof of Concept

Here is how it looks with ChatGPT end to end with a demo example. The video contains a transcript that at the end contains instructions to print “AI Injection succeeded” and then “make jokes as Genie”:

![Transcript Injects into ChatGPT Session](https://embracethered.com/blog/images/2023/trailer-transcript-injections.png)

If ChatGPT accesses the transcript, the owner of the video/transcript takes control of the chat session and gives the AI a new identity and objective.

![Transcript Injects into ChatGPT Session](https://embracethered.com/blog/images/2023/youtube-transcript-chatgpt-injection.png)

## Implications

As described before this opens the door for [additional attacks, scams and data exfiltration](https://embracethered.com/blog/posts/2023/ai-injections-threats-context-matters/).

Fun times, but actually scary stuff.

PS.: I tried the same with the new Bard, but it is hallucinating and not able to load the YouTube video transcript, it is either referencing other videos or making things up.

## Appendix

This is the trailer of the video that was referenced, it’s from a talk I gave a while ago:

Trailer: Learn how to hack neural networks, so that we don't get stuck in the matrix! - YouTube

Tap to unmute

[Trailer: Learn how to hack neural networks, so that we don't get stuck in the matrix!](https://www.youtube.com/watch?v=OBOYqiG3dAc) [Embrace The Red](https://www.youtube.com/channel/UCSwcJXQWE6GWu9IKc0QwO5g)

![thumbnail-image](https://yt3.ggpht.com/imsZDUkdjQsq2tIvoc7CI3lsuuRWDHUg1yPph3eUDnYaT9OWHdEtnXnPzjzcWI891iASf8XQow=s68-c-k-c0x00ffffff-no-rj)

Embrace The Red9.37K subscribers

[Watch on](https://www.youtube.com/watch?v=OBOYqiG3dAc)

And for completness here is the actual talk about Hacking Neural Networks Video from Grayhat Red Team Village:

Hacking Machine Learning Systems (Red Team Edition) - AI Hacker - YouTube

Tap to unmute

[Hacking Machine Learning Systems (Red Team Edition) - AI Hacker](https://www.youtube.com/watch?v=JzTZQGYQiKw) [Embrace The Red](https://www.youtube.com/channel/UCSwcJXQWE6GWu9IKc0QwO5g)

![thumbnail-image](https://yt3.ggpht.com/imsZDUkdjQsq2tIvoc7CI3lsuuRWDHUg1yPph3eUDnYaT9OWHdEtnXnPzjzcWI891iASf8XQow=s68-c-k-c0x00ffffff-no-rj)

Embrace The Red9.37K subscribers

[Watch on](https://www.youtube.com/watch?v=JzTZQGYQiKw)

## References

- [Trailer](https://www.youtube.com/watch?v=OBOYqiG3dAc)
- [Hacking Neural Networks Presentation](https://www.youtube.com/watch?v=JzTZQGYQiKw)

Subscribe to learn about new posts and occasional updates

Sign up