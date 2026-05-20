// tests/unit/cache.test.ts
import { describe, it, expect } from "vitest";
import { parseCacheIndicators, hasCacheLayer } from "../../src/core/cache";

describe("cache indicators", () => {
  it("detects X-Cache HIT", () => {
    const i = parseCacheIndicators({ "x-cache": "HIT" });
    expect(i.hit).toBe(true);
  });
  it("detects CF-Cache-Status MISS + Age", () => {
    const i = parseCacheIndicators({ "cf-cache-status": "MISS", age: "12" });
    expect(i.hit).toBe(false);
    expect(i.age).toBe(12);
    expect(i.cdnFamily).toBe("cloudflare");
  });
  it("hasCacheLayer true when any indicator present", () => {
    expect(hasCacheLayer({ via: "1.1 varnish" })).toBe(true);
    expect(hasCacheLayer({})).toBe(false);
  });
  it("Cache-Control public flagged cacheable", () => {
    const i = parseCacheIndicators({ "cache-control": "public, max-age=3600" });
    expect(i.cacheable).toBe(true);
  });
});
