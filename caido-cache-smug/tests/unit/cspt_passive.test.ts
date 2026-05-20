// tests/unit/cspt_passive.test.ts
import { describe, it, expect } from "vitest";
import { scanCsptPassive } from "../../src/modules/cache_deception/cspt_passive";

describe("scanCsptPassive", () => {
  it("flags template-string fetch with user input", () => {
    const js = "fetch(`/api/me/${params.get('next')}`)";
    const leads = scanCsptPassive(js, "https://x.test/app.js");
    expect(leads).toHaveLength(1);
    expect(leads[0].subtype).toBe("cspt-cache-deception-candidate");
  });
  it("ignores static fetch", () => {
    expect(scanCsptPassive("fetch('/api/me')", "https://x.test/app.js")).toHaveLength(0);
  });
});
