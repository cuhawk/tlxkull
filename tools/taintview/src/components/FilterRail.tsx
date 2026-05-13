import type { Chain } from "../state/chains";
import type { FilterState, Verdict } from "../state/filters";

type Props = {
  chains: Chain[];
  filters: FilterState;
  setFilters: (f: FilterState) => void;
};

function uniq(xs: Iterable<string>): string[] {
  return [...new Set(xs)].sort();
}

function toggle<T>(set: Set<T>, v: T): Set<T> {
  const out = new Set(set);
  if (out.has(v)) out.delete(v);
  else out.add(v);
  return out;
}

export function FilterRail({ chains, filters, setFilters }: Props) {
  const srcTax = uniq(chains.map((c) => c.source.taxonomy_id));
  const sinkTax = uniq(chains.map((c) => c.sink.taxonomy_id));
  const verdicts: Verdict[] = ["tp", "fp", "undet", "none"];

  return (
    <aside className="h-full overflow-auto p-3 space-y-4 text-xs">
      <section>
        <h3 className="text-zinc-400 mb-1">source taxonomy</h3>
        {srcTax.map((t) => (
          <label key={t} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={filters.sourceTaxonomies.size === 0 || filters.sourceTaxonomies.has(t)}
              onChange={() =>
                setFilters({ ...filters, sourceTaxonomies: toggle(filters.sourceTaxonomies, t) })
              }
            />
            <span>{t}</span>
          </label>
        ))}
      </section>

      <section>
        <h3 className="text-zinc-400 mb-1">sink taxonomy</h3>
        {sinkTax.map((t) => (
          <label key={t} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={filters.sinkTaxonomies.size === 0 || filters.sinkTaxonomies.has(t)}
              onChange={() =>
                setFilters({ ...filters, sinkTaxonomies: toggle(filters.sinkTaxonomies, t) })
              }
            />
            <span>{t}</span>
          </label>
        ))}
      </section>

      <section>
        <h3 className="text-zinc-400 mb-1">score &gt;= {filters.scoreMin}</h3>
        <input
          type="range"
          min={0}
          max={100}
          value={filters.scoreMin}
          onChange={(e) => setFilters({ ...filters, scoreMin: Number(e.target.value) })}
          className="w-full"
        />
      </section>

      <section>
        <h3 className="text-zinc-400 mb-1">depth &lt;= {filters.depthMax}</h3>
        <input
          type="range"
          min={1}
          max={20}
          value={filters.depthMax}
          onChange={(e) => setFilters({ ...filters, depthMax: Number(e.target.value) })}
          className="w-full"
        />
      </section>

      <section>
        <h3 className="text-zinc-400 mb-1">verdict</h3>
        {verdicts.map((v) => (
          <label key={v} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={filters.verdicts.has(v)}
              onChange={() => setFilters({ ...filters, verdicts: toggle(filters.verdicts, v) })}
            />
            <span>{v}</span>
          </label>
        ))}
      </section>
    </aside>
  );
}
