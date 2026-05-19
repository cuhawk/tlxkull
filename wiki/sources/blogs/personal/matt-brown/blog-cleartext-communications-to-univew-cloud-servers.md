---
source: matt-brown
source_url: https://brownfinesecurity.com/blog/cleartext-communications-to-univew-cloud-servers
title: "Enterprise IoT Pentesting: Cleartext Cloud Communications - Brown Fine Security"
---

# Enterprise IoT Pentesting: Cleartext Cloud Communications

In the [last segment](/blog/firmware-extraction-and-analysis-of-uniview-camera) in our Enterprise IoT Pentesting series, we extracted and analyzed the firmware from a Uniview SC-3243 security camera. Part of that analysis was checking for the encryption of *data at rest*. In this segment, we turn to an analysis of *data in transit*. (data sent over a network)

This is distinct from an analysis of *Network Services* which will be discussed in a separate post.

The difference between Network Communications and Network Services can be a gray area, but generally when the IoT device is acting as a client we are dealing with Network Communications. When the IoT device is acting as a server, we are dealing with Network Services.

## Capturing Network Communications

Next we need a way to capture all traffic between our Enterprise IoT camera and the internet. The Uniview SC-3243 device transmits data via Ethernet.

We could use a SPAN port on a managed switch in order to capture all packets transmitted over the device's ethernet interface.

However, we will instead use a setup that will not only allow for packet captures, but also to facilitate man-in-the-middle (mitm) attacks. For this, we will use [mitmrouter](https://github.com/nmatt0/mitmrouter).

## Mitmrouter Setup

We will setup [mitmrouter](https://github.com/nmatt0/mitmrouter) to use a USB-to-Ethernet adapter on our Linux computer to act as the LAN of our testing network. A WiFi network is also created that we will not need for this assessment. A bridge interface, `br0`

, is created to allow us to capture traffic and optionally add iptables rules to route certain traffic to other destinations to conduct mock mitm attacks.

## Cleartext HTTP Communications to the Cloud

At first, we simply want to passively view all the traffic coming from our IoT camera to the cloud. To do this, we use Wireshark on the `br0`

interface. After powering on the device, we immediately see the device making cleartext HTTP requests to www.star4live.com.

The data being submitted is QR code data that is used in the device enrollment process. If an attacker were to get their hands on this data they could gain access to the video feed via the cloud backend by enrolling the device to their own account.

## Cleartext HTTP is a Thing in 2025?

It turns out that it was simple to find a vulnerability just by opening Wireshark and looking at the data being communicated over the network.

You might be tempted to believe that this type of finding doesn't really occur today. You would be wrong. I have found these issues in many IoT devices from top tech companies and been paid out in bug bounties. They exist. All you have to do is look at the network data!

### Need IoT Security Expertise?

Brown Fine Security provides expert IoT penetration testing to help secure your connected devices. From hardware analysis to cloud API testing, we uncover vulnerabilities before attackers do.

[Get a Free Consultation](/contact)

### Want to Learn IoT Hacking?

Ready to break into IoT security? Our hands-on training courses teach real-world hardware hacking, firmware analysis, and IoT exploitation techniques used by professional pentesters.

[Explore Training Courses](https://training.brownfinesecurity.com/)