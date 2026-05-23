---
title: polyfill.io CDN takeover (Funnull, 2024)
slug: polyfill-io-cdn-2024
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/cdn, technique/domain-takeover, technique/conditional-payload, target/web]
inbound: []
---

# polyfill.io CDN takeover (Funnull, 2024)

## What happened

In **February 2024** the `polyfill.io` domain and its associated
GitHub organisation were sold by the original maintainer (Andrew
Betts, who created the project at the Financial Times in 2014) to a
new owner -- a Chinese company operating as **"Funnull"**. The
project's original purpose was to serve user-agent-conditional
JavaScript polyfills from `cdn.polyfill.io` so that legacy browsers
got the feature shims they needed and modern browsers got an empty
response. After the acquisition Funnull modified the CDN to serve
**conditional malicious JavaScript** alongside the polyfill payload
on requests from mobile user agents.

Betts publicly disowned the domain on 2024-02-25 (advising every
embedder to remove the script). The Sansec forensics team published
the active-malware writeup on **2024-06-25**, having confirmed the CDN
was redirecting mobile visitors of embedding sites to a fake sports-
betting / gambling network and serving secondary malicious payloads.
At peak embed count Censys identified ~384k hosts referencing
`cdn.polyfill.io`, including major brand sites. **Cloudflare**
shipped a real-time rewriter that replaced the script with its own
clean copy; **Google** flagged ad accounts depending on
`cdn.polyfill.io`; **Namecheap** suspended the domain shortly after
Sansec's disclosure. Some research linked the operator infrastructure
to a broader Chinese-aligned threat cluster; SecurityWeek reporting
later associated Funnull-controlled infrastructure with DPRK-linked
activity, though attribution remains contested.

## Attack chain

1. **Buy the trust.** Acquire a long-lived JS-CDN domain that is
   embedded as `<script src="https://cdn.polyfill.io/v3/polyfill.min.js">`
   on hundreds of thousands of sites. The acquisition is a legal
   transaction; the embedders inherit the new owner's trust
   relationship without any consent step. No code change is required
   on the victim sites for the attacker to gain near-universal JS
   execution rights.
2. **Conditional response based on User-Agent + hour-of-day.** The
   modified CDN responds with benign polyfill JS for desktop UAs and
   for admin-looking sessions. For mobile UAs at specific hours the
   server appends a malicious script that fingerprinted and
   conditionally redirected the visitor to attacker-controlled
   gambling / drainer pages.
3. **Reverse-engineering defences.** The malicious payload checked
   for the presence of well-known web-analytics scripts (Google
   Analytics, etc.) and delayed activation when they were detected,
   keeping the attack out of customer aggregate stats. It also
   suppressed itself for users that looked like admins (presence of
   admin-cookie names, source IPs matching backend ranges).
4. **Detection.** Sansec's eComscan engine flagged the dynamic
   payload behaviour on customer Magento storefronts. They published
   the timeline plus IOCs on 2024-06-25; Cloudflare and Namecheap
   moved within hours.
5. **Mitigation lag.** Even after the domain was sinkholed, every
   embedder still shipping the original `<script src="cdn.polyfill.io">`
   tag was exposed to the next owner of any DNS record that replaced
   it. The advisable fix was to remove the tag entirely or self-host
   the polyfill bundle from the site's own origin.

## Lessons for bug hunters

- **CDN-script audit on every target.** For any bug-bounty target,
  grep the rendered HTML for third-party `<script src=>` tags. Any
  reference to a domain not owned by the target itself, AWS/GCP/Azure
  static-hosting, or a vetted CDN should be flagged. `polyfill.io`,
  `bootcdn.net`, `staticfile.org`, and any domain that has changed
  ownership in the last 12 months are first-priority. See
  [[ua-parser-js]] and [[event-stream-flatmap-stream]] for the JS-dep
  cousin pattern.
- **Look up domain ownership history.** Tools like SecurityTrails,
  whoisxml history, or `whois` archives expose the date of a
  registrant change. A JS-CDN domain that just changed hands is a
  reportable risk on programs that scope third-party trust.
- **Conditional payloads need a real browser to detect.** Static
  fetching of a CDN'd script will return the benign desktop variant.
  Use a real Chrome with a mobile User-Agent (or a Caido-proxied
  mobile-emulation profile) to surface conditional malicious responses.
- **Subresource Integrity (SRI) is the structural fix.** A target
  that pins SRI hashes on every external `<script>` tag is defended
  against this class of attack -- the new payload's hash will not
  match. Hunters can file a hardening finding when a target embeds an
  external CDN script with no `integrity=` attribute.
- **Cloudflare-style "rewrite to safe" is a stopgap, not a remediation.**
  Bug-bounty writeups should still demand removal of the dependency,
  not reliance on a CDN provider's mitigation.

## Primary sources

- [Sansec: Polyfill supply chain attack hits 100K+ sites (2024-06-25)](https://sansec.io/research/polyfill-supply-chain-attack)
  -- the original disclosing forensics writeup.
- [Censys: Digging into the web of compromised polyfill.io domains (2024-07-02)](https://censys.com/blog/july-2-polyfill-io-supply-chain-attack-digging-into-the-web-of-compromised-domains/)
  -- corroborating infrastructure-pivot analysis with the full set of
  related domains.

## Related

- [[ua-parser-js]]
- [[event-stream-flatmap-stream]]
- [[lottie-player-npm-2024]]
- [[ccleaner-floxif]]
- [[shai-hulud-npm-worm-2025]]
