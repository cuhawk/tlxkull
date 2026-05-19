---
source: daniel-miessler
source_url: https://danielmiessler.com/blog/network-ports
title: "Network Ports | Daniel Miessler"
description: "Many who are new to networking and security wonder what it means to have “ports” open on your computer. Some get rather anxious when an online port"
---

Many who are new to networking and security wonder what it means to have "ports" open on your computer. Some get rather anxious when an online port scan reveals that something’s open on their system. What follows is a silly, but hopefully memorable way for beginners to remember how network ports work.

Imagine a house with many, many windows. And imagine that all these windows are spring-loaded so they slam shut when they aren’t being actively held open. Also within the house are a number of midgets. Each one is able to talk to people outside the house temporarily, but only through an open window.

Well, ports on a computer are the windows on the house, and the applications running on your computer are the midgets. And just like our spring-loaded windows, ports are always closed by default. The second an application stops holding one open, it closes.

So when you find open ports on your system, don’t worry about the port itself. It can’t stay open without help. Instead, focus on the *reason* it’s open, i.e. the application that’s keeping it that way.

For that task you can use a program from Foundstone called Fport. It’ll give you the name of the program so you can find it and shut it down. Once you’ve shut down the program the port will be closed again. ::