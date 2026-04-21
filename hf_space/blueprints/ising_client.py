"""
Ising Calibration client.

Thin client for NVIDIA's Ising-Calibration-1 vision-language model. Supports
two modes:

  - Mock: no credentials needed, returns a canned-but-structurally-realistic
    response. Use this for demos, CI, and offline development.
  - Live: posts to the NVIDIA Build / NIM endpoint exposing Ising Calibration.
    Requires NVIDIA_API_KEY.

The canonical Ising Calibration model card lives on Hugging Face and the
managed endpoint lives at build.nvidia.com. See:
  https://developer.nvidia.com/blog/nvidia-ising-accelerates-useful-quantum-computing/
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import httpx


NIM_BASE_URL_DEFAULT = "https://integrate.api.nvidia.com/v1"
ISING_CALIBRATION_MODEL_ID = "nvidia/ising-calibration-1"


@dataclass
class CalibrationFinding:
    """Structured interpretation of a QPU measurement trace."""

    experiment_type: str            # e.g. "rabi_oscillation", "t1_decay", "ramsey"
    classification: str             # e.g. "miscalibrated_drive_amplitude"
    severity: str                   # "within_spec" | "drift" | "fault"
    recommended_action: str         # human-readable next step
    suggested_parameters: dict[str, Any]  # parameters for the corrective pulse
    confidence: float               # 0.0 to 1.0
    rationale: str                  # VLM's reasoning, for transparency


class IsingClient:
    """Client for Ising Calibration 1."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = NIM_BASE_URL_DEFAULT,
        model: str = ISING_CALIBRATION_MODEL_ID,
        mock: bool | None = None,
    ):
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.model = model
        # Auto-enable mock mode if no key is present, unless caller forces.
        self.mock = mock if mock is not None else (self.api_key is None)

    def analyze(self, trace: dict[str, Any]) -> CalibrationFinding:
        """Analyze a QPU measurement trace and return a structured finding."""
        if self.mock:
            return self._mock_analyze(trace)
        return self._live_analyze(trace)

    # -- live path --

    def _live_analyze(self, trace: dict[str, Any]) -> CalibrationFinding:
        if not self.api_key:
            raise RuntimeError("Live mode requires NVIDIA_API_KEY")
        prompt = _build_prompt(trace)
        resp = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        payload = resp.json()
        content = payload["choices"][0]["message"]["content"]
        return _parse_finding(json.loads(content))

    # -- mock path --

    def _mock_analyze(self, trace: dict[str, Any]) -> CalibrationFinding:
        """Deterministic iteration-aware canned response for demos. Reads
        prior corrections out of the trace so successive calls recommend
        progressively smaller adjustments, the way a real calibration loop
        would behave."""
        qubit_id = trace.get("qubit_id", "q0")
        peak = trace.get("peak_frequency_hz") or trace.get("measurement", {}).get("peak_hz")
        prior_scale = trace.get("applied_scale")

        if prior_scale is None:
            # First iteration: large visible drift, full recommended correction.
            new_scale = 0.92
            classification = "miscalibrated_drive_amplitude"
            action = (
                f"Reduce drive amplitude on {qubit_id} by approximately 8% "
                "and re-run Rabi sweep over 0.6 to 1.2 of current amplitude."
            )
            rationale = (
                "Observed Rabi envelope peak shifted above the expected pi-pulse "
                "amplitude, indicating the drive line is overdriving the qubit. "
                "A ~8% reduction typically brings the Rabi peak back to the "
                "pi-pulse target for superconducting transmons."
            )
        else:
            # Subsequent iteration: halve the residual drift toward unity.
            residual = 1.0 - float(prior_scale)
            new_scale = float(prior_scale) + residual * 0.5
            classification = "residual_drift"
            action = (
                f"Fine-tune drive amplitude on {qubit_id} to scale "
                f"{new_scale:.3f}, halving the residual drift observed after "
                "the prior correction."
            )
            rationale = (
                "Post-correction trace shows residual drift from the prior "
                f"scale of {prior_scale:.3f}. Recommending a halving step to "
                "converge without overshooting."
            )

        drift = abs(1.0 - new_scale)
        severity = "within_spec" if drift <= 0.05 else "drift"

        return CalibrationFinding(
            experiment_type="rabi_oscillation",
            classification=classification,
            severity=severity,
            recommended_action=action,
            suggested_parameters={
                "qubit_id": qubit_id,
                "drive_amplitude_scale": new_scale,
                "sweep_range": [0.6, 1.2],
                "sweep_points": 41,
                "peak_frequency_hz": peak,
            },
            confidence=0.87,
            rationale=rationale,
        )


# -- helpers --

_SYSTEM_PROMPT = (
    "You are Ising Calibration, a vision-language model specialized in "
    "quantum processor calibration. Given a measurement trace, classify the "
    "experiment, assess whether the result is within spec, drifting, or a "
    "fault, and recommend a concrete corrective action with parameters. "
    "Respond as a JSON object matching the schema in the user message."
)


def _build_prompt(trace: dict[str, Any]) -> str:
    schema = {
        "experiment_type": "string",
        "classification": "string",
        "severity": "within_spec | drift | fault",
        "recommended_action": "string",
        "suggested_parameters": "object",
        "confidence": "number between 0 and 1",
        "rationale": "string",
    }
    return (
        "Analyze this QPU measurement trace and return a JSON object matching "
        f"this schema:\n{json.dumps(schema, indent=2)}\n\n"
        f"Trace:\n{json.dumps(trace, indent=2)}"
    )


def _parse_finding(raw: dict[str, Any]) -> CalibrationFinding:
    return CalibrationFinding(
        experiment_type=str(raw.get("experiment_type", "unknown")),
        classification=str(raw.get("classification", "unknown")),
        severity=str(raw.get("severity", "unknown")),
        recommended_action=str(raw.get("recommended_action", "")),
        suggested_parameters=dict(raw.get("suggested_parameters") or {}),
        confidence=float(raw.get("confidence", 0.0)),
        rationale=str(raw.get("rationale", "")),
    )
