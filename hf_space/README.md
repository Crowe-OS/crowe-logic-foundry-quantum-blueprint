---
title: Crowe Logic Quantum Calibration Blueprint
emoji: "\U0001F3AF"
colorFrom: indigo
colorTo: gray
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
license: apache-2.0
tags:
  - quantum-computing
  - agent
  - nvidia-ising
  - qec
  - calibration
  - crowe-logic
models:
  - nvidia/ising-calibration-1
---

# Crowe Logic Foundry Quantum Calibration Blueprint

Live demo of an agentic QPU calibration loop combining NVIDIA Ising Calibration 1 with Crowe Logic's quantum stack (Synapse-Lang, Qubit-Flow, Trinity bridge) and the Crowe Logic Foundry orchestrator pattern.

Runs fully in mock mode with zero credentials. Set `NVIDIA_API_KEY` as a Space secret to enable live calls to the NVIDIA Build Ising Calibration NIM endpoint.

**Source (Apache 2.0):** https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

**About Crowe Logic Foundry:** universal AI agent runtime with first-class scientific-computing primitives, including quantum circuit authoring and physical-layer calibration.
