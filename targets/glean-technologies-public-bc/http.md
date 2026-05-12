# glean-technologies-public

- program: Glean Technologies Public Engagement
- platform: bugcrowd
- url: https://bugcrowd.com/engagements/glean-technologies-public
- category: bug_bounty
- bounty: $200 - $5,000
  - P1: $5000
  - P2: $2500
  - P3: $600
  - P4: $200

## scope

- in: https://app.glean.com/login?qe=https://bug-bounty-be.glean.com&skip_to_sso=1
- in: bug-bounty-be.glean.com

## notes

- Glean AI-powered enterprise search and work assistant
- Scope rating 1/4 — small target surface
- In-scope: Glean search, assistant/chat, HTML Artifacts, Code Writer, File upload, Code interpreter, External Links features
- Out of scope: any customer domains (customer.glean.com), any repo not owned by user, www.glean.com
- New features: HTML Artifacts (sandboxed iframe), Code Writer, Chat Sharing V2, Skills (SKILL.md upload)
- Known not-rewardable: IDOR in chat sharing to specific people/groups, IDOR in snapshot edit
- All IDORs in user generated content (Collections, Prompts, Answers, GoLinks, Announcements) → P4/P5
- Automated scanners strictly prohibited
