const RULES: Array<{ name: string; re: RegExp }> = [
  { name: "blob-ctor", re: /new\s+Blob\s*\(\s*\[/ },
  { name: "create-object-url", re: /URL\.createObjectURL/ },
  { name: "anchor-download", re: /\.download\s*=|<a[^>]+download[\s=>]/i },
  { name: "ms-save-or-open-blob", re: /msSaveOrOpenBlob/ },
  { name: "data-octet", re: /data:application\/octet-stream;base64,/ },
  { name: "atob-large", re: /atob\(['"][A-Za-z0-9+/=]{200,}['"]\)/ },
  { name: "uint8-from-atob", re: /new\s+Uint8Array.*atob/ },
  { name: "sw-fetch-response", re: /addEventListener\(['"]fetch['"][^)]*\)/ }
];

export interface BlobScan {
  indicators: string[];
  score: number;
}

export function scanBlobDownload(body: string): BlobScan {
  const indicators: string[] = [];
  for (const r of RULES) if (r.re.test(body)) indicators.push(r.name);
  return { indicators, score: indicators.length };
}
