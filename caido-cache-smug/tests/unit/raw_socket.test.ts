// tests/unit/raw_socket.test.ts
import { describe, it, expect } from "vitest";
import * as net from "node:net";
import { rawSend } from "../../src/modules/smuggling/raw_socket";

describe("rawSend", () => {
  it("sends raw bytes and reads response from echo server", async () => {
    const server = net.createServer((c) => {
      c.on("data", (chunk) => {
        c.write("HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello");
        c.end();
      });
    });
    await new Promise<void>((r) => server.listen(0, "127.0.0.1", () => r()));
    const port = (server.address() as net.AddressInfo).port;
    const start = Date.now();
    const res = await rawSend({ host: "127.0.0.1", port, tls: false, raw: "GET / HTTP/1.1\r\nHost: x\r\n\r\n", timeoutMs: 2000 });
    const elapsed = Date.now() - start;
    expect(res.bytes).toContain("hello");
    expect(elapsed).toBeLessThan(2000);
    await new Promise<void>((r) => server.close(() => r()));
  });
});
