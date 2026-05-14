---
title: Age-to-DoB Leak (Temporal Differencing of Profile Data)
slug: age-to-dob-leak
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/info-disclosure, technique/pii]
inbound: []
---

# Age-to-DoB Leak (Temporal Differencing of Profile Data)

## Pattern

A vuln that leaks a target's **age** (integer years) appears low-impact
in isolation. Across time, however, the age value transitions from `N` to
`N+1` on exactly one day - the victim's birthday. An attacker who polls
the leak daily (or who can replay a historical leak against today's
value) recovers the **full date of birth**: birthday from the
transition day, year from the age + current date.

Generalises: any monotonically-incrementing PII derived from a hidden
date leaks the underlying date if the attacker can sample over time.
Examples:
- Account age in years (registration date).
- "Days since last login" (last-login date).
- Tenure-based badges or ranks (start date).
- "Time-to-renewal" countdowns (subscription anchor date).

PII rules (GDPR Art. 4, US state laws) treat full DoB as a higher-
sensitivity class than age alone. Report severity should reflect the
recoverable underlying value, not the surface leak.

## Preconditions

- Vuln leaks a derived value (age, account age, days-since-X) without
  rate limit.
- Attacker can sample at least once per change interval (daily for
  age-in-years).

## Detection

- Inventory every numeric value an unauthenticated or low-priv user can
  read about another user.
- For each, derive: "what date does this number's change reveal?"

## Triggering

```
# Day 1 of monitoring: victim age = 29
# Day 137 of monitoring: response now shows 30
# Birthday = today's date on Day 137
# Year of birth = today.year - 30
```

A single-shot leak combined with a leak of "account creation year"
(often public in user-profile JSON blobs) is enough to narrow DoB to a
365-element search space - bruteforceable against any service that
accepts DoB for password reset.

## Bypasses

Not applicable.

## Seen in the wild

- {date: 2026-04-23, source: CT Ep 171} - Justin Gardner: leaked age via a vuln on an undisclosed program; flagged the daily-sampling DoB-derivation pattern as a severity-uplift argument.

## References

- Critical Thinking Podcast Ep 171 - <https://www.youtube.com/watch?v=l5fs7Okdj3o>
- Related: [[../xs-leaks/force-cache-cors-leak]] - broader xs-leaks class.
