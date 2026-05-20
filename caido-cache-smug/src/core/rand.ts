import { randomBytes } from "node:crypto";

export function randHex(len: number): string {
  return randomBytes(Math.ceil(len / 2)).toString("hex").slice(0, len);
}

export function canary(): string {
  return `cnry-${randHex(8)}.evil.test`;
}

export function cacheBuster(): string {
  return randHex(8);
}
