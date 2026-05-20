// tests/unit/cl_te.test.ts
import { describe, it, expect, vi } from "vitest";
import { probeClTe } from "../../src/modules/smuggling/cl_te";

describe("probeClTe", () => {
  it("returns candidate when malformed request times out > baseline", async () => {
    const raw = vi.fn()
      .mockResolvedValueOnce({ bytes: "HTTP/1.1 200 OK\r\n\r\n", elapsedMs: 100, timedOut: false })
      .mockResolvedValueOnce({ bytes: "", elapsedMs: 6000, timedOut: true });
    const result = await probeClTe(raw, { host: "x.test", port: 443, tls: true });
    expect(result.candidate).toBe(true);
  });
});
