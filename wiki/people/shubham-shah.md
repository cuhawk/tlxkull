---
title: Shubham Shah (infosec_au)
slug: shubham-shah
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [infosec_au, shubham_shah]
role: researcher
primary_focus: server-side
tags: [person, role/researcher, vendor/assetnote, focus/n-day, focus/enterprise, focus/recon, focus/server-side]
inbound: []
---

# Shubham Shah (infosec_au)

## Identity

- Real name: Shubham Shah ("Shubs").
- Co-founder and CTO of [Assetnote](https://www.assetnote.io/) (founded
  2018 with Michael Gianarakis; now part of Searchlight Cyber's
  Assetnote Security Research Center).
- Top-tier HackerOne bug-bounty hunter — historically ranked in the
  top 30-50 globally, started bounty hunting as a teenager.
- Based in Sydney, Australia.

## Focus areas

- **N-day on enterprise / appliance software** — Citrix NetScaler/ADC,
  F5 BIG-IP, Atlassian Confluence, ServiceNow, Sitecore, Adobe
  ColdFusion / Experience Manager, Palo Alto PAN-OS, Next.js.
- **Server-side vulnerability classes** — pre-auth RCE chains, SAML
  buffer overflows, path-confusion auth bypass, template injection,
  order-of-operations validation bugs, hardcoded credentials.
- **Reconnaissance at internet scale** — the original Assetnote thesis;
  builder of [kiterunner](https://github.com/assetnote/kiterunner) and
  contextual content-discovery tooling, BigQuery-driven IIS file
  enumeration, blind-SSRF chain catalog.
- **SaaS attack surface** — ServiceNow tenant data theft chain,
  Salesforce-adjacent research lineage at Assetnote.
- **Bug-bounty meta** — collaboration mechanics, triage relations,
  career path content.

## Online presence

- Personal blog: [shubs.io](https://shubs.io)
- Company / research hub:
  [assetnote.io/resources/research](https://www.assetnote.io/resources/research)
  (legacy posts also at `blog.assetnote.io`)
- X / Twitter: [@infosec_au](https://twitter.com/infosec_au)
- GitHub: [github.com/infosec-au](https://github.com/infosec-au)
  (personal) and [github.com/assetnote](https://github.com/assetnote)
  (org — kiterunner, wordlists, nowafpls, blind-ssrf-chains)
- LinkedIn: [linkedin.com/in/shubhamshah](https://www.linkedin.com/in/shubhamshah/)

## Key research / posts

Co-authored work is noted; Assetnote research is increasingly a team
output with Adam Kues, Dylan Pindur, and Sean Yeoh.

- **A Glossary of Blind SSRF Chains** (2021-01-15) —
  [shubs.io](https://shubs.io/a-glossary-of-blind-ssrf-chains/).
  Canonical reference catalogue of blind-SSRF-to-impact escalations;
  the page the rest of the industry cites. Seeds wiki technique notes
  under [../techniques/server-side/](../techniques/server-side/).
- **Finding Hidden Files and Folders on IIS using BigQuery**
  (2020-09-18) —
  [shubs.io](https://shubs.io/finding-hidden-files-and-folders-on-iis-using-bigquery/).
  Recon technique: mine Common Crawl / BigQuery to find shortname-style
  hidden IIS paths at scale. Foundational for content-discovery at
  internet scope. Cross-links
  [../techniques/recon/](../techniques/recon/).
- **Expanding the Attack Surface: React Native Android Applications**
  (2020-02-01) —
  [shubs.io](https://shubs.io/expanding-the-attack-surface-react-native-android-applications/).
  Mobile attack-surface playbook for RN apps — JS bundle extraction,
  endpoint enumeration.
- **Discovering a zero day and getting code execution on Mozilla's AWS
  Network** (2019-05-19) —
  [shubs.io](https://shubs.io/discovering-a-zero-day-and-getting-code-execution-on-mozillas-aws-network/).
  Classic recon-to-RCE narrative; demonstrates the Assetnote thesis
  of "find the forgotten asset, find the bug".
- **Analysis of CVE-2023-3519 in Citrix ADC and NetScaler Gateway**
  (2023-07-04) with Dylan Pindur —
  [assetnote.io](https://www.assetnote.io/resources/research/analysis-of-cve-2023-3519-in-citrix-adc-and-netscaler-gateway).
  Buffer overflow in Citrix SAML auth processing (requires SAML
  enabled); built version-independent error-differential detection.
- **Continuing the Citrix Saga: CVE-2023-5914 & CVE-2023-6184**
  (2023) —
  [assetnote.io](https://www.assetnote.io/resources/research/continuing-the-citrix-saga-cve-2023-5914-cve-2023-6184).
  Follow-on Citrix work covering Session Recording and additional
  NetScaler issues.
- **Citrix Denial of Service: Analysis of CVE-2024-8534** (2024) —
  [assetnote.io](https://www.assetnote.io/resources/research/citrix-denial-of-service-analysis-of-cve-2024-8534).
  Continuation of the multi-year NetScaler-internals series.
- **Chaining Three Bugs to Access All Your ServiceNow Data**
  (2024-07-11) led by Adam Kues; Shubham on the team —
  [assetnote.io](https://www.assetnote.io/resources/research/chaining-three-bugs-to-access-all-your-servicenow-data).
  CVE-2024-4879 / -5178 / -5217. Template-injection chain via XML
  injection inside `<style>` tags, single-quote namespace bypass,
  pre-canonicalization `..` traversal; reads DB creds, full instance
  takeover. Affected ~42k Vancouver/Washington instances.
- **Leveraging An Order of Operations Bug to Achieve RCE in Sitecore
  8.x – 10.x** (2024-11-22) with Dylan Pindur & Adam Kues —
  [assetnote.io](https://www.assetnote.io/resources/research/leveraging-an-order-of-operations-bug-to-achieve-rce-in-sitecore-8-x---10-x).
  Validation-ordering bug in Sitecore bundle endpoint → unauth file
  read → RCE via config files.
- **Doing the Due Diligence: Analyzing the Next.js Middleware Bypass
  (CVE-2025-29927)** (2025-03-24) with Adam Kues —
  [assetnote.io](https://www.assetnote.io/resources/research/doing-the-due-diligence-analyzing-the-next-js-middleware-bypass-cve-2025-29927).
  Improved detection for the Next.js middleware bypass, catching apps
  using redirects (not just rewrites) that public PoCs missed. Wiki
  technique: [../techniques/server-side/nextjs-middleware-subrequest-bypass.md](../techniques/server-side/nextjs-middleware-subrequest-bypass.md).
- **How an obscure PHP footgun led to RCE in Craft CMS** (2025) —
  [assetnote.io](https://www.assetnote.io/resources/research/how-an-obscure-php-footgun-led-to-rce-in-craft-cms).
  PHP language-quirk → unauth RCE in Craft CMS.
- **Atlassian Questions for Confluence hardcoded password
  (CVE-2022-26138)** — Assetnote disclosure (with Orange Tsai / DEVCORE
  on related Confluence WebDAV work). The `disabledsystemuser` account
  shipped with a trivially-recoverable hardcoded password
  (`disabled1system1user6708`) in plugin versions 2.7.34, 2.7.35,
  3.0.2.
- **Adobe ColdFusion admin DOM XSS → RCE (CVE-2015-0345)** — early
  Shubham research published via Bishop Fox; demonstrated chaining
  reflected DOM-XSS in the ColdFusion admin panel into server-side
  code execution.
- **Adobe Experience Manager forms (CVE-2025-54253 / -54254)**
  (2025-07) with Adam Kues, published via Searchlight Cyber.

## CT podcast appearances

- [2023-08-03 Ep 30 — Shubham Shah: From Burgers to Bounties](../sources/podcasts/ct/20230803_K0XYnsgMvYU_Shubham_Shah_-_From_Burgers_to_Bounties_Ep._30.en.vtt)
  — origin story, friendly rivalry that fueled recon obsession,
  collaboration philosophy, Assetnote's evolution from recon tool to
  enterprise ASM platform, art of debugging, bug-bounty economics.

Related (Assetnote teammate):
- [2023-07-27 Ep 29 — Sean Yeoh: Live Chat with an AssetNote Engineer](../sources/podcasts/ct/20230727_nEQPTLDKfmM_Sean_Yeoh_-_Live_Chat_with_an_AssetNote_Engineer_Ep._29.en.vtt).

## Notes

- **Research-as-marketing flywheel.** Assetnote's commercial ASM
  product is fed (and validated) by the SRC pumping out high-quality
  n-day analyses on widely-deployed enterprise software. Each
  publication doubles as a detection-rule asset for paying customers
  and a hiring/recruitment beacon. The Citrix multi-year series and
  the ServiceNow chain are the clearest examples.
- **N-day after the CVE.** The signature move is reading a vendor
  advisory or public PoC, then doing a deeper variant-hunt or
  detection-engineering pass — finding additional CVEs in the same
  code path, or producing more reliable / scope-expanding detection
  than the original. Next.js CVE-2025-29927 follow-up, the Citrix
  saga, and the F5 BIG-IP work all fit this mold.
- **Recon-first lineage.** Even the n-day work descends from the
  recon thesis: if you know exactly which assets across the internet
  are vulnerable, the vulnerability research becomes a force
  multiplier on the ASM platform.
- **Collaboration over solo glory.** A recurring theme on Ep 30 and
  on his "ugly side of collaboration" blog post; most modern Assetnote
  output is multi-author (Adam Kues, Dylan Pindur, Sean Yeoh) with
  Shubham as senior reviewer / co-author rather than sole lead.
- **Tooling shipped publicly.** kiterunner (Aho-Corasick API route
  brute-forcer aware of header/method requirements), `nowafpls` Burp
  WAF-bypass extension, `wordlists` (Assetnote daily-rotating
  wordlists), `blind-ssrf-chains` — the bug-hunter side leaks into
  open source frequently.

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/assetnote/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

