---
source: daniel-miessler
source_url: https://danielmiessler.com/blog/the-sleepy-puppy-xss-payload-management-framework
title: "The Sleepy Puppy XSS Payload Management Framework | Daniel Miessler"
description: "I am one of the leaders of the OWASP Bay Area group, and we’ve had some great local meetups recently—one at Twitter and another at Netflix. At the N"
---

I am one of the leaders of the OWASP Bay Area group, and we’ve had some great local meetups recently—one at Twitter and another at Netflix.

At the Netflix one last Thursday there were a few talks, including one by Scott Behrens on a tool called [Sleepy Puppy](https://github.com/sbehrens/sleepy-puppy?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=the-sleepy-puppy-xss-payload-management-framework) >. It is a great project, but it was pitched as a "Blind XSS" tool, which I found troubling.

They basically have a tool that creates trackable XSS payloads and then listens for evidence that they’ve been detonated somewhere within a target environment. They work at Netflix, so they started the project to protect their own org.

So if you hit a lower user with a payload, you might get one thing. And if you hit an admin you might get another. But what if the payload gets stored in some database, or some key/value table, and doesn’t get retrieved for months?

Normally you lose that stuff, because by the time it pops you’re no longer paying attention. Sleepy Puppy is designed to be there when it finally gets triggered!

It’s a phenomenal concept, but it’s way bigger than "Blind XSS", which doesn’t even make sense. During the feedback period I told them I thought they were selling the project short, and that they should adjust it in a few ways. I also created an issue in the repo to capture the points.

Here were the main ones:

Blind XSS isn’t the point, and doesn’t really make much sense as a name anyway. It’s evidently called "blind" because the attacker doesn’t get feedback when it detonates. Huh? XSS detonates on the victim box, not the attacker’s, so it’s always blind until you get an out of band communication showing you it worked (a cookie sent to you on the internet, for example). So I think there was confusion on the use of the "blind" concept.

The tool is really more about "delayed" XSS, and, more importantly, about having a framework that can handle the receipt of delayed payloads and then know which campaign they were associated with.

**This is huge!**

I cannot tell you how many times I’ve been doing a web assessment, and doing a PoC for XSS when I wished I had something like this. BeEF is nice, but this is designed specifically for the task.

What’s really cool about this tool, or at least how I think they should use it, is that it allows internal orgs to employ an "inject and listen" approach to testing. So you can buckshot an app full of tagged XSS payloads and then leave your listener framework up indefinitely.

The key is that you will then see if some random user stumbles across the payload weeks or months later, in something like a second or third order fashion. And not only does the tool catch the fact that it was triggered, but it sends the listener framework tons of information about the user who executed it.

You get screenshots of the page it hit on. Cookies. Etc. You get CONTEXT. It’s so sick.

The other thing I mentioned to Scott was the fact that this could be used for long-term attack campaigns against organizations, where you could tag the payloads according to victim, and just wait for them to pop.

It sucks, but that’s the double-edge of security research. This helps good guys, and it could also help bad guys. That’s just reality.

Anyway, I just wanted to capture this stuff here and give a shout out to Scott and the project. Seriously great stuff!