# Crowe Logic Foundry — Agentic QPU Calibration Blueprint

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Crowe-OS/crowe-logic-foundry-quantum-blueprint)](https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint/releases)
[![Discussions](https://img.shields.io/github/discussions/Crowe-OS/crowe-logic-foundry-quantum-blueprint)](https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint/discussions)
[![Ising Calibration](https://img.shields.io/badge/NVIDIA-Ising%20Calibration%201-76b900)](https://huggingface.co/nvidia/ising-calibration-1)
[![Hugging Face Space](https://img.shields.io/badge/%F0%9F%A4%97%20Space-CroweLogic%2Fising--calibration--blueprint-yellow)](https://huggingface.co/spaces/CroweLogic/ising-calibration-blueprint)

**An end-to-end agentic workflow for quantum processor calibration, built on Crowe Logic Foundry, Synapse-Lang, Qubit-Flow, and NVIDIA Ising.**

Most coding agents can help you write a quantum circuit. This blueprint shows an agent that can *run the full loop*: interpret real QPU measurement output, decide what to recalibrate, generate the corrective pulse sequence, execute it, and propose the next experiment. The quantum stack is first-class, not a chat transcript.

## Why this exists

NVIDIA shipped [Ising Calibration 1](https://developer.nvidia.com/blog/nvidia-ising-accelerates-useful-quantum-computing/), the first open vision-language model for QPU calibration. It slots naturally into agentic workflows. But the surrounding workflow, turning Ising's recommendations into executable calibration circuits and driving the experiment loop, needs a quantum-native orchestrator.

Crowe Logic Foundry is that orchestrator. It ships with:

- A quantum specialist agent (`agents/quantum.yaml`) that reasons over circuits
- The **Quantum Trinity**: [Synapse-Lang](https://pypi.org/project/synapse-lang/) for evaluation, [Qubit-Flow](https://pypi.org/project/qubit-flow/) for circuit authoring, and a Trinity pipeline tying them together
- A model-agnostic orchestrator that routes through NVIDIA, Azure AI Foundry, or local Ollama

This blueprint is the wire-up: Ising Calibration (VLM that reads experiments) + Trinity (circuit synthesis and execution) + Foundry's agent (the decision-making loop).

## The loop

```
  Measurement trace (QPU output)
           |
           v
  +----------------------------+
  |  Ising Calibration VLM     |   <-- NVIDIA NIM endpoint
  |  "This is a Rabi fit;      |
  |   drive amplitude is 8%    |
  |   above optimum."          |
  +----------------------------+
           |
           v
  +----------------------------+
  |  Crowe Logic Foundry       |   <-- Quantum agent reasons about next step
  |  quantum agent             |
  +----------------------------+
           |
           v
  +----------------------------+
  |  Qubit-Flow                |   <-- Authors the corrective circuit
  |  (refined pulse schedule)  |
  +----------------------------+
           |
           v
  +----------------------------+
  |  Trinity pipeline          |   <-- Executes, feeds results back in
  +----------------------------+
           |
           v
  +----------------------------+
  |  Synapse-Lang              |   <-- Scores and summarizes the iteration
  +----------------------------+
           |
           +--> next measurement trace, loop until within spec
```

## Quickstart

```bash
git clone https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint
cd crowe-logic-foundry-quantum-blueprint
pip install -e ".[quantum]"

# Mock mode: runs end-to-end against a canned Ising response. Works offline.
clqb calibrate data/sample_qpu_trace.json

# Real mode: hits NVIDIA Build's Ising Calibration NIM endpoint.
export NVIDIA_API_KEY=nvapi-...
clqb calibrate data/sample_qpu_trace.json --live
```

## What makes this Crowe Logic

Other coding agents can integrate with Ising Calibration. They cannot assemble the rest of the loop because they do not own the quantum-authoring primitives. Crowe Logic does:

- **Synapse-Lang**: symbolic quantum-program evaluator (published PyPI, authored by Crowe Logic)
- **Qubit-Flow**: declarative quantum circuit DSL (published PyPI, authored by Crowe Logic)
- **Trinity bridge**: execution pipeline connecting both to real and simulated backends
- **Foundry orchestrator**: the agent runtime that knows when to call which

Ising brings the physical-layer intelligence. Crowe Logic brings the rest of the stack. Together they are the first fully open, fully agentic QPU calibration loop.

## Repository layout

```
blueprints/
  cli.py                  Command-line entry point
  calibrate_qpu.py        The core calibration loop
  ising_client.py         NIM client for Ising Calibration (mock + live)
  trinity_adapter.py      Bridge to Synapse / Qubit-Flow / Trinity
agents/
  quantum_calibration.yaml  Specialized agent config scoped to this workflow
data/
  sample_qpu_trace.json   Synthetic superconducting-qubit trace for demos
docs/
  ARCHITECTURE.md         How the pieces fit and why
hf_space/                 Hugging Face Space (Gradio app) for browser demo
launch/                   Launch kit: ready-to-send drafts for every channel
scripts/
  launch-day.sh           Orchestrates opening every pre-filled launch URL
  email-drafts.sh         Creates Mail.app drafts for vendor outreach (review + send)
  send-emails.py          Programmatic Gmail SMTP sender with safety rails
  traction.sh             Dashboard for stars, views, HF Space status
tests/
```

## Status

This is an alpha reference implementation. It is intended to be readable, forkable, and cite-able, not production-grade. For production deployment against real QPUs, pair with Crowe Logic Foundry directly ([contact](mailto:michael@crowelogic.com)).

## License

Apache License 2.0. See [LICENSE](LICENSE).

Crowe Logic Foundry itself is proprietary. This blueprint is open to enable the full community to build on the pattern.
