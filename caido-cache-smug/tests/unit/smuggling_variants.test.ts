// tests/unit/smuggling_variants.test.ts
import { describe, it, expect, vi } from "vitest";
import { probeTeCl } from "../../src/modules/smuggling/te_cl";
import { probeTeTe } from "../../src/modules/smuggling/te_te";
import { probeHopByHop } from "../../src/modules/smuggling/hop_by_hop";

const rawOK = vi.fn().mockResolvedValue({ bytes: "HTTP/1.1 200 OK\r\n\r\n", elapsedMs: 100, timedOut: false });
const rawSlow = vi.fn()
  .mockResolvedValueOnce({ bytes: "HTTP/1.1 200 OK\r\n\r\n", elapsedMs: 100, timedOut: false })
  .mockResolvedValueOnce({ bytes: "", elapsedMs: 6000, timedOut: true });

describe("smuggling variants", () => {
  it("TE.CL candidate on timeout", async () => {
    const r = await probeTeCl(rawSlow, { host: "x", port: 443, tls: true });
    expect(r.candidate).toBe(true);
  });
  it("TE.TE returns array of obfuscation results", async () => {
    const r = await probeTeTe(rawOK, { host: "x", port: 443, tls: true });
    expect(Array.isArray(r)).toBe(true);
  });
  it("hop-by-hop returns boolean for each candidate header", async () => {
    const r = await probeHopByHop(rawOK, { host: "x", port: 443, tls: true }, ["Content-Length"]);
    expect(r.length).toBe(1);
  });
});
