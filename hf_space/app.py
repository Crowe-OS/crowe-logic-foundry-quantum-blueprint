"""
Hugging Face Space: Crowe Logic Foundry Quantum Calibration Blueprint.

Live demo of the agentic QPU calibration loop. Edit the JSON trace on the
left, click Run, and watch the loop iterate Ising Calibration against the
Trinity execution backend until convergence.

Mock mode runs fully offline (zero credentials). Set NVIDIA_API_KEY as a
Space secret to flip on live Ising Calibration calls to NVIDIA Build.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import gradio as gr

from blueprints.calibrate_qpu import run_loop
from blueprints.ising_client import IsingClient
from blueprints.trinity_adapter import TrinityAdapter


SAMPLE_TRACE_PATH = Path(__file__).parent / "data" / "sample_qpu_trace.json"
SAMPLE_TRACE = json.dumps(json.loads(SAMPLE_TRACE_PATH.read_text()), indent=2)

HAS_LIVE_KEY = bool(os.environ.get("NVIDIA_API_KEY"))


def run_calibration(trace_json: str, live_mode: bool, max_iters: int):
    try:
        trace = json.loads(trace_json)
    except json.JSONDecodeError as e:
        return (
            f"JSON parse error: {e}",
            "",
            "",
        )
    tmp_path = Path("/tmp/clqb_input.json")
    tmp_path.write_text(json.dumps(trace))

    if live_mode and not HAS_LIVE_KEY:
        return (
            "Live mode requested but NVIDIA_API_KEY is not set as a Space "
            "secret. Falling back to mock mode.",
            "",
            "",
        )

    ising = IsingClient(mock=not live_mode)
    trinity = TrinityAdapter()
    result = run_loop(
        tmp_path,
        ising=ising,
        trinity=trinity,
        max_iterations=int(max_iters),
    )

    outcome = "CONVERGED" if result.converged else "NOT CONVERGED (iteration cap reached)"
    header = f"Status: {outcome}  |  iterations: {len(result.iterations)}"

    lines = []
    for i, step in enumerate(result.iterations):
        lines.append(f"--- iteration {i} ---")
        lines.append(f"classification : {step.finding.classification}")
        lines.append(f"severity       : {step.finding.severity}")
        lines.append(f"confidence     : {step.finding.confidence:.2f}")
        lines.append(f"action         : {step.finding.recommended_action}")
        lines.append(f"exec summary   : {step.execution.summary}")
        lines.append(f"exec converged : {step.execution.converged}")
        lines.append("")
    trace_log = "\n".join(lines)

    final = json.dumps(result.final_trace, indent=2)
    return header, trace_log, final


with gr.Blocks(title="Crowe Logic Quantum Calibration Blueprint") as demo:
    gr.Markdown(
        """
        # Crowe Logic Foundry  x  NVIDIA Ising Calibration

        Live demo of an **agentic QPU calibration loop**. The loop:

        1. Sends the measurement trace to Ising Calibration for interpretation.
        2. Authors a corrective circuit via Qubit-Flow (simulated).
        3. Executes the circuit through the Trinity pipeline (simulated).
        4. Feeds the new trace back in. Repeats until within spec.

        Apache 2.0. Source on [GitHub](https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint).
        """
    )
    with gr.Row():
        with gr.Column():
            trace_input = gr.Code(
                value=SAMPLE_TRACE,
                language="json",
                label="QPU measurement trace (edit freely)",
                lines=22,
            )
            live_mode = gr.Checkbox(
                label=(
                    "Live mode (hits NVIDIA Build NIM endpoint)"
                    if HAS_LIVE_KEY
                    else "Live mode (disabled: set NVIDIA_API_KEY as a Space secret)"
                ),
                value=False,
                interactive=HAS_LIVE_KEY,
            )
            max_iters = gr.Slider(
                minimum=1, maximum=10, value=5, step=1,
                label="Max iterations",
            )
            run_button = gr.Button("Run calibration loop", variant="primary")
        with gr.Column():
            status_out = gr.Textbox(label="Status", interactive=False)
            trace_log_out = gr.Textbox(
                label="Iteration log", lines=20, interactive=False,
            )
            final_trace_out = gr.Code(
                language="json", label="Final trace", lines=12,
            )

    run_button.click(
        run_calibration,
        inputs=[trace_input, live_mode, max_iters],
        outputs=[status_out, trace_log_out, final_trace_out],
    )

    gr.Markdown(
        """
        ---
        **About.** Crowe Logic Foundry is a universal AI agent runtime. This
        blueprint demonstrates Foundry's quantum agent pattern paired with
        NVIDIA's open-weight Ising Calibration model. For the full
        orchestrator-driven version, see the
        [GitHub repository](https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint).
        """
    )


if __name__ == "__main__":
    demo.launch()
