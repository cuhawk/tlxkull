// tests/unit/data_type.test.ts
import { describe, it, expect } from "vitest";
import { scanDataType } from "../../src/modules/html_smuggling/data_type";

describe("scanDataType", () => {
  it("flags large inline base64 data URI", () => {
    const big = "A".repeat(1500);
    const html = `<img src=data:image/png;base64,${big}>`;
    expect(scanDataType(html).findings).toContain("large-data-uri");
  });
  it("flags SVG foreignObject", () => {
    expect(scanDataType("<svg><foreignObject>...</foreignObject></svg>").findings).toContain("svg-foreign-object");
  });
});
