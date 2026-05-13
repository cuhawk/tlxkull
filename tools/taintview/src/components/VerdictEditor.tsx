import { useState } from "react";
import { postVerdict } from "../api";
import type { Verdict, VerdictRecord } from "../state/filters";

type Props = {
  target: string;
  chainId: number;
  current: VerdictRecord | undefined;
  onSaved: (rec: VerdictRecord) => void;
};

const choices: Exclude<Verdict, "none">[] = ["tp", "fp", "undet"];

export function VerdictEditor({ target, chainId, current, onSaved }: Props) {
  const [verdict, setVerdict] = useState<Exclude<Verdict, "none">>(current?.verdict ?? "undet");
  const [note, setNote] = useState(current?.note ?? "");
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    try {
      const rec = await postVerdict(target, chainId, verdict, note);
      onSaved(rec);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-2 text-xs">
      <div className="flex gap-2">
        {choices.map((c) => (
          <label key={c} className="flex items-center gap-1">
            <input
              type="radio"
              checked={verdict === c}
              onChange={() => setVerdict(c)}
            />
            {c}
          </label>
        ))}
      </div>
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        className="w-full h-20 bg-zinc-900 p-2 rounded font-mono"
        placeholder="note…"
      />
      <button
        disabled={busy}
        onClick={save}
        className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 rounded disabled:opacity-50"
      >
        {busy ? "saving…" : "save verdict"}
      </button>
    </div>
  );
}
