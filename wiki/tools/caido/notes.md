---
title: Caido - Plugin Notes
slug: caido-plugin-notes
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [tool/caido, tool/plugin]
inbound: []
---

# Caido Plugin Notes

Append-only log of useful third-party Caido plugins and quirks.

## Static-Flow Notes Plugin (Tanner)

- Markdown-rendering notes plugin built into Caido. Tanner ("Static-Flow")
  authored. Released alongside CT Ep 97.
- Features that distinguish it from a generic notes pane:
  - Live markdown render side-by-side with edit pane.
  - Export to file.
  - Key-binding launch directly from replay tab.
  - **Cross-link replay tabs**: paste a replay tab reference into a note
    and click it to jump straight to that request. Built feasible only on
    Caido's HTML/JS UI; equivalent in Burp blocked by Swing.
- Use case: write engagement-scoped reports inside Caido instead of
  context-switching to Obsidian.

## Source: CT Ep 97

- <https://www.youtube.com/watch?v=m5mR6dvhtpg>
- See [[../../sources/podcasts/ct/20241114_m5mR6dvhtpg_Bcrypt_Hash_Input_Truncation_Mobile_Device_Threat_Modeling_Ep._97]]
