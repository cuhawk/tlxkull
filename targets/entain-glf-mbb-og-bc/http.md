# Entain Game Logic Flaws Bug Bounty — Bugcrowd

**URL:** https://bugcrowd.com/engagements/entain-glf-mbb-og
**Category:** BBP
**Safe harbor:** Yes
**Disclosure:** Coordinated (explicit permission required)
**Started:** 2024-01-16
**Industry:** Entertainment (online gambling / sports betting)

## Legal note
- No liability to Bugcrowd if researcher breaches anti-gambling laws
- Researcher must make their own legal decision about participating; program brief identifies this as an online gambling provider

## Targets

### In Scope: Casino Game Engines (P1=$6,100–6,500; bonus up to $10,000)
- ONLY games listed in Entain-Casino-Games-Engine-List.pdf (attached in program brief)
- Websites hosting the games are NOT in scope — only the game logic itself
- BetMGM USA: https://www.betmgm.com / https://casino.nj.betmgm.com/en/games (GeoIP restricted)
- Must create account to test; use VPN from UK or USA with matching address

## Rewards
| Priority | Range | Example |
|----------|-------|---------|
| P1 | $6,100–6,500 | Predict/influence game outcome or perform successful action violating rules → financial impact |
| P2 | $2,100–2,500 | Free-spin on out-of-bounds bases; modify permitted free-spin amount |
| P3 | $300–800 | Successful action against game rules without financial impact |
| Bonus | Up to $10,000 | Exceptional P1 findings |

## Auth
- Sign up with @bugcrowdninja.com email
- VPN from UK or USA required to access GeoIP-restricted assets
- Create account, navigate to casino section, search for game, log in to play

## Focus areas (Game Logic Flaws ONLY)
- Place bet with negative stake?
- Play with insufficient funds?
- Circumvent game to violate defined game rules?
- Predict game outcomes?

## Game Engine Map
- PDF resource: Entain-Casino-Games-Engine-List.pdf (in program brief Resources tab)
- Map shows which games across platforms share the same engine

## Out of scope
- Anything NOT related to Game/Business Logic Flaws
- Social engineering
- 3rd party services/infrastructure
- Current/former employees and immediate family

## Notes
- Disclosure: Coordinated with explicit permission required
- No traditional web security vulns in scope — purely game logic
