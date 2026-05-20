// tests/unit/form_attr.test.ts
import { describe, it, expect } from "vitest";
import { scanFormAttr } from "../../src/modules/html_smuggling/form_attr";

describe("scanFormAttr", () => {
  it("flags input form attr referencing form id outside its tree", () => {
    const html = "<form id=loginForm action=/login></form><input form=loginForm name=redirect value=https://attacker>";
    const r = scanFormAttr(html);
    expect(r.findings).toContain("input-form-attr-outside");
  });
  it("flags formaction override on input", () => {
    const html = "<form id=x><input formaction=https://attacker formtarget=_blank type=submit></form>";
    const r = scanFormAttr(html);
    expect(r.findings).toContain("formaction-override");
  });
});
