// tests/unit/url_credential.test.ts
import { describe, it, expect } from "vitest";
import { scanUrlCredential } from "../../src/modules/html_smuggling/url_credential";

describe("scanUrlCredential", () => {
  it("flags document.URL sink", () => {
    expect(scanUrlCredential("var x = document.URL;").findings).toContain("document-url-sink");
  });
  it("flags anchor.username read", () => {
    expect(scanUrlCredential("a.username + a.password").findings).toContain("anchor-userinfo");
  });
});
