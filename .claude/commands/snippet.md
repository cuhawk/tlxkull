---
description: Fetch source for a function by qualified name from the indexed target. Usage: /snippet <qname>.
argument-hint: "<qname>"
---

# /snippet

Quick wrapper over `js_get_snippet`:

1. Read current target from `memory.md`.
2. Call `js_get_snippet(qname="$ARGUMENTS")` on that target.
3. Print the result with a triple-fenced ```js block.
4. If the qname isn't found, list the 5 most similar qnames from
   `targets/<current>/index/nodes.jsonl`.
