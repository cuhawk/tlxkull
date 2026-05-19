---
title: Matt Brown
slug: matt-brown
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [nmatt0, mattbrwn]
role: researcher
primary_focus: iot-hardware
tags: [person, role/researcher, focus/iot-hardware, focus/firmware, focus/embedded, focus/hardware-rev, focus/ble, focus/robotics, org/brown-fine-security]
inbound: []
---

# Matt Brown

## Identity

- **Real name:** Matt Brown
- **Primary handle:** `nmatt0` (GitHub, X); `mattbrwn` (YouTube, LinkedIn)
- **Role:** Founder & Principal Consultant, Brown Fine Security. Independent IoT pentester and hardware-hacking YouTuber.
- **Notoriety:** 10+ years in IoT/hardware security. Most Valuable Hacker at the 2023 H1-213 HackerOne LHE (Amazon hardware track) — the first HackerOne LHE focused on hardware hacking. Found 0-days in Amazon IoT devices. Operates the largest active YouTube channel in the hardware-hacking space (200k+ subscribers). Research featured in Wired, Ars Technica, 404 Media, Tom's Guide, Motor1.

## Focus areas

- IoT pentest end-to-end — board-level → firmware → cloud
- Hardware reverse engineering — chip-off firmware extraction, BGA reballing, firmware-chip readers, UART/JTAG/SWD bring-up
- BLE / Wi-Fi / IP-camera attack surface
- Robotics security (CT Ep. 153 topic — humanoid / consumer robots)
- Hybrid AI-assisted IoT pentesting (IoTHackBot — Claude Skills + custom tools)
- IoT recon & OSINT — finding exposed devices via Censys/Shodan-style fingerprinting

## Online presence

- [brownfinesecurity.com](https://brownfinesecurity.com/) — consulting site + bio
- [brownfinesecurity.com/about](https://brownfinesecurity.com/about) — credentials, awards, press
- [YouTube — @mattbrwn](https://www.youtube.com/@mattbrwn) — hardware-hacking channel, 200k+ subs
- [X — @nmatt0](https://x.com/nmatt0)
- [GitHub — nmatt0](https://github.com/nmatt0) — personal repos
- [GitHub — BrownFineSecurity](https://github.com/BrownFineSecurity) — org repos (iothackbot)
- [LinkedIn — mattbrwn](https://www.linkedin.com/in/mattbrwn/)

## Key research / posts

- [Hacking a Motorola Automatic License Plate Reader — Firmware Extraction and Password Cracking (YouTube)](https://www.youtube.com/watch?v=yvINGzIa2fg) — bought a Motorola ReaperHD ALPR off eBay, extracted firmware, cracked credentials. Companion X thread: [status/1872692066498851291](https://x.com/nmatt0/status/1872692066498851291).
- [Researcher Turns Insecure License Plate Cameras Into Open Source Surveillance Tool (404 Media)](https://www.404media.co/researcher-turns-insecure-license-plate-cameras-into-open-source-surveillance-tool/) — follow-on: hundreds of Motorola ALPR units misconfigured to stream video + plate data unauthenticated to the open internet; PoC scraper that timestamps plate sightings. Coverage: [Tom's Guide](https://www.tomsguide.com/computing/online-security/millions-at-risk-due-to-severe-security-flaw-in-license-plate-readers), [Motor1](https://www.motor1.com/news/746496/license-plate-cameras-easy-to-hack/), [CarBuzz](https://carbuzz.com/law-enforcement-cameras-easily-hacked/).
- [GPS Tracker teardown (YouTube via X)](https://x.com/nmatt0/status/1800847806032392411) — reversing a consumer GPS tracker on stream; community-sourced exploit ideas.
- [Intro to Hardware Hacking with Matt Brown (YouTube)](https://www.youtube.com/watch?v=SpPd0Q6dmYI) — gateway video for the channel's audience; methodology overview.
- [LIVE IoT Hacking — AMA / Hardware Hacking (YouTube)](https://www.youtube.com/watch?v=x9n5o1RaJ2I) — live-stream pentest format he popularized.
- [Open Source Intelligence for IoT Hacking (X)](https://x.com/nmatt0/status/1858901671146827966) — public talk slides / OSINT methodology for finding exposed IoT.
- [IoT pentest methodology thread (X)](https://x.com/nmatt0/status/1816087328097517761) — "hardware hacking is a means to an end; the end goal is software vulns" — his framing of where hardware sits in an IoT engagement.
- [AI HackBots finding zero days (X)](https://x.com/nmatt0/status/1990795157621653752) — IoTHackBot results teaser.
- [HackerOne H1-213 LHE Recap (LinkedIn)](https://www.linkedin.com/posts/mattbrwn_hackerone-live-hacking-event-recap-los-angeles-activity-7089716325341638656-rIZr) — first-person notes on the Amazon hardware LHE where he took MVH.

### GitHub repos worth knowing

- [BrownFineSecurity/iothackbot](https://github.com/BrownFineSecurity/iothackbot) — Claude Skills + tooling for hybrid IoT pentesting (Python, ~750 stars). Directly relevant prior art for TLX's skill model.
- [nmatt0/mitmrouter](https://github.com/nmatt0/mitmrouter) — bash setup for a Linux router that MitMs IoT traffic incl. SSL. Standard kit for IoT engagements.
- [nmatt0/bletools](https://github.com/nmatt0/bletools) — BLE pentest scripts.
- [nmatt0/mitmtools](https://github.com/nmatt0/mitmtools) — supporting scripts for various MitM workflows.

### External podcast appearances

- [Phosphorus — The Wild West of IoT (podcast)](https://phosphorus.io/podcast-matt-brown/)
- [Eclypsium BTS #37 — Hardware Hacking](https://eclypsium.com/podcasts/bts-37-hardware-hacking-matt-brown/)
- [Phillip Wylie — Hardware Hacking & Content Creation](https://thehackermaker.com/matt-brown-hardware-hacking-content-creation/)

## CT podcast appearances

- [2024-09-19 Ep. 89 — The Untapped Bug Bounty Landscape of IoT w/ Matt Brown](../sources/podcasts/ct/20240919_tSpDLTm5POs_The_Untapped_Bug_Bounty_Landscape_of_IoT_w_Matt_Brown_Ep._89.en.vtt)
- [2025-12-18 Ep. 153 — Hacking the Robots of the Future: Hardware, AI, and Bug Bounties with Matt Brown](../sources/podcasts/ct/20251218_01O5oYG8rao_Hacking_the_Robots_of_the_Future_-_Hardware_AI_and_Bug_Bounties_with_Matt_Brown_Ep.153.en.vtt) — covers robotics attack surface, IoTHackBot, and his Zero-to-Hero Hardware Hacking guide.

## Notes

- **Hardware-first hunter.** Unlike most CT guests (web/mobile/cloud), Matt's default lens is the physical device. His pipeline: buy used hardware on eBay → board-level teardown → UART/JTAG or chip-off → firmware extraction → reverse → cloud/auth analysis → CVE. The Motorola ALPR chain is the canonical example end-to-end.
- **YouTube as research multiplier.** He treats the channel as a live-research notebook — AMAs, GPS-tracker streams, ALPR teardowns. The signature pattern "post live stream → community surfaces follow-up bug ideas → next video resolves them" is unusual in this space and worth modeling for our own technique-discovery loop.
- **IoTHackBot is direct prior art for TLX.** Same architecture: Claude Skills + custom tools wrapping a domain (IoT instead of web JS). Worth a deep read of the repo when designing new TLX skills, especially for the firmware-extract / mitm phases that don't exist in TLX today.
- **Bug-bounty programs of interest he calls out:** Amazon IoT (Ring, Echo — what H1-213 was built around), and the broader Synack/H1 IoT track that most web hunters skip because the upfront hardware cost looks high. Matt's pitch on Ep. 89: hardware acquisition is amortized — same dev kit hits many programs.
- **Signature tradecraft:** chip-off → external programmer → patch firmware → reflash → boot back into a modified system for debug. BGA reballing is the part most hunters won't replicate; he teaches it on YouTube.
- **Press surface:** when he ships a finding, mainstream tech press picks it up (ALPR story ran across Wired-adjacent outlets). Useful precedent if we ever ship hardware-side findings — the disclosure-via-YouTube pattern works.
- **Religious affiliation on GitHub bio** ("Soli Deo Gloria") — context, not security-relevant.

<!-- sources:auto:start -->
## Ingested blog posts

- [attacking enterprise iot mobile apps](../sources/blogs/personal/matt-brown/blog-attacking-enterprise-iot-mobile-apps.md)
- [bypassing restricted shell on uniview security camera](../sources/blogs/personal/matt-brown/blog-bypassing-restricted-shell-on-uniview-security-camera.md)
- [cleartext communications to univew cloud servers](../sources/blogs/personal/matt-brown/blog-cleartext-communications-to-univew-cloud-servers.md)
- [firmware extraction and analysis of uniview camera](../sources/blogs/personal/matt-brown/blog-firmware-extraction-and-analysis-of-uniview-camera.md)
- [hanwha firmware file decryption](../sources/blogs/personal/matt-brown/blog-hanwha-firmware-file-decryption.md)
- [hardware hacking tools beginners guide](../sources/blogs/personal/matt-brown/blog-hardware-hacking-tools-beginners-guide.md)
- [intercepting mobile traffic with caido and frida](../sources/blogs/personal/matt-brown/blog-intercepting-mobile-traffic-with-caido-and-frida.md)
- [iot pentesting basics uart root shells](../sources/blogs/personal/matt-brown/blog-iot-pentesting-basics-uart-root-shells.md)
- [iot pentesting roadmap](../sources/blogs/personal/matt-brown/blog-iot-pentesting-roadmap.md)
- [iot vulnerability basics onvif missing authentication](../sources/blogs/personal/matt-brown/blog-iot-vulnerability-basics-onvif-missing-authentication.md)
- [police bodycam data to china](../sources/blogs/personal/matt-brown/blog-police-bodycam-data-to-china.md)
- [sidebar](../sources/blogs/personal/matt-brown/blog-sidebar.md)
- [uniview camera network services](../sources/blogs/personal/matt-brown/blog-uniview-camera-network-services.md)
- [vstarcam cb73 hardcoded root password](../sources/blogs/personal/matt-brown/blog-vstarcam-cb73-hardcoded-root-password.md)
- [vstarcam cb73 proprietary encryption analysis](../sources/blogs/personal/matt-brown/blog-vstarcam-cb73-proprietary-encryption-analysis.md)
- [blog](../sources/blogs/personal/matt-brown/blog.md)
- [iot penetration testing](../sources/blogs/personal/matt-brown/iot-penetration-testing.md)

<!-- sources:auto:end -->

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/matt-brown/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

