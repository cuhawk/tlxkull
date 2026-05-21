import { z } from "zod";

export const ConfidenceSchema = z.enum(["high", "medium", "low", "lead"]);
export type Confidence = z.infer<typeof ConfidenceSchema>;

export const ModuleSchema = z.enum([
  "cache-poison",
  "cache-deception",
  "html-smuggling",
  "smuggling",
  "race"
]);
export type Module = z.infer<typeof ModuleSchema>;

export const EndpointSchema = z.object({
  id: z.string(),
  method: z.string(),
  host: z.string(),
  path: z.string(),
  query: z.record(z.string()).default({}),
  caido_request_id: z.string()
});
export type Endpoint = z.infer<typeof EndpointSchema>;

export const HttpMessageSchema = z.object({
  method: z.string().optional(),
  url: z.string().optional(),
  status: z.number().optional(),
  headers: z.record(z.string()),
  body: z.string()
});
export type HttpMessage = z.infer<typeof HttpMessageSchema>;

export const FindingSchema = z.object({
  id: z.string(),
  module: ModuleSchema,
  subtype: z.string(),
  endpoint: z.string(),
  primitive: z.record(z.any()),
  confidence: ConfidenceSchema,
  evidence: z.record(z.any()),
  poc_curl: z.string(),
  wiki_ref: z.string()
});
export type Finding = z.infer<typeof FindingSchema>;

export const RunMetaSchema = z.object({
  host: z.string(),
  ts: z.string(),
  duration_ms: z.number(),
  endpoints_probed: z.number(),
  probes_sent: z.number(),
  modules_run: z.array(ModuleSchema),
  interrupted: z.boolean().default(false)
});
export type RunMeta = z.infer<typeof RunMetaSchema>;
