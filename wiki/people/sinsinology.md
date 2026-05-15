---
title: Sina Kheirkhah (SinSinology)
slug: sinsinology
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [sinsinology, summoningteam]
role: researcher
primary_focus: enterprise-software
tags: [person, role/researcher, focus/enterprise-software, focus/dotnet-exploitation, focus/deserialization, focus/pwn2own, focus/n-day, focus/auth-bypass, focus/reverse-engineering]
inbound: []
---

# Sina Kheirkhah (SinSinology)

## Identity

- Real name: **Sina Kheirkhah**. Publishes under handle **SinSinology**.
- Full-time vulnerability researcher and founding member of **Summoning Team** (`summoning.team`), a boutique vuln-research outfit focused on enterprise software n-days and Pwn2Own.
- Pwn2Own competitor across 2022, 2023, 2024 (twice) and 2025 (three times). **Master of Pwn** winner at Pwn2Own Tokyo 2025 (solo) and Pwn2Own Cork Ireland 2025 (with team). First-ever winner of Pwn2Own Berlin 2025's AI category (Chroma DB exploit, $20k).
- Trainer — runs *Advanced .NET Exploitation Training* at REcon Montreal (4 days, 15+ RCE chains across real-world software).
- Team members at Summoning: [@_mccaulay](https://x.com/_mccaulay), [@Yogehi](https://x.com/Yogehi), [@Ch0pin](https://x.com/Ch0pin), [@hyprdude](https://x.com/hyprdude).

> Note: question prompt asked about "Nguyen Jang" — that is **Jang (`Janggggg`)**, a separate ZDI/VCSLAB researcher (Pwn2Own 2023 SharePoint). Not SinSinology.

## Focus areas

- **Enterprise on-prem software n-days** — Veeam, Ivanti, Citrix, Fortinet, SonicWall, SysAid, Progress (WhatsUp Gold, MOVEit, Telerik Report Server), Cleo, Oracle E-Business Suite. The "post-Pwn2Own writeup that drops a working chain a few days after patch" niche.
- **.NET internals and exploitation** — .NET Remoting, WCF (Windows Communication Foundation), deserialization gadget chains, IIS module abuse, mitigation bypasses. Signature pivot: turning a small primitive (path traversal, SQLi, hardcoded JWT secret) into a full Remoting/WCF RCE.
- **Java deserialization** — VMware NSX Manager, vRealize Network Insight chains.
- **Auth-bypass-into-RCE chaining** — most blog posts begin with a creative auth bypass (hardcoded secret, allow-list vs block-list mismatch, path-confusion) and end in deserialization or command injection.
- **Pwn2Own server-category exploitation** — Microsoft SharePoint and Exchange targeting; AI category (Chroma) for Berlin 2025.

## Online presence

- Team site / blog: [summoning.team](https://summoning.team/) and [summoning.team/blog](https://summoning.team/blog/).
- About / team bio: [summoning.team/about](https://summoning.team/about/).
- X / Twitter: [@SinSinology](https://x.com/SinSinology). Team account: [@SummoningTeam](https://x.com/SummoningTeam).
- GitHub: [github.com/sinsinology](https://github.com/sinsinology) (20 repos, activity set to private).
- Medium: [sinsinology.medium.com](https://sinsinology.medium.com) — profile exists but currently has no published stories (writing happens on the Summoning blog).
- REcon 2025 training: [recon.cx/2025/trainingAdvanced.NETExploitationTraining.html](https://recon.cx/2025/trainingAdvanced.NETExploitationTraining.html).

## Key research / posts

- **[Oracle E-Business Suite Pre-Auth RCE Chain — CVE-2025-61882](https://summoning.team/blog/well-well-well.-its-another-day.-oracle-e-business-suite-pre-auth-rce-chain-cve-2025-61882/)** — Pre-auth RCE chain against Oracle EBS; representative of the Summoning "post-disclosure full chain walk-through" format.
- **[Fortinet FortiSIEM Pre-Auth Command Injection — CVE-2025-25256](https://summoning.team/blog/should-security-solutions-be-secure-maybe-were-all-wrong-fortinet-fortisiem-pre-auth-command-injection-cve-2025-25256/)** — Pre-auth RCE in the phMonitor RPC service.
- **[Fortinet FortiWeb Fabric Connector — CVE-2025-25257](https://summoning.team/blog/pre-auth-sql-injection-to-rce-fortinet-fortiweb-fabric-connector-cve-2025-25257/)** — Pre-auth SQL injection lifted into RCE. Canonical "SQLi → RCE on a security appliance" pattern.
- **["CitrixBleed 2" — Citrix NetScaler Memory Disclosure CVE-2025-5777](https://summoning.team/blog/how-much-more-must-we-bleed-citrix-netscaler-memory-disclosure-citrixbleed-2-cve-2025-5777/)** — Uninitialized-variable memory disclosure; mirror of the original CitrixBleed pattern.
- **[SonicBoom — SonicWall SMA CVE-2023-44221 + CVE-2024-38475](https://summoning.team/blog/sonicboom-from-stolen-tokens-to-remote-shells-sonicwall-sma-cve-2023-44221-cve-2024-38475/)** — Apache path-confusion chained with a post-auth stack overflow.
- **[SysAid On-Premise Pre-Auth RCE Chain — CVE-2025-2775](https://summoning.team/blog/sysowned-your-friendly-support-ticket-sysaid-on-premise-pre-auth-rce-chain-cve-2025-2775-and-friends/)** — Pre-auth XXE leaks admin password, post-auth command injection finishes the chain.
- **[Veeam Backup & Replication Domain-Level RCE — CVE-2025-23120](https://summoning.team/blog/domain-level-rce-in-veeam-backup-replication-cve-2025-23120/)** — Allow-list vs block-list mismatch bypass in deserialization filter; second Veeam pre-auth chain.
- **[Veeam Backup & Replication Pre-Auth (3-bug) RCE — CVE-2024-40711](https://summoning.team/blog/veeam-backup-response-rce-with-auth-but-mostly-without-auth-cve-2024-40711/)** — Three-bug chain over **.NET Remoting**. The "Veeam .NET Remoting" reference.
- **[Ivanti Connect Secure Pre-Auth RCE — CVE-2025-0282](https://summoning.team/blog/ivanti-connect-secure-rce-cve-2025-0282/)** + **[walkthrough](https://summoning.team/blog/ivanti-connect-secure-rce-walkthrough-and-techniques-cve-2025-0282-copy/)** — Stack overflow in the IFT TLS VPN protocol; full exploitation walk-through with mitigation bypasses.
- **[Citrix Virtual Apps and Desktops Pre-Auth RCE — CVE-2024-8068/8069](https://summoning.team/blog/citrix-virtual-apps-and-desktops-unauth-rce/)** — .NET deserialization in the Session Recording feature.
- **[Ivanti EPM Pre-Auth RCE — CVE-2024-29847](https://summoning.team/blog/ivanti-epm-cve-2024-29847-deserialization-rce/)** — CVSS 9.8 deserialization RCE.
- **[Fortimanager Pre-Auth RCE — CVE-2024-47575 ("FortiJump")](https://summoning.team/blog/hop-skip-fortijump-fortijump-higher-fortinet-fortimanager-cve-2024-47575/)** — Reverse-engineering the fgfm protocol, auth bypass, 0day chain.
- **[WhatsUp Gold series — CVE-2024-6670 / 4885 / 4883 / 5009](https://summoning.team/blog/progress-whatsup-gold-rce-cve-2024-4885/)** — Four-post arc: SQLi → auth bypass, two path-traversal-to-RCE primitives (`GetFileWithoutZip`, `WriteDataFile`), plus `SetAdminPassword` privesc. The post that spawned his .NET WCF abuse research.
- **[MOVEit Transfer Auth Bypass — CVE-2024-5806](https://summoning.team/blog/authentication-bypass-moveit-transfer-cve-2024-5806/)** — Creative auth-bypass technique combined with .NET exploitation.
- **[Progress Telerik Report Server — CVE-2024-4358 + CVE-2024-1800](https://summoning.team/blog/progress-report-server-rce-cve-2024-4358-cve-2024-1800/)** — Zero-day auth bypass chained with .NET deserialization. "Molding lies into reality."
- **[Veeam Recovery Orchestrator — CVE-2024-29855](https://summoning.team/blog/veeam-recovery-orchestrator-auth-bypass-cve-2024-29855/)** + **[Veeam Enterprise Manager — CVE-2024-29849](https://summoning.team/blog/veeam-enterprise-manager-cve-2024-29849-auth-bypass/)** — Hardcoded JWT secret → token forgery for any user.
- **[PHP CGI argument-injection — CVE-2024-4577](https://summoning.team/blog/no-way-php-strikes-again-cve-2024-4577/)** — Walkthrough of the Best-Fit-mapping CGI RCE.
- **[VMware NSX Manager Pre-Auth RCE — CVE-2021-39144 + CVE-2022-31678](https://summoning.team/blog/vmware-nsx-manager-rce-cve-2021-39144-cve-2022-31678/)** — Java deserialization RCE.
- **[VMware vRealize Network Insight RCE — CVE-2023-20887](https://summoning.team/blog/vmware-vrealize-network-insight-rce-cve-2023-20887/)** + **[static-SSH-key RCE — CVE-2023-34039](https://summoning.team/blog/vmware-vrealize-network-insight-rce-cve-2023-34039/)** — Pre-auth code execution; second post is hardcoded-credential abuse.

## CT podcast appearances

- [2024-07-18 Ep 80 — Pwn2Own VS H1 Live Hacking Event (feat SinSinology)](../sources/podcasts/ct/20240718_S78r0Pc5ph4_Pwn2Own_VS_H1_Live_Hacking_Event_feat_SinSinology_Ep._80.en.vtt) — Origin story, contrast between Pwn2Own (binary RE / on-prem enterprise / time-boxed live demo) and H1 Live Hacking events (web bug bounty / scope-bounded / per-bug payout). Episode page: [criticalthinkingpodcast.io/episode-80-pwn2own-vs-h1-live-hacking-event-feat-sinsinology](https://www.criticalthinkingpodcast.io/episode-80-pwn2own-vs-h1-live-hacking-event-feat-sinsinology/); HackerNotes: [blog.criticalthinkingpodcast.io/p/hackernotes-ep80-pwn2own-vs-h1-live-hacking-event-feat-sinsinology](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep80-pwn2own-vs-h1-live-hacking-event-feat-sinsinology); Spotify: [open.spotify.com/episode/0gDljQ29oulbiywpXrmEE0](https://open.spotify.com/episode/0gDljQ29oulbiywpXrmEE0).

## Notes

- **Enterprise-server n-day specialist, not a web-bug-bounty hunter.** Output cadence is "vendor advisory drops → Summoning blog drops a working chain a few days later." Bookmark the blog RSS rather than waiting for advisories.
- **Pwn2Own competitor profile.** Server category and AI category (Berlin 2025 Chroma). Historically targeted Microsoft SharePoint and Exchange in the server bracket per ZDI rules; the prompt's "ProxyShell-class chains" framing is directionally correct but ProxyShell itself is Orange Tsai / DEVCORE — not SinSinology. Cross-link technique pages there if you want the ProxyShell lineage.
- **.NET exploitation house style.** Recurring building blocks across his catalog: `.NET Remoting` services (Veeam), `WCF` services (WhatsUp Gold), `BinaryFormatter` / `SoapFormatter` / `NetDataContractSerializer` deserialization, IIS module hijack, and allow-list-vs-block-list filter bypasses. If a target ships any of those primitives, this blog is the first thing to read.
- **Auth-bypass-first methodology.** Almost every chain starts with a small auth bypass (hardcoded secret, path confusion, encoding mismatch, allow-list collision) before the deserialization or command injection actually fires. Useful framing for our own chain triage: rate the auth-bypass surface separately from the post-auth gadget surface.
- **Tooling** — no public flagship tool from SinSinology himself; the artifacts are the blog posts plus the REcon training. GitHub is set to private-activity so PoCs are released via Summoning blog inline rather than as standalone repos.
- **Adjacent researchers to track together** — Orange Tsai (DEVCORE, ProxyShell/ProxyLogon lineage), Peterjson (Pwn2Own 2021 Exchange chain reproductions), Janggggg / ZDI (SharePoint Pwn2Own 2023). Different teams, overlapping target surface.
- **Cross-refs** — when we encounter targets shipping .NET Remoting, WCF, hardcoded JWT secrets, deserialization filters, or Veeam/Citrix/Ivanti/Fortinet/WhatsUp Gold/SonicWall, his blog is the canonical reference. Seed candidates for future `wiki/techniques/` pages: `.NET Remoting RCE`, `WCF service abuse`, `deserialization allow-list bypass`, `hardcoded JWT secret token forgery`.
