---
title: Mutable OAuth Claim Used as Account Identifier (ATO)
slug: mutable-claim-ato
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/oauth, technique/ato]
inbound: []
---

# Mutable OAuth Claim Used as Account Identifier (ATO)

## Pattern

OAuth/OIDC tokens contain both stable claims (e.g. `sub` — globally unique,
assigned by the IdP, immutable) and user-facing display claims (e.g.
`preferred_username`, `email`, `name`) that some providers allow the user to
change. If an application or library uses a **mutable claim** as the account
lookup key (UID), an attacker can:

1. Create their own account on the same IdP.
2. Change their `preferred_username` (or other mutable claim) to match a
   victim's value.
3. Authenticate → receive a token with that claim set to the victim's value.
4. The application looks up the account by the claim value → logs in as victim.

A second, related variant: if a **permission/role claim** is mutable, an
attacker can overwrite it to escalate privileges rather than impersonate a
specific user.

## Preconditions

- Application or library resolves user identity from a mutable claim field
  (not `sub`).
- The IdP used (e.g. Okta, NetIQ) exposes that claim as user-editable.
- No additional binding between `sub` and the account record is enforced.

## Detection

- Identify which claim the application uses as its user lookup key. Look for:
  - Django OAuth Toolkit: `OIDC_UNIQUE_USER_CLAIM` setting (default may be
    `preferred_username`).
  - Custom code: `user = User.objects.get(username=token['preferred_username'])`
- Check IdP documentation / profile settings: is `preferred_username` or
  `email` editable by the user?
- `js_analyzer`: look for JWT claim extraction followed by ORM lookups that
  don't also check `sub`.

## Triggering

1. Identify target app's account-lookup claim (e.g. `preferred_username`).
2. On your own controlled IdP account (same provider), change
   `preferred_username` to the victim's value.
3. Initiate OAuth flow → obtain token with victim's `preferred_username`.
4. Exchange code for token, present token to the application.
5. Application resolves account → authenticated as victim.

For privilege escalation via mutable permission claim:
1. Identify a claim that controls role/permission (e.g. `groups`, `role`).
2. Edit that claim on your account's IdP profile or through any profile-update
   API.
3. Re-authenticate → token contains elevated claim → application grants
   higher privilege.

## Bypasses

- **`sub` not checked at all**: library only compares the mutable claim, no
  secondary binding.
- **Claim uniqueness not enforced at IdP**: Okta allows duplicate
  `preferred_username` values across tenants — collision is straightforward.
- **Refresh token staleness**: after a user is deactivated, their refresh
  token may still issue new access tokens with the old claims — test whether
  a deactivated-user's refresh token still works.

## Seen-in-the-wild

| date | target / library | notes |
|---|---|---|
| 2025 | Django OAuth Toolkit (2M monthly downloads) | ZeroPath: 7 vulns. `preferred_username` used as account UID. Okta and NetIQ identifiers mutable. Tokens for deactivated users could be refreshed indefinitely. CVE series reported by ZeroPath. |

- {date: 2026-04-09, source: CT Ep 169} — Brandon: also applicable to "mutable permission claim" privilege-escalation variant; recommends auditing every claim used as a permissions source.

## References

- Episode source: `../../sources/podcasts/ct/20260409_mo9LoNHmDhI_OAuth_changes_MCP_Authorization_PKCE_Downgrades_Ep._169.en.vtt`
- Podcast: "OAuth changes, MCP Authorization, & PKCE Downgrades (Ep. 169)" — <https://www.youtube.com/watch?v=mo9LoNHmDhI>
- ZeroPath Django OAuth write-up (referenced in episode): search "ZeroPath Django OAuth preferred_username"
- OIDC Core spec — `sub` claim: <https://openid.net/specs/openid-connect-core-1_0.html#IDToken>
- [PKCE Downgrade](pkce-downgrade.md)
- [OAuth SUMMARY](SUMMARY.md)
