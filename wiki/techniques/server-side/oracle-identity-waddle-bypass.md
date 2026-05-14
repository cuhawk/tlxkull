---
title: Oracle Identity Manager pre-auth RCE — `;.waddle` path-param + Java annotation compile-time exec (CVE-2025-61757)
slug: oracle-identity-waddle-bypass
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/java, technique/auth-bypass, technique/rce, sink/groovy-script-status]
inbound: []
---

# Oracle Identity Manager pre-auth RCE — `;.waddle` path-param + Java annotation compile-time exec (CVE-2025-61757)

## Pattern

Searchlight Cyber's chain against Oracle Identity Manager / Identity
Governance suite. Two-step:

1. **Filter bypass via Java path-parameter.** The application uses a
   *single* central servlet auth filter for every route; the developers
   want to let WSDL files through unauthenticated, so the filter rule
   matches `getRequestURI()` ending in `.waddle`. Java URI semantics
   treat `;` as a path-parameter delimiter — `getRequestURI()` returns
   the full path *including* the `;...` suffix, but the application's
   downstream routing strips it. So `/protected;.waddle` hits the
   protected route while the filter rule sees the `.waddle` suffix and
   waves it through.
2. **Compile-time RCE via Java annotations.** The unauthenticated
   endpoint reached, `groovyScriptStatus`, takes Groovy source and
   *only* runs the Groovy compiler to report syntax errors — the
   compiled code is not executed at runtime. However: Java annotations
   declared in the Groovy source are processed at **compile time** by
   the JVM annotation processor. A custom annotation with a static
   initializer or a Class-literal-side-effect runs arbitrary code
   during the compile phase.

The combined pattern: filter-bypass + sink that "doesn't execute user
code" but does invoke a compile-time path that takes user code.

## Preconditions

- Java application using one central servlet filter for auth.
- Filter rule based on path suffix or extension.
- Java request routing strips `;...` path parameters; filter inspects
  pre-strip URI.
- Reachable endpoint that compiles user-supplied Groovy/Java source —
  even if it doesn't execute the result.

## Detection

- Find the filter mapping in `web.xml` / `@WebFilter` annotation; look
  for suffix-based exclusions.
- Probe protected routes with `;.<allowed-suffix>` and observe response
  code change from 401/403 to 200/4xx.
- Inspect reachable endpoints for compile/validate functionality —
  Groovy, JSP, Velocity, MVEL.

## Triggering

Filter bypass:
```
GET /idm/admin/groovyScriptStatus;.waddle HTTP/1.1
```
Compile-time RCE via custom annotation:
```groovy
@interface Pwn {}
class Holder {
  static { Runtime.getRuntime().exec(new String[]{"sh","-c","..."}); }
}
@Pwn
class Trigger {}
```
The Holder static initializer runs during annotation processing.

## Bypasses

- Some servlet containers (Jetty 12+) reject `;` in URIs by default;
  test on actual deployment.
- If suffix-filter uses `getRequestURL()` instead of `getRequestURI()`,
  bypass changes (URL strips path params); try `?param=value` or
  encoded variants.

## Seen in the wild

- {date: 2025-11-27, source: CT Ep 150} — Searchlight Cyber disclosure of
  CVE-2025-61757 in Oracle Identity Manager; published the day before
  the episode.

## References

- Searchlight Cyber blog — Oracle Identity Manager pre-auth RCE
- CVE-2025-61757
- Critical Thinking Podcast Ep 150
- Orange Tsai BlackHat 2018 — Java path-parameter abuse (origin
  research)
- Related: [[../dom-xss/cspt-react-useparams]] (different stack, similar
  filter-bypass shape)
