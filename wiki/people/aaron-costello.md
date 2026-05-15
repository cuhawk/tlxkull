---
title: Aaron Costello (ConspiracyProof)
slug: aaron-costello
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [conspiracyproof, aaron-costello, aaron_costello]
role: researcher
primary_focus: saas-misconfig
tags: [person, role/researcher, focus/saas-misconfig, focus/salesforce, focus/servicenow, focus/power-pages, focus/netsuite, focus/access-control]
inbound: []
---

# Aaron Costello (ConspiracyProof)

## Identity

- **Real name:** Aaron Costello
- **Primary handle:** `ConspiracyProof` (X). GitHub handle is
  `aaron-costello`. Personal blog brand: "Enumerated".
- **Based:** Ireland.
- **Role:** Researcher / vendor-eng. Former Chief of SaaS Security
  Research at AppOmni (led the AO Labs research arm); previously
  Principal SaaS Security Engineer there. Background in offensive
  security testing (7+ years) prior to AppOmni.
- **Domain specialty:** SaaS misconfiguration at scale — Salesforce
  Communities/Lightning, ServiceNow, Microsoft Power Pages, Oracle
  NetSuite. Effectively defined "SaaS misconfig" as its own bug class
  in modern bug bounty.

## Focus areas

- Salesforce Lightning / Aura API exploitation (guest access, OLS/FLS/RLS).
- ServiceNow ACL / public widget data exposure (Simple List, Knowledge Bases).
- Microsoft Power Pages access-control misconfigs (Web API, column security).
- Oracle NetSuite access-control / record exposure.
- Low-code platform security (OmniStudio, Salesforce Industry Clouds).
- Emerging: agentic-AI / prompt-injection in enterprise SaaS (ServiceNow Now Assist).

## Online presence

- [Blog — Enumerated](https://www.enumerated.ie)
- [AppOmni author archive](https://appomni.com/author/aaron-costello/)
- [X / Twitter — @ConspiracyProof](https://x.com/ConspiracyProof)
- [GitHub — aaron-costello](https://github.com/aaron-costello)
- [LinkedIn](https://ie.linkedin.com/in/aaron-c-226858a7)
- [Security Boulevard author archive](https://securityboulevard.com/author/aaron-costello-principal-saas-security-engineer/)
- [SC Media contributor page](https://www.scworld.com/contributor/aaron-costello)

## Key research / posts

- [Salesforce Lightning — An in-depth look at exploitation vectors for the everyday community](https://www.enumerated.ie/index/salesforce)
  (2020-10-09) — The seminal write-up. Guest-user abuse of the Aura
  API (`SelectableListDataProviderController`, custom Apex methods
  without `with sharing` / proper checks) to enumerate custom objects
  and dump records (PII, case attachments) from misconfigured
  Communities. Seeded the Nuclei `salesforce-aura-misconfig` template
  and an entire bug-bounty subgenre. Cross-link:
  `../techniques/saas-misconfig/salesforce-aura-guest-access.md`.
- [Salesforce Lightning — Tinting the Windows](https://www.enumerated.ie/index/salesforce-lightning-tinting-the-windows)
  (2020-12-16) — Follow-up on hardening / detection from the defender
  side; useful for understanding which guest-profile knobs actually
  matter.
- [Data Exposure and ServiceNow: The Elephant in the ITSM Room](https://www.enumerated.ie/index/servicenow-data-exposure)
  (2023-10-14) — Default-config exposure via the "Simple List" UI
  macro widget (sys_id `5b255672cb03020000f8d856634c9c28`): public
  ACLs + a widget that honours `t=` (table) and `f=` (field) GET
  params lets unauth users dump any table the public role can read
  (commonly `sys_user`). Exposure has existed since ~2015; ServiceNow
  added an "explicitly public" check in March 2023. No CVE — vendor
  classifies as configuration risk. Cross-link:
  `../techniques/saas-misconfig/servicenow-public-widget-acl.md`.
- [Enterprise ServiceNow Knowledge Bases at Risk](https://appomni.com/ao-labs/servicenow-knowledge-bases-data-exposures-uncovered/)
  — Tested 1000+ ServiceNow instances; ~45% had unintentionally
  exposed Knowledge Base data, ~70% had at least one misconfig
  permitting unauth extraction.
- [Microsoft Power Pages: Data Exposure Reviewed](https://appomni.com/ao-labs/microsoft-power-pages-data-exposure-reviewed/)
  (2024-11) — Misconfigured Web API + global anonymous access + zero
  column-level security across his sample. Several million sensitive
  records exposed during authorized testing; one NHS shared-service
  provider was leaking 1.1M employee PII records. Repeated the
  Salesforce-Communities playbook on a different low-code platform.
- [Potential Widespread Data Exposure Analysis: Oracle NetSuite](https://appomni.com/ao-labs/oracle-netsuite-data-exposure-analysis/)
  (2024-08-15, also at [enumerated.ie](https://www.enumerated.ie/index/from-exposure-to-exploitation-how-attackers-can-access-exposed-netsuite-data))
  — Same pattern, fourth SaaS platform: misconfigured NetSuite record
  access exposes data via public APIs.
- [Salesforce Industry Clouds: 0-days and Exploitable Misconfigs](https://appomni.com/ao-labs/salesforce-industry-clouds-security-report-omnistudio-cves/)
  — 20+ OmniStudio findings including 5 CVEs in Salesforce
  industry-cloud products. First time the SaaS-misconfig methodology
  produced assigned CVEs at scale.
- [SaaS Risks in Healthcare: Anatomy of a Data Exposure at the HSE](https://appomni.com/blog/saas-risks-in-healthcare-data-exposure-in-hse/)
  — Case study of Ireland's HSE vaccination portal (Salesforce Health
  Cloud) leaking 1M+ vaccination records via the same Aura-guest
  pattern.
- [BodySnatcher (CVE-2025-12420): Broken Authentication and Agentic Hijacking in ServiceNow](https://appomni.com/ao-labs/bodysnatcher-agentic-ai-security-vulnerability-in-servicenow/)
  — Pivot into agentic-AI security. Broken-auth + AI-agent hijacking
  primitive in ServiceNow's Now Assist.
- [When AI Turns on Its Team: Exploiting Agent-to-Agent Discovery via Prompt Injection](https://appomni.com/ao-labs/ai-agent-to-agent-discovery-prompt-injection/)
  — Second-order prompt injection abusing ServiceNow agent-discovery.

### Open-source tooling

- [aaron-costello/ServiceNow-Schema](https://github.com/aaron-costello/ServiceNow-Schema)
  — Shortlist of core ServiceNow tables. Reference table set for
  driving `t=` enumeration against the Simple List widget. Use this
  as the wordlist when testing ServiceNow instances.
- Nuclei template `salesforce-aura-misconfig.yaml` (authored by him,
  maintained in
  [projectdiscovery/nuclei-templates](https://github.com/projectdiscovery/nuclei-templates))
  — Detects exposure of the Aura endpoint on Salesforce Communities.

## CT podcast appearances

- [2025-01-30 Ep 108 — How to Hack Salesforce, ServiceNow, and Other SaaS Products with Aaron Costello](../sources/podcasts/ct/20250130_mBJyO1eJBI8_How_to_Hack_Salesforce_ServiceNow_and_Other_SaaS_Products_With_Aaron_Costello_Ep._108.en.vtt)
  — HackerNotes recap:
  [blog.criticalthinkingpodcast.io/p/new-post-6b9f](https://blog.criticalthinkingpodcast.io/p/new-post-6b9f).
  Episode covers SaaS misconfig as its own bug class with worked
  examples across Salesforce (Aura + custom Apex), ServiceNow (Simple
  List + ACL public role), and Power Pages (Web API + column security).

## Notes

- **One pattern, repeated across four platforms.** Aaron's playbook
  is: (1) identify the platform's "give the public a read view"
  primitive (Aura controllers / ServiceNow widgets / Power Pages Web
  API / NetSuite record access), (2) recognise that customers leave
  ACLs/OLS/FLS/RLS open by default or by convenience, (3) enumerate
  exposed tables/objects/columns, (4) demonstrate scale by mass-testing
  internet-facing instances. Same primitive form, four vendors, ~five
  years. Useful framing: if a SaaS platform exposes a guest API, ask
  "what's their version of the Aura controller?"
- **Misconfig vs vuln.** Most of his work doesn't get CVEs because
  vendors classify customer misconfigs as configuration risk, not
  product flaws. Bug-bounty implication: programs running these SaaS
  platforms have these as in-scope; Aaron's research is effectively a
  pre-built test plan for any program using Salesforce Communities,
  ServiceNow public-facing portals, or Power Pages. The OmniStudio
  work shows that pushing hard enough on the product (not just the
  config) does eventually yield CVEs.
- **Methodology heuristic from Ep 108.** Always check for: open
  registration → guest-tier API access → object/column enumeration via
  error messages → custom (tenant-written) code without `with sharing`
  or equivalent auth check. Custom Apex / scripted REST endpoints are
  consistently weaker than vendor-shipped controllers.
- **Companion wordlist:** when hitting a Salesforce Community, drive
  Aura enumeration with object-name lists derived from his write-up;
  when hitting ServiceNow, drive `t=` enumeration with the
  ServiceNow-Schema repo above.
- **Recent pivot.** From mid-2025 onward (BodySnatcher, agent-to-agent
  prompt injection) he is extending the SaaS-misconfig lens into
  agentic-AI features bolted onto these platforms — a credible new
  bug-class frontier for SaaS programs.
