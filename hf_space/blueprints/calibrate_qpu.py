"""
The calibration loop.

Drives the full agentic QPU calibration workflow:

  1. Read a measurement trace (JSON on disk, or streamed from a backend).
  2. Send it to Ising Calibration for interpretation.
  3. Hand the finding to the Trinity adapter to author a corrective circuit.
  4. Execute the circuit, get a new trace.
  5. Repeat until converged or iteration cap reached.

This loop is the Crowe Logic Foundry pattern in miniature. In production,
the orchestrator decisions at each step are made by the `quantum` agent in
Foundry rather than the plain for-loop here. This file exists so that
people without Foundry can still run and fork the pattern.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from blueprints.ising_client import IsingClient, CalibrationFinding
from blueprints.trinity_adapter import TrinityAdapter, ExecutionResult


@dataclass
class LoopIteration:
    index: int
    trace_in: dict[str, Any]
    finding: CalibrationFinding
    execution: ExecutionResult


@dataclass
class LoopResult:
    converged: bool
    iterations: list[LoopIteration]
    final_trace: dict[str, Any]


def run_loop(
    trace_path: str | Path,
    ising: IsingClient | None = None,
    trinity: TrinityAdapter | None = None,
    max_iterations: int = 5,
) -> LoopResult:
    """Run the calibration loop to convergence or the iteration cap."""
    ising = ising or IsingClient()
    trinity = trinity or TrinityAdapter()

    trace = _load_trace(trace_path)
    iterations: list[LoopIteration] = []

    for i in range(max_iterations):
        finding = ising.analyze(trace)
        circuit = trinity.synthesize_circuit(finding)
        execution = trinity.execute(circuit)
        iterations.append(LoopIteration(
            index=i,
            trace_in=trace,
            finding=finding,
            execution=execution,
        ))
        if execution.converged:
            return LoopResult(
                converged=True,
                iterations=iterations,
                final_trace=execution.trace,
            )
        trace = execution.trace

    return LoopResult(
        converged=False,
        iterations=iterations,
        final_trace=trace,
    )


def _load_trace(path: str | Path) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)
