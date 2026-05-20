#!/usr/bin/env node
import { Command } from "commander";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import readline from "node:readline";
import pino from "pino";
import { parseConfig } from "./config.js";
import { CaidoClient } from "./caido/client.js";
import { CaidoSender } from "./caido/send.js";
import { Throttle } from "./core/throttle.js";
import { discoverEndpoints } from "./caido/discover.js";
import { runCachePoison } from "./modules/cache_poison/index.js";
import { runCacheDeception } from "./modules/cache_deception/index.js";
import { runHtmlSmuggling } from "./modules/html_smuggling/index.js";
import { runSmuggling } from "./modules/smuggling/index.js";
import { writeFindings } from "./report/findings.js";
import { renderReport } from "./report/markdown.js";
import type { Finding, HttpMessage } from "./types.js";

const log = pino({ level: "info" });

const program = new Command();
program
  .name("caido-cache-smug")
  .requiredOption("--host <hostname>", "target hostname (HTTPQL req.host.cont)")
  .option("--caido-url <url>", "Caido API URL", "http://localhost:8080")
  .option("--caido-token <pat>", "Caido PAT (else env CAIDO_API_TOKEN)")
  .option("--project <name>", "Caido project name")
  .option("--max-requests <n>", "max requests to discover", (v: string) => parseInt(v, 10), 500)
  .option("--rps <n>", "global throttle", (v: string) => parseFloat(v), 5)
  .option("--out <dir>", "output directory")
  .option("--passive-only", "skip active probes", false)
  .option("--modules <list>", "comma list", (v: string) => v.split(","))
  .option("--auth-cookie <kv>", "auth cookie e.g. session=abc")
  .option("--aggressive-smuggling", "enable Module D (raw-socket CL/TE)", false)
  .option("--collaborator <fqdn>", "OOB collaborator for smuggling confirmation")
  .action(async (raw: Record<string, unknown>) => {
    const cfg = parseConfig(raw, process.env);
    if (cfg.aggressiveSmuggling || cfg.rps > 20) {
      const ok = await confirm(`Aggressive mode against ${cfg.host}. Proceed? [y/N] `);
      if (!ok) { log.warn("aborted by user"); process.exit(1); }
    }

    const ts = new Date().toISOString().replace(/[:.]/g, "-");
    const outDir = cfg.out ?? join("out", cfg.host, ts);
    mkdirSync(outDir, { recursive: true });

    const client = new CaidoClient({ url: cfg.caidoUrl, token: cfg.caidoToken });
    const throttle = new Throttle({
      rps: cfg.rps,
      hardFloorRps: cfg.aggressiveSmuggling ? 1 : undefined
    });
    const sender = new CaidoSender(client, throttle);

    log.info({ host: cfg.host }, "discovering endpoints");
    const endpoints = await discoverEndpoints(client, cfg.host, cfg.maxRequests);
    log.info({ count: endpoints.length }, "endpoints discovered");

    const start = Date.now();
    const findings: Finding[] = [];
    let probes = 0;
    for (const ep of endpoints) {
      const baseline = await sender.send({
        method: ep.method,
        url: `https://${ep.host}${ep.path}`,
        headers: cfg.authCookie ? { Cookie: cfg.authCookie } : {},
        body: ""
      });
      probes++;
      const msg: HttpMessage = baseline.response;
      msg.method = ep.method;
      msg.url = `https://${ep.host}${ep.path}`;
      if (!cfg.passiveOnly && cfg.modules.includes("cache-poison"))
        findings.push(...(await runCachePoison(sender, ep, msg)));
      if (!cfg.passiveOnly && cfg.modules.includes("cache-deception"))
        findings.push(...(await runCacheDeception(sender, ep, msg)));
      if (cfg.modules.includes("html-smuggling"))
        findings.push(...runHtmlSmuggling(ep, msg));
      if (cfg.modules.includes("smuggling"))
        findings.push(...(await runSmuggling(ep, { aggressive: cfg.aggressiveSmuggling, collaborator: cfg.collaborator })));
    }
    const duration = Date.now() - start;

    const meta = {
      host: cfg.host,
      ts: new Date().toISOString(),
      duration_ms: duration,
      endpoints_probed: endpoints.length,
      probes_sent: probes,
      modules_run: cfg.modules,
      interrupted: false
    };
    await writeFindings(outDir, { host: cfg.host, ts: meta.ts, findings });
    writeFileSync(join(outDir, "report.md"), renderReport(meta, findings), "utf8");
    writeFileSync(join(outDir, "run.json"), JSON.stringify(meta, null, 2), "utf8");
    log.info({ outDir, findings: findings.length }, "complete");
  });

program.parseAsync(process.argv).catch((err: unknown) => {
  log.error({ err }, "fatal");
  process.exit(1);
});

function confirm(prompt: string): Promise<boolean> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(prompt, (a: string) => { rl.close(); resolve(/^y/i.test(a.trim())); });
  });
}
