"""String abstract domain — three-level lattice for property keys.

Plan: plans/ARCHITECTURE_EVOLUTION.md §2.2 step 2.

Three lattice levels:

  Top       — any string. The bottom of usefulness; collapses every
              constraint.
  Const(s)  — a single concrete string.
  Set({s1, s2, ...})
            — bounded set of concrete strings. Cap = 16.

The implementation lives in pure Python — no AST dependency — so the
ast_extractor.js side can emit raw "string events" (assignments,
concatenations) and this module reduces them to a fact.

Public API:

  v = StringLattice.top()
  v = StringLattice.const("foo")
  v = StringLattice.set({"a", "b"})

  v3 = StringLattice.join(v1, v2)           # join two lattice points
  v3 = StringLattice.concat(v1, v2)         # string concatenation

  v.contains("foo")                          # for `obj[v]` resolution
  list(v.iter_values())                      # at most 16 values

  ev = StringLattice.evaluate(expr, env)     # evaluate a tiny expr-tree
                                              # against a {var: lattice} env
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


__all__ = ["StringLattice", "StringFact", "MAX_SET"]


MAX_SET = 16


@dataclass(frozen=True)
class StringLattice:
    level: str                                # "top" | "const" | "set"
    value: str | None = None                  # populated when level == "const"
    members: frozenset[str] = frozenset()     # populated when level == "set"

    # ── Constructors ──────────────────────────────────────────────────

    @classmethod
    def top(cls) -> "StringLattice":
        return cls(level="top")

    @classmethod
    def const(cls, s: str) -> "StringLattice":
        return cls(level="const", value=s)

    @classmethod
    def set(cls, members: set[str] | frozenset[str]) -> "StringLattice":
        m = frozenset(members)
        if not m:
            return cls.top()
        if len(m) == 1:
            return cls.const(next(iter(m)))
        if len(m) > MAX_SET:
            return cls.top()
        return cls(level="set", members=m)

    # ── Queries ───────────────────────────────────────────────────────

    @property
    def is_top(self) -> bool:
        return self.level == "top"

    @property
    def is_const(self) -> bool:
        return self.level == "const"

    @property
    def is_set(self) -> bool:
        return self.level == "set"

    def contains(self, s: str) -> bool:
        if self.level == "top":
            return True
        if self.level == "const":
            return self.value == s
        return s in self.members

    def iter_values(self) -> Iterator[str]:
        if self.level == "top":
            return iter(())
        if self.level == "const":
            return iter((self.value,))
        return iter(sorted(self.members))

    # ── Operations ────────────────────────────────────────────────────

    @classmethod
    def join(cls, a: "StringLattice", b: "StringLattice") -> "StringLattice":
        if a.is_top or b.is_top:
            return cls.top()
        if a.is_const and b.is_const:
            if a.value == b.value:
                return a
            return cls.set({a.value, b.value})  # type: ignore[arg-type]
        # Otherwise both yield finite sets; union them.
        union: set[str] = set()
        for v in a.iter_values():
            union.add(v)
        for v in b.iter_values():
            union.add(v)
        return cls.set(union)

    @classmethod
    def concat(cls, a: "StringLattice", b: "StringLattice") -> "StringLattice":
        if a.is_top or b.is_top:
            return cls.top()
        # Cartesian product, bounded by MAX_SET.
        product: set[str] = set()
        for av in a.iter_values():
            for bv in b.iter_values():
                product.add(av + bv)
                if len(product) > MAX_SET:
                    return cls.top()
        return cls.set(product)

    # ── Evaluate a tiny expression tree ───────────────────────────────

    @classmethod
    def evaluate(cls, expr: dict, env: dict[str, "StringLattice"]) -> "StringLattice":
        """Walk a JSON-shaped expression node.

        expr forms supported (matches what the AST extractor emits in
        the string-lattice phase):

          {"kind": "literal", "value": "foo"}
          {"kind": "ident", "name": "x"}
          {"kind": "concat", "args": [<expr>, <expr>, ...]}
          {"kind": "template", "quasis": ["a", "b"], "exprs": [<expr>]}
          {"kind": "call", "callee": "String", "arg": <expr>}
          {"kind": "ternary", "cons": <expr>, "alt": <expr>}
          {"kind": "unknown"}    # any other shape; degrades to top
        """
        kind = expr.get("kind", "unknown")
        if kind == "literal":
            v = expr.get("value")
            return cls.const(str(v)) if isinstance(v, str) else cls.top()
        if kind == "ident":
            return env.get(expr.get("name", ""), cls.top())
        if kind == "concat":
            args = expr.get("args") or []
            if not args:
                return cls.top()
            acc = cls.evaluate(args[0], env)
            for sub in args[1:]:
                acc = cls.concat(acc, cls.evaluate(sub, env))
            return acc
        if kind == "template":
            quasis = expr.get("quasis") or []
            exprs = expr.get("exprs") or []
            acc = cls.const(quasis[0] if quasis else "")
            for i, sub in enumerate(exprs):
                acc = cls.concat(acc, cls.evaluate(sub, env))
                next_q = quasis[i + 1] if i + 1 < len(quasis) else ""
                acc = cls.concat(acc, cls.const(next_q))
            return acc
        if kind == "call" and expr.get("callee") in ("String",):
            return cls.evaluate(expr.get("arg") or {}, env)
        if kind == "ternary":
            return cls.join(
                cls.evaluate(expr.get("cons") or {}, env),
                cls.evaluate(expr.get("alt") or {}, env),
            )
        return cls.top()


@dataclass
class StringFact:
    node_id: int
    var_name: str
    lattice: StringLattice
    line: int | None = None

    def serialize_values(self) -> str | None:
        if self.lattice.is_top:
            return None
        import json
        return json.dumps(sorted(self.lattice.iter_values()))
