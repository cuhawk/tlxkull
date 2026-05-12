# <target-program-name>

> Rename `_TEMPLATE_http.md` to `<target-name>/http.md` and fill in.
> (Filename stays `http.md` even for non-HTTP scope — that's the seed
> name `target-init` looks for.) `target-init` reads this file and
> writes `status.json` next to it. Everything downstream depends on
> this seed being correct.

## Scope

> Assets the program declares in-scope. One per line. Each entry is
> `in:` or `out:` followed by `<value>` and an optional `# type: <kind>`
> tag. Supported `type` values:
>
> | type | example |
> |---|---|
> | `domain` | `api.example.com` |
> | `wildcard` | `*.example.com` (converted to regex by target-init) |
> | `url` | `https://example.com/admin` (path-anchored) |
> | `ip` | `203.0.113.10` |
> | `cidr` | `203.0.113.0/24`, `2001:db8::/32` |
> | `asn` | `AS64512` |
> | `android_app` | `com.example.app` (package id, optional `@<sha256>`) |
> | `ios_app` | `com.example.app` (bundle id) |
> | `macos_app` | `com.example.desktop` (bundle id) or `Example.app` |
> | `windows_app` | `Example.exe` or `Example-Setup.msi` |
> | `binary` | generic native binary, sha256 if known |
> | `firmware` | device model + version |
> | `repo` | `github.com/example/api` (source-only programs) |
> | `api` | named API surface, e.g. `GraphQL@/graphql` |
> | `email` | `*@example.com` (for phishing-payload programs only) |
>
> If `type` is omitted, target-init defaults to `domain` for hostnames,
> `cidr` for slashed-IPs, `wildcard` for entries containing `*`. Use
> the tag whenever inference would be ambiguous (e.g. an Android
> package id and a reverse-DNS hostname look identical).

- in:  example.com                              # type: domain
- in:  *.example.com                            # type: wildcard
- in:  api.example.com
- in:  203.0.113.0/24                           # type: cidr
- in:  com.example.android                      # type: android_app
- in:  com.example.ios                          # type: ios_app
- in:  Example.app                              # type: macos_app
- in:  github.com/example/api                   # type: repo
- out: blog.example.com
- out: status.example.com
- out: marketing.example.com                    # type: domain

## Auth

> `type` is one of: `session | bearer | mtls | oauth | api_key |
> mobile_token | none`.
> `creds` lines reference Caido workflows, env vars, or keychain
> entries — NEVER paste raw credentials here.
> For mobile/desktop targets, list test accounts the same way; the
> mobile harness reads `creds:` to wire `mitmproxy`/Frida hooks.

- type: session
- creds: caido_workflow:login-user-a
- creds: caido_workflow:login-user-b   # second account for IDOR/BAC
- creds: env:EXAMPLE_MOBILE_BEARER     # used by mobile_app instrumentation

## Notes

> Free text. Use for prior intel — rate limits, payout speed, known
> auth quirks, platform versions tested, paths/screens already
> explored, anything that helps future sessions resume context.

- payout speed: ~7 days
- triagers prefer SARIF + html PoC bundle
- session cookie TTL: 4 hours; re-login needed often
- watch out for: cloudflare rate limit on /api/* paths
- mobile: Android 14 + iOS 17 in-scope; older versions out
- desktop: macOS app distributed via Sparkle, auto-update endpoint is in-scope
- ip ranges: 203.0.113.0/24 is the prod edge; staging at 198.51.100.0/24 is OOS

## Optional: known peer IDs (for caido-idor and mobile-idor)

> If you have known peer-owned identifiers (numeric ids, UUIDs,
> emails, device tokens, install ids), drop them here. `caido-idor`
> and any mobile-idor harness read this list when fuzzing IDs. NEVER
> include personal data of strangers — only test-account peers you
> control.

- peer_ids:
  - 42
  - 51e8a3c2-b7a1-4d6f-9e0f-4bc1234abcde
  - peer-test@example.com
  - device:ANDROID_INSTALL_ID_PEER_B
  - apns:0123456789abcdef0123456789abcdef01234567

## Optional: artifact pointers

> For non-web scope, point to where the artifact lives locally so
> skills (mobile-harvest, binary-recon, firmware-explode) can pick it
> up without re-downloading. Paths are relative to `targets/<name>/`.

- artifacts:
  - android_apk: raw/com.example.android-3.14.2.apk
  - ios_ipa:    raw/com.example.ios-7.2.0.ipa
  - macos_dmg:  raw/Example-2.1.dmg
  - windows_msi: raw/Example-Setup-5.0.msi
  - firmware:   raw/example-router-fw-1.4.bin
