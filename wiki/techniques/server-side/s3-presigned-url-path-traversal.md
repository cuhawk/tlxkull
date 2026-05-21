---
title: S3 Pre-Signed URL — Path Traversal to Directory Listing
slug: s3-presigned-url-path-traversal
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/server-side, technique/path-traversal, technique/idor, technique/cloud]
inbound: []
---

# S3 Pre-Signed URL — Path Traversal to Directory Listing

## Pattern

AWS S3 pre-signed URLs allow servers to delegate file access to clients without
exposing AWS credentials. The server generates a signed URL scoped to a specific
file; the client uses the URL directly against S3. Security assumptions are:

1. The signature is bound to a specific `S3Key` (file path).
2. Clients cannot read other files because they cannot forge signatures.

Vulnerability: if the server generates a pre-signed URL based on a `S3Key`
parameter that the client controls, and the parameter is not validated, the
client can inject `../` to traverse directories or replace the file path
entirely. If the manipulated key points to a directory (just a `/` or empty
path), and the S3 bucket has `s3:ListBucket` permission, S3 returns a directory
listing of the entire bucket.

In the Franz Rosen finding: the application accepted a `key` parameter, didn't
validate it, and asked S3 for a pre-signed URL for that key. Injecting `/`
caused S3 to sign a listing request; following the redirect returned all bucket
contents. In this case, internal and user files were co-located in one bucket.

## Preconditions

- Server generates S3 pre-signed URLs from a user-supplied `S3Key` or file path.
- `S3Key` parameter is not validated (no path normalization, no prefix enforcement).
- S3 bucket has `s3:ListBucket` permission (common when the same bucket stores
  both application files and user uploads).

## Detection

- Intercept the request that asks the server to generate a download URL.
- Replace the file path/key parameter with `../../../` or `/`.
- Follow the redirect to see if a directory listing is returned.
- Try traversing to known paths: `../../config/`, `../../admin/`.

## Triggering

```python
import requests

# Normal request: GET /api/files/download?key=users/123/avatar.jpg
# Traversal attempt:
resp = requests.get(
    "https://target.example/api/files/download",
    params={"key": "/"},  # or "../" or "../../"
    cookies={"session": "VALID_SESSION"}
)
# Follow redirect to signed URL — observe if XML directory listing appears
print(resp.text)
```

## Bypasses

- URL encoding: try `%2F` if `/` is filtered at the application layer.
- Empty key: some S3 SDKs accept empty string as valid key.
- Null byte: `file.txt\x00../` in case server validation uses C-string comparison.

## Seen in the wild

- ~2019–2020 — Undisclosed program, $25,000 ($15k base + $10k bonus). Found by
  Franz Rosen (Detectify). Path traversal in S3 key parameter exposed directory
  listing of an entire bucket containing millions of files (internal data mixed
  with user data in one bucket).
  [BBRE](https://www.youtube.com/watch?v=G7Pre3Y46Fs)
- ~2022 — Private program (Greg, $20k). Pre-signed URL path traversal for S3
  avatar bucket also used for sensitive user files; `../` in S3 key read arbitrary
  files from the bucket.
  [BBRE](https://www.youtube.com/watch?v=MBQJJ3jfJ8k)

## References

- AWS S3 pre-signed URL documentation
- See also: [secondary-context-path-traversal](secondary-context-path-traversal.md)
- See also: [symlink-tar-arbitrary-file-read](symlink-tar-arbitrary-file-read.md)
