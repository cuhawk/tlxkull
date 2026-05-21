---
title: ZipSlip — Path Traversal via Archive Entry Name
slug: zip-slip-path-traversal
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/supply-chain, technique/path-traversal, technique/archive-extraction, technique/rce]
inbound: []
---

# ZipSlip — Path Traversal via Archive Entry Name

## Pattern

Archive extraction libraries that naively concatenate the extraction
directory with the entry filename allow `../` sequences in the entry name
to traverse outside the intended extraction root. An attacker crafts a
ZIP (or TAR, JAR, WAR, etc.) whose entries have names like
`../../../../var/www/html/shell.jsp`, causing the server to write arbitrary
files to arbitrary filesystem locations on extraction.

Because the entry name is stored inside the archive (not visible until
opened), many application-level validators miss it.

## Preconditions

- Application extracts user-supplied archives on the server.
- Extraction library does not normalize or sanitize entry names.
- Attacker can write to a path that triggers code execution (webroot,
  cron directory, startup scripts, etc.).

## Detection

- Craft a ZIP with `../../../tmp/test.txt` as an entry name.
- After upload, verify `/tmp/test.txt` was created on the server.
- CodeQL query available to detect this pattern in Java/Python/Ruby.

## Triggering

```python
import zipfile, os
zf = zipfile.ZipFile('exploit.zip', 'w')
zf.write('/tmp/shell.jsp', '../../../../var/www/html/shell.jsp')
zf.close()
```

## Bypasses

- If the server uses `os.path.basename()` after extraction, the traversal
  is stopped. Verify the exact library used.
- Some libraries strip leading `/` but not `../` — test both.

## Seen in the wild

- 2023-04-24 — GitHub Security Lab, $5,500. CodeQL query detecting ZipSlip
  (CVE pattern) written by Greg (BBRE host) detected the pattern in Java
  frameworks and was accepted. [BBRE](https://www.youtube.com/watch?v=F95U912u7OQ)
- Multiple instances in GitLab migration/import flows (see also
  [symlink-tar-arbitrary-file-read](symlink-tar-arbitrary-file-read.md)).

## References

- Snyk ZipSlip research (2018)
- GitHub CodeQL query: `java/zipslip`
- See also: [symlink-tar-arbitrary-file-read](../server-side/symlink-tar-arbitrary-file-read.md),
  [dependency-confusion](dependency-confusion.md)
