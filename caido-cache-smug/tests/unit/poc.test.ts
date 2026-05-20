// tests/unit/poc.test.ts
import { describe, it, expect } from "vitest";
import { synthCurl } from "../../src/report/poc";

describe("synthCurl", () => {
  it("redacts cookie", () => {
    const out = synthCurl({ method: "GET", url: "https://x/", headers: { Cookie: "s=abc" }, body: "" });
    expect(out).not.toContain("abc");
    expect(out).toContain("Cookie: <redacted>");
  });
  it("includes method + url + headers", () => {
    const out = synthCurl({ method: "POST", url: "https://x/", headers: { "X-Foo": "bar" }, body: "k=v" });
    expect(out).toMatch(/curl -X POST/);
    expect(out).toContain("X-Foo: bar");
    expect(out).toContain("k=v");
  });
});
