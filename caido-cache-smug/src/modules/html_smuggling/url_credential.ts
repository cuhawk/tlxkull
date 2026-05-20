export interface UrlCredScan {
  findings: string[];
}

export function scanUrlCredential(body: string): UrlCredScan {
  const findings: string[] = [];
  if (/document\.URL\b/.test(body)) findings.push("document-url-sink");
  if (/\.username\b|\.password\b/.test(body)) findings.push("anchor-userinfo");
  return { findings };
}
