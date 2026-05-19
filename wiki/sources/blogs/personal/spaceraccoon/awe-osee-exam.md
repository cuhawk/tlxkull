---
source: spaceraccoon
source_url: https://spaceraccoon.dev/awe-osee-exam/
title: "Passing the New OSEE Exam After Forgetting Everything | Spaceraccoon's Blog"
published: 2023-10-07T06:47:00+00:00
description: "The Offensive Security Exploitation Expert (OSEE) certification is a legendary apex achievement among OffSec’s offerings - unabashedly featuring a skull logo and grim reaper iconography in previous iterations. Here’s how I tackled it while busy at work."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Passing the New OSEE Exam After Forgetting Everything

Oct 7, 2023
·

1146 words

·

6 minute read


The Offensive Security Exploitation Expert (OSEE) certification is a legendary apex achievement among OffSec’s offerings, unabashedly featuring a skull logo and grim reaper iconography in previous iterations. Here’s how I tackled it as a busy working adult.

# The Advanced Windows Exploitation (AWE) Course [🔗](https://spaceraccoon.dev/awe-osee-exam/\#the-advanced-windows-exploitation-awe-course)

The OSEE is famous for being the only OffSec certification that includes an in-person-only training, the Advanced Windows Exploitation (AWE) course. Unlike all the other OffSec courses available on the OffSec online portal, you must attend AWE in-person either when its held at a conference or specially brought in for a group. I took the AWE at Black Hat USA in August 2022.

As most people have shared, the course is very rigorous. On the first day, you are confronted with a huge binder of course notes that will, incredibly, be covered in four days. The course content itself is not end-to-end in terms of coverage like the [Windows User Mode Exploit Development (EXP-301) course](https://spaceraccoon.dev/rop-and-roll-exp-301-offensive-security-exploit-development-osed-review-and/); it assumes a lot of prior knowledge in memory corruption exploits, especially heap exploitation, as well as some Windows internals like interprocess communication and exploit mitigations.

The course covers browser, virtual machine, and kernel vulnerabilities, but the focus is not on discovering them. As the name suggests, it is about exploiting the primitives offered by the initial vulnerabilities (such as read-write) to achieve key objectives (like arbitrary shellcode execution or privilege escalation) while bypassing a multitude of exploit mitigations in Windows, such as DEP, ASLR, CFG, ACG and CET. It was interesting to start with a single exploit that bypasses DEP with ROP as usual, then gradually piling on more and more bypasss with each new mitigation activated.

To that end, you will not walk away from the course as an expert in browser or VM vulnerabilities specifically. Instead, the course equips you in more granular techniques in the primitives so that regardless of the context of the vulnerability, you can bypass mitigations and get to your desired outcome. To put it concretely, the goal is to be able to take a vulnerability discovery report - such as a Google Project Zero blogpost with minimal information, maybe an incomplete proof-of-concept code - and complete the full chain into a working, robust exploit.

Overall, while the course was comprehensive, it was extremely hectic and I fell behind by the third day. Worse, I was also preparing for [three](https://www.youtube.com/watch?v=2q-E2AKUxJ4) [separate](https://web.archive.org/web/20220827073617/https://reconvillage.org/talks/#talk-11) [talks](https://web.archive.org/web/20220812192015/https://cloud-village.org/) at DEF CON and two live hacking events during Hacker Summer Camp. Fortunately, on top of the course notes, you are given the lab VMs and the slides so that you can continue to practice after the course.

# Preparing for the Exam [🔗](https://spaceraccoon.dev/awe-osee-exam/\#preparing-for-the-exam)

Unfortunately, after finishing the course, the new OSEE exam was still being developed and would not be ready until more than half a year later, in April 2023. On one hand, I thought this was a good idea because previous reviews mentioned that the OSEE exam was surprisingly less challenging than the course itself and outdated. On the other hand, this meant that I had forgotten most of the course by the time the exam rolled around.

Worse, because of a busy period at work I could not take the exam right away, and kept delaying it until end-September. By the time August rolled around, I had not done any preparation. It was time to get to work.

My studying framework followed this process:

- 3 weeks: Review the entire course notes again with minimal lab practice, about 30 pages a day.
- 2 weeks: Do most of the extra miles, allowing time to re-review the relevant course materials. Along the way, create a playbook for every technique used. For example, for bypassing SMEP, the exact steps needed to overwrite the bytes I needed.
- 1 week: Review the playbook and read up on relevant materials like Connor McGarr’s [blog](https://connormcgarr.github.io/) that covers some of the materials.

Soon enough, it was the exam. Fortunately, the exam itself was rigorous but not way beyond what the materials covered; I would rank it among some of the more involved extra miles in the course materials. In other words, if you do all of the extra miles and prepare the playbooks as mentioned, I think you should be well prepared for the exam. I really appreciated the update to the exam, because it was intentionally crafted to test your understanding of the exploit primitives and bypasses covered in the course. I did not feel that it was outdated or too easy.

I took about two days to complete the exam out of the total 72 hours, taking breaks as usual and even having to step out to attend a work meeting. I managed to complete both of the tasks.

Quick tip: Closely read the [OSEE Exam Guide](https://help.offsec.com/hc/en-us/articles/360046458732-EXP-401-Advanced-Windows-Exploitation-OSEE-Exam-Guide) as well as the instructions during the exam itself. It will save you a ton of time. Don’t rush into doing the tasks and fully understand what is required first.

1 week after submitting my report, I got my passing result!

# Value of OSEE [🔗](https://spaceraccoon.dev/awe-osee-exam/\#value-of-osee)

Recently, there has been some discussion about the big price hike for the AWE course. While I took the course prior to the price increase, I think this reflects one of the key challenges in scaling cybersecurity trainings. There are two main types of trainings available today - platform-as-a-service online trainings with relatively lower prices and in-person, instructor-led trainings usually held at conferences with largely eye-popping prices. For an individual trainer with a good reputation in the field, the latter model is sufficiently profitable, but for a larger training company like OffSec, it does not scale, especially for a specialised topic that requires constant updates like advanced Windows exploitation.

So why does OffSec still offer the AWE and OSEE? In a way, there’s a brand reputation element to demonstrate that they possess the capabilities to still be on the leading edges of security research. Some of the materials covered in AWE and OSEE feature original research by the instructors with unpublished information about Windows internals and other bypass techniques. The price hike helps to balance the equation and make it at least a breakeven product. Maybe there’s a parallel here with car companies fielding F1 teams despite often losing money on them.

For the consumer, I think it helps to be aware of exactly what AWE and OSEE offers: an in-depth, advanced course on Windows exploitation - including Windows-specific kernel and heap structures. It is not meant to teach vulnerability discovery. In the organizational context, this is more useful for the exploit development team that receives crash reports from the fuzzing team or proof-of-concept exploits from n-day reports and converts them into reliable exploit chains. This is of course a rather narrow use case, and consequently demand is both inelastic and small. In that sense, it’s not a surprise that OffSec has increased its price - only that they haven’t done it sooner.

[reverse engineering](https://spaceraccoon.dev/tags/reverse-engineering) [binary](https://spaceraccoon.dev/tags/binary) [exploit](https://spaceraccoon.dev/tags/exploit)