// tests/unit/smuggling_index.test.ts
import { describe, it, expect } from "vitest";
import { runSmuggling } from "../../src/modules/smuggling";

describe("runSmuggling", () => {
  it("skips when flag off", async () => {
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const findings = await runSmuggling(endpoint, { aggressive: false });
    expect(findings).toHaveLength(0);
  });
});
