import { useEffect, useRef } from "react";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import coseBilkent from "cytoscape-cose-bilkent";
import dagre from "cytoscape-dagre";
import type { GraphModel } from "../state/chains";

cytoscape.use(coseBilkent);
cytoscape.use(dagre);

type Props = {
  model: GraphModel;
  layout: "cose-bilkent" | "dagre";
  highlightedNodes: Set<string>;
  highlightedEdges: Set<string>;
  onNodeClick: (qname: string) => void;
  registerPulser: (visit: (id: string) => void) => void;
};

export function Graph({
  model,
  layout,
  highlightedNodes,
  highlightedEdges,
  onNodeClick,
  registerPulser,
}: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const elements: ElementDefinition[] = [
      ...model.nodes.map((n) => ({
        data: { id: n.id, role: n.role, count: n.chainCount, label: n.id.split("::").slice(-1)[0] },
      })),
      ...model.edges.map((e) => ({
        data: { id: e.id, source: e.source, target: e.target, weight: e.weight },
      })),
    ];
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "background-color": "#475569",
            color: "#e5e7eb",
            "font-size": 10,
            "text-valign": "bottom",
            "text-margin-y": 4,
            width: "mapData(count, 1, 50, 12, 56)" as unknown as number,
            height: "mapData(count, 1, 50, 12, 56)" as unknown as number,
          },
        },
        { selector: "node[role = 'source']", style: { "background-color": "#dc2626" } },
        { selector: "node[role = 'sink']", style: { "background-color": "#9f1239" } },
        { selector: "node[role = 'both']", style: { "background-color": "#f97316" } },
        {
          selector: "edge",
          style: {
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "line-color": "#3f3f46",
            "target-arrow-color": "#3f3f46",
            width: "mapData(weight, 1, 20, 1, 6)" as unknown as number,
            opacity: 0.7,
          },
        },
        { selector: ".dim", style: { opacity: 0.1 } },
        { selector: ".hi", style: { opacity: 1, "line-color": "#fbbf24", "target-arrow-color": "#fbbf24" } },
        { selector: ".pulse", style: { "background-color": "#fbbf24", "line-color": "#fbbf24" } },
      ],
      layout: { name: layout, animate: false } as cytoscape.LayoutOptions,
      wheelSensitivity: 0.2,
    });
    cy.on("tap", "node", (evt) => onNodeClick(evt.target.id()));
    cyRef.current = cy;

    const pulse = (id: string) => {
      const ele = cy.getElementById(id);
      if (!ele.empty()) {
        ele.addClass("pulse");
        setTimeout(() => ele.removeClass("pulse"), 800);
      }
    };
    registerPulser(pulse);

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [model, layout]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    if (highlightedNodes.size === 0 && highlightedEdges.size === 0) {
      cy.elements().removeClass("dim").removeClass("hi");
      return;
    }
    cy.elements().addClass("dim").removeClass("hi");
    highlightedNodes.forEach((id) => cy.getElementById(id).removeClass("dim").addClass("hi"));
    highlightedEdges.forEach((id) => cy.getElementById(id).removeClass("dim").addClass("hi"));
  }, [highlightedNodes, highlightedEdges]);

  return <div ref={containerRef} className="w-full h-full bg-zinc-950" />;
}
