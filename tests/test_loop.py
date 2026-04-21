"""Smoke test: the loop runs end-to-end in mock mode on the sample trace."""

from pathlib import Path

from blueprints.calibrate_qpu import run_loop
from blueprints.ising_client import IsingClient
from blueprints.trinity_adapter import TrinityAdapter


SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_qpu_trace.json"


def test_loop_converges_in_mock_mode():
    result = run_loop(
        SAMPLE,
        ising=IsingClient(mock=True),
        trinity=TrinityAdapter(),
        max_iterations=5,
    )
    assert result.iterations, "loop ran at least one iteration"
    assert result.converged, "mock loop converges within the iteration cap"


def test_first_finding_is_structured():
    result = run_loop(SAMPLE, ising=IsingClient(mock=True), max_iterations=1)
    f = result.iterations[0].finding
    assert f.experiment_type
    assert 0.0 <= f.confidence <= 1.0
    assert f.recommended_action
