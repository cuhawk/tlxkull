---
title: Symlink in TAR Archive — Arbitrary File Read on Extraction
slug: symlink-tar-arbitrary-file-read
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/server-side, technique/path-traversal, technique/archive-extraction]
inbound: []
---

# Symlink in TAR Archive — Arbitrary File Read on Extraction

## Pattern

When a server extracts a TAR (or ZIP) archive and does not strip symlinks,
an attacker can plant a symbolic link inside the archive pointing to an
arbitrary path on the server filesystem. After extraction, any later read
of the extracted "file" resolves the symlink and reads the target file
instead.

Unlike ZIP Slip (which writes arbitrary files), this technique achieves
*arbitrary file read* by having the server later serve the symlink-resolved
content.

## Preconditions

- Target application extracts user-supplied archives (TAR, TAR.GZ, etc.).
- Extraction does not sanitize symlinks (`os.Symlink` entries preserved).
- The extracted files are later served or imported by the application in a
  way that dereferences symlinks (e.g., file attachment download, import
  functionality).

## Detection

- Test file upload / import features that handle archives.
- Upload an archive containing a symlink (e.g., `ln -s /etc/passwd symlink`).
- Observe whether the symlink is preserved post-extraction.
- Attempt to download/view the extracted "file" to see if it resolves the symlink.

## Triggering

```bash
# Create a symlink pointing to target file
mkdir exploit_dir && cd exploit_dir
ln -s /etc/gitlab/secrets.yaml symlink_file

# Create a tar preserving the symlink
tar --create --file exploit.tar symlink_file
```

For import functionality that uses a random-named directory: first upload
a legitimate file to discover the storage path prefix, then create your
symlink with the same filename as the legitimate file within the same
path prefix.

## Bypasses

- If the extraction uses `os.path.realpath` or `tarfile.extractall` with
  `numeric_owner=True`, symlinks may be preserved unresolved.
- GitLab-specific: attachments are stored in UUID-named directories, but
  the import flow uses a known path prefix pattern during group migrations.

## Seen in the wild

- 2022-10-18 — GitLab, $29,000. Group import (group-from-URL) flow packed
  attachments in TAR archive. Symlink survived extraction. Server served
  symlink-resolved file contents via attachment download, enabling arbitrary
  file read including `/etc/gitlab/secrets.yaml`.
  Reporter: William Bowling. [BBRE](https://www.youtube.com/watch?v=GRDbs-MvDBA)

## References

- See also: [../server-side/secondary-context-path-traversal](secondary-context-path-traversal.md)
- ZipSlip is the write-variant: [../supply-chain/zip-slip-path-traversal.md](zip-slip-path-traversal.md)
