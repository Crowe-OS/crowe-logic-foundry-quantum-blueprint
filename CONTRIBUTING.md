# Contributing

Thanks for considering a contribution. This repository is an open reference implementation, not a product, so the contribution surface is deliberately narrow.

## Good contributions

- **Real-hardware validation.** If you have access to a QPU and can run the calibration loop against real traces, open an [issue](https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint/issues/new?template=qpu-access-offer.yml) describing your setup. This is the single most valuable contribution.
- **Ising Calibration schema alignment.** If NVIDIA publishes or recommends a canonical schema for Ising outputs, a PR that updates the `CalibrationFinding` dataclass to match is welcome.
- **Trinity adapter implementations.** The current adapter emits placeholder Qubit-Flow source. PRs that swap in real Qubit-Flow DSL emission, Qiskit transpilation, or Pulser sequences are welcome.
- **Additional calibration experiment types.** The mock response today covers Rabi oscillations. PRs that add T1, Ramsey, spectroscopy, or two-qubit-gate calibration paths are welcome.
- **Bug fixes with a failing test.** Open a PR with the fix and a regression test.

## Weaker contributions

- Dependency bumps without a reason
- Style-only refactors that do not improve readability
- Large architectural proposals without a prior [Discussion](https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint/discussions) thread

## Development setup

```bash
git clone https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint
cd crowe-logic-foundry-quantum-blueprint
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest tests/ -v
.venv/bin/clqb calibrate data/sample_qpu_trace.json
```

CI runs on Python 3.11 and 3.12 against every push and PR. Green CI is required for merge.

## License

By contributing you agree your contributions are licensed under Apache 2.0 (the repository's license).
