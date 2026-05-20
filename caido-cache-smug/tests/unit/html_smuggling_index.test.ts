// tests/unit/html_smuggling_index.test.ts
import { describe, it, expect } from "vitest";
import { runHtmlSmuggling } from "../../src/modules/html_smuggling";

describe("runHtmlSmuggling", () => {
  it("emits finding when >=2 indicators present", () => {
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = {
      method: "GET",
      url: "https://x.test/",
      headers: {},
      body: "var b=new Blob([d]);URL.createObjectURL(b);a.download='x.exe';",
      status: 200
    };
    const findings = runHtmlSmuggling(endpoint, baseline);
    expect(findings).toHaveLength(1);
    expect(findings[0].confidence).toBe("medium");
  });
  it("emits lead when exactly 1 indicator", () => {
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "URL.createObjectURL(b)", status: 200 };
    const findings = runHtmlSmuggling(endpoint, baseline);
    expect(findings[0]?.confidence).toBe("lead");
  });
});
