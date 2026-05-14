---
title: WordPress nonce-as-access-control bypass
slug: nonce-as-access-control
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/wordpress, technique/access-control, technique/csrf]
inbound: []
---

# WordPress nonce-as-access-control

## Pattern

A WordPress "nonce" is misnamed -- it's a CSRF token, not a unique
number. WordPress nonces are tied to user + session + action + a
12-hour-bucketed timestamp (each nonce is valid for ~24h with a 12h
overlap). Plugins frequently use the **ability to read the nonce from
some page** as a stand-in for authorization. If the nonce shows up
anywhere a low-privilege user can reach (even unauthenticated, via
`admin-post.php` / `admin-init` hook output), the access control is
broken: the low-privilege user grabs the nonce, then submits the
privileged action with it.

Worst case: Elementor < 3.1.4 (subscriber -> RCE, May 2021). Onboarding
module ran on every `admin_init` hook, did `wp_verify_nonce` only, then
accepted an arbitrary zip upload that got extracted into the plugins
directory. Any subscriber-role user could read the nonce from the
admin page they had access to, then upload a webshell-bearing zip.

## Preconditions

- Plugin uses `wp_verify_nonce` or `check_admin_referer` as the **only**
  protection on a privileged callback.
- The nonce is emitted somewhere a lower-privilege user can read
  (admin_init JSON response, profile page, etc.).
- No `current_user_can()` capability check on the callback.

## Detection

- Static: grep plugin for `check_admin_referer(` /
  `wp_verify_nonce(` followed by a privileged operation (file_put_contents,
  update_user_meta with role, etc.).
- Dynamic: with subscriber credentials, walk all admin pages
  (`wp-admin/profile.php`, `wp-admin/admin.php?page=*`) and harvest
  every `name="_wpnonce"` / `nonce: '...'` JS literal you see.
- Replay each harvested nonce against admin-ajax/admin-post endpoints
  that look privileged.

## Triggering

```http
POST /wp-admin/admin-ajax.php?action=<privileged-action> HTTP/1.1
Cookie: <subscriber session>

_wpnonce=<nonce-harvested-from-profile-page>&...
```

Page-Now path-traversal nonce harvest (Mark Montpas / WPScan, e.g.
UpdraftPlus): WordPress's `page_now` global uses `PHP_SELF` to determine
the current admin page. On certain server configs (some NGINX setups),
`/wp-admin/profile.php/%00/admin.php` makes `page_now` think it's
`admin.php` while the routing actually serves `profile.php` -- output the
admin-only nonce to a subscriber-accessible page.

## Bypasses

- Servers that have normalised `PHP_SELF` close the page_now trick;
  test per-target.
- Some plugins use a single global nonce -- even more lenient; one
  harvested nonce works for every action.

## Defence

- `wp_verify_nonce` + `current_user_can($capability)` together. Always
  the second check before the action runs.
- Action-scoped nonces (per-callback label) not global.

## Seen in the wild

- {date: 2021, source: Elementor < 3.1.4} -- subscriber -> RCE via
  onboarding zip upload + nonce-only protection.
- {date: 2024-01-25, source: CT Ep 55} -- Ram Gall (WordFence) confirms
  this is one of the most common WordPress plugin bug classes.
- {date: 2024, source: UpdraftPlus} -- Mark Montpas / WPScan
  page_now path-traversal nonce harvest.

## References

- Critical Thinking Podcast Ep 55
- WordFence -- "Common WordPress Vulnerabilities and Prevention Through
  Secure Coding Best Practices" (PDF)
- Elementor CVE-2021-24486
- Mark Montpas / WPScan UpdraftPlus disclosure
- Related: [[wp-rest-route-enum]], [[wp-get-body-parse]],
  [[../csrf/form-action-csp-gap]]
