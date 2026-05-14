---
title: WordPress admin-ajax / admin-post unauthenticated action hooks
slug: admin-ajax-unauth-action
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/wordpress, technique/access-control]
inbound: []
---

# WordPress admin-ajax / admin-post unauthenticated action hooks

## Pattern

WordPress plugins register code via `add_action('admin_init', ...)` and
`add_action('wp_ajax_<action>', ...)` /
`add_action('wp_ajax_nopriv_<action>', ...)`. Counter-intuitively:

- **`admin_init`** fires on **every** request to a `/wp-admin/*` path,
  including unauthenticated visits to `/wp-admin/admin-post.php` and
  `/wp-admin/admin-ajax.php`. Anybody can trigger the callback.
- **`wp_ajax_<action>`** requires login but **no nonce check by
  default**.
- **`wp_ajax_nopriv_<action>`** is fully unauthenticated.
- `is_admin()` is **not** a permission check -- it returns true any time
  the request URI is under `/wp-admin/`, regardless of user role.

Confusingly named: `admin-ajax.php`, `admin-init`, `is_admin()` all read
like access-control but provide none.

## Preconditions

- WordPress plugin registers a callback against one of the above hooks
  without an internal capability check.
- Callback performs a privileged action (file write, user update, option
  update) using request input.

## Detection

- Grep plugin source:
  - `add_action(\s*['"]admin_init` -- every match is suspect.
  - `add_action(\s*['"]wp_ajax_(?!nopriv_)` -- auth required but no
    nonce; CSRF candidate.
  - `add_action(\s*['"]wp_ajax_nopriv_` -- fully unauth; highest yield.
  - `is_admin()` used as a permission gate -- always wrong.
- Dynamic: enumerate REST routes
  ([[wp-rest-route-enum]]) and admin-ajax actions from JS bundles, then
  replay with `Cookie:` removed.

## Triggering

```http
POST /wp-admin/admin-ajax.php?action=<action_name> HTTP/1.1

# or unauthenticated:
POST /wp-admin/admin-post.php?action=<action_name> HTTP/1.1
```

The plugin may register on `admin_init` and parse `$_REQUEST` directly;
no auth necessary for the callback to fire.

## Bypasses

- Plugins sometimes gate inside the callback on
  `current_user_can('manage_options')` -- not bypassable.
- Many gate only on `wp_verify_nonce` -- see
  [[nonce-as-access-control]].

## Seen in the wild

- {date: 2024-01-25, source: CT Ep 55} -- Ram Gall: "There's no in-place
  CSRF protection, there's no in-place access control" on these hooks.
- Effectively every WordPress plugin RCE / privesc CVE catalogued at
  WordFence over the last five years touches at least one of these
  hooks.

## References

- Critical Thinking Podcast Ep 55
- WordFence -- secure coding PDF
- WordPress Plugin Handbook -- actions/filters
- Related: [[nonce-as-access-control]], [[wp-rest-route-enum]],
  [[wp-get-body-parse]]
