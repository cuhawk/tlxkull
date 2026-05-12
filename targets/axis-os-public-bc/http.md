# AXIS OS

> Platform: Bugcrowd — https://bugcrowd.com/engagements/axis-os-public
> Type: BBP
> Bounty: P1 $40000 | P2 $10000 | P3 $2000 | P4 $500 (+ $50000 bonus max)
> Status: In progress

## Scope

- in:  AXIS OS (Linux-based OS for Axis edge devices — 400+ products including cameras, intercoms, access control)   # type: firmware
- in:  VAPIX API endpoints on AXIS OS devices   # type: api
- in:  ONVIF API endpoints on AXIS OS devices   # type: api

## Auth

- type: device
- notes: Self-provisioned via Axis device web interface. Admin/operator/viewer accounts supported.

## Notes

- status: ACTIVE
- notes: Firmware/IoT program. Test AXIS OS Linux-based OS for edge devices. VAPIX library docs at https://www.axis.com/vapix-library. No direct device access currently (being replaced by virtual loan system). CVE assignments available as CNA. CVSS v3.1 scoring.
- notes: Excluded: CSRF/XSS in web interface, ACAP app vulns, DoS, MitM-dependent attacks, local access unless enables priv esc.

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
