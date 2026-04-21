# Hugging Face Blog submission

**How HF blog submissions work:** community blog posts are submitted as a pull request to https://github.com/huggingface/blog. Instructions: https://github.com/huggingface/blog/blob/main/README.md

**Filename convention:** `YYYY-MM-DD-title.md` at the repo root.
**Suggested filename:** `2026-04-22-agentic-qpu-calibration-ising.md`

## Submission body

```markdown
---
title: "Closing the Quantum Calibration Loop: Ising Calibration Meets an Open Agent Stack"
thumbnail: /blog/assets/crowe-logic-quantum/thumbnail.png
authors:
- user: CroweLogic
  org: CroweLogic
---

# Closing the Quantum Calibration Loop

NVIDIA's [Ising Calibration 1](https://huggingface.co/nvidia/ising-calibration-1) is the first open vision-language model built for quantum processor calibration. It reads an experimental measurement trace and tells you what's wrong and what to do about it. That is the physical-layer intelligence nobody had shipped before.

What it is not, by itself, is a calibration workflow. A real QPU calibration loop has four parts:

1. **Interpret** the measurement trace (this is what Ising does).
2. **Author** a corrective pulse sequence from the recommendation.
3. **Execute** the sequence on the device or a simulator.
4. **Decide** whether the system is within spec, or iterate.

We wrote a small open-source blueprint that wires all four parts together using Ising Calibration 1 plus open quantum authoring primitives (Synapse-Lang, Qubit-Flow) and an orchestrator pattern borrowed from Crowe Logic Foundry. It is Apache 2.0, runs in mock mode with zero credentials, and converges on a synthetic superconducting-qubit trace in two iterations.

## The loop

```
  Measurement trace (QPU output)
            |
            v
  [ Ising Calibration VLM ]    "This is a Rabi fit; reduce drive
            |                   amplitude by ~8%; confidence 0.87."
            v
  [ Crowe Logic agent ]         Decides: execute? escalate? re-sweep?
            |
            v
  [ Qubit-Flow ]                Authors the corrective circuit.
            |
            v
  [ Trinity pipeline ]          Executes on backend, emits new trace.
            |
            v
  Loop until within spec.
```

## Why structure the output

Ising's raw response is a vision-language interpretation. To make it agent-usable, the blueprint parses it into a small dataclass:

```python
@dataclass
class CalibrationFinding:
    experiment_type: str        # "rabi_oscillation", "t1_decay", ...
    classification: str         # "miscalibrated_drive_amplitude", ...
    severity: str               # "within_spec" | "drift" | "fault"
    recommended_action: str
    suggested_parameters: dict[str, Any]
    confidence: float
    rationale: str
```

This is what converts a chat interaction into an agentic loop. An orchestrator can branch on `severity`, gate on `confidence`, parameterize a corrective circuit from `suggested_parameters`, and log `rationale` for operator review.

## Confidence-gated execution

The blueprint's agent prompt (the `quantum_calibration.yaml` file) mandates operator escalation when `confidence < 0.6`. Calibration mistakes cost QPU time at best and can damage hardware at worst. Treating low-confidence findings as a pause rather than a proceed is the pattern real labs will want.

## What Crowe Logic brings

NVIDIA brings the physical-layer intelligence. The open quantum ecosystem brings circuit authoring (Qubit-Flow DSL), evaluation (Synapse-Lang), and execution (Trinity pipeline). What Crowe Logic brings is the decision-making runtime: the agent that knows when to call which, when to ask the operator, and how to summarize progress. The full workflow is hard to assemble from scratch; the blueprint ships the wire-up.

## Try it

- Repo (Apache 2.0): https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint
- Live Space: https://huggingface.co/spaces/CroweLogic/ising-calibration-blueprint

```bash
git clone https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint
cd crowe-logic-foundry-quantum-blueprint
pip install -e ".[quantum]"
clqb calibrate data/sample_qpu_trace.json
```

## What is next

Three directions we are working on:

1. **Ising Decoding integration.** The Decoding models are CNNs for real-time quantum error correction. Plugging them into the same orchestrator pattern extends the blueprint from calibration to live QEC.
2. **Real-hardware partners.** The blueprint runs today against synthetic traces. We are reaching out to QPU vendors to test against real devices.
3. **NeMo Agent Toolkit reference implementation.** A second entry point that builds the same loop on NeMo's agent primitives, for shops already committed to that stack.

Pull requests welcome. If you run a QPU and want to try this on real data, open an issue.
```

## Submission steps

1. Fork https://github.com/huggingface/blog
2. Add the file at `_blog/2026-04-22-agentic-qpu-calibration-ising.md`
3. Open a PR titled `Add blog post: Closing the Quantum Calibration Loop`
4. Brief PR body referencing the Space link and the GitHub repo
5. Tag `@Wauplin`, `@philschmid`, or `@_akhaliq` for review visibility
