import { z } from "zod";
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
  collaborator: z.string().optional()
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
  return cfg;
}
