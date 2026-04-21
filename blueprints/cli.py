"""Command-line entry point for the blueprint."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from blueprints.calibrate_qpu import run_loop
from blueprints.ising_client import IsingClient
from blueprints.trinity_adapter import TrinityAdapter


console = Console()


@click.group()
def main():
    """Crowe Logic Foundry quantum calibration blueprint."""


@main.command()
@click.argument("trace_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--live/--mock", default=False,
              help="Live hits the Ising Calibration NIM endpoint; "
                   "mock returns a canned response.")
@click.option("--max-iterations", default=5, show_default=True,
              help="Stop after this many iterations if not converged.")
@click.option("--backend", default="simulator", show_default=True,
              help="Trinity execution backend identifier.")
def calibrate(trace_path, live, max_iterations, backend):
    """Run the full calibration loop against a QPU trace."""
    console.print(Panel(
        "[bold]Crowe Logic Foundry Quantum Calibration[/bold]\n"
        f"Trace: {trace_path}\n"
        f"Mode: {'LIVE (NVIDIA NIM)' if live else 'MOCK'}\n"
        f"Max iterations: {max_iterations}",
        border_style="cyan",
    ))

    ising = IsingClient(mock=not live)
    trinity = TrinityAdapter(backend=backend, iterations_max=max_iterations)
    result = run_loop(
        trace_path,
        ising=ising,
        trinity=trinity,
        max_iterations=max_iterations,
    )

    table = Table(title="Iterations", show_lines=True)
    table.add_column("#", justify="right")
    table.add_column("Classification")
    table.add_column("Severity")
    table.add_column("Action (truncated)")
    table.add_column("Converged?", justify="center")
    for step in result.iterations:
        table.add_row(
            str(step.index),
            step.finding.classification,
            step.finding.severity,
            _truncate(step.finding.recommended_action, 70),
            "yes" if step.execution.converged else "no",
        )
    console.print(table)

    outcome = "[bold green]CONVERGED[/bold green]" if result.converged else "[bold yellow]NOT CONVERGED[/bold yellow]"
    console.print(f"\nFinal status: {outcome}")
    console.print(f"Final trace: {json.dumps(result.final_trace, indent=2)}")


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "..."


if __name__ == "__main__":
    main()
