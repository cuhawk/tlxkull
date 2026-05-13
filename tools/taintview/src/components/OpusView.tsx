import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { getOpus } from "../api";

type Props = { target: string; chainId: number };

export function OpusView({ target, chainId }: Props) {
  const [md, setMd] = useState<string | null | "loading">("loading");
  useEffect(() => {
    setMd("loading");
    getOpus(target, chainId).then(setMd, () => setMd(null));
  }, [target, chainId]);
  if (md === "loading") return <div className="text-zinc-500 text-xs">loading opus…</div>;
  if (md === null) return <div className="text-zinc-500 text-xs">no opus writeup</div>;
  return (
    <div className="prose prose-invert prose-sm max-w-none">
      <ReactMarkdown>{md}</ReactMarkdown>
    </div>
  );
}
