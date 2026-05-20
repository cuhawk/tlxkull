import type { CaidoSender } from "../../caido/send.js";

export interface PersistenceResult {
  reseeds: number;
  survivalSeconds: number;
  finalHit: boolean;
}

export async function measurePersistence(
  sender: CaidoSender,
  url: string,
  poisonHeaders: Record<string, string>,
  shots: number
): Promise<PersistenceResult> {
  for (let i = 0; i < shots; i++) {
    await sender.send({ method: "GET", url, headers: poisonHeaders, body: "" });
  }
  const probe = await sender.send({ method: "GET", url, headers: {}, body: "" });
  const finalHit = /HIT/i.test(probe.response.headers["x-cache"] ?? "");
  const age = parseInt(probe.response.headers["age"] ?? "0", 10) || 0;
  return { reseeds: shots, survivalSeconds: age, finalHit };
}
