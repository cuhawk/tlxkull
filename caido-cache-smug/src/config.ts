import { z } from "zod";
import { readFileSync } from "node:fs";
import { ModuleSchema } from "./types.js";

const RawConfigSchema = z.object({
  host: z.string().min(1, "--host is required"),
  caidoUrl: z.string().url().default("http://localhost:8080"),
  caidoToken: z.string({ required_error: "Caido token required" }).min(1, "Caido token required"),
  project: z.string().optional(),
  maxRequests: z.number().int().positive().default(500),
  rps: z.number().positive().default(5),
  out: z.string().optional(),
  passiveOnly: z.boolean().default(false),
  modules: z.array(ModuleSchema).default(["cache-poison", "cache-deception", "html-smuggling"]),
  authCookie: z.string().optional(),
  aggressiveSmuggling: z.boolean().default(false),
  collaborator: z.string().optional(),
  race: z.boolean().default(false),
  raceConcurrency: z.number().int().min(2).max(50).default(20),
  raceAllowMutate: z.boolean().default(false),
  raceEndpoints: z.string().optional(),
  raceAllowlist: z.array(z.object({ method: z.string(), path: z.string() })).default([])
});

export type RuntimeConfig = z.infer<typeof RawConfigSchema>;

export function parseConfig(
  args: Record<string, unknown>,
  env: Record<string, string | undefined>
): RuntimeConfig {
  const merged = {
    ...args,
    caidoToken: args.caidoToken ?? env.CAIDO_API_TOKEN,
    caidoUrl: args.caidoUrl ?? env.CAIDO_URL ?? "http://localhost:8080"
  };
  const cfg = RawConfigSchema.parse(merged);

  if (cfg.modules.includes("smuggling") && !cfg.aggressiveSmuggling) {
    throw new Error("smuggling module requires --aggressive-smuggling flag");
  }

  if (cfg.race && !cfg.modules.includes("race")) cfg.modules.push("race");
  if (cfg.modules.includes("race") && !cfg.race) {
    throw new Error("race module requires --race flag");
  }
  if (cfg.raceAllowMutate) {
    if (!cfg.raceEndpoints) {
      throw new Error("--race-allow-mutate requires --race-endpoints <path>");
    }
    cfg.raceAllowlist = readAllowlist(cfg.raceEndpoints);
    if (cfg.raceAllowlist.length === 0) {
      throw new Error(`--race-endpoints ${cfg.raceEndpoints} is empty`);
    }
  }
  return cfg;
}

function readAllowlist(path: string): Array<{ method: string; path: string }> {
  const text = readFileSync(path, "utf8");
  const out: Array<{ method: string; path: string }> = [];
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const m = line.match(/^([A-Z]+)\s+(.+)$/);
    if (!m) throw new Error(`race allowlist: bad line "${line}" (expected "METHOD /path")`);
    out.push({ method: m[1], path: m[2] });
  }
  return out;
}
