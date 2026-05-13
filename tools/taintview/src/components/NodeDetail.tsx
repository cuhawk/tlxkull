import type { Chain } from "../state/chains";
import type { VerdictRecord } from "../state/filters";
import { OpusView } from "./OpusView";
import { SnippetView } from "./SnippetView";
import { VerdictEditor } from "./VerdictEditor";

type Props = {
  target: string;
  selectedChain: Chain | null;
  selectedQname: string | null;
  verdict: VerdictRecord | undefined;
  onVerdictSaved: (rec: VerdictRecord) => void;
};

export function NodeDetail({ target, selectedChain, selectedQname, verdict, onVerdictSaved }: Props) {
  if (!selectedChain && !selectedQname) {
    return <div className="p-3 text-zinc-500 text-xs">select a chain or node</div>;
  }
  const qname = selectedQname ?? selectedChain?.sink.qname ?? null;
  return (
    <div className="h-full overflow-auto p-3 space-y-4">
      {qname && (
        <section>
          <h3 className="text-zinc-400 text-xs mb-1">node</h3>
          <div className="font-mono text-xs break-all">{qname}</div>
        </section>
      )}
      {qname && (
        <section>
          <h3 className="text-zinc-400 text-xs mb-1">snippet</h3>
          <SnippetView target={target} qname={qname} />
        </section>
      )}
      {selectedChain && (
        <section>
          <h3 className="text-zinc-400 text-xs mb-1">opus verdict</h3>
          <OpusView target={target} chainId={selectedChain.id} />
        </section>
      )}
      {selectedChain && (
        <section>
          <h3 className="text-zinc-400 text-xs mb-1">manual verdict</h3>
          <VerdictEditor
            target={target}
            chainId={selectedChain.id}
            current={verdict}
            onSaved={onVerdictSaved}
          />
        </section>
      )}
    </div>
  );
}
