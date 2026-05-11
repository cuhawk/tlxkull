## Static analysis mode

Trace data flow from source to sink. Identify entry points first
(handlers, public APIs, CLI args, deserialization boundaries). Note all
external input handling — flag tainted variables explicitly.

For each dangerous pattern surfaced, cite `file_path:line_number` and the
exact construct. Distinguish:
- direct sinks (eval, exec, shell, raw SQL, deserialize)
- indirect sinks (template render, ORM raw, reflection)
- guards present and whether they actually constrain the taint

Prefer concrete edges over generalities. Do not speculate about behavior
that cannot be confirmed in the code under review.

## Large file RAG workflow

When analyzing a file larger than ~500 lines or ~20KB:
1. Call `docs_ingest` (single file) or `docs_ingest_dir` (directory of files) first.
2. Use `docs_query` with targeted questions rather than reading the whole file.
3. Follow each query with concrete findings — never summarize without evidence.

For JS/TS app analysis: ingest the entire JS directory first, then query for
specific patterns (sinks, sources, dangerous imports, eval usage).

For HTML outputs from crawler/playwright: ingest the output directory,
then query for specific elements (forms, scripts, CSP headers, inline event handlers).

For large prompt files passed via path: ingest the file, then query section by section.
Do not attempt to read a >500-line file directly into context.
