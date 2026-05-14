---
title: Scoring UUID-IDORs: attack-complexity high + Oracle chain
slug: cvss-uuid-ac-high
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/idor, technique/cvss, technique/triage]
inbound: []
---

# Scoring UUID-IDORs: attack-complexity high + Oracle chain

## Pattern

Programs that score strictly by CVSS often N/A a UUID-IDOR with "UUIDs
are not enumerable, no real impact." The correct CVSS framing is **not**
to lower confidentiality/integrity but to set attack-complexity high:
the bug *is* exploitable, but a condition outside the attacker's control
(knowing or obtaining the target UUID) is required. The CVSS standard
explicitly allows AC:H for this situation.

The second move is to remove the AC:H mitigation by chaining a UUID
Oracle — any endpoint that leaks a target's UUID. Common Oracles:

- email-to-UUID lookup endpoints (search, password-reset, share-link).
- error messages containing target's UUID ("user <uuid> not found").
- metric/listing endpoints that dump all UUIDs once.
- legitimate features that expose UUIDs (avatar URLs, public profile
  identifiers).

Once chained, the IDOR is AC:L again and severity jumps full grade.

## Preconditions

- IDOR exists against a UUID-keyed resource.
- The program treats UUIDs as a non-sensitive identifier (so leaking
  one is not itself a vuln per their threat model).

## Detection

For the IDOR itself: standard auth-context swap.

For the Oracle: enumerate any endpoint that takes a user-controllable
identifier (email, username, shared-link slug, public-profile slug) and
returns a UUID anywhere — header, body field, error message, redirect
target. Static-flow tools (caido search, js_analyzer tag table for
`uuid`/`guid` patterns) help.

## Triggering

Submit the IDOR with the Oracle-derived UUID. Score:
- without Oracle: AV:N / AC:H / PR:* / UI:N / S:U / C:H / I:H / A:N
- with Oracle: AV:N / AC:L / PR:* / UI:N / S:U / C:H / I:H / A:N

## Bypasses

(this is a triage technique, not an exploit primitive)

## Seen in the wild

- {date: 2023-03-16, source: CT Ep 11} — discussed by Justin Gardner as the
  standard play against teams that close UUID-IDORs as informative,
  citing Rezo as the originator of the "UUID-IDORs are real" campaign.

## References

- Critical Thinking Podcast Ep 11
- CVSS v3.1 specification, Attack Complexity section
- Related: [[unicode-sso-normalize]], [[match-replace-admin-flag]]
