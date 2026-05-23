---
title: Kaseya VSA / REvil (CVE-2021-30116, Jul 2021)
slug: kaseya-vsa-revil
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, actor/revil, technique/auth-bypass, technique/sql-injection, technique/code-signing-abuse, vuln/cve-2021-30116, target/msp]
inbound: []
---

# Kaseya VSA / REvil (CVE-2021-30116, Jul 2021)

## What happened

On **2021-07-02**, hours before the US July 4 weekend, the **REvil /
Sodinokibi** ransomware crew exploited a chain of zero-days in the
**Kaseya VSA** (Virtual System Administrator) on-prem RMM server to
push ransomware *through the legitimate VSA agent* to **~1,500
downstream customer environments** across **~60 managed-service
providers**. Each MSP that ran a public on-prem VSA was used to
ransomware its own customers' fleets. Total downstream victim count
was disputed; REvil claimed >1M endpoints, defenders confirmed ~1,500
businesses fully encrypted. The most-publicised victim was the Swedish
grocery chain **Coop** -- 800 stores closed because its POS terminals
were managed by a downstream MSP of Visma EssCom.

The bug chain (CVE-2021-30116, -30119, -30120) had been **previously
reported by Dutch DIVD researcher Wietse Boonstra** to Kaseya in April
2021 and was in coordinated disclosure -- Kaseya was still patching.
REvil weaponised it before the patch shipped. Kaseya pulled all SaaS
VSA instances within hours; on-prem customers were told to shut down
servers immediately. A universal decryptor surfaced ~3 weeks later
(provenance disputed -- possibly via the FBI rather than the ransom
payment).

## Attack chain

1. **CVE-2021-30116: authentication bypass.** The VSA web frontend
   accepted a forged session cookie / credential check on a specific
   endpoint, granting an authenticated session without valid creds.
   This is the front door.
2. **CVE-2021-30119: stored XSS** in the VSA admin UI -- usable for
   admin-on-admin escalation in a multi-tenant VSA, though in this
   attack mainly used for session hijack on the path to the agent
   procedure.
3. **CVE-2021-30120: 2FA bypass** on the VSA auth flow. Bypasses the
   MFA gate that would otherwise block the auth-bypass.
4. **SQL injection in `/userFilterTableRpt.asp`.** Used to write the
   payload into the database, then trigger execution via VSA's "agent
   procedure" workflow -- a feature legitimately used to push scripts
   to all agents.
5. **Push ransomware as "Kaseya VSA Agent Hot-fix" procedure.** The
   agent procedure dropped `agent.exe` to `c:\kworking\` (VSA's default
   working dir) and ran it with SYSTEM privileges via the trusted VSA
   agent on every downstream endpoint. The dropper used **DLL
   sideloading**: a legitimate signed Microsoft binary (`MsMpEng.exe`,
   the old Defender) loaded a malicious `mpsvc.dll` from the same
   directory, which decrypted and ran the REvil payload. Defender's
   own AMSI bypass was therefore not needed -- the loader was Microsoft
   itself.
6. **No outbound C2 needed for encryption.** REvil encrypted offline
   using a per-victim ephemeral key wrapped with the campaign's public
   key. Files renamed `*.<random>`. Ransom note dropped per-host with
   instructions to a Tor portal.

## Lessons for bug hunters

- **Multi-tenant management consoles are a force multiplier.** Any
  product whose normal function is "run my code on N customer
  endpoints" -- RMM (Kaseya, ConnectWise, N-able), MDM (Jamf,
  Workspace ONE, Intune), config-management (Tanium, BigFix, SCCM) --
  has the same blast-radius shape. Auth-bypass + write-procedure =
  fleetwide RCE. Test every console UI for: cookie predictability,
  endpoint-level auth coverage (every `.asp` / `.ashx` / API route),
  2FA-bypass paths via OAuth redirect or session reuse, SQLi on
  *write* endpoints. See [[rmm-mdm-fleet-rce]].
- **DLL sideloading via Microsoft binaries is a living technique.**
  REvil dropped `MsMpEng.exe` + `mpsvc.dll` and let Defender's old
  loader execute the malware for them. On Windows targets, audit any
  process that's signed by Microsoft but loaded from a user-writable
  directory -- AV, OneDrive, Edge updater, even MsMpEng all show up.
  See [[dll-sideload-living-off-the-land]].
- **Pre-patch zero-day in coordinated disclosure is a real timing
  risk.** Multiple zero-days from the same CVD bundle were exploited
  before Kaseya's patch shipped. If a target is running a product whose
  vendor has a public DIVD / ZDI advisory pending, that's the window.
  See [[zdi-pre-patch-window]].
- **Agent procedures / arbitrary-script-push features.** Look for any
  vendor product with a "run shell on every endpoint" feature whose
  ACL is "authenticated admin". That's the keys-to-the-kingdom
  endpoint; auth on it must be perfect.
- **On-prem RMM vs SaaS RMM.** Kaseya's SaaS instances were
  protected by Kaseya's own infra (shut down within hours); on-prem
  customers had to react themselves. Target inventory: every
  internet-exposed RMM with a vendor login page is a possible victim
  of the next CVE.

## Primary sources

- [Kaseya: "Incident Overview & Technical Details" (helpdesk.kaseya.com)](https://helpdesk.kaseya.com/hc/en-gb/articles/4403584098961-Incident-Overview-Technical-Details)
  -- vendor post-mortem with the CVE chain, attacker timeline, and
  remediation steps.
- [Huntress: "Rapid Response: Mass MSP Ransomware Incident" (2021-07-02
  -- updated)](https://www.huntress.com/blog/rapid-response-kaseya-vsa-mass-msp-ransomware-incident)
  -- discoverer's running technical thread, with the auth-bypass +
  SQLi + agent-procedure mechanic, IOCs, and the DLL-sideload chain.

## Related

- [[notpetya-medoc]]
- [[solarwinds-orion-sunburst]]
- [[rmm-mdm-fleet-rce]]
- [[dll-sideload-living-off-the-land]]
- [[zdi-pre-patch-window]]
