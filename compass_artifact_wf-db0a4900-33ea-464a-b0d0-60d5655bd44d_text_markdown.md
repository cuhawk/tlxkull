# Beyond the AST: A Landscape of Program Representations for JavaScript Static Analysis, with Recommendations for GFA

## TL;DR
- **The single highest-leverage upgrade for GFA is to add an Object/Multiversion Dependence Graph layer on top of your existing Babel AST + call graph** — specifically, replicate the Multiversion Dependency Graph (MDG) used by Graph.js (PLDI'24) and Explode.js (PLDI'25), which already outperforms ODGen (USENIX'22) on Node.js taint and prototype-pollution detection, and which Explode.js uses to generate working exploits with 100% precision and 4.02× more exploits than FAST.
- **Stop thinking "AST" and start thinking "layered graph": AST + CFG + PDG + points-to + object-dependence + module graph, queryable from a graph store**. Joern's Code Property Graph (CPG), CodeQL's relational dataflow IR, Snyk's "event graph", and Semgrep Pro's IL all converge on this design; for JS specifically the ODG/MDG variants add object-property state evolution that vanilla CPGs miss.
- **For bundled/minified bug-bounty targets, run a deobfuscation pipeline (webcrack → restringer → humanify-style LLM renaming) before graph construction, then use LLM-assisted taint-spec inference (à la IRIS/SemTaint) to feed sources/sinks into the graph queries** — this is the practical sweet spot in 2025 and gives you something neither CodeQL nor ODGen alone can match.

## Key Findings

1. **The "AST-only" baseline is the weakest representation for security work.** Even Semgrep documents this: "ASTs … cannot directly represent execution or data flow, which is crucial for comprehensive taint tracking … you need a data flow graph (DFG) and control flow graph (CFG) for that" (Spaceraccoon, comparing CodeQL and Semgrep). CodeQL's docs are explicit that the dataflow graph is a *distinct* representation from the AST: "Nodes in the abstract syntax tree represent syntactic elements such as statements or expressions. Nodes in the data flow graph, on the other hand, represent semantic elements that carry values at runtime."

2. **The Code Property Graph (CPG) is the dominant academic abstraction**, fusing AST + CFG + PDG into one queryable property graph (Yamaguchi et al., IEEE S&P 2014, Test-of-Time award 2024). Joern is the reference implementation, with a JavaScript frontend; ShiftLeft/Qwiet's Ocular is the commercial fork; Plume targets the JVM. Joern stores CPGs in OverflowDB (its own embedded graph database) and queries them in a Scala DSL; it can also export to Neo4j/Cypher.

3. **For JavaScript specifically, plain CPGs miss object-property state evolution and prototype-chain semantics** — the very thing that drives prototype pollution, gadget chains, and most Node.js RCEs. Two purpose-built graphs solve this:
   - **ODG (Object Dependence Graph)** — Li, Kang, Hou, Cao, USENIX Security 2022. ODGen built ODGs via abstract interpretation and "correctly reported 180 zero-day vulnerabilities, among which we have received 70 CVE identifiers."
   - **MDG (Multiversion Dependency Graph)** — Ferreira et al., PLDI 2024 (Graph.js). It captures the *state evolution of objects and their properties* by versioning each property mutation. MDGs are "significantly simpler" than ODGs ("only 0.14× the nodes and 0.42× the edges") and Graph.js found 49 previously undiscovered npm vulnerabilities while outperforming ODGen.

4. **2025 state-of-the-art for Node.js bug-bounty is Explode.js (PLDI 2025)**, which builds on Graph.js's MDG and adds a symbolic-execution stage (ECMA-Symb). Authors Marques, Ferreira, Nascimento, Coimbra, Santos, Jia, and Fragoso Santos report: "when applied to real-world Node.js packages, Explode.js uncovered 44 zero-day security vulnerabilities, for which 4 new CVEs have been assigned … Explode.js finds 4.02× more exploits than FAST and 6.61× more exploits than NodeMedic-Fine … both Explode.js and NodeMedic have zero FPs … 100% precision. In contrast, FAST generates 52 FPs." Repo: https://github.com/formalsec/explode-js.

5. **Industrial SAST tools have converged on three IR families**:
   - **Semgrep**: AST → generic intermediate language (IL); intra-procedural by default, cross-file in Pro. Pattern matching is fast but loses "class inheritance and overrides that significantly impact taint tracking."
   - **CodeQL (GitHub)**: language-specific extractor → relational database queried with Datalog-style QL. JavaScript analysis already has rich taint libraries with `RemoteFlowSource`, `ClientRequest::Range`, flow labels, threat-model sources, and a model-as-data extensibility layer (YAML extensions with `sourceModel`/`sinkModel`/`summaryModel`).
   - **Snyk Code (ex-DeepCode)**: "Snyk Code uses an abstract syntax tree (AST) and event graph (EG), which allows a data flow-sensitive, context-aware analysis" (Snyk blog). The DeepCode AI Fix paper confirms: "DeepCode AI Fix uses Snyk Code … a proprietary commercial static analyzer," and CodeReduce narrows program slices around defects before feeding them to an LLM. Snyk product docs state the engine was "Trained on over 25 million data flow cases from open-source projects, it supports 19+ languages."

6. **Classical JS abstract interpreters (TAJS, SAFE, JSAI, WALA) are scientifically rigorous but practically un-scalable to bundled real-world apps.** SAFElsa benchmarks showed "TAJS and WALA analyze 11 and 3 versions of jQuery … both TAJS and WALA fail to analyze any of 5 [popular website] programs"; this is why every modern production tool (CodeQL, Snyk, ODGen, MDG/Graph.js, FAST) intentionally trades soundness for scalability via flow- and context-sensitivity tuned to security questions, not full type inference.

7. **For prototype-pollution gadget chains specifically, Silent Spring (USENIX'23, Shcherbakov–Balliu–Staicu) and GHunter (USENIX'24, Cornelissen–Shcherbakov–Balliu) define the SOTA.** Silent Spring is static and built on CodeQL multi-label taint; GHunter is dynamic, using lightweight V8 taint instrumentation. GHunter beats Silent Spring on benchmarks: "GHUNTER is more precise (0.43 compared to 0.11) and has better recall (0.88 compared to 0.64)" against Silent Spring's own benchmark on Node.js v16, and "better precision (0.62 compared to 0.18) and recall (0.90 compared to 0.50)" on Node.js v21. GHunter identified "56 new gadgets in Node.js and 67 gadgets in Deno … arbitrary code execution (19), privilege escalation (31), path traversal (13), and more."

8. **LLM + static analysis hybrids are now the frontier**, validating GFA's overall architecture:
   - **IRIS (Li, Dutta, Naik, ICLR 2025)** combines LLMs with CodeQL for whole-repository taint inference. A state-of-the-art CodeQL deployment detects only 27 of the 120 vulnerabilities in CWE-Bench-Java, "whereas IRIS with GPT-4 detects 55 (+28)" and "IRIS with GPT-4 achieves an average false discovery rate of 84.82%, which is 5.21% lower than that of CodeQL" (arXiv:2405.17238).
   - **SemTaint** ("Multi-Agent Taint Specification Extraction for Vulnerability Detection," Chen et al., arXiv:2601.10865, Jan 2025) augments CodeQL on JS with LLM agents for callee resolution and flow summaries: "evaluated it on 162 known vulnerabilities that CodeQL alone could not detect … found 106 (65.43%) of the previously undetectable vulnerabilities … identified four previously unknown vulnerabilities."
   - **LATTE** applied LLMs to binary taint analysis: "LATTE has found 37 new bugs in real-world firmware, which the baselines failed to find … 10 of them have been assigned CVE numbers."

9. **GNN-on-CPG approaches (Devign, ReGVD, IVDetect, LineVul, Vul-LMGNN) are mature for C/C++ research benchmarks but currently weaker for JS bug bounty** because they require labeled training data and produce a coarse "vulnerable / not vulnerable" signal at the function level rather than a sourced sink trace. GraphCodeBERT explicitly uses a *data flow graph* representation during pre-training: "GraphCodeBERT extends CodeBERT by incorporating code's data flow information into the training objective." Snyk DeepCode is the only major industrial product that operationalizes this hybrid at scale (the "25 million data flow cases" figure above).

10. **Bundler/minification handling is a pipeline problem, not a representation problem.** Webcrack ("deobfuscator.io, unminify, transpile, and unpack webpack/browserify"), Restringer (40+ deobfuscation modules with isolated-vm sandboxing for unsafe transforms), and humanify (LLM identifier renaming) are the canonical stack; the JsDeObsBench benchmark (Chen, Jin, Lin, ACM CCS 2025, arXiv:2506.20170) provides "36,260 unique obfuscated JS programs with ground truth and 4,515 malicious obfuscated JS programs." JsDeObsBench cites Ren et al. (2023) for the related finding that obfuscation increases the false-negative rate of static ML-based malicious-JS detectors by 21.8%.

## Details

### A. Classical IRs and what they buy you over an AST

| IR | What it adds beyond AST | JS-specific limitation | Suitability for GFA |
|---|---|---|---|
| **AST** (Babel/Acorn/SWC/OXC) | Syntax only; cheap to build | No data/control flow; loses semantic context | Baseline (what GFA already does) |
| **CFG** | Intra-procedural control flow | Need exception/promise edges; eval/Function() break the graph | Necessary prerequisite for DFG/PDG |
| **DFG** | Reaching-definition / def-use chains | Heap-allocated objects ruin precision without points-to | Essential for taint |
| **PDG** (control + data dependence) | Slicing-friendly | Hard to interprocedural-ize without function summaries | Required for sound taint |
| **SDG** (System Dependence Graph) | Interprocedural PDG via summary edges | Higher-order JS breaks Horwitz–Reps–Binkley assumptions | Useful only with k-CFA-style call graph |
| **SSA / Three-Address Code** | Canonical variable form for analyses | JS has hoisting, closures, mutable bindings | V8/Hermes use it internally; not exposed |
| **CPS / ANF** | Models continuations and async/await as control flow | Heavy transformation cost on real bundles | Theoretical; rarely worth implementing |
| **CPG** (Yamaguchi) | AST + CFG + PDG fused | Doesn't model objects-as-graph nodes | Joern's JS frontend works but is weak vs ODGen/MDG |
| **ODG** (Li et al.) | Objects as nodes + branch-sensitive points-to | Scales poorly; ODGen "takes significantly longer to analyze prototype pollution" (Graph.js paper) | Excellent for prototype-pollution research |
| **MDG** (Ferreira et al.) | Versioned object/property states; encodes shape + dependency analysis in one graph | New; only Graph.js/Explode.js implement | **Best current option for Node.js taint + proto pollution** |
| **Call graphs** (CHA, RTA, VTA, 0-CFA, k-CFA, m-CFA) | Resolve dynamic dispatch | Van Horn–Mairson proved k-CFA EXPTIME-complete for functional/JS-like languages | 0-CFA or m-CFA usually all you can afford; CFA2 adds pushdown precision |
| **Points-to** (Andersen inclusion / Steensgaard unification) | Heap aliasing | Prototype chains require special handling | Needed for true field-sensitivity |
| **IFDS/IDE** (Reps–Horwitz–Sagiv) | Polynomial-time interprocedural distributive dataflow | Works only when problem is distributive | CodeQL's `DataFlow::Global` and SemmleCode use IFDS-flavored solvers under the hood |
| **VSA** (Value Set Analysis) | Numeric ranges, useful for buffer/array bugs | Less critical for web vuln classes | Lower priority for JS |

The clear lesson: **for JavaScript security work, the IR hierarchy that matters is AST → CFG → PDG → Points-to → ODG/MDG**, and *only* the last layer captures the dynamic property-mutation behavior that drives modern Node.js CVEs.

### B. The graph-database axis

- **Joern + OverflowDB** — open-source, Apache 2.0, with a JavaScript CPG frontend. Best for offline research; the Scala/Ammonite DSL has a learning curve. CPG spec at https://cpg.joern.io/ is explicit about JS limitations: "for languages like Javascript, it is common that we may know the (short-) name of the invoked method, but we do not know at compile time which method will actually be invoked, e.g., because it depends on a dynamic import."
- **CodeQL** — proprietary but free for open source. Its JS extractor models promises, AMD/CommonJS/ESM modules, popular libraries (lodash, fs-extra, globby, fetch, async), and provides `DataFlow::Global<MyConfig>`, `TaintTracking::Global<MyConfig>`, `FlowLabel`/flow states, and model-as-data YAML extensions (`sourceModel`, `sinkModel`, `summaryModel`). It's the single best off-the-shelf JS taint engine.
- **Neo4j + Graph.js (MDG)** — open source, Cypher queries. The Graph.js repo (https://github.com/formalsec/graphjs) exports `.csv` nodes/edges and runs Cypher detection queries for CWE-22, CWE-78, CWE-94, CWE-1321.
- **Snyk Code event graph** — closed source; "rules run against Snyk's internal 'event graph' representation" via a proprietary Datalog-based query language.
- **Sourcegraph SCIP** — open Protobuf-based code-intelligence format that replaced LSIF; emits symbol-resolution and cross-file reference edges. Useful as a *call-graph backbone* across files/packages, but does **not** capture dataflow — it complements but cannot replace a CPG/MDG.

### C. JavaScript-specific analyzers

- **TAJS** (Aarhus, Jensen/Møller/Thiemann, SAS'09) — sound dataflow analysis using monotone frameworks over a CFG. Can analyze 11 versions of jQuery but fails on most modern websites.
- **WALA JS** (IBM) — model-based; legendary for the "dynamic determinacy" technique but the latest open-source release doesn't ship it.
- **SAFE / SAFElsa** (KAIST, Ryu) — "outperforms the state-of-the-art JavaScript static analyzers in analyzing top 5 JavaScript libraries and the main web pages of the 5 most popular websites."
- **JSAI** (UCSB Kashyap, Dewey, et al., FSE'14) — formally specified, sound, configurable abstract interpreter. Found "several previously unknown soundness bugs in TAJS."
- **Pushdown JS** (Van Horn & Might) — CFA2-style precise call/return matching via pushdown automata.
- **Jalangi2** — dynamic shadow values; basis for ExpoSE.
- **ExpoSE** (Loring, Mitchell, Kinder) — DSE on Node.js with Z3 + sound regex semantics (PLDI'19).
- **Hermes (Facebook)** — AOT JS engine for React Native; pipeline is JS → AST → high-level IR (SSA) → Hermes bytecode (HBC). ReuNify (TOSEM 2024) converts Hermes bytecode to Soot's Jimple IR for whole-program analysis of React Native apps — directly relevant if GFA wants to handle mobile JS targets.

### D. Vulnerability-detection-specific graphs

- **ODGen** (Li et al., USENIX'22) — abstract-interpretation-built Object Dependence Graphs; 180 zero-days, 70 CVEs.
- **DAPP** (Kim et al.) — pattern-based AST+CFG analysis for prototype pollution; lightweight, low precision/recall.
- **ObjLupAnsys** (Li et al., ESEC/FSE'21) — flow/context/branch-sensitive points-to for prototype-pollution sinks.
- **FAST** (Mingqing Kang, Yichao Xu, Song Li, Rigel Gjomemo, Jianwei Hou, V. N. Venkatakrishnan, Yinzhi Cao, "Scaling JavaScript Abstract Interpretation to Detect and Exploit Node.js Taint-style Vulnerability," IEEE S&P 2023) — scales abstract interpretation by analyzing only instructions with dependencies to the sink; "242 zero-day vulnerabilities in NPM with 21 CVE identifiers."
- **Graph.js + MDG** (Ferreira et al., PLDI'24) — 49 previously undiscovered npm vulnerabilities; outperforms ODGen on FN and time.
- **Explode.js + ECMA-Symb** (Marques et al., PLDI'25) — MDG + symbolic exploit generation; **first tool to synthesize multi-interaction exploit chains**; 44 zero-days, 4 CVEs, 100% precision on its dataset.
- **Silent Spring** (Shcherbakov et al., USENIX'23) — multi-label CodeQL queries + Node.js core gadget hunt; "11 universal gadgets in core Node.js APIs … 8 RCE vulnerabilities in three high-profile applications such as NPM CLI, Parse Server, and Rocket.Chat."
- **GHunter** (Cornelissen et al., USENIX'24) — dynamic V8 taint; 123 new gadgets across Node.js + Deno.
- **DAPP / Synode / Probe-the-Proto** (Cao group, NDSS'22) — client-side prototype pollution at 1M-website scale, 2917 zero-days.
- **AdCPG** (Lee & Son, CCS'23) — CPG for JS ad/tracker classification with explanations.

### E. Learned / embedding-based representations

- **code2vec / code2seq** — random AST paths as the basic unit; useful for code search, weak for taint sinks.
- **CodeBERT** — bimodal NL/PL transformer; AST-only.
- **GraphCodeBERT** — pre-trained with *data flow graphs*, not just AST; "GraphCodeBERT extends CodeBERT by incorporating code's data flow information into the training objective."
- **CuBERT, UniXcoder, CodeT5, StarCoder, Code Llama** — increasingly large code LMs; useful as the LLM half of a neuro-symbolic stack.
- **Devign** (NeurIPS'19) — Gated GNN over a joint AST+CFG+DFG+NCS graph (essentially a CPG) for graph-level vulnerability classification (C code).
- **ReGVD, VulCNN, LineVul, IVDetect, SySeVR, VulDeePecker** — successor models; all rely on some form of graph-of-code + GNN/Transformer. None is JS-specific, none has matched the CVE-finding throughput of ODGen/MDG/Explode.js in JS.
- **Vul-LMGNN** (2024) — explicitly combines pre-trained CodeBERT with Joern CPGs and a gated graph NN.
- **GNN-vuln-detection caveat**: Research evidence shows GNN-on-CPG models are pattern matchers, not reasoners. **Treat GNNs as a ranking layer over a real taint engine, not as a replacement.**

### F. Handling JavaScript dynamic features

| Feature | What goes wrong with plain AST | Best-known representation fix |
|---|---|---|
| **Prototype chain** | Property reads can resolve to inherited properties from `Object.prototype` | ODG/MDG: objects-as-nodes with `__proto__` edges |
| **Higher-order functions** | Callees unknown statically | k-CFA / m-CFA / type-tracking (CodeQL's `TypeTracker`) |
| **async/await, Promises** | Implicit continuations cross function boundaries | CodeQL models promises as taint-preserving wrappers; Semgrep IL desugars `await`; CPS transform for sound analyses |
| **Event loop / callbacks** | No syntactic edge between `setTimeout` and its callback | Custom flow steps (CodeQL `isAdditionalFlowStep`); event graph (Snyk) |
| **eval / Function()** | Arbitrary code at runtime | Bounded string analysis (TAJS); Synode (string constraints); concede unsoundness |
| **Modules** (ESM/CJS/AMD) | Cross-file flow lost | Module graph + symbol resolution (CodeQL `moduleImport`, SCIP, madge) |
| **Bundlers** (webpack/rollup/esbuild/vite) | Single mangled file, scope shaken | Unbundle with **webcrack** before analysis; reconstruct module boundaries |
| **Minification + obfuscation** | Identifier names lost; control-flow flattened; string arrays | **restringer** (rule-based, 40+ modules) + **humanify** (LLM identifier rename); JsDeObsBench benchmark for measuring fidelity |
| **Source maps** | Optional; often stripped in production | Use when present to re-link names; otherwise rely on deob |
| **TypeScript types** | Erased after compilation | Use TS Compiler API to retain symbol tables when source is TS |

### G. Industrial tools — what IR they use and what to copy

| Tool | Representation | Best feature to steal |
|---|---|---|
| **CodeQL** | Relational dataflow DB | Model-as-data YAML extensions; flow states; threat models |
| **Semgrep Pro** | Generic AST → IL | Pattern-friendly rule syntax; cross-file analysis |
| **Snyk Code** | AST + Event Graph | DeepCode AI Fix's *CodeReduce* (program slice → LLM) |
| **SonarQube / Veracode / Checkmarx / Fortify / Coverity** | Proprietary IRs around SSA + taint | Less innovative for JS specifically; not worth reverse-engineering |
| **Joern** | CPG in OverflowDB | Open CPG spec; Scala DSL; exportable to Neo4j |
| **NodeJSScan** | Semgrep rules + AST patterns | Quick rule pack baseline |

### H. Efficiency / scalability tradeoffs

- **AST construction**: O(n), milliseconds per file with SWC/OXC.
- **CFG/PDG**: O(n) to O(n²) intra-procedural; the constant matters.
- **Andersen points-to**: subcubic worst case; usually fine on single-package npm; explodes on bundled apps.
- **k-CFA**: EXPTIME for k≥1 in JS-like languages (Van Horn–Mairson, PLDI'10). Use 0-CFA + selective context, or m-CFA which is polynomial.
- **ODG**: scales poorly — Graph.js paper notes "scalability issues have been recently highlighted in ODGen … ODGen takes significantly longer to analyze prototype pollution vulnerabilities. This delay is primarily due to the considerable expansion in the size of its ODG."
- **MDG**: "only 0.14× the nodes and 0.42× the edges" of the ODG for the same package — practical for npm-scale work.
- **CodeQL database build**: minutes per repo; queries amortize.
- **Incremental analysis**: CPGs are amenable to per-function rebuild; CodeQL has incremental DB updates; Semgrep diff-aware scans only changed files.

### I. Hybrid / emerging approaches

- **Symbolic execution + MDG**: Explode.js's design — use the graph to find a *candidate flow*, then symbolically execute that slice to produce a working PoC. This is exactly the architecture GFA should aspire to.
- **Concolic execution**: Aratha, ExpoSE, Jalangi2 — runtime taint with constraint solving.
- **LLM-augmented taint spec mining**: IRIS, SemTaint, LATTE — let the LLM propose sources/sinks/summaries; let the static engine prove the path.
- **Retrieval-augmented program analysis**: ChromaDB-style RAG over CPG nodes/snippets — exactly what GFA already does; combining it with a graph store would let you retrieve *connected subgraphs* rather than disconnected text snippets.
- **Differentiable program analysis** (research-only): not yet practical.

### J. The npm supply-chain / malicious-package axis

This is a separate problem from vulnerability detection in a target codebase, but it lives in the same toolbox. Key tools/papers:
- **Amalfi** (GitHub, Ferreira et al.) — ML classifier + reproducibility checks + clone detection.
- **Cloudflare Page Shield MPGCN** — message-passing GCN over JS scripts: per Cloudflare's October 2025 engineering blog, "Everyday, Cloudflare Page Shield assesses 3.5 billion scripts per day or 40,000 scripts per second."
- **Ant Group OSCAR** (arXiv 2409.09356) — sandboxed dynamic analysis with API hook points; "identified 10,404 malicious NPM packages and 1,235 malicious PyPI packages."
- **Package-Inferno / npm-threat-emulation** (Splunk) — behavioral static analysis for Shai-Hulud-class supply-chain worms.
- **Taint-Based Code Slicing for LLMs** (arXiv 2512.12313) — taint slicing → LLM classification for malicious npm.

## Recommendations

GFA today: **Babel AST + call graph + inter-proc taint + multi-LLM + ChromaDB RAG + webcrack**. That's a solid mid-tier stack. Here is the staged path to make it state-of-the-art:

### Stage 1 — Immediate (weeks): Layer a CFG + intra-procedural DFG over the existing Babel AST.
- Use Babel's traversal to emit basic blocks + edges, then standard reaching-definitions for a per-function DFG.
- Why: every higher-precision feature below assumes this layer. Without it you are doing flow-insensitive taint, which is what loses you precision on async/promise chains and conditional sanitizers.
- **Threshold to move on**: when your false-positive rate on real Node.js packages exceeds ~30% or you start missing path-sensitive sanitizers.

### Stage 2 — Near-term (1–2 months): Adopt the MDG and run Cypher queries on Neo4j.
- Fork/integrate **Graph.js** (https://github.com/formalsec/graphjs) — it already emits CSV nodes/edges. Pipe its output into your own Neo4j or kùzu instance.
- Replicate its four built-in queries (CWE-22, 78, 94, 1321) and extend with your own for SSRF, deserialization, ReDoS, postMessage sinks, eval/Function sinks.
- This is the single best ROI move. You inherit the entire PLDI'24/PLDI'25 research line for free.
- **Threshold**: switch to writing custom Cypher when out-of-the-box CodeQL/Semgrep miss vulnerabilities you can describe as graph patterns.

### Stage 3 — Add CodeQL as a parallel engine, not a replacement.
- Run CodeQL on every target alongside your MDG pipeline. Use its `model-as-data` YAML extension to inject GFA-specific sources/sinks discovered by the LLM layer. CodeQL is the most mature JS taint library in existence and has years of hardening you cannot replicate.
- For obfuscation-resilience: CodeQL needs deobfuscated input — so feed it the **webcrack → restringer → humanify** pipeline output.

### Stage 4 — Replace "LLM confirmation loop" with neuro-symbolic taint-spec inference (IRIS / SemTaint pattern).
- Today your LLMs confirm a candidate finding. The better pattern (IRIS, ICLR'25; SemTaint, arXiv:2601.10865) is: let the LLM *propose* taint specs (sources, sinks, sanitizers, summaries) for unknown library APIs in the dependency tree, then materialize them as CodeQL/MDG facts and rerun the static engine.
- SemTaint reports "found 106 (65.43%) of the previously undetectable vulnerabilities" on CodeQL's blind spots. That is exactly the kind of recall delta GFA should be aiming for.
- **Threshold to move on**: track "LLM-proposed spec acceptance rate" — if your LLMs are right >70% of the time on spec inference, the loop pays for itself.

### Stage 5 — Add symbolic exploit synthesis (Explode.js pattern).
- Once you have an MDG flow, compile it to a Vulnerable Interaction Scheme (chain of API calls + arg types) and symbolically execute against the target with ECMA-Symb-like machinery (ExpoSE/Jalangi2 are the open-source primitives).
- Outcome: GFA emits *working PoCs*, not just findings. This is the bug-bounty differentiator — triage time on a finding with a PoC is an order of magnitude lower.

### Stage 6 — For client-side / DOM XSS / postMessage / client-side prototype pollution targets:
- Integrate DOM Invader–style dynamic gadget scanning (browser-runtime tainting) for client-side bundles. GHunter's lightweight V8 taint approach (USENIX'24) is a directly portable design.
- Use forced execution + dynamic taint (Steffens thesis, Saarland) for postMessage handlers; the resulting traces are far more accurate than static modeling of `window.addEventListener`.

### What NOT to do (with reasons)
- **Do not try to replicate TAJS/WALA/SAFE/JSAI-grade sound analysis.** They take person-years and still fail on jQuery. Trade soundness for scalability like every production tool does.
- **Do not build a GNN-only vulnerability classifier.** Devign-class models give graph-level "is vulnerable" verdicts that are useless for bug-bounty triage; you need *paths*, not labels. Use GNNs only as a *ranking* layer (à la Snyk's reachability) over real flows.
- **Do not store everything in one giant CPG and query it ad hoc.** Use *layered* graphs with clearly named edge types (AST, CFG, DDG, CG, MDG, MODULE) so that queries can target the right view. Joern's experience shows that mixed-edge graphs become unqueryable beyond toy size.
- **Do not skip the deobfuscation pipeline for bundled targets.** webcrack first, restringer second, humanify (or your own LLM rename pass) third — *then* parse and graph. Skipping this destroys recall on ~every modern web app.

### Quick-win integrations to try this quarter
1. **Graph.js / MDG** as a second analysis pass; merge findings with your AST-taint findings.
2. **CodeQL CLI** in CI for every package you analyze; ingest its SARIF into the same finding store.
3. **Sourcegraph SCIP indexer** (`scip-typescript`) to get cross-file symbol/reference edges as a call-graph backbone — cheaper than building a full call graph yourself.
4. **Joern's JS frontend** for cases where you want a single queryable CPG; export to Neo4j and co-query with your MDG.
5. **GHunter-style V8 taint** for any time you actually need to confirm a client-side gadget chain.
6. **Restringer + humanify** in front of every minified target before graph construction.

## Caveats

- **Soundness vs. scalability is a real trade.** Every tool listed above is intentionally unsound to scale. Expect false negatives. The only way to bound them is dynamic execution (ExpoSE/GHunter/Jalangi2) or symbolic execution on flow slices (Explode.js).
- **GNN-on-CPG numbers in research papers do not transfer.** They're trained on labeled C/C++ datasets (Devign, ReVeal, BigVul, DiverseVul). For JS, you would need to label your own dataset; expect 6–12 months of data work before you see the F1 numbers in those papers.
- **Joern's JavaScript frontend is materially weaker than its C/Java frontends** — its CPG spec acknowledges that callees may be unknown due to dynamic imports. Treat Joern-JS as a research substrate, not a production engine, until you have validated it on your own corpus.
- **CodeQL's JS analysis is excellent but proprietary and license-restricted** for commercial use of GitHub Advanced Security. If GFA is a commercial product, plan accordingly.
- **The 21.8% false-negative figure for malicious-JS detectors under obfuscation is not an original JsDeObsBench measurement** — it is quoted from Ren et al. (2023), "An Empirical Study on the Effects of Obfuscation on Static Machine Learning-Based Malicious JavaScript Detectors." Cite accordingly.
- **GHunter and Silent Spring metrics are reported on benchmarks that each side curated**, so the 0.43-vs-0.11 precision gap is real but should not be over-interpreted as universal superiority.
- **MDG/ODG/CPG are all flow- and context-sensitive at *function* granularity**; whole-program JavaScript analysis at the npm-monorepo scale (thousands of packages) is still an open research problem. Expect to operate per-package, not per-ecosystem.
- **Bundler artifacts shift faster than tools update.** webpack 5 module federation, Vite's ESM-first behavior, esbuild's tree-shaking aggressiveness, and Hermes's bytecode shipping all break a year-old deobfuscator. Budget for ongoing maintenance of the deob pipeline.
- **LLM-assisted spec inference is only as good as the LLM.** IRIS shows +28 detections with GPT-4 vs CodeQL alone, but the same architecture with weaker models produces worse-than-baseline noise. Your multi-LLM confirmation loop helps here — keep it.