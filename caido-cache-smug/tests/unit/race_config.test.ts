import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { parseConfig } from "../../src/config";

let tmp: string;
let allowlistPath: string;
let emptyPath: string;

beforeAll(() => {
  tmp = mkdtempSync(join(tmpdir(), "race-cfg-"));
  allowlistPath = join(tmp, "allow.txt");
  writeFileSync(allowlistPath, "POST /apply-coupon\n# comment\n\nDELETE /sessions\n", "utf8");
  emptyPath = join(tmp, "empty.txt");
  writeFileSync(emptyPath, "# only comments\n\n", "utf8");
});

afterAll(() => rmSync(tmp, { recursive: true, force: true }));

describe("race config gating", () => {
  it("--race in modules requires --race flag", () => {
    expect(() =>
      parseConfig({ host: "x.test", caidoToken: "tk", modules: ["race"] }, {})
    ).toThrow(/--race flag/);
  });

  it("--race adds 'race' to modules implicitly", () => {
    const cfg = parseConfig({ host: "x.test", caidoToken: "tk", race: true }, {});
    expect(cfg.modules).toContain("race");
  });

  it("--race-allow-mutate without --race-endpoints throws", () => {
    expect(() =>
      parseConfig({ host: "x.test", caidoToken: "tk", race: true, raceAllowMutate: true }, {})
    ).toThrow(/race-endpoints/);
  });

  it("--race-allow-mutate with empty allowlist throws", () => {
    expect(() =>
      parseConfig(
        {
          host: "x.test",
          caidoToken: "tk",
          race: true,
          raceAllowMutate: true,
          raceEndpoints: emptyPath
        },
        {}
      )
    ).toThrow(/empty/);
  });

  it("--race-allow-mutate with populated allowlist parses entries", () => {
    const cfg = parseConfig(
      {
        host: "x.test",
        caidoToken: "tk",
        race: true,
        raceAllowMutate: true,
        raceEndpoints: allowlistPath
      },
      {}
    );
    expect(cfg.raceAllowlist).toEqual([
      { method: "POST", path: "/apply-coupon" },
      { method: "DELETE", path: "/sessions" }
    ]);
  });
});
