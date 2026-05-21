import { describe, it, expect } from "vitest";
import {
  scoreEndpoint,
  inAllowlist,
  isDestructiveNumericIdPath
} from "../../src/modules/race/candidate";
import type { Endpoint, HttpMessage } from "../../src/types";

const KEYWORDS = ["apply", "coupon", "transfer", "redeem", "vote"];

function ep(over: Partial<Endpoint> = {}): Endpoint {
  return {
    id: "e1",
    method: "POST",
    host: "x.test",
    path: "/apply-coupon",
    query: {},
    caido_request_id: "r1",
    ...over
  };
}

function msg(headers: Record<string, string> = {}): HttpMessage {
  return { headers, body: "" };
}

describe("scoreEndpoint", () => {
  it("scores auth-bound mutating POST against keyword path", () => {
    const result = scoreEndpoint(
      ep({ method: "POST", path: "/account/apply-coupon" }),
      msg({ Cookie: "session=abc" }),
      KEYWORDS
    );
    expect(result.score).toBeGreaterThanOrEqual(3);
    expect(result.mutating).toBe(true);
    expect(result.reasons.join(",")).toContain("keyword:");
    expect(result.reasons.join(",")).toContain("auth:");
    expect(result.reasons.join(",")).toContain("verb:POST");
    expect(result.reasons.join(",")).toContain("no-idempotency-key");
  });

  it("drops idempotency-key bonus when header present", () => {
    const r = scoreEndpoint(
      ep({ method: "POST", path: "/transfer" }),
      msg({ Cookie: "s=1", "Idempotency-Key": "uuid" }),
      KEYWORDS
    );
    expect(r.reasons).not.toContain("no-idempotency-key");
  });

  it("rewards sensitive GET query params", () => {
    const r = scoreEndpoint(
      ep({ method: "GET", path: "/v/redeem", query: { token: "abc" } }),
      msg({ Authorization: "Bearer x" }),
      KEYWORDS
    );
    expect(r.score).toBeGreaterThanOrEqual(2);
    expect(r.mutating).toBe(false);
    expect(r.reasons.join(",")).toContain("query:token");
  });

  it("returns 0 on irrelevant unauthenticated GET", () => {
    const r = scoreEndpoint(
      ep({ method: "GET", path: "/static/logo.svg", query: {} }),
      msg({}),
      KEYWORDS
    );
    expect(r.score).toBe(0);
    expect(r.mutating).toBe(false);
  });
});

describe("inAllowlist", () => {
  it("matches case-insensitive method + exact path", () => {
    expect(
      inAllowlist(ep({ method: "post", path: "/apply" }), [{ method: "POST", path: "/apply" }])
    ).toBe(true);
    expect(
      inAllowlist(ep({ method: "POST", path: "/apply" }), [{ method: "POST", path: "/applyx" }])
    ).toBe(false);
  });
});

describe("isDestructiveNumericIdPath", () => {
  it("flags DELETE on /api/users/42", () => {
    expect(isDestructiveNumericIdPath(ep({ method: "DELETE", path: "/api/users/42" }))).toBe(true);
  });
  it("does not flag DELETE on /api/users", () => {
    expect(isDestructiveNumericIdPath(ep({ method: "DELETE", path: "/api/users" }))).toBe(false);
  });
  it("does not flag POST on /api/users/42", () => {
    expect(isDestructiveNumericIdPath(ep({ method: "POST", path: "/api/users/42" }))).toBe(false);
  });
});
