import pytest
from recon_mcp.tools import (
    ReconStartIn, ReconStatusIn, ReconResultsIn, ReconCancelIn,
)


def test_start_input_defaults():
    inp = ReconStartIn(targets=["1.2.3.4"], target_name="acme")
    assert inp.scan_region == "nyc1"
    assert inp.probe_regions == []
    assert inp.max_droplets == 10


def test_start_input_multi_region():
    inp = ReconStartIn(targets=["*.x.com"], target_name="x", probe_regions=["nyc1", "fra1"])
    assert inp.probe_regions == ["nyc1", "fra1"]


def test_start_input_rejects_unknown_field():
    with pytest.raises(Exception):
        ReconStartIn(targets=["x"], target_name="t", banana=1)


def test_status_in_requires_job_id():
    with pytest.raises(Exception):
        ReconStatusIn()


def test_cancel_in_requires_job_id():
    with pytest.raises(Exception):
        ReconCancelIn()
