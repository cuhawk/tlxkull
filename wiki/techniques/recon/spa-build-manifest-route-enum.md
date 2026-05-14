---
title: SPA route enumeration via build manifests + webpack chunks
slug: spa-build-manifest-route-enum
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/recon, technique/spa, technique/js-recon]
inbound: []
---

# SPA route enumeration via build manifests + webpack chunks

## Pattern
Modern SPAs (Next.js, React+react-router, Angular, Vue) render most of
their surface client-side. The set of valid client routes lives inside
the JS bundle, not the server's routing table — and is often easier to
extract than scraping the live UI.

Specific sources:

- **Next.js**: `/_next/static/.../_buildManifest.js` lists every page's
  bundle filename, from which route paths are trivially derived. Tool:
  `ThankYouNext` (`-tnu`).
- **Webpack**: the `chunks` map in the runtime entry chunk lists every
  lazy-loaded chunk. Sourcemaps (when shipped) expose the original `pages/`
  / `src/pages/` folder of `.tsx`/`.jsx` files.
- **React-router**: search for `path:` / `<Route path=...>` in bundled
  JS.

Beyond the routes themselves, the JS files often contain:

- Specific API endpoint paths used only by that route.
- Lazy-loaded chunks that fetch additional functionality (auth-guarded
  admin routes typically lazy-load).
- TypeScript-stripped data shapes (request bodies, GraphQL operation
  names) usable for fuzzing.

## Why it matters
Two hunter benefits:

1. **Triggering DOM XSS in client routes** — navigating to a previously
   undiscovered client-side route can fire vulnerable code paths
   (template strings, `dangerouslySetInnerHTML`, hash-routing sinks).
2. **State without API spelunking** — instead of reverse-engineering the
   API contract, just navigate the SPA to the state that fetches the
   data you want and watch the network.

## Preconditions
- Target is an SPA serving its bundle to unauthenticated clients (most
  are; the bundle predates auth).
- Build manifest / chunks / sourcemap not stripped at deploy time.

## Tooling
- `ThankYouNext` — parses `_buildManifest.js`, prints routes.
- `js-weasel` — does lazy-load unpacking, webpack chunk merging.
- Manual: `curl /_next/static/<hash>/_buildManifest.js` + grep.

## Seen in the wild
- {date: 2023-11-30, source: CT Ep 47} — JG: "I've popped several XSS
  over the past week because of this trick."

## References
- Critical Thinking Podcast Ep 47
- ThankYouNext repo (`ItsIgnacioPortal`)
- Related: [[client-side-template-injection]]
