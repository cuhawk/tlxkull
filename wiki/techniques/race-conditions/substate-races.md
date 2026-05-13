---
title: Sub-state races — INSERT-default vs UPDATE-correct windows
slug: substate-races
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/race-condition]
inbound: []
---

# Sub-state races

James Kettle — "Smashing the State Machine" / DEFCON 2023.

## Pattern
Exploit timing windows inside a single HTTP request handler. Example:
user is created with default admin role, then UPDATE sets correct
non-admin role. Race two parallel sign-up + use-account requests against
the window between INSERT-default-admin and UPDATE-set-correct → second
request reads the user with default-admin role still set.

GitLab change-email race: function passes destination as parameter but
reads confirmation token from DB at template-render time → race two
change-email calls; you receive other email's token at your address.

## Preconditions
- Multi-statement handler with intermediate sensitive state.
- Two parallel requests can hit the same row mid-write.
- HTTP/2 backend lets you single-packet-attack (eliminates network
  jitter).

## Detection
- Trace SQL/state-machine of any handler that creates+modifies a
  privileged object.
- Look for default-then-update patterns (defaults often more permissive).

## Triggering
Burp Repeater: group N tabs → "Send group in parallel". Tab 1 = signup;
Tab 2 = use-account request that reads role.

## Related
- [[uuidv1-sandwich]]
- [[single-packet-attack]] (existing)

## Seen in the wild
- GitLab email-confirmation race (James Kettle PoC).
- Multiple in-the-wild ATO chains.

## References
- portswigger.net/research — "Smashing the State Machine"
- Critical Thinking Podcast Ep 32
