---
title: Ep 55 -- Popping WordPress Plugins -- Methodology Brain Dump (with Ram Gall)
slug: ct-ep-55-popping-wordpress-plugins
url: https://www.youtube.com/watch?v=Ju-xmHusOsI
fetched_utc: 2026-05-14T00:00:00Z
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, wordpress, access-control, csrf, recon, code-review]
inbound: []
---

# Ep 55 -- Popping WordPress Plugins -- Methodology Brain Dump

- Date: 2024-01-25
- video_id: Ju-xmHusOsI
- Speakers: Justin Gardner (JG), guest Ram Gall (WordFence security researcher)

## Summary

Live walk-through of the WordPress plugin attack surface led by Ram Gall
(WordFence). Counter-intuitive named-hook semantics: `add_action(admin_init)`
fires for every `/wp-admin/*` request including unauthenticated traffic to
`admin-ajax.php` and `admin-post.php`; `is_admin()` only checks whether the
URI is under `/wp-admin/`, not the user's role; `check_admin_referer` does
not check the referer header. Subscriber-to-RCE on Elementor 3.x onboarding
module used the only-`wp_verify_nonce`-as-access-control pattern plus
arbitrary zip extraction. Ram explains the page_now path-traversal nonce
harvest (Mark Montpas / UpdraftPlus) where `PHP_SELF` normalisation on some
NGINX configs lets a subscriber visit a page that emits an admin-only nonce.
Free 80%-yield recon: every WordPress install exposes `/?rest_route=/`
unauthenticated, returning a full Swagger-style catalogue of plugin routes,
methods, and parameter schemas. WordPress REST core also parses HTTP body
for **every** method including GET -- JSON-in-GET-body bypasses
$_GET/$_POST/$_REQUEST while still landing in `WP_REST_Request::get_param`,
yielding parser-confusion bugs when plugins mix the two access patterns.
Discussion of patch-diffing approach: download zips from `wordpress.org/plugins/`,
diff versions, exploit pre-patch immediately. WPScan limitations mean
plugins without known CVEs are skipped by mass scanners -- high-value cold
scope. Closes with role taxonomy (subscriber -> contributor -> author -> editor
-> administrator) and short-codes / `add_filter` callback abuse via
`update_profile` and `update_post` hooks any non-admin can trigger.

## Techniques extracted

- [[../../techniques/wordpress/admin-ajax-unauth-action]] -- `admin_init` / `wp_ajax_nopriv_*` fire unauthenticated; `is_admin()` is not a permission check; `check_admin_referer` doesn't check referer.
- [[../../techniques/wordpress/nonce-as-access-control]] -- plugins use ability-to-read-the-nonce as a stand-in for capability; subscribers harvest nonces from accessible pages.
- [[../../techniques/wordpress/wp-rest-route-enum]] -- `/?rest_route=/` is a free unauthenticated Swagger catalogue of every plugin route.
- [[../../techniques/wordpress/wp-get-body-parse]] -- REST core reads HTTP body on GET; param-source confusion between `$_GET` / `$_REQUEST` / `WP_REST_Request::get_param`.

## Tools mentioned

- WordFence -- sponsor; bug bounty platform with 6.25x multiplier campaigns; new plugins enter scope when they cross 50k active installs.
- WPScan -- community-DB plugin scanner; only knows about CVE-listed plugins, so anything you bypass-find is untouched by automation.
- Justin's WordPress-automation rig -- AST-based plugin code review; "kicking out a lot of vulns" with new plugin code monitoring.

## Quotes

> "There's no in-place CSRF protection, there's no in-place access control."
> -- Ram, on `admin_init` / `wp_ajax_*` hook callbacks.

> "It will read the entire raw post body for all request methods."
> -- Ram, on WordPress REST parsing GET bodies.

> "You should never assume that someone can't access a nonce."
> -- Ram, on nonce-as-access-control bypasses.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
