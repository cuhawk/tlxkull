export type Visitor = (id: string) => void;

export async function pulsePath(
  path: string[],
  visit: Visitor,
  opts: { stepMs?: number } = {},
): Promise<void> {
  if (path.length < 2) return;
  const step = opts.stepMs ?? 250;
  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < path.length; i++) {
    visit(path[i]);
    if (i < path.length - 1) {
      await sleep(step);
      visit(`${path[i]}>>${path[i + 1]}`);
      await sleep(step);
    }
  }
}
