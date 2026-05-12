"""DigitalOcean region metadata."""
from __future__ import annotations


class RegionError(Exception):
    pass


REGIONS: dict[str, dict[str, str]] = {
    "nyc1": {"country": "US", "city": "New York"},
    "nyc3": {"country": "US", "city": "New York"},
    "sfo3": {"country": "US", "city": "San Francisco"},
    "tor1": {"country": "CA", "city": "Toronto"},
    "lon1": {"country": "GB", "city": "London"},
    "ams3": {"country": "NL", "city": "Amsterdam"},
    "fra1": {"country": "DE", "city": "Frankfurt"},
    "sgp1": {"country": "SG", "city": "Singapore"},
    "blr1": {"country": "IN", "city": "Bangalore"},
    "syd1": {"country": "AU", "city": "Sydney"},
}


def country_for(slug: str) -> str:
    try:
        return REGIONS[slug]["country"]
    except KeyError as e:
        raise RegionError(f"unknown region: {slug!r}") from e


def validate_regions(slugs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    bad: list[str] = []
    for s in slugs:
        if s not in REGIONS:
            bad.append(s)
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    if bad:
        raise RegionError(f"unknown region(s): {bad}")
    return out


def default_probe_set() -> list[str]:
    return ["nyc1", "fra1", "sgp1", "syd1"]
