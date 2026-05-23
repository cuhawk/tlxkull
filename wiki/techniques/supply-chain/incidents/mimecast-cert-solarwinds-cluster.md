---
title: Mimecast certificate compromise (SolarWinds cluster, Jan 2021)
slug: mimecast-cert-solarwinds-cluster
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, surface/email-security, surface/oauth-cert, technique/stolen-cert, technique/m365-ews-mitm, actor/solarwinds-cluster]
inbound: []
---

# Mimecast certificate compromise (SolarWinds cluster, Jan 2021)

## What happened

In January 2021 Mimecast disclosed that **a certificate it issued for
use with Microsoft 365 Exchange Web Services** had been stolen by a
"sophisticated threat actor". By mid-March Mimecast confirmed the
actor was the **Sunburst / SolarWinds** cluster (UNC2452 /
NOBELIUM). Roughly **10% of Mimecast's 36,000 customers** -- ~3,600
tenants -- used the affected certificate to authenticate the
**Mimecast Sync & Recover**, **Continuity Monitor**, and **Internal
Email Protect (IEP)** services to their M365 Exchange Online
tenants. With possession of the stolen cert, the attacker could
**impersonate Mimecast to the customer's Microsoft 365 tenant** and
read or modify mail through the Mimecast service principal's OAuth
permissions.

Mimecast estimated the actor targeted only a "low single-digit
number" of those customer tenants, primarily US Federal customers
adjacent to the broader SolarWinds intrusion set. Microsoft revoked
the cert on 2021-01-18; Mimecast rotated all customer cert bindings
and disclosed the SolarWinds attribution on 2021-03-16. Mimecast also
admitted source-code theft from the Sunburst foothold. In 2024 the
SEC filed administrative charges against Mimecast for materially
misleading disclosures during the incident.

## Attack chain

1. **SolarWinds Orion compromise as initial access.** Mimecast's
   internal network ran a Sunburst-trojaned SolarWinds Orion build.
   The actor used the standard Sunburst beacon -> Cobalt Strike ->
   credentialed-pivot kill chain to reach the certificate-management
   infrastructure.
2. **Certificate exfiltration.** Mimecast generates a per-product
   X.509 cert that customers register as a **service-principal
   credential** inside their own Azure AD tenant for the **Mimecast
   Sync & Recover** application. The attacker stole the private key
   matching one of these certs.
3. **OAuth as Mimecast SP into 3,600 customer tenants.** With the
   private key the actor could mint OAuth client_assertion JWTs as
   the **Mimecast service principal** for any customer that had
   registered the affected cert. The Mimecast SP has
   `Mail.Read`/`full_access_as_app` scope on the customer mailbox
   to back up and sync mail; the attacker inherited the same
   scopes.
4. **Targeted EWS read.** From outside the customer's network, the
   actor issued EWS / Graph API calls authenticated as the Mimecast
   SP. Because the call genuinely came from a registered
   service-principal credential, neither Conditional Access nor
   token-anomaly detection flagged it without bespoke configuration.
5. **Source-code theft and persistence.** Mimecast also disclosed
   "some" source-code repos were exfiltrated from the Sunburst
   foothold -- useful for the actor to spot *future* vulnerabilities
   in Mimecast tooling, including the certificate-issuance pipeline
   itself.

## Lessons for bug hunters

- **Vendor-issued service-principal certs are a long-lived
  authentication primitive.** When auditing a SaaS that asks the
  customer to register a cert into their M365 / Google Workspace /
  AWS IAM, ask: who at the vendor can mint or read that cert? How is
  it rotated? Can a customer enumerate which certs are bound to
  their tenant? Misconfigurations in this surface pay well. See
  [[oauth-app-overpermission]].
- **OAuth scopes survive backdoor removal.** Even after a customer
  patches Sunburst out of their environment, a stolen cert keeps
  working until either the customer rotates the SP credential OR
  Microsoft revokes the cert. Persistence via cert >> persistence via
  agent.
- **Email-security gateways are *more* privileged than they look.**
  Spam filters, archive systems, and DLP relays all hold
  `Mail.ReadWrite` or `full_access_as_app` on the mailbox. Treat the
  vendor as part of the mailbox's TCB when scoping. Cross-link
  [[shadow-tcb-email-gateway]].
- **Vendor breach != one-shot risk.** Source-code theft from a
  security vendor expands the threat actor's *future* capability;
  any zero-day later found in that vendor's product is post-hoc
  attributable to the earlier breach. When reporting in this lineage,
  link your finding to the prior breach if plausibly relevant.
- **Disclosure timing has SEC consequences now.** Material breach
  disclosure has teeth. As an external researcher, when you suspect
  a vendor is under-disclosing impact, document your evidence and
  the public statement side-by-side -- relevant to the regulator and
  to the program.

## Primary sources

- [Mimecast Incident Report (Jan-Mar 2021 timeline, archived)](https://web.archive.org/web/20210316215353/https://www.mimecast.com/blog/important-update-from-mimecast/)
  -- Mimecast's own public post-mortem with the SolarWinds
  attribution and the 10% customer-base figure.
- [SEC: In the Matter of Mimecast Limited (33-11322, 2024)](https://www.sec.gov/files/litigation/admin/2024/33-11322.pdf)
  -- the SEC's administrative-proceeding filing with the most
  detailed publicly-available timeline of the cert theft and
  disclosure decisions.

## Related

- [[ms-storm-0558]]
- [[oauth-app-overpermission]]
- [[shadow-tcb-email-gateway]]
