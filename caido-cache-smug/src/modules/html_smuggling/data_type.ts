export interface DataTypeScan {
  findings: string[];
}

const BIG_DATA_URI = /data:(?:image|application)\/[^;]+;base64,[A-Za-z0-9+/=]{1024,}/;
const SVG_FOREIGN = /<foreignObject\b/i;

export function scanDataType(body: string): DataTypeScan {
  const findings: string[] = [];
  if (BIG_DATA_URI.test(body)) findings.push("large-data-uri");
  if (SVG_FOREIGN.test(body)) findings.push("svg-foreign-object");
  return { findings };
}
