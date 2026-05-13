import type { Chain } from "../state/chains";
import type { Verdict, VerdictRecord } from "../state/filters";

type Props = {
  chains: Chain[];
  selectedId: number | null;
  verdictByChain: Record<string, VerdictRecord>;
  onSelect: (id: number) => void;
  onAnimate: (id: number) => void;
};

function verdictLabel(v: VerdictRecord | undefined): Verdict {
  return v?.verdict ?? "none";
}

export function ChainTable({ chains, selectedId, verdictByChain, onSelect, onAnimate }: Props) {
  return (
    <div className="h-full overflow-auto text-xs font-mono">
      <table className="w-full border-collapse">
        <thead className="sticky top-0 bg-zinc-900 text-zinc-300">
          <tr>
            <th className="text-left px-2 py-1">id</th>
            <th className="text-left px-2 py-1">src tax</th>
            <th className="text-left px-2 py-1">sink tax</th>
            <th className="text-right px-2 py-1">depth</th>
            <th className="text-right px-2 py-1">score</th>
            <th className="text-left px-2 py-1">verdict</th>
            <th className="text-left px-2 py-1">reach</th>
            <th className="text-left px-2 py-1">hot</th>
          </tr>
        </thead>
        <tbody>
          {chains.map((c) => {
            const v = verdictLabel(verdictByChain[c.id]);
            const isSel = c.id === selectedId;
            return (
              <tr
                key={c.id}
                className={`cursor-pointer ${isSel ? "bg-zinc-800" : "hover:bg-zinc-900"}`}
                onClick={() => onSelect(c.id)}
                onDoubleClick={() => onAnimate(c.id)}
              >
                <td className="px-2 py-1">{c.id}</td>
                <td className="px-2 py-1">{c.source.taxonomy_id}</td>
                <td className="px-2 py-1">{c.sink.taxonomy_id}</td>
                <td className="px-2 py-1 text-right">{c.depth}</td>
                <td className="px-2 py-1 text-right">{c.score.toFixed(0)}</td>
                <td className="px-2 py-1">{v}</td>
                <td className="px-2 py-1">{c.reach}</td>
                <td className="px-2 py-1">{c.is_hot ? "yes" : ""}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
