---
source: bughunters
source_url: https://bughunters.google.com/blog/google-vrps-in-review-2025
title: "Google VRPs in Review – 2025 - Google Bug Hunters"
description: "This blog post takes you through the 2025 highlights across the assorted VRPs at Google."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/google-vrps-in-review-2025#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Google VRPs in Review – 2025

![](https://storage.googleapis.com/bughunters-article-images/blogs/tony.jpg)

Tony Mendez

Technical Program Manager

![](https://storage.googleapis.com/bughunters-article-images/blogs/goedi.jpg)

Dirk Göhmann

Technical Writer

Published: Mar 11, 2026

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Google VRPs in Review – 2025

2025 marked a special year in the history of vulnerability rewards and bug
bounty programs at Google: our 15th anniversary 🎉🎉🎉! Originally
[started in 2010](https://security.googleblog.com/2010/11/rewarding-web-application-security.html),
our vulnerability reward program (VRP) has seen constant additions and
expansions over the past decade and a half, clearly indicating the value the
programs under this umbrella contribute to the safety and security of Google and
its users, but also highlighting their acceptance by the external research
community, without which such programs cannot function.

Coming back to 2025 specifically, our VRP once again confirmed the ongoing value
of engaging with the external security research community to make Google and its
products safer. This was more evident than ever as we awarded over $17 million
(an all-time high and more than 40% increase compared to 2024!) to over 700
researchers based in countries around the globe – across all of our
[programs](https://bughunters.google.com/about/rules/6744710187712512).

## Vulnerability Reward Program 2025 in Numbers

![](https://storage.googleapis.com/bughunters-article-images/blogs/google-vrps-in-review-2025_01.png)

![](https://storage.googleapis.com/bughunters-article-images/blogs/google-vrps-in-review-2025_02.png)

Want to learn more about who’s reporting to the VRP? Check out our
[Leaderboard](https://bughunters.google.com/leaderboard) on the
[Google Bug Hunters site](https://bughunters.google.com/).

## VRP Highlights in 2025

In 2025 we made a series of changes and improvements to our VRP and related
initiatives, and continued to invest in the security research community through
a series of focused events:

- The new, dedicated AI VRP was
[launched](https://bughunters.google.com/blog/6116887259840512/announcing-google-s-new-ai-vulnerability-reward-program),
underscoring the importance of this space to Google and its relevance for
external researchers. Previously organized as a part of the Abuse VRP,
moving into a dedicated VRP has gone hand in hand with improvements to the
rules, offering researchers more clarity on scope and reward amounts (see
the dedicated section below for more details).
- Similarly, the Chrome VRP now also includes reward categories for problems
found in
[AI features](https://bughunters.google.com/about/rules/chrome-friends/5745167867576320/chrome-vulnerability-reward-program-rules#gemini-ai-vulnerabilities)
(see the dedicated section below for more details).
- We
[launched](https://bughunters.google.com/blog/6551590643040256/new-patch-rewards-program-for-osv-scalibr)
a patch rewards program for OSV-SCALIBR, Google's open source tool for
finding vulnerabilities in software dependencies. Contributors are rewarded
for providing novel OSV-SCALIBR plugins for inventory, vulnerability, or
secret detection that expand the tool’s scanning capabilities. Besides
strengthening the tool’s capabilities for all users, user submissions
already helped us uncover and remediate a number of leaked secrets
internally!
- As part of Google's Cybersecurity Awareness Month campaign in October, we
hosted our very own
[security conference in Mexico City, ESCAL8](https://bughunters.google.com/blog/6489680025550848/escal8-2025-gathering-cybersecurity-expertise-in-mexico-city).
The conference included init.g(mexico), our cybersecurity workshop for
students, HACKCELER8, Google’s CTF finals, and a _Safer with Google_
seminar, sharing technical thought leadership with Mexican government
officials.
- bugSWAT, our special invite-only live hacking event, saw several editions in
2025 and delivered some outstanding findings across different areas:
  - We hosted our first dedicated
    [AI bugSWAT (Tokyo) in April](https://bughunters.google.com/blog/5753079171252224/ai-bugswat-in-tokyo-2025-hacker-roadshow)
    which yielded a whopping 70+ reports filed and over $400,000 in rewards
    issued.
  - We continued the momentum in early summer with
    [Cloud bugSWAT (Sunnyvale) in June](https://bughunters.google.com/blog/hardening-google-cloud-insights-from-the-latest-cloud-vrp-bugswat)
    resulting in 130 reports, with $1,600,000 in rewards paid out.
  - Next in line was bugSWAT Las Vegas in August, leading to 77 reports and
    rewards of $380,000.
  - And finally, as part of ESCAL8 in Mexico City,
    [bugSWAT Mexico](https://bughunters.google.com/blog/6489680025550848/escal8-2025-gathering-cybersecurity-expertise-in-mexico-city#bugswat-hacking-for-a-safer-internet)
    focused on many different targets and spaces including AI, Android, and
    Cloud, and resulted in the filing of 107 reports, totalling $566,000 in
    rewards to date.

More detailed updates on selected programs are shared in the following sections.

## Reports from VRPs

### Android & Devices

In 2025, the Android and Google Devices Security Reward Program awarded over
$2,900,000, navigating a year defined by new hardware and evolving adversarial
tactics, but also by an increasingly security-hardened environment. Our
researchers met the challenge and delivered more quality than ever – we've
observed a notable increase in bugs that were rated High or Critical.

**Hardening in Action:** The investment in platform hardening is reshaping the
threat landscape. As
[memory-safe languages](https://security.googleblog.com/2024/10/safer-with-google-advancing-memory.html)
and hardware mitigations successfully neutralize traditional memory corruption
primitives, we observed a distinct tactical shift in 2025. The year’s most
sophisticated exploit chains relied less on breaking code and more on logic
vulnerabilities. This evolution confirms our strategy: we aren't just patching
bugs; we are forcing attackers to rewrite their playbooks.

**New Frontiers AI & XR:** As AI moves to the edge, our scope has also expanded.
Researchers identified novel logic bugs in on-device Gemini implementations,
including creative lockscreen bypasses. We also prepared for the future by
launching a private grant program for Android XR.

**Top Honors:** The "Crown Jewel" of 2025 was a report by **lovepink** for a
critical firmware breakthrough. This finding was a masterclass in research,
bypassing multiple defense-in-depth layers to compromise the kernel from the
GPU, a reminder that as we harden the OS, the battleground shifts deeper into
the silicon.

**Community Shoutouts:** We extend our deepest gratitude to the researchers
defining this new era:

- **Songzhou Shi (石松洲) ( [@canyie](https://github.com/canyie)) of LSPosed**
**Team**: Our 2025 Champion, securing both the highest total reward amount and
tying for the highest number of valid reports.
- **Alena Skliarova ( [@askliarova](https://www.linkedin.com/in/askliarova))**:
Named "Most Valuable Hacker" at the ESCAL8 live hacking event for her
dominance in the Pixel track.

### Chrome

Overall, Chrome rewarded $3,716,750 to over 100 different reporters.

In particular, Chrome researchers dug into the **v8 sandbox**, finding several
holes and providing new classes of escape for the v8 team to remove, thus
strengthening the security boundary the v8 sandbox provides. To achieve this,
researchers created novel in-process instrumentation and fault injection
mechanisms, working on the leading edge of academic fuzzer research.

Pivoting to **memory safety efforts** – While improvements like raw\_ptr and
object quarantining within Chrome have reduced the number of reported sandbox
escapes with full chain exploits, two researchers were still able to find logic
bugs in Chrome’s IPC mechanisms with demonstrated exploitation, leading to
rewards of $250,000.

In summary, Chrome’s [Top 20 researchers](https://issues.chromium.org/473635778)
worked across all facets of Chrome, from memory safety and fuzzing to
user-interface issues including permission hijacking and displaying URLs
correctly for two web pages at once using split-view.

Finally, Chrome is leading the way in making Gemini available to help people
browse the web and the Chrome VRP now includes reward categories for problems
found in
[AI features](https://bughunters.google.com/about/rules/chrome-friends/5745167867576320/chrome-vulnerability-reward-program-rules#gemini-ai-vulnerabilities).
Researchers invited to live hack events (bugSWAT) got a sneak peek at these
features and provided invaluable examples of security bugs to avoid as they
advanced beyond the prototype stage.

### Cloud

2025 marked the Cloud Vulnerability Reward Program's first full year of
operation, after its
[launch in October 2024](https://cloud.google.com/blog/products/identity-security/google-cloud-launches-new-vulnerability-rewards-program),
when it was spun out from the Google VRP to drive a more focused investment into
securing Google Cloud.

Our commitment to recognizing and rewarding top-tier research is reflected in
the substantial payouts made this year. We awarded a total of $3,574,399 in
rewards to 143 different researchers, demonstrating the high impact and quality
of the vulnerabilities reported.

Throughout the year, the Cloud VRP processed 1,774 security reports. Our
researcher’s invaluable contributions led to the discovery and remediation of
critical vulnerabilities, strengthening the security of Google Cloud for our
users and customers. Insights gleaned from multiple reports prompted significant
architectural changes in several Google Cloud products. These proactive changes
enhance long-term security and resilience, moving beyond just patching to
fundamental improvements for our customers.

Furthermore, we deeply appreciated engaging and collaborating with researchers
through our **bugSWAT events**. The program successfully conducted three
bugSWATs, bringing Cloud security engineers and product engineers together with
our world-class researchers. A major highlight of 2025 was the launch of our
inaugural Google Cloud-specific bugSWAT, tailored to address unique security
challenges within the Google Cloud ecosystem. This focused effort yielded
excellent results, further solidifying Cloud VRP's role in proactive security.

### AI

In October, we
[launched the AI VRP](https://bughunters.google.com/blog/announcing-googles-new-ai-vulnerability-reward-program),
recognizing that securing Generative AI Products requires specialized research
distinct from traditional vulnerabilities. Our
[updated rules and scope](https://bughunters.google.com/about/rules/google-friends/ai-vulnerability-reward-program-rules)
offer more clear incentives for research into high-impact issues such as rogue
actions, data exfiltration, and context poisoning.

Since the AI VRP launch, we’ve issued over $350,000 in rewards, bringing our
2025 AI reward total to over $890,000. Notable reports included Nassi, Cohen,
and Yair’s fantastic
“ [Invitation Is All You Need](https://arxiv.org/abs/2508.12175),” which
highlighted some real-world risks of indirect prompt injection, and led to an
accelerated rollout of
[additional defenses](https://security.googleblog.com/2025/06/mitigating-prompt-injection-attacks.html)
on our part.

In 2025 we also hosted our first-ever **AI bugSWAT in Tokyo**, a massive success
that generated over 70 valid reports and $400,000 in rewards. This event proved
that live, hands-on collaboration between researchers and our AI Security and
Trust & Safety Teams is the fastest way to harden models and integrations – and
was the first bugSWAT featured in a
[podcast](https://www.criticalthinkingpodcast.io/episode-122-we-won-googles-ai-hacking-event-in-tokyo-main-takeaways/)!

### Abuse

The Abuse VRP program saw a 65% year-over-year increase in rewards, even while
accounting for the October separation of the Abuse and AI programs. In 2025, we
issued a total of $482,000 in non-AI rewards. Notable reports included Arvin
Shivram’s identification of a
[vulnerability chain](https://brutecat.com/articles/leaking-google-phones)
allowing an attacker to brute-force a user’s account recovery phone number.

### OSS

Over the year 2025, the OSS VRP processed 192 security reports, of which 62 were
rewarded monetarily, with an overall amount of $327,672 going to security
researchers. We focused on supply chain security compromises and updated GitHub
security rules to prevent major compromises, based on submitted bug reports. We
prevented a significant class of vulnerabilities from running dangerous GitHub
Actions workflows on unreviewed code, by adding org-wide controls learned from
these reports.

- The **top reward** was given to
[inspector-ambitious](https://x.com/inspector_amb) for discovering a supply
chain compromise on Bazel Central Registry (BCR). This included a $1,000
bonus for a very well crafted and complete report, including following up
from previous vulnerability research on BCR. The entire attack starts from
exploiting a race condition and then bypassing presubmit checks.
Effectively, the malicious user can bypass the entire BCR pipeline, pushing
malicious Bazel packages and poisoning any Bazel build in the world.
- Another noteworthy piece of research submitted to us was a report about
prompt injection in the "Gemini Automated Issue Triage" GitHub workflow
which exfiltrates `GITHUB_TOKEN`, `GEMINI_API_KEY`, and
`GOOGLE_CLOUD_ACCESS_TOKEN` from any affected repository. The researcher
identified a custom GitHub App with overly broad permissions. The app used a
custom prompt for Gemini, and the prompt contained template arguments for
`github.event.issue` fields. Thus, attackers could create issues with
maliciously crafted titles and bodies to get full control of the GitHub app.
This exploit was also
[publicly disclosed](https://www.aikido.dev/blog/promptpwnd-github-actions-ai-agents).
- We updated our [Patch Rewards Program](http://g.co/prp) rules to place every
Google-filed OSS vulnerability explicitly into scope!

## What’s coming in 2026

In 2026, we remain fully committed to fostering collaboration, innovation, and
transparency with the security community by hosting several bugSWAT events
throughout the year, and following up with the next edition of our cybersecurity
conference, ESCAL8. More broadly, our goal remains to stay ahead of emerging
threats, adapt to evolving technologies, and continue to strengthen the security
posture of Google’s products and services – all of which is only possible in
collaboration with the external community of researchers we are so lucky to
collaborate with!

In this spirit, we'd like to extend a huge thank you to our bug hunter community
for helping us make Google products and platforms more safe and secure for our
users around the world – and invite researchers not yet engaged with the
Vulnerability Reward Program to join us in our mission to keep Google safe
(check out our [programs](https://bughunters.google.com/about/rules/6744710187712512) for inspiration 🙂)!

_Thank you to Tony Mendez, Dirk Göhmann, Alissa Scherchen, Krzysztof Kotowicz,_
_Martin Straka, Michael Cote, Sam Erb, Jason Parsons, Alex Gough, and Mihai_
_Maruseac._

Tip: Want to be informed of new developments and events around our Vulnerability
Reward Program? Follow the [Google VRP channel](https://x.com/GoogleVRP) on X to
stay in the loop and be sure to check out
the [Security Engineering blog,](https://bughunters.google.com/blog) which covers topics ranging from VRP
updates to security practices and vulnerability descriptions!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab