---
title: Facebook implicit-flow access token app-confusion ATO
slug: facebook-implicit-flow-app-confusion
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/oauth, technique/facebook, technique/account-takeover, sink/access-token]
inbound: []
---

# Facebook implicit-flow access token app-confusion ATO

## Pattern

Facebook OAuth's implicit flow returns the access token directly to
the client-side relying party (RP) — no server-side code exchange.
The RP receives the token, hits Facebook's Graph API to confirm
identity (`GET /me`), and then logs the user in based on the
returned email.

The token, however, is bound to **the Facebook app that minted it**,
not to the RP. Facebook's documentation says: "Before trusting the
token, call `GET /debug_token?input_token=<received>&access_token=
<your-app-token>` and verify `data.app_id == <your-app-id>`." Most
RPs miss this step.

Attack:
1. Attacker pops or controls any low-value Facebook app — call it
   `App-X`. Many such apps exist; they need only be approved for
   email scope on a victim user.
2. Victim is enrolled in `App-X` (or attacker socially engineers
   them to authorize it).
3. Attacker uses `App-X`'s tokens to call the RP's "log in with
   Facebook" callback.
4. RP doesn't check `app_id`; calls `/me`; gets victim's email;
   logs attacker in as the victim.

Salt Labs demonstrated against Grammarly + two other RPs.

## Preconditions

- RP implements Facebook OAuth implicit flow client-side only.
- RP authenticates users by calling `/me` after receiving the token
  and uses the returned email as the identity assertion.
- RP omits the `debug_token` validation step.
- Attacker has access to (or can sign up for) any Facebook app the
  victim has authorized with email scope.

## Detection

- Inspect the RP's Facebook-login JS. Look for direct calls to
  `/me` after receiving the token without an intermediate request
  to `/debug_token`.
- Trace network: from the moment the implicit-flow callback fires,
  the only Facebook request should be `/me` if the RP is
  vulnerable.

## Triggering

1. Authorize `App-X` (your malicious app) as the victim — many
   low-value apps already pop tokens for any visitor.
2. Capture the resulting access token.
3. Hit the RP's Facebook-login callback URL with that token:
   ```
   https://rp.example.com/auth/fb/callback#access_token=<token>&token_type=bearer
   ```
4. The RP fetches `/me` with the token, gets the victim's email,
   issues an authenticated session for the attacker.

## Bypasses

- Some RPs do check `app_id` but accept a whitelist of Facebook apps
  (their own + corporate partner apps); compromise a partner app
  for the same effect.
- Authorization-code flow (server-side exchange with `client_secret`)
  prevents this attack — the code exchange ties the token to
  `client_id`.

## Seen in the wild

- {date: 2023-11-09, source: CT Ep 44} — Salt Labs writeup; three RPs
  including Grammarly affected; Grammarly's separate $100k bug-bounty
  was for zero-click and this required one click.

## References

- Salt Labs blog — Facebook implicit-flow app-confusion
- Facebook developer docs — `debug_token` endpoint
- Critical Thinking Podcast Ep 44
- Related: [[redirect-uri-bypass]], [[oauth2-proxy-regex-anchor]]
