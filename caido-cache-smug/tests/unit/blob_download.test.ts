// tests/unit/blob_download.test.ts
import { describe, it, expect } from "vitest";
import { scanBlobDownload } from "../../src/modules/html_smuggling/blob_download";

describe("scanBlobDownload", () => {
  it("scores Blob + createObjectURL + download attribute = 3", () => {
    const js = "var b = new Blob([data], {type:'application/octet-stream'}); var u = URL.createObjectURL(b); var a = document.createElement('a'); a.download='x.exe'; a.href=u; a.click();";
    const score = scanBlobDownload(js);
    expect(score.indicators.length).toBeGreaterThanOrEqual(3);
  });
  it("scores zero on clean JS", () => {
    expect(scanBlobDownload("function add(a,b){return a+b}").indicators).toHaveLength(0);
  });
});
