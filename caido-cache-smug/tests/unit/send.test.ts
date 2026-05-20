// tests/unit/send.test.ts
import { describe, it, expect, vi } from "vitest";
import { CaidoSender } from "../../src/caido/send";
import { Throttle } from "../../src/core/throttle";

describe("CaidoSender", () => {
  it("acquires throttle slot before send", async () => {
    const throttle = new Throttle({ rps: 100, burst: 1 });
    const acquire = vi.spyOn(throttle, "acquire");
    const client = { graphql: vi.fn().mockResolvedValue({ sendRequest: { request: { id: "r" }, response: { id: "p", status: 200, headers: "{}", body: "ok" } } }) } as any;
    const s = new CaidoSender(client, throttle);
    await s.send({ method: "GET", url: "https://x.test/", headers: {}, body: "" });
    expect(acquire).toHaveBeenCalledOnce();
  });
});
