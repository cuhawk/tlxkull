import pytest
from recon_mcp.regions import (
    REGIONS, validate_regions, default_probe_set, country_for, RegionError,
)


def test_known_regions_have_country():
    assert country_for("nyc1") == "US"
    assert country_for("fra1") == "DE"
    assert country_for("sgp1") == "SG"


def test_unknown_region_raises():
    with pytest.raises(RegionError, match="unknown"):
        country_for("mars1")


def test_validate_filters_unknown():
    with pytest.raises(RegionError, match="mars1"):
        validate_regions(["nyc1", "mars1"])


def test_validate_dedupes_and_orders():
    assert validate_regions(["nyc1", "nyc1", "fra1"]) == ["nyc1", "fra1"]


def test_default_probe_set_is_diverse():
    s = default_probe_set()
    countries = {country_for(r) for r in s}
    assert len(countries) >= 4
    assert "US" in countries
