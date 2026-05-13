import { describe, expect, it, vi } from "vitest";
import { pulsePath } from "../util/animate";

describe("pulsePath", () => {
  it("calls visit(node) and visit(edge) in chronological order", async () => {
    const visits: string[] = [];
    const visit = vi.fn((id: string) => visits.push(id));
    await pulsePath(["A", "B", "C"], visit, { stepMs: 1 });
    expect(visits).toEqual(["A", "A>>B", "B", "B>>C", "C"]);
  });

  it("returns immediately on empty or single-node paths", async () => {
    const visit = vi.fn();
    await pulsePath([], visit, { stepMs: 1 });
    await pulsePath(["solo"], visit, { stepMs: 1 });
    expect(visit).not.toHaveBeenCalled();
  });
});
