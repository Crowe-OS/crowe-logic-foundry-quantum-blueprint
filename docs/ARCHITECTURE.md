# Architecture

## Why this shape

A coding agent can write a quantum circuit. That is not the interesting
problem. The interesting problem is running the feedback loop between a
noisy physical QPU and a classical agent that decides what to do next. That
requires four ingredients in one orchestrator:

1. **Physical-layer intelligence**: a model that reads raw measurement traces
   and tells you what they mean. NVIDIA Ising Calibration 1.
2. **Quantum authoring primitives**: a way to emit corrective pulse sequences
   without hand-writing Qiskit every iteration. Qubit-Flow (DSL) +
   Synapse-Lang (evaluation).
3. **Execution bridge**: a pipeline that takes authored programs and runs
   them on a real or simulated backend. Trinity.
4. **Decision-making runtime**: an agent that sequences the above, asks
   the operator when unsure, and summarizes progress. Crowe Logic Foundry's
   quantum agent.

No single existing open tool spans all four. This blueprint is the
wire-up.

## Components

### IsingClient (`blueprints/ising_client.py`)

Thin HTTPX client for NVIDIA's Ising Calibration NIM endpoint. Returns a
`CalibrationFinding` dataclass. Supports a mock mode for demos and CI so
the blueprint is runnable without credentials.

### TrinityAdapter (`blueprints/trinity_adapter.py`)

Authors and executes calibration circuits. Today it emits placeholder
Qubit-Flow source; once `qubit-flow` is installed it will emit real DSL.
Execution today is simulated; once Foundry is installed it routes through
the real Trinity pipeline.

### Calibration loop (`blueprints/calibrate_qpu.py`)

The plain for-loop that drives: `trace -> Ising -> finding -> Trinity ->
circuit -> execution -> new trace`. Terminates on convergence or iteration
cap.

### Quantum calibration agent (`agents/quantum_calibration.yaml`)

The Foundry-native version. Same loop, but each step is a tool call made
by the `crowelm-pro` quantum agent, with reasoning and operator escalation
at each step. Drop this file into `crowe-logic-foundry/agents/` to activate.

## Two ways to run

| Mode        | Requirements                                | What runs                              |
|-------------|---------------------------------------------|----------------------------------------|
| Open path   | `pip install -e .` only                     | Plain loop with mock Ising + sim exec  |
| Live path   | `NVIDIA_API_KEY` env var                    | Real Ising Calibration, sim exec       |
| Foundry     | Crowe Logic Foundry installed and licensed  | Agent-driven loop, real Trinity exec   |

## Design choices worth naming

**Mock-first.** The blueprint must run end-to-end with no credentials. That
is the difference between a repo people fork and a repo people bookmark.

**Structured findings, not freeform.** `CalibrationFinding` is a dataclass
with explicit fields. Ising's freeform VLM response is parsed into this
structure. This is what turns a chat interaction into an agentic loop.

**Confidence gating.** The agent prompt mandates operator escalation when
Ising's confidence drops below 0.6. Calibration mistakes waste QPU time at
best and damage hardware at worst. The blueprint treats low-confidence
findings as a pause, not a proceed.

**Backend-agnostic execution.** Trinity is treated as a swappable backend.
The blueprint does not presuppose qiskit-aer, cuQuantum, or real hardware.
Pick one at run time.
