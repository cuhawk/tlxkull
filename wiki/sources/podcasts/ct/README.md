---
title: Critical Thinking — Bug Bounty Podcast (Justin Gardner, Joel Margolis)
slug: ct-podcast
url: https://www.youtube.com/@criticalthinkingpodcast
fetched_utc: 2026-05-12T00:00:00Z
kind: podcast
extracted: true
extract_model: sonnet
tags: [source, podcast, ct]
inbound: []
---

# Critical Thinking — Bug Bounty Podcast

Justin Gardner + Joel Margolis weekly conversation on live bug-bounty
research. ~170 episodes as of 2026-05-12. Strong signal-to-noise.

## Local mirror

- Episode catalog: `episodes.txt` (`<youtube_id>|<title>|<upload_date>`)
- Auto-subs (en, vtt): `<upload_date>_<id>_<slug>.en.vtt` per episode.
- Download log: `yt-dlp.log`.

## Refresh

```bash
cd wiki/sources/podcasts/ct && \
  yt-dlp --write-auto-sub --skip-download --sub-lang en --sub-format vtt \
    --output "%(upload_date)s_%(id)s_%(title)s.%(ext)s" \
    --restrict-filenames --no-warnings --ignore-errors \
    "https://www.youtube.com/@criticalthinkingpodcast/videos"
```

Idempotent — yt-dlp skips already-downloaded transcripts.

## Extraction policy

- Transcripts stay raw in this folder. NOT embedded into `wiki` RAG
  collection by default (too noisy, mostly conversational).
- On-demand: when a session topic matches an episode title, Read the
  vtt + extract any payload / technique / target intel into the
  matching `wiki/techniques/<class>/<pattern>.md` + back-link to the
  episode file.
- Extraction model: Sonnet (per `feedback_extract_model`).

## High-priority extraction queue

Top candidates by title:

- [x] Ep 169 — OAuth + MCP authorization, PKCE downgrades. **Extracted 2026-05-12.**
  - `wiki/techniques/oauth/pkce-downgrade.md`
  - `wiki/techniques/oauth/mcp-cimd-ssrf.md`
  - `wiki/techniques/oauth/mutable-claim-ato.md`
- [x] Ep 170 — Claude Code + tmux, websockets, Korea LHE takeaways. **Extracted 2026-05-12.**
  - `wiki/tools/karpathy/lhe-workflow.md`
  - `wiki/tools/protoscope/notes.md` (protoscope tool notes)
- [x] Ep 171 — Path-scoped cookies, post-based protobuf XSS. **Extracted 2026-05-12.**
  - `wiki/techniques/server-side/path-scoped-cookie-bypass.md`
  - `wiki/techniques/dom-xss/post-based-protobuf-xss.md`
- [x] Ep 172 — Source-code review meta analysis. **Extracted 2026-05-12.**
  - `wiki/tools/karpathy/source-code-review.md`
- [x] Ep 173 — "Is Bug Bounty Dead?" (meta). **Reviewed 2026-05-12. No extraction — meta-only.** See `extracts.md`.

(See `episodes.txt` for complete list.)
