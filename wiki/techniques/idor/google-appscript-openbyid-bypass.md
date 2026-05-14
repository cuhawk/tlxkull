---
title: Google Apps Script SpreadsheetApp.openById threat-model bypass
slug: google-appscript-openbyid-bypass
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/idor, technique/google-vrp, technique/threat-model-bypass]
inbound: []
---

# Google Apps Script `SpreadsheetApp.openById` threat-model bypass

## Pattern
The Apps Script runtime in *your own* spreadsheet can call
`SpreadsheetApp.openById(victimDocId)` against a document on which you only
have **read access**. The opened object exposes server-side methods
(`getFormUrl()`, `getEditors()`, etc.) that return data the standard
Google Drive UI threat model says read-only viewers should not see —
form-source URL, editor email addresses, etc.

Each Apps Script function is its own independent IDOR primitive against
the document's metadata surface. As new functions are added to the SDK,
diff the docs.

## Preconditions
- Attacker has at least *view* access to the target document (sharing
  link, "anyone with the link can view", etc.).
- Apps Script function exists that returns data outside the view-role
  threat model.

## Detection
- Diff Apps Script SDK release notes (Google updates the surface
  regularly). Test each new function against a read-only doc.
- Document any function returning more than the read-role threat model
  allows.

## Triggering
```javascript
function bypass() {
  const docId = "VICTIM_DOC_ID";  // attacker has read-only access
  const ss = SpreadsheetApp.openById(docId);
  return {
    formUrl: ss.getFormUrl(),         // $7500 Google VRP bug
    editors: ss.getEditors().map(e => e.getEmail()),  // $15000 bug
  };
}
```

## Bypasses / hardening
- Google fixes case-by-case. Future diffs of the Apps Script docs are
  the recon vector.

## Seen in the wild
- {date: 2024, source: CT Ep 116} — two consecutive Google VRP awards
  ($7.5K + $15K) by the same researcher.

## References
- Google VRP disclosed reports — "Loophole of getting Google form
  associated with Google Sheets with no editor/owner access"
- Critical Thinking Podcast Ep 116
- Related: [[vertical-idor]], [[horizontal-bola]]
