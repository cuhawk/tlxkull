"""Generic identifier-pattern detector + mutation generator for IDOR sweeps.

Pure-Python, no I/O. Used by ``idor_sweep.py`` to:

1. Decide whether a request parameter / path segment / JSON-body field
   *looks like* an identifier (so the sweep should mutate it).
2. Classify the **shape** of an identifier value (int, uuid, hex, ulid,
   email, slug, base64, hashid, mongo objectid) so we can generate
   shape-respecting mutations instead of random fuzz.
3. Walk a captured HTTP request (URL + query + headers + body) and emit
   the list of (location, name, value, shape, score) candidates ranked
   by how likely they are to gate authorization.

Design notes:

- We do **not** maintain a per-target ID dictionary. Patterns are
  universal — the same shapes ('uuid', 'objectid', '+1 int') show up on
  every program. A per-target peer-id corpus is layered on top by the
  driver, not here.
- Confidence is a float 0..1. Threshold the driver applies is 0.3 —
  below that the candidate is dropped to avoid swap-the-pagination-cursor
  noise.
- Mutations are deterministic and side-effect-free. The driver is
  responsible for actually sending them through Caido.

The detector is a single source-of-truth for *what counts as an ID* —
both ``idor_sweep.py`` and ``auth_state.py`` (V2 §23) should consume it
rather than re-implement.
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlparse


__all__ = [
    "IdShape",
    "IdCandidate",
    "Mutation",
    "classify_value",
    "score_name",
    "extract_candidates",
    "enumerate_mutations",
]


# ---------------------------------------------------------------------------
# Name heuristics
# ---------------------------------------------------------------------------

# Strong-positive name patterns (case-insensitive, fragment match).
# Score 0.9.
_ID_NAME_STRONG = re.compile(
    r"(?:^|[_\W])"
    r"(?:id|uuid|guid|gid|sid|uid|tid|cid|pid|rid|nid|oid|fid"
    r"|user_?id|account_?id|owner_?id|customer_?id|tenant_?id"
    r"|org(?:anization)?_?id|workspace_?id|company_?id|team_?id"
    r"|project_?id|board_?id|channel_?id|room_?id|group_?id"
    r"|order_?id|invoice_?id|payment_?id|transaction_?id|tx_?id"
    r"|session_?id|token_?id|message_?id|msg_?id|thread_?id"
    r"|comment_?id|post_?id|article_?id|document_?id|doc_?id"
    r"|file_?id|asset_?id|attachment_?id|upload_?id|resource_?id"
    r"|record_?id|row_?id|entity_?id|object_?id|item_?id|node_?id)"
    r"(?:$|[_\W])",
    re.IGNORECASE,
)

# Medium-confidence (0.6): trailing/leading Id but generic word stem.
_ID_NAME_MEDIUM = re.compile(
    r"(?:^|[_\W])"
    r"(?:[A-Za-z][A-Za-z0-9]*_?(?:id|key|ref|slug|handle|number|no))"
    r"(?:$|[_\W])",
    re.IGNORECASE,
)

# Weak (0.4): email / username / phone — auth-relevant but indirect.
_ID_NAME_WEAK = re.compile(
    r"(?:^|[_\W])"
    r"(?:email|e_?mail|user(?:name)?|login|account|phone|mobile|"
    r"member|owner|customer|tenant|workspace|company)"
    r"(?:$|[_\W])",
    re.IGNORECASE,
)

# Things that look ID-shaped but are NOT auth identifiers — pagination,
# enum keys, common settings. Hard-zero these regardless of name match.
_NAME_BLOCKLIST = re.compile(
    r"^(?:"
    r"page|page_?size|per_?page|limit|offset|cursor|after|before"
    r"|sort|order|order_?by|asc|desc|direction|dir"
    r"|q|query|search|filter|select|fields|include|exclude|expand"
    r"|lang|locale|timezone|tz|format|version|v|api_?version"
    r"|callback|jsonp|tab|view|mode|status|state|kind|type"
    r"|count|total|max|min|first|last|skip|take"
    r"|debug|verbose|trace|nocache|nocache_?bust|_|__"
    r")$",
    re.IGNORECASE,
)


def score_name(name: str) -> float:
    """Return 0..1 confidence that ``name`` denotes an identifier."""
    if not name:
        return 0.0
    n = name.strip()
    if _NAME_BLOCKLIST.match(n):
        return 0.0
    if _ID_NAME_STRONG.search(n):
        return 0.9
    if _ID_NAME_MEDIUM.search(n):
        return 0.6
    if _ID_NAME_WEAK.search(n):
        return 0.4
    return 0.0


# ---------------------------------------------------------------------------
# Value-shape classifier
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IdShape:
    name: str        # 'int' | 'uuid' | 'objectid' | 'hex' | 'ulid'
                     # | 'email' | 'slug' | 'b64' | 'jwt' | 'hashid' | 'unknown'
    confidence: float
    extra: dict[str, Any] = field(default_factory=dict)


_INT_RE = re.compile(r"^-?\d{1,18}$")
_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_OBJECTID_RE = re.compile(r"^[0-9a-fA-F]{24}$")
_HEX_RE = re.compile(r"^[0-9a-fA-F]{16,128}$")
_ULID_RE = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")  # Crockford base32, 26 chars
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){1,8}$")
_JWT_RE = re.compile(
    r"^[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}$"
)
_B64_RE = re.compile(r"^[A-Za-z0-9+/=_-]{16,512}$")
_HASHID_RE = re.compile(r"^[A-Za-z0-9]{6,32}$")  # hashids/sqids/youtube-style


def classify_value(value: Any) -> IdShape:
    """Return the most specific identifier shape for ``value``.

    Ints win over hashids; UUID/ObjectId/ULID win over generic hex.
    """
    if value is None:
        return IdShape("unknown", 0.0)
    if isinstance(value, bool):
        return IdShape("unknown", 0.0)
    if isinstance(value, int):
        return IdShape("int", 0.95, {"int_value": value})
    if not isinstance(value, str):
        return IdShape("unknown", 0.0)
    s = value.strip()
    if not s:
        return IdShape("unknown", 0.0)

    if _INT_RE.match(s):
        try:
            return IdShape("int", 0.95, {"int_value": int(s)})
        except ValueError:
            pass
    if _UUID_RE.match(s):
        try:
            uuid.UUID(s)
            return IdShape("uuid", 0.99)
        except ValueError:
            pass
    if _JWT_RE.match(s) and s.count(".") == 2:
        return IdShape("jwt", 0.95)
    if _ULID_RE.match(s):
        return IdShape("ulid", 0.9)
    if _OBJECTID_RE.match(s):
        return IdShape("objectid", 0.9)
    if _EMAIL_RE.match(s):
        return IdShape("email", 0.95)
    if _HEX_RE.match(s):
        return IdShape("hex", 0.7, {"length": len(s)})
    if _SLUG_RE.match(s):
        return IdShape("slug", 0.55)
    if _B64_RE.match(s) and len(s) >= 20:
        return IdShape("b64", 0.5, {"length": len(s)})
    if _HASHID_RE.match(s):
        return IdShape("hashid", 0.45, {"length": len(s)})
    return IdShape("unknown", 0.0)


# ---------------------------------------------------------------------------
# Candidate extraction from an HTTP request
# ---------------------------------------------------------------------------

@dataclass
class IdCandidate:
    location: str       # 'path' | 'query' | 'header' | 'body.json' | 'body.form'
    name: str           # parameter name OR path-segment index 'seg[3]'
    value: Any
    shape: IdShape
    name_score: float
    pointer: str        # JSONPath-style locator, e.g. '$.query.userId' or '$.path[3]'

    @property
    def score(self) -> float:
        """Combined confidence — geometric mean of name + shape."""
        return (self.name_score * self.shape.confidence) ** 0.5


# Headers that *carry* identifiers (rather than meta). Lower-cased.
_AUTH_RELEVANT_HEADERS = {
    "x-user-id", "x-account-id", "x-tenant-id", "x-org-id",
    "x-workspace-id", "x-company-id", "x-customer-id",
    "x-impersonate", "x-on-behalf-of", "x-as-user",
    "x-actor-id", "x-owner-id", "x-resource-id",
}


def _walk_json(obj: Any, prefix: str = "$"):
    """Yield (json-pointer, key-name, value) for every leaf in a JSON tree."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_prefix = f"{prefix}.{k}"
            if isinstance(v, (dict, list)):
                yield from _walk_json(v, new_prefix)
            else:
                yield new_prefix, str(k), v
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_prefix = f"{prefix}[{i}]"
            if isinstance(v, (dict, list)):
                yield from _walk_json(v, new_prefix)
            else:
                # Lists of scalars get the parent key as the name —
                # we don't know what the array slot represents.
                yield new_prefix, prefix.rsplit(".", 1)[-1], v


def _parse_body(headers: dict, body: Any) -> tuple[str, Any]:
    """Return (kind, parsed) for the request body. kind ∈ {json,form,raw,none}."""
    if body in (None, "", b""):
        return "none", None
    ctype = ""
    for k, v in (headers or {}).items():
        if k.lower() == "content-type":
            ctype = (v or "").lower()
            break
    if isinstance(body, (dict, list)):
        return "json", body
    if isinstance(body, bytes):
        try:
            body = body.decode("utf-8", errors="replace")
        except Exception:
            return "raw", body
    if not isinstance(body, str):
        return "raw", body
    if "application/json" in ctype or (
        body and body.lstrip()[:1] in "{["
    ):
        try:
            return "json", json.loads(body)
        except (ValueError, TypeError):
            return "raw", body
    if "x-www-form-urlencoded" in ctype or ("=" in body and "{" not in body):
        try:
            return "form", dict(parse_qsl(body, keep_blank_values=True))
        except Exception:
            return "raw", body
    return "raw", body


def extract_candidates(req: dict) -> list[IdCandidate]:
    """Walk an HTTP request dict and return ranked ID candidates.

    ``req`` shape (matches caido_get_request output):
        {
          "method": "GET",
          "url":    "https://api.x.com/v1/users/42/orders?status=open&order_id=99",
          "headers": {"Cookie": "...", "X-User-Id": "42", ...},
          "body":   "..."   (str | bytes | dict | None)
        }
    """
    out: list[IdCandidate] = []

    # --- URL path segments
    parsed = urlparse(req.get("url", ""))
    segs = [s for s in parsed.path.split("/") if s]
    for i, seg in enumerate(segs):
        shape = classify_value(seg)
        if shape.confidence < 0.3:
            continue
        # Path segments rarely have a "name" — use prev segment as the
        # name hint (e.g. /users/42 → name="users").
        hint = segs[i - 1] if i > 0 else ""
        name_score = max(score_name(hint + "_id"), 0.5)  # path-position prior
        out.append(IdCandidate(
            location="path",
            name=hint or f"seg{i}",
            value=seg,
            shape=shape,
            name_score=name_score,
            pointer=f"$.path[{i}]",
        ))

    # --- Query string
    for k, v in parse_qsl(parsed.query, keep_blank_values=True):
        ns = score_name(k)
        if ns < 0.3:
            continue
        shape = classify_value(v)
        if shape.confidence < 0.3:
            continue
        out.append(IdCandidate(
            location="query",
            name=k,
            value=v,
            shape=shape,
            name_score=ns,
            pointer=f"$.query.{k}",
        ))

    # --- Headers
    for k, v in (req.get("headers") or {}).items():
        low = k.lower()
        ns = 0.9 if low in _AUTH_RELEVANT_HEADERS else score_name(k)
        if ns < 0.3:
            continue
        shape = classify_value(v)
        if shape.confidence < 0.3:
            continue
        out.append(IdCandidate(
            location="header",
            name=k,
            value=v,
            shape=shape,
            name_score=ns,
            pointer=f"$.headers.{k}",
        ))

    # --- Body
    kind, parsed_body = _parse_body(req.get("headers") or {}, req.get("body"))
    if kind == "json":
        for ptr, name, val in _walk_json(parsed_body, "$.body"):
            ns = score_name(name)
            if ns < 0.3:
                continue
            shape = classify_value(val)
            if shape.confidence < 0.3:
                continue
            out.append(IdCandidate(
                location="body.json",
                name=name,
                value=val,
                shape=shape,
                name_score=ns,
                pointer=ptr,
            ))
    elif kind == "form" and isinstance(parsed_body, dict):
        for name, val in parsed_body.items():
            ns = score_name(name)
            if ns < 0.3:
                continue
            shape = classify_value(val)
            if shape.confidence < 0.3:
                continue
            out.append(IdCandidate(
                location="body.form",
                name=name,
                value=val,
                shape=shape,
                name_score=ns,
                pointer=f"$.body.{name}",
            ))

    out.sort(key=lambda c: c.score, reverse=True)
    return out


# ---------------------------------------------------------------------------
# Mutation generator
# ---------------------------------------------------------------------------

@dataclass
class Mutation:
    name: str          # human label, e.g. 'plus_one', 'swap_uuid', 'empty'
    value: Any
    rationale: str     # why we expect this to surface a bug


def enumerate_mutations(
    cand: IdCandidate,
    peer_values: Iterable[Any] = (),
) -> list[Mutation]:
    """Generate shape-respecting mutations for one ID candidate.

    ``peer_values`` are identifiers known to belong to another
    authenticated user (the most signal-rich mutation). The driver
    sources these from a per-target ``peer_ids.json`` if available.
    """
    muts: list[Mutation] = []
    shape = cand.shape

    # Universal mutations — work against any shape.
    muts.append(Mutation("empty", "", "drop the id and see if the route still resolves"))
    muts.append(Mutation("null_literal", None, "JSON null may bypass equality checks"))
    muts.append(Mutation("array_wrap", [cand.value], "MongoDB / Mongoose $in array confusion"))
    muts.append(Mutation("wildcard", "*", "literal-asterisk LIKE / regex injection"))

    # Peer values — the cleanest IDOR test.
    seen_peers = set()
    for pv in peer_values:
        if pv == cand.value or pv in seen_peers:
            continue
        seen_peers.add(pv)
        muts.append(Mutation(
            f"peer_value:{str(pv)[:32]}", pv,
            "swap to a known peer-user identifier",
        ))

    # Shape-specific.
    if shape.name == "int":
        n = shape.extra.get("int_value")
        if n is not None:
            for delta in (-1, 1, 2, -2):
                muts.append(Mutation(
                    f"int_delta_{delta:+d}", n + delta,
                    f"sequential id ± {abs(delta)}",
                ))
            muts.append(Mutation("int_zero", 0, "boundary: 0 sometimes maps to system row"))
            muts.append(Mutation(
                "int_max", 2_147_483_647,
                "32-bit int max — overflow on legacy backends",
            ))
            muts.append(Mutation(
                "int_negative_one", -1,
                "-1 sometimes treated as 'no filter' (admin scope)",
            ))
    elif shape.name == "uuid":
        muts.append(Mutation(
            "uuid_nil", "00000000-0000-0000-0000-000000000000",
            "nil UUID may match unset-owner rows",
        ))
        muts.append(Mutation(
            "uuid_random", str(uuid.UUID(int=0xDEADBEEFCAFEBABE0123456789ABCDEF)),
            "deterministic random UUID — should 404 if scoped",
        ))
        # Bit-flip last char to test loose validation.
        last = cand.value[-1] if isinstance(cand.value, str) else ""
        if last:
            flipped = "0" if last != "0" else "1"
            muts.append(Mutation(
                "uuid_bitflip_last", cand.value[:-1] + flipped,
                "off-by-one char — should 404, 200 = relaxed validation",
            ))
    elif shape.name == "objectid":
        muts.append(Mutation(
            "objectid_zero", "000000000000000000000000",
            "all-zero ObjectId — may match unset-owner rows",
        ))
        muts.append(Mutation(
            "objectid_increment", _shift_hex(cand.value, +1),
            "increment trailing hex — adjacent mongo doc",
        ))
    elif shape.name == "email":
        muts.append(Mutation(
            "email_admin", "admin@" + cand.value.split("@", 1)[-1],
            "guess sibling admin@ account in same tenant",
        ))
        muts.append(Mutation(
            "email_plus_tag", _email_plus_tag(cand.value),
            "+tag aliasing sometimes bypasses uniqueness checks",
        ))
    elif shape.name in ("hex", "hashid", "ulid", "b64"):
        # Generic increment-last-char mutation.
        muts.append(Mutation(
            "shift_last_char", _shift_last_char(str(cand.value)),
            "off-by-one neighbour id — same encoding, sibling record",
        ))
    elif shape.name == "slug":
        muts.append(Mutation("slug_admin", "admin", "guess admin/root slug"))
        muts.append(Mutation("slug_root", "root", "guess admin/root slug"))

    # Type-confusion: send int as string (and vice versa).
    if shape.name == "int":
        muts.append(Mutation(
            "type_confusion_str", str(cand.value),
            "stringify int — some ORMs parse loosely",
        ))
    elif shape.name in ("uuid", "objectid", "hashid", "hex"):
        muts.append(Mutation(
            "type_confusion_int", 1,
            "send int 1 — some routers fall back to default record",
        ))

    return muts


def _shift_hex(s: str, delta: int) -> str:
    if not s:
        return s
    try:
        n = int(s, 16)
        bumped = (n + delta) & ((1 << (len(s) * 4)) - 1)
        return f"{bumped:0{len(s)}x}"
    except ValueError:
        return s


def _shift_last_char(s: str) -> str:
    if not s:
        return s
    last = s[-1]
    if last.isdigit():
        return s[:-1] + str((int(last) + 1) % 10)
    if last.isalpha():
        nxt = chr(((ord(last.lower()) - ord("a") + 1) % 26) + ord("a"))
        return s[:-1] + (nxt.upper() if last.isupper() else nxt)
    return s[:-1] + "0"


def _email_plus_tag(s: str) -> str:
    if "@" not in s:
        return s
    local, domain = s.split("@", 1)
    return f"{local}+idor@{domain}"
