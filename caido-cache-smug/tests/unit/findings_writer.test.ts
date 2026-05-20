// tests/unit/findings_writer.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { writeFindings } from "../../src/report/findings";

describe("writeFindings", () => {
  let dir: string;
  beforeEach(() => { dir = mkdtempSync(join(tmpdir(), "ccs-")); });

  it("writes findings.json with schema-valid content", async () => {
    await writeFindings(dir, {
      host: "x.test",
      ts: "2026-05-20T00:00:00Z",
      findings: [{
        id: "cp-1", module: "cache-poison", subtype: "unkeyed-header",
        endpoint: "GET /", primitive: {}, confidence: "high", evidence: {},
        poc_curl: "curl", wiki_ref: "wiki/x.md"
      }]
    });
    const content = JSON.parse(readFileSync(join(dir, "findings.json"), "utf8"));
    expect(content.schema_version).toBe(1);
    expect(content.findings).toHaveLength(1);
    rmSync(dir, { recursive: true, force: true });
  });
});
