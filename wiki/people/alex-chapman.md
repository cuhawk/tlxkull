---
title: Alex Chapman (ajxchapman)
slug: alex-chapman
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [ajxchapman]
role: hunter
primary_focus: server-side
tags: [person, role/hunter, focus/server-side, focus/ci-cd, focus/container-escape, focus/source-review, focus/lhe]
inbound: []
---

# Alex Chapman (ajxchapman)

## Identity

- **Real name:** Alex Chapman
- **Primary handle:** `ajxchapman`
- **Role:** Full-time bug bounty hunter
- **Based:** London, UK
- **Background:** Computer Science BSc (2007). Started as pentester at Deloitte (2007), then 6 years at Context Information Security (pentest / red team / security research). Went full-time bounty April 2019.

## Focus areas

- Server-side bugs on technically-interesting targets (over hunting a specific vuln class)
- CI/CD pipeline security (GitLab, BitBucket Pipelines)
- Container escapes (Docker, Kata Containers, privileged containers)
- White / grey box source review — leverages access to source or binaries
- Native applications and embedded scripting language sandboxes
- Live Hacking Events (LHE) — known for landing repeated crits

## Online presence

- [Blog — blog.ajxchapman.com](https://blog.ajxchapman.com/)
- [X / Twitter — @ajxchapman](https://x.com/ajxchapman)
- [GitHub — @ajxchapman](https://github.com/ajxchapman)
- [HackerOne — ajxchapman](https://hackerone.com/ajxchapman)
- [Bluesky — @ajxchapman.bsky.social](https://bsky.app/profile/ajxchapman.bsky.social)
- [bughuntr.io](https://bughuntr.io) — training platform he created for security professionals

## Key research / posts

- [Exploit Archeology — Exploiting an old unknown Server Side Browser](https://blog.ajxchapman.com/posts/2024/05/08/exploit-archeology.html) — UAF in `JSArray::sortCompactedVector` in an outdated WebKit-based server-side renderer; OOB read/write primitives → RCE on the server processing user HTML/JS. Signature "find weird old tech, weaponise it" piece.
- [Bug Bounty Reports Explained: The secret to finding many Criticals](https://blog.ajxchapman.com/posts/2024/06/25/bbre.html) — video on how he sustains a high crit rate.
- [BitBucket Pipelines Kata Containers VM Escape (CVE-2020-28914)](https://blog.ajxchapman.com/posts/2021/02/28/kata-containers-escape.html) — read-only mount bypass in Kata → host VM escape from a CI runner.
- [Moby — remapped root → real root (CVE-2021-21284)](https://blog.ajxchapman.com/posts/2021/02/02/CVE-2021-21284.html) — privilege escalation in Docker `userns-remap`.
- [Privileged Container Escape via cgroup `release_agent`](https://blog.ajxchapman.com/posts/2020/11/19/privileged-container-escape.html) — canonical write-up of the `release_agent` escape from a `--privileged` container.
- [GitLab — project-archive import overwrites other users' uploads (CVE-2019-5469)](https://blog.ajxchapman.com/posts/2019/12/11/hackerone-gitlab-534794.html) — file overwrite via the import flow when secret + filename are known.
- [Kata Containers `hostPath` file write](https://blog.ajxchapman.com/posts/2020/11/30/bugcrowd-private-7bf77429-2b94-44ea-b6f9-c1fc59b2fd17.html) — companion to the Kata escape; CVE-2020-28914 root.
- [44Con 2019 — Continuous Integration, Continuous Bounties](https://blog.ajxchapman.com/posts/2019/09/11/continuous-integration-continuous-bounties.html) — conference talk on systematic CI/CD bug hunting methodology.
- [On Full-Time Bug Bounty Hunting](https://blog.ajxchapman.com/posts/2020/02/10/on-full-time-bug-bounty-hunting.html) — reflections after the first 12 months full-time.
- [Hacker Spotlight interview — HackerOne](https://www.hackerone.com/blog/hacker-spotlight-interview-ajxchapman) — methodology / engagement-driver interview.
- [Ask a hacker: ajxchapman — GitLab blog](https://about.gitlab.com/blog/ajxchapman-ask-a-hacker/) — long-form interview about hunting on the GitLab program.

## Tooling (GitHub)

- [ReServ](https://github.com/ajxchapman/ReServ) — scriptable HTTP/HTTPS + DNS servers for callbacks and configurable response fuzzing.
- [sshreverseshell](https://github.com/ajxchapman/sshreverseshell) — full-TTY reverse shell over SSH.
- [CmdRunner](https://github.com/ajxchapman/CmdRunner) — modular command encoder for running commands across multi-hop systems.
- [researchservers_c2](https://github.com/ajxchapman/researchservers_c2) — minimal single-user C2 built on top of his research servers.

## CT podcast appearances

- [2023-08-10 Ep 31 — Alex Chapman: How to Be a High-Impact Hacker / The Man of Many Crits](https://www.criticalthinkingpodcast.io/episode-31-alex-chapman-the-man-of-many-crits/)

## Notes

- **LHE specialist.** Recurring theme in CT and HackerOne content: lands repeated criticals at Live Hacking Events. Justin Gardner on CT Ep 31 framed him as "the man of many crits"; the "Justin vs. Alex at a LHE" anecdote in the HackerOne writeups refers to head-to-head crit hunts.
- **High-impact-first mindset.** Explicitly avoids hunting "by bug class" — picks the most technically-interesting asset on a program (CI/CD runner, custom binary, sandboxed scripting engine) and hunts for crits there. The Exploit Archeology post is the purest expression: pick an obscure old component nobody else is looking at, weaponise it.
- **White / grey box bias.** Strong preference for programs that expose source or binaries (GitLab being the archetype). Reads diffs and fix commits to find adjacent variants — a pattern worth mirroring in our own workflow when programs ship open source.
- **CI/CD as a hunting ground.** Half his public CVE list lives in container runtimes used by CI (Docker, Kata, runners). Worth pairing with our own CI/CD scope on relevant targets.
- **Engagement-driven.** Publicly states that responsive triagers + personal acknowledgement materially change which programs he keeps hitting. Useful signal when evaluating program quality.

<!-- sources:auto:start -->
## Ingested blog posts

- [posts 2020 11 19 privileged container escape](../sources/blogs/personal/alex-chapman/posts-2020-11-19-privileged-container-escape.md)
- [posts 2021 02 28 kata containers escape](../sources/blogs/personal/alex-chapman/posts-2021-02-28-kata-containers-escape.md)
- [posts 2021 11 10 practical security recommendations for startups](../sources/blogs/personal/alex-chapman/posts-2021-11-10-practical-security-recommendations-for-startups.md)
- [posts 2024 05 08 exploit archeology](../sources/blogs/personal/alex-chapman/posts-2024-05-08-exploit-archeology.md)

<!-- sources:auto:end -->

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/alex-chapman/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

