import type { Endpoint, Finding, HttpMessage } from "../../types.js";
import { scanBlobDownload } from "./blob_download.js";
import { scanFormAttr } from "./form_attr.js";
import { scanUrlCredential } from "./url_credential.js";
import { scanDataType } from "./data_type.js";

export function runHtmlSmuggling(endpoint: Endpoint, baseline: HttpMessage): Finding[] {
  const body = baseline.body;
  const blob = scanBlobDownload(body);
  const form = scanFormAttr(body);
  const cred = scanUrlCredential(body);
  const data = scanDataType(body);
  const all = [...blob.indicators, ...form.findings, ...cred.findings, ...data.findings];
  if (all.length === 0) return [];
  const confidence = all.length >= 2 ? "medium" : "lead";
  return [
    {
      id: `hs-${endpoint.id}`,
      module: "html-smuggling",
      subtype: "indicators",
      endpoint: `${endpoint.method} ${endpoint.path}`,
      primitive: { indicators: all },
      confidence,
      evidence: { blob: blob.indicators, form: form.findings, credential: cred.findings, data_type: data.findings },
      poc_curl: `curl '${baseline.url}'`,
      wiki_ref: "wiki/techniques/dom-xss/form-attribute-smuggling.md"
    }
  ];
}
