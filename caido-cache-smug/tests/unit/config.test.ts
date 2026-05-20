// tests/unit/config.test.ts
import { describe, it, expect } from "vitest";
import { parseConfig } from "../../src/config";

describe("parseConfig", () => {
  it("requires --host", () => {
    expect(() => parseConfig({}, {})).toThrow(/host/);
  });

  it("uses CAIDO_API_TOKEN env when --caido-token missing", () => {
    const cfg = parseConfig({ host: "x.test" }, { CAIDO_API_TOKEN: "tk" });
    expect(cfg.caidoToken).toBe("tk");
  });

  it("errors when no token anywhere", () => {
    expect(() => parseConfig({ host: "x.test" }, {})).toThrow(/token/);
  });

  it("defaults rps to 5", () => {
    const cfg = parseConfig({ host: "x.test", caidoToken: "tk" }, {});
    expect(cfg.rps).toBe(5);
  });

  it("smuggling module requires aggressiveSmuggling flag", () => {
    expect(() =>
      parseConfig(
        { host: "x.test", caidoToken: "tk", modules: ["smuggling"] },
        {}
      )
    ).toThrow(/aggressive/);
  });
});
