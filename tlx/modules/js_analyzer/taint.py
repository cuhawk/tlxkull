"""Intra-procedural taint solver.

Given list of taint_facts (variable assignments, source reads, sink uses),
returns confirmed source→sink flows within that function.

Algorithm: line-ordered worklist on per-variable label sets. Conservative —
no control-flow precision (if/else, loops are union).

Property-level taint:
    Variable names may be static dotted paths emitted by ast_extractor.js
    (e.g. "req.body.user", "this.cfg.secret"). The solver treats these as
    opaque distinct names — taint on "req.body.user" is independent of
    taint on "req.body" or "req". This gives per-property precision when
    the source code uses static member access; computed indexes
    (req[x]) and aliasing (const b = req.body) still collapse to the
    base identifier.
"""


def solve_function_taint(taint_facts: list[dict]) -> list[dict]:
    """Return list of confirmed flows.

    Each flow:
      {
        "source_rule": str,
        "source_line": int,
        "sink_rule": str,
        "sink_line": int,
        "via_vars": [str],
        "sanitised_by": str | None,
        "sanitiser_clears": list,
      }
    """
    tainted: dict[str, set[str]] = {}
    sanitised: dict[str, set[str]] = {}
    source_lines: dict[tuple[str, str], int] = {}
    flows: list[dict] = []

    facts = sorted(taint_facts, key=lambda f: f.get("line", 0))

    for fact in facts:
        kind = fact.get("kind")

        if kind == "source_arg":
            # Pre-taint: a function argument passed directly into an SSRF sink
            # (fetch/axios) is treated as already-tainted from the start of the
            # function. Lets the solver flag `function f(url) { fetch(url) }`
            # without needing an in-function source assignment.
            name = fact.get("var")
            rule_id = fact.get("rule_id")
            line = fact.get("line", 0)
            if name and rule_id:
                tainted.setdefault(name, set()).add(rule_id)
                sanitised.setdefault(name, set())
                if (name, rule_id) not in source_lines:
                    source_lines[(name, rule_id)] = line
            continue

        if kind == "var_init":
            name = fact.get("name")
            source = fact.get("source")
            line = fact.get("line", 0)
            if source and name:
                tainted[name] = {source}
                sanitised[name] = set()
                source_lines[(name, source)] = line

        elif kind == "var_assign":
            name = fact.get("name")
            if not name:
                continue
            source = fact.get("source")
            sanitiser = fact.get("sanitiser")
            arg_vars = fact.get("arg_vars") or []
            line = fact.get("line", 0)

            if source:
                tainted[name] = {source}
                sanitised[name] = set()
                source_lines[(name, source)] = line
            elif arg_vars:
                new_taint: set[str] = set()
                new_san: set[str] = set()
                for v in arg_vars:
                    new_taint |= tainted.get(v, set())
                    new_san |= sanitised.get(v, set())
                    for s in tainted.get(v, set()):
                        if (name, s) not in source_lines:
                            src_line = source_lines.get((v, s), line)
                            source_lines[(name, s)] = src_line
                tainted[name] = new_taint
                sanitised[name] = new_san
            else:
                tainted[name] = set()
                sanitised[name] = set()

            if sanitiser:
                sanitised[name] = sanitised.get(name, set()) | {sanitiser}

        elif kind == "sanitiser_use":
            target_var = fact.get("target_var")
            taxonomy_id = fact.get("taxonomy_id")
            arg_vars = fact.get("arg_vars") or []
            line = fact.get("line", 0)

            if not target_var:
                continue

            new_taint = set()
            new_san = set()
            for v in arg_vars:
                new_taint |= tainted.get(v, set())
                new_san |= sanitised.get(v, set())
                for s in tainted.get(v, set()):
                    if (target_var, s) not in source_lines:
                        src_line = source_lines.get((v, s), line)
                        source_lines[(target_var, s)] = src_line
            tainted[target_var] = new_taint
            sanitised[target_var] = new_san
            if taxonomy_id:
                sanitised[target_var] |= {taxonomy_id}

        elif kind == "sink_use":
            sink_rule = fact.get("rule_id")
            sink_line = fact.get("line", 0)
            arg_vars = fact.get("arg_vars") or []

            seen_sources: set[tuple[str, str]] = set()
            for v in arg_vars:
                for source_rule in tainted.get(v, set()):
                    key = (source_rule, v)
                    if key in seen_sources:
                        continue
                    seen_sources.add(key)
                    san_set = sanitised.get(v, set())
                    flows.append({
                        "source_rule": source_rule,
                        "source_line": source_lines.get((v, source_rule), 0),
                        "sink_rule": sink_rule,
                        "sink_line": sink_line,
                        "via_vars": [v],
                        "sanitised_by": sorted(san_set)[0] if san_set else None,
                        "sanitiser_clears": [],
                    })

    return flows
