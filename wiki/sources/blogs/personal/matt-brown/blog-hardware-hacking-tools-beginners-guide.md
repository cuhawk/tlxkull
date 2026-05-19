---
source: matt-brown
source_url: https://brownfinesecurity.com/blog/hardware-hacking-tools-beginners-guide
title: "A Beginner's Guide to Hardware Hacking Tools - Brown Fine Security"
---

# A Beginner's Guide to Hardware Hacking Tools

A common question for those wanting to dip their toes into the world of hardware hacking is: what tools should I buy?

This question comes up because hardware hacking, as apposed to web/network hacking, does require some equipment depend on the task. In this guide I'm going to discuss X basic tools to buy on the cheap to get you started in the world of hardware hacking.

## #0: A Device to Hack

Ok, so the first item on the list isn't a tool. It may seem obvious, but the first thing we are going to need for our hardware hacking adventure is a target device! Luckily, there are many great places you can find random IoT devices for free or cheap.

Some of the places I love finding device targets are:

- Goodwill or other thrift stores
- eBay
- Amazon

### What type of device should I get?

Some will ask what kind of device to get. I wouldn't suggest going and buying the latest IoT device from a big tech company like Google or Amazon. Those kind of big targets are going to be hard going and we are just getting started. I would suggest finding an old/used WiFi router. These usually run Linux and older WiFi routers provide an excellent target for finding security vulnerabilities even if you have zero hardware hacking tools!

[This WiFi router](https://amzn.to/3YqjjqH) from Amazon is only $23 and Tenda is a cheap brand that doesn't care about security. A great target!

## #1: Basic Toolkit

Now that we have a device to hack on, we need to open it up! We are going to need a screwdriver with multiple bit types and some pry tools for opening those plastic enclosures.

My top choice that I use to this very day is the [iFixit Pro Tech Toolkit](https://amzn.to/408Kfwr). There are certainly some [cheaper alternatives](https://amzn.to/4f8LboG) out there, but you may find yourself upgrading over time when you find you don't have the right bit you need.

## #2: Digital Multimeter

Next we will need a multimeter to measure voltages and trace PCB components on our target device. As hardware hackers we do not need a high quality multimeter. We only need it to perform voltage measurements and continuity testing.

While I personally have a better multimeter, The [UNI-T UT133A Digital Multimeter](https://amzn.to/4hn6Z27) fits our needs perfectly.

## #3: USB to 3.3v UART Cable + Jumper Wire

Most of those cheap Linux WiFi routers will expose a UART serial interface that we can interact with. To do that, we need a [USB to 3.3v UART Cable](https://amzn.to/4h4G7DD) and some [Jumper Wires](https://amzn.to/4eOrZgk) so that we can connect our computer to the device.

We are making some assumptions here:

- that the device will have an exposed UART interface (sometimes they don't)
- that the UART interface voltage is 3.3v (rarely you will see v1.8 or v2.5)

## #4: Soldering Iron + Solder

Maybe you find that UART interface on the device PCB, but its not populated with a header that you can easily plug your jumper wires into. Now we need some soldering gear!

There are many quality soldering irons out there, but a good and cheap one is the [PINECIL Portable Soldering Iron](https://amzn.to/48cxNxD). We will also need to get some [Solder](https://amzn.to/3UdhISN).

## #5: Wire Strippers

If we are going to be soldering a lot of wires we will need a pair of cheap wire strippers. Nothing fancy required. These [Klein Tools Wire Strippers](https://amzn.to/4eMUYkv) will work just fine.

## Happy Hacking

What's next? Start Hacking!!

- Open up the device
- Try to learn everything you can about what you see on the device PCB
- Look for UART!
- Try stuff.
- Make mistakes!

**PLEASE avoid the temptation** to buy a tool before you have a real need for it. Every tool you buy should either solve a problem that you couldn't before or solve it faster/better/cheaper than your current solution.

### Need IoT Security Expertise?

Brown Fine Security provides expert IoT penetration testing to help secure your connected devices. From hardware analysis to cloud API testing, we uncover vulnerabilities before attackers do.

[Get a Free Consultation](/contact)

### Want to Learn IoT Hacking?

Ready to break into IoT security? Our hands-on training courses teach real-world hardware hacking, firmware analysis, and IoT exploitation techniques used by professional pentesters.

[Explore Training Courses](https://training.brownfinesecurity.com/)