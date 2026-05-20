// tests/unit/cf_header_overflow.test.ts
import { describe, it, expect, vi } from "vitest";
import { sweepCfHeaderOverflow } from "../../src/modules/cache_poison/cf_header_overflow";

describe("sweepCfHeaderOverflow", () => {
  it("returns lead when method-override succeeds with junk header pad", async () => {
    const sender = {
      send: vi.fn().mockResolvedValue({
        requestId: "r",
        response: { status: 200, headers: { "cf-cache-status": "HIT", "content-length": "0" }, body: "" }
      })
    } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/static/app.js", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/static/app.js", headers: {}, body: "", status: 200 };
    const findings = await sweepCfHeaderOverflow(sender, endpoint, baseline, "cloudflare");
    expect(findings[0]?.subtype).toBe("cf-header-overflow");
  });

  it("skips when CDN family not cloudflare", async () => {
    const sender = { send: vi.fn() } as any;
    const endpoint = { method: "GET", host: "x.test", path: "/", query: {}, id: "b", caido_request_id: "b" };
    const baseline = { method: "GET", url: "https://x.test/", headers: {}, body: "", status: 200 };
    const findings = await sweepCfHeaderOverflow(sender, endpoint, baseline, null);
    expect(findings).toHaveLength(0);
    expect(sender.send).not.toHaveBeenCalled();
  });
});
