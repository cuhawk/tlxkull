import http from "node:http";

export function startMockTarget(opts: { reflectUnkeyed?: boolean } = {}): Promise<{ server: http.Server; port: number }> {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const xfh = req.headers["x-forwarded-host"];
      const body = opts.reflectUnkeyed && xfh
        ? `<base href="https://${xfh}/"><p>welcome</p>`
        : `<p>welcome</p>`;
      res.writeHead(200, { "x-cache": "MISS", "cache-control": "public, max-age=300" });
      res.end(body);
    });
    server.listen(0, "127.0.0.1", () => {
      const port = (server.address() as { port: number }).port;
      resolve({ server, port });
    });
  });
}
