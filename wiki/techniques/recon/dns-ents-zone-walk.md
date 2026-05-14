---
title: DNS subdomain enum — ENTs, NSEC zone walking, NSEC3 cracking, CZDS
slug: dns-ents-zone-walk
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/recon, technique/dns, technique/subdomain-enum]
inbound: []
---

# DNS subdomain enum — ENTs, NSEC zone walking, NSEC3 cracking, CZDS

## Pattern

Three under-used DNS primitives + one ICANN data feed that together
extend subdomain enumeration well past the standard cert-transparency /
brute-force pipeline.

### 1. ENT (Empty Non-Terminal) NOERROR signal

A DNS node can have **no records of its own** but **have descendants
with records**. Query for `ctbb.runerator.com` — the authoritative
server returns `NOERROR` (not `NXDOMAIN`) with no answer; this means
"this name exists in the zone as a parent of some other name." That
narrows where to fuzz: brute-force a level under any ENT NOERROR
response; don't waste packets brute-forcing under NXDOMAIN.

### 2. NSEC zone walking

DNSSEC's `NSEC` record proves non-existence of a name by *pointing to
the next existing name in canonical order*. Walking from `a.example.`
forward yields every signed name in the zone. Old technique but still
works on zones that haven't migrated to NSEC3.

### 3. NSEC3 hashed zone walking

NSEC3 replaces plaintext "next name" with `SHA1(name + salt)`. Iterate
hashed responses to enumerate the set of *hashes*; crack them offline
with the same salt + iterations. Tool: **nsec3map**. You can still
estimate total record count from the number of unique hashes returned
even without cracking.

### 4. ICANN CZDS (Centralized Zone Data Service)

ICANN's portal where you can request the zone file for any gTLD that
participates (`czds.icann.org`). After approval, you get bulk
downloads — every domain on the TLD that has an authoritative NS or
DS record set. Especially valuable for obscure TLDs (`.do`, `.world`,
new gTLDs) where a target with a vanity hostname is exclusively
findable from the zone file.

## Preconditions

- ENT/NSEC/NSEC3: target zone returns the relevant record types (most
  signed zones do).
- CZDS: ICANN-approved account; only gTLDs (not ccTLDs).

## Detection

- `dig <name> @<ns> +noall +answer +authority` — observe NOERROR vs
  NXDOMAIN.
- `dig <name> NSEC` / `NSEC3 @<ns>` — confirm DNSSEC + algorithm.

## Triggering

ENT signal:
```
dig ctbb.runerator.com @ns.runerator.com +noanswer
# Status: NOERROR + Authority section = ENT, brute-force under this name.
```

NSEC walk:
```
dig a. example.com NSEC @ns.example.com +noall +answer
# Returns next name; iterate forward.
```

NSEC3 crack:
```
nsec3map -z example.com -n ns.example.com
# Returns hashed names; pipe to hashcat with the published salt.
```

CZDS:
```
# request access at czds.icann.org per TLD;
# downloaded zone is gzipped flat text.
grep '^<target-string>' tld.zone | awk '{print $1}'
```

## Bypasses

(this is a recon technique, not an exploit primitive)

## Seen in the wild

- {date: 2025-11-27, source: CT Ep 150} — Justin Gardner episode coverage;
  attributes the talk to social-sec (zero-x-zero-social-sec) handle on
  Twitter. Cited as not-frequently-known in the bounty community.

## References

- Critical Thinking Podcast Ep 150
- nsec3map repository (NSEC3 hash cracker)
- ICANN CZDS portal — czds.icann.org
- Related: [[threat-intel-creds-residential]]
