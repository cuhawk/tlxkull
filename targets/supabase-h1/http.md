# Supabase

> Platform: HackerOne — https://hackerone.com/supabase
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 91% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2025-06-22

## Scope

- in:  https://*.database.dev/    # type: wildcard # max: medium # not eligible for bounty
- in:  supabase.com    # type: url # max: critical # not eligible for bounty
- in:  api.supabase.com    # type: url # max: critical # not eligible for bounty
- in:  https://github.com/supabase-community/supabase-mcp    # type: url # max: critical # not eligible for bounty
- in:  https://mcp.supabase.com/mcp    # type: url # max: critical # not eligible for bounty
- in:  https://supabase.store    # type: url # max: medium # not eligible for bounty
- in:  https://multiplayer.dev    # type: url # max: low # not eligible for bounty
- in:  https://supabase.help    # type: url # max: none # not eligible for bounty
- in:  https://supabase.link    # type: url # max: none # not eligible for bounty
- in:  https://github.com/supabase    # type: repo # max: critical # not eligible for bounty
- out:  https://*.supabase.co    # type: wildcard # max: none
- out:  db.*.supabase.co    # type: wildcard # max: none
- out:  https://supabase.dev/    # type: url # max: none
- out:  https://supabase.productions/    # type: url # max: none
- out:  https://api.supabase.com/platform/pg-meta/project_id/query    # type: url # max: none
- out:  https://ctf.supabase.com    # type: url # max: none
- out:  supabase.sh    # type: url # max: none
- out:  https://github.com/supabase-community/    # type: repo # max: none
- out:  ctf.supabase.com    # type: url # max: none
- out:  https://db.*.supabase.co    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
