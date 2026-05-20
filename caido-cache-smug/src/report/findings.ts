import { writeFile, mkdir } from "node:fs/promises";
import { join } from "node:path";
import type { Finding } from "../types.js";

export interface FindingsFile {
  host: string;
  ts: string;
  findings: Finding[];
}

export async function writeFindings(outDir: string, file: FindingsFile): Promise<void> {
  await mkdir(outDir, { recursive: true });
  const body = JSON.stringify({ schema_version: 1, ...file }, null, 2);
  await writeFile(join(outDir, "findings.json"), body, "utf8");
}
