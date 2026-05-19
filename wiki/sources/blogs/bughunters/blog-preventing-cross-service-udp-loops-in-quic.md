---
source: bughunters
source_url: https://bughunters.google.com/blog/preventing-cross-service-udp-loops-in-quic
title: "Preventing Cross-Service UDP Loops in QUIC - Google Bug Hunters"
description: "Infinite loops between servers can lead to performance degradation or network overload. In this blog, we'll take a look at how we prevented cross-service UDP loops in QUIC and share some general conclusions."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/preventing-cross-service-udp-loops-in-quic#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Preventing Cross-Service UDP Loops in QUIC

![](https://storage.googleapis.com/bughunters-article-images/blogs/damian.jpg)

Damian Menscher

Security Reliability Engineer

Published: Mar 26, 2024

[RSS Feed](https://bughunters.google.com/feed/en)

# Preventing Cross-Service UDP Loops in QUIC

Infinite loops between servers are something that must be carefully avoided to
prevent performance degradation or network overload. Methods of avoiding loops
vary:

- The `ping` utility is implemented using two different ICMP packet types to
prevent looping: ECHO\_REQUEST and ECHO\_RESPONSE.
- TCP will not respond to a RST packet with another RST.
- IP decrements a time-to-live (TTL) counter for each pass through a router,
producing an ICMP TIME\_EXCEEDED when the TTL reaches 0.

However, some types of looping are still possible. Over 20 years ago, attacks
exploited loops between the `chargen` and `echo` services: a `chargen` server
responds to any packet with a copy of the ASCII table, while an `echo` server
simply reflects any packet back to the source. This would result in an infinite
loop if a packet from an `echo` server was sent to a `chargen` server.

An
[advisory](https://cispa.saarland/group/rossow/Loop-DoS)
published on March 19, 2024 identifies several previously unreported methods of
triggering loops that are possible using other protocols, or due to buggy
software. As a simple example, because a DNS server will include the question
along with its response, buggy DNS servers can loop with each other if they
assume that all inbound packets are DNS queries, and don't ignore packets with
the response flag set. Buggy implementations of other services can also lead to
looping behavior, and the researchers even discovered new looping behavior
between services of different types (similar to the `chargen` / `echo` case
described above).

In light of the heightened awareness of this attack vector, now is a good time
to discuss looping behavior which impacted our implementation of QUIC and review
the postmortem action items that followed each event. Our experience diagnosing
and mitigating attacks, as well as deploying fixes, may assist others attempting
to address similar threats.

## SPDY and QUIC

Google developed SPDY (later standardized as HTTP/2) to allow multiplexing of
requests on a single connection. This reduced the total number of connections
required, leading to an overall improvement of web performance. But the shift to
mobile highlighted two major challenges:

1. Users would change IPs frequently (while moving through the physical world).
2. Packet loss would stall the entire connection.

To address those challenges, Google developed QUIC (later standardized as
HTTP/3). QUIC is based on UDP rather than TCP, which avoids two constraints
inherent to TCP:

1. Unlike TCP connections which are identified by a 5-tuple, QUIC connections
are identified by a connection ID. This allows mobile users to change IP
addresses without completing a new handshake.
2. QUIC maintains reliable data transfer for each individual stream, ensuring a
single dropped packet doesn't impact all multiplexed streams.

QUIC must rebuild all the connection management capabilities of TCP, and
utilizes a connection ID to handle the common case. Packets that cannot be
attributed to any connection (perhaps due to a server restart) will trigger a
Stateless Reset response, informing the sender the session has failed and that
they need to create a new one. As in the case of TCP, implementers
[must](https://datatracker.ietf.org/doc/html/rfc9000#name-looping) ensure a
Reset isn't sent in response to a Reset in order to avoid looping behavior.
Because the QUIC designers wanted to ensure a middlebox couldn't distinguish the
Reset from any other packet, the packet couldn't contain a fixed identifier.
This makes it more challenging to avoid sending a Reset in response to a Reset.

## CLDAP amplification vs. QUIC

Several years ago, a ~10-minute CLDAP amplification attack targeted our QUIC
implementation. The attack was carried out by sending requests to thousands of
CLDAP servers all over the world with a faked source IP address to make it
appear the requests had originated from Google. \[Those packets\
[should not have been allowed](https://www.rfc-editor.org/bcp/bcp38.txt) onto\
the public internet, but several companies are negligent in filtering their\
outbound traffic of obvious abuse.\] The adversary anticipated that the CLDAP
servers would respond to the 86-byte request with a large response (around 3,000
bytes), thereby resulting in a flood of bandwidth to Google's network. Our
expected behavior was to absorb the bandwidth flood, and respond to the
unexpected packets with QUIC Stateless Reset packets.

Curiously, a small fraction (around 400) of the remote servers didn't operate as
expected, and rather than discard our QUIC Reset packets as malformed CLDAP
requests, they instead reflected those packets back to us. We responded to the
reflected Reset packet with a new Reset, thereby completing the loop. The result
was a sustained 20 million packets per second (Mpps) bouncing between the
misbehaving reflectors and our servers. This was a bit tricky to root-cause, as
it initially appeared to be a sustained CLDAP amplification attack. The clue
that it was a loop was the fact that despite the traffic all coming from the
CLDAP source port 389, the packets were all small. We speculated there could be
a loop, and reproduced the bug by spoofing a request from an `echo` server to
our production frontends.

![](https://storage.googleapis.com/bughunters-article-images/blogs/quic_02.png)

_Fig. 1. Packet capture showing an echo server talking to our production QUIC_
_server to confirm loopy behavior_

We implemented several changes to guard against a repeat event:

1. You might have noticed we were responding to a (reflected) Reset with a new
Reset. We fixed this oversight in the following days, by ensuring we'd only
issue Reset packets that were shorter than the incoming packet (until we
reach a minimum packet size and no Reset is sent).
2. We suffered extremely high CPU usage while generating the Reset packets. In
the QUIC design, a Stateless Reset must contain at least 38 bits of
"unpredictable" filler, which we had implemented using a pseudo-random
number generator (PRNG). Unfortunately, we over-shot and used a
cryptographically secure PRNG, which was quite costly to execute. Switching
to a different PRNG improved performance 100x.
3. We contemplated introducing some artificial packet loss to break any
potential future loops. Simply failing to send 1% of Reset packets would
have minimal negative impact, but might attenuate future looping behavior.
After careful consideration, we considered the previous changes sufficient
and did not pursue this further.

## ISAKMP/IKE amplification vs. QUIC

Several months later, we experienced a similar attack which was intended to
reflect off of ISAKMP/IKE servers. That protocol reacts to invalid packets (such
as QUIC Stateless Resets) in two ways:

- INVALID-SPI notification (80-byte packet)
- DELETE (76-byte packet)

Note that each of those is larger than the QUIC Stateless Reset, which means we
respond to _both_ of them. They then respond to each of our responses with two
more (larger) packets, and so on, resulting in looping behavior that grows
_exponentially_, thwarting defenses that reduce the packet size on each loop, or
even drop a small fraction of outbound Resets. In this case we saw the looping
rapidly surge to 600 Mpps from approximately 30,000 remote endpoints. The
traffic then fell off exponentially over time, presumably as remote systems were
restarted and exited the loop.

![](https://storage.googleapis.com/bughunters-article-images/blogs/quic_01.png)

_Fig. 2. Rate of packets received by victim infrastructure, highlighting the_
_rapid rise time and slow exponential decay of looping traffic after the initial_
_incident, as well as the impact of interventions_

After using our network abuse systems to break the loop (with a regional rollout
targeting the most-impacted regions first), we updated our servers to guard
against remote endpoints that might exacerbate a loop by sending multiple large
packets. In particular, we introduced an overall throttle on Stateless Reset
packets, ensuring no loop could grow out of control. We additionally added a
check to never respond to a packet that doesn't adhere to the QUIC packet
layout.

## Resilience recommendations

Blameless postmortems, a core principle of [SRE](https://sre.google/) incident
response, are a great way to learn about design or implementation flaws and
agree on the best fixes. In this case, our key takeaways included:

- Avoiding loops across protocols can be challenging, as other protocols might
behave in unexpected ways. Multiple layers of defense, such as throttles on
responses to malformed packets, throttles on responses to packets from any
single remote endpoint, and a global throttle, can guard against both
expected and unexpected behaviors.
- The capability to apply customized filters at a per-packet level can provide
immediate relief until the underlying servers can be patched. The challenge
then becomes recognizing that a loop is occurring, which is most easily
accomplished via manual inspection of a bidirectional packet capture.
- Not all random numbers need to be cryptographically secure—fast PRNGs still
have their place for certain applications.

We alerted other QUIC stack maintainers to our experience, and hope that the
details we’ve shared here help you understand what we at Google are doing (and
what you can do) to make the internet and its services safer and more reliable.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab