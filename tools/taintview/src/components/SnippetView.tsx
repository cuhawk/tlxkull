import { useEffect, useState } from "react";
import { getSnippet, type SnippetPayload } from "../api";

type Props = { target: string; qname: string };

export function SnippetView({ target, qname }: Props) {
  const [state, setState] = useState<"loading" | { ok: SnippetPayload } | { err: string }>("loading");

  useEffect(() => {
    setState("loading");
    getSnippet(target, qname).then((r) => {
      if ("error" in r) setState({ err: r.error });
      else setState({ ok: r });
    }, (e) => setState({ err: String(e) }));
  }, [target, qname]);

  if (state === "loading") return <pre className="text-zinc-500">loading snippet…</pre>;
  if ("err" in state) return <pre className="text-amber-400">snippet unavailable: {state.err}</pre>;

  const { source, start, line, end_line, file } = state.ok;
  const lines = source.split("\n");
  return (
    <div className="text-xs font-mono">
      <div className="text-zinc-400 mb-1">{file} lines {start}–{start + lines.length - 1}</div>
      <pre className="bg-zinc-900 p-2 rounded overflow-auto">
        {lines.map((l, i) => {
          const lineNo = start + i;
          const isHi = lineNo >= line && lineNo <= end_line;
          return (
            <div key={lineNo} className={isHi ? "bg-amber-900/40" : ""}>
              <span className="text-zinc-500 select-none mr-3">{lineNo.toString().padStart(4)}</span>
              {l}
            </div>
          );
        })}
      </pre>
    </div>
  );
}
