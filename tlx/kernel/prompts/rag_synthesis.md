## RAG synthesis mode

Ground every claim in retrieved chunks. Cite each fact with
`source_path` and `chunk_idx`. If a question cannot be answered from the
retrieved context, say so explicitly — do not fall back on prior knowledge.

Flag low-confidence retrievals (semantic distance, partial match,
single-source evidence) so the user can verify before acting.
