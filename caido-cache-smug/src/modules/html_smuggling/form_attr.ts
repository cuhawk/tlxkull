export interface FormAttrScan {
  findings: string[];
}

const INPUT_FORM_ATTR = /<input[^>]+form\s*=\s*["']?[\w-]+["']?[^>]*>/i;
const FORMACTION = /<input[^>]+formaction\s*=/i;

export function scanFormAttr(html: string): FormAttrScan {
  const findings: string[] = [];
  if (INPUT_FORM_ATTR.test(html)) findings.push("input-form-attr-outside");
  if (FORMACTION.test(html)) findings.push("formaction-override");
  return { findings };
}
