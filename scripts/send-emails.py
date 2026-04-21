#!/usr/bin/env python3
"""
send-emails.py

Programmatic sender for the QPU vendor outreach emails via Gmail SMTP.

Safety rails this script enforces:

  - Credentials come from env vars only. Never from CLI args, never hardcoded.
      GMAIL_USER            Gmail or Google Workspace address (the SMTP user)
      GMAIL_APP_PASSWORD    Google App Password (16 chars, 2FA required)
      GMAIL_FROM            Optional. From address to appear on the envelope,
                            in case sending through Workspace with an alias.
                            Defaults to GMAIL_USER.

  - --dry-run prints what would be sent, sends nothing.

  - Without --yes, prompts for confirmation before each send.

  - Enforces a minimum spacing (default 90s) between sends to stay under
    Gmail's outbound anti-abuse thresholds.

  - Appends a JSON-lines record to launch/sent.log for every send attempt.
    Already-sent vendors are skipped on re-runs unless --resend is passed.

Usage:

  export GMAIL_USER="mike@southwestmushrooms.com"
  export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"       # from myaccount.google.com/apppasswords

  # Preview what would be sent, no sending:
  ./scripts/send-emails.py --dry-run

  # Send to a single vendor with confirmation:
  ./scripts/send-emails.py --only ibm

  # Send to all (with per-email confirmations):
  ./scripts/send-emails.py --all

  # Send to all without confirmation (requires --yes):
  ./scripts/send-emails.py --all --yes

App Password setup:
  1. Enable 2FA on the Google account: https://myaccount.google.com/security
  2. Create an App Password: https://myaccount.google.com/apppasswords
     (name it "crowe-logic-outreach", scope "Mail").
  3. Export the 16-char password as GMAIL_APP_PASSWORD (spaces ok, stripped).
"""

from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import sys
import time
from dataclasses import dataclass, asdict
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "launch" / "sent.log"
ENV_FILE = ROOT / ".env.local"


def _load_env_local() -> None:
    """Load KEY=VALUE lines from .env.local into os.environ without
    overriding values already set by the caller's shell. Safe to call
    even if the file is missing. Values may be quoted or bare."""
    if not ENV_FILE.is_file():
        return
    for raw in ENV_FILE.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_local()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
MIN_SPACING_SECONDS = 90


@dataclass
class Vendor:
    key: str          # short id: "ibm", "ionq", etc. used for --only
    company: str
    to: str
    subject: str
    body: str


VENDORS: list[Vendor] = [
    Vendor(
        key="ibm",
        company="IBM Quantum",
        to="research-collaborations@us.ibm.com",
        subject="Agentic calibration loop for IBM Quantum, using NVIDIA Ising + open quantum stack",
        body=(
            "Hi IBM Quantum team,\n\n"
            "I am Michael Crowe, founder of Crowe Logic. We just published an "
            "Apache 2.0 reference implementation of an end-to-end agentic QPU "
            "calibration loop: NVIDIA Ising Calibration 1 for physical-layer "
            "interpretation, plus our open quantum DSL stack (Synapse-Lang and "
            "Qubit-Flow on PyPI) for authoring and executing corrective "
            "circuits, plus an orchestrator pattern that handles iteration and "
            "operator escalation.\n\n"
            "Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint\n\n"
            "Today it runs against synthetic superconducting-qubit traces. To "
            "matter, it needs to run against real devices. I would love to "
            "test this against an IBM Quantum backend, ideally one of the "
            "Eagle or Heron systems via Qiskit Runtime.\n\n"
            "What is the right path to do that? Research collaboration, IBM "
            "Quantum Network access, or something else? Happy to share more "
            "detail on the orchestrator pattern, or to jump on a call.\n\n"
            "Michael Crowe\n"
            "Founder, Crowe Logic, Inc.\n"
            "https://crowelogic.com\n"
            "github.com/Crowe-OS\n"
            "mike@southwestmushrooms.com\n"
        ),
    ),
    Vendor(
        key="ionq",
        company="IonQ",
        to="partnerships@ionq.com",
        subject="Agentic calibration loop for IonQ, using NVIDIA Ising + open quantum stack",
        body=(
            "Hi IonQ team,\n\n"
            "I am Michael Crowe, founder of Crowe Logic. We published an "
            "Apache 2.0 agentic QPU calibration loop last week combining "
            "NVIDIA Ising Calibration 1 with an open quantum DSL stack "
            "(Synapse-Lang and Qubit-Flow on PyPI) and an orchestrator pattern "
            "that drives iteration and operator escalation.\n\n"
            "Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint\n\n"
            "Ising Calibration was trained across multiple qubit modalities, "
            "including trapped ions, so IonQ is one of the most interesting "
            "targets to validate this against. The blueprint currently runs "
            "on synthetic traces; I would like to test it against real IonQ "
            "calibration data.\n\n"
            "Is there a path to test this via IonQ Cloud or through a "
            "research collaboration? Also interested in how your calibration "
            "workflow handles drift across long jobs, since that is exactly "
            "where this loop shape earns its keep.\n\n"
            "Michael Crowe\n"
            "Founder, Crowe Logic, Inc.\n"
            "https://crowelogic.com\n"
            "github.com/Crowe-OS\n"
            "mike@southwestmushrooms.com\n"
        ),
    ),
    Vendor(
        key="quantinuum",
        company="Quantinuum",
        to="info@quantinuum.com",
        subject="Agentic calibration loop for Quantinuum H-series, using NVIDIA Ising + open quantum stack",
        body=(
            "Hi Quantinuum team,\n\n"
            "I am Michael Crowe, founder of Crowe Logic. We just published an "
            "open agentic QPU calibration blueprint using NVIDIA Ising "
            "Calibration 1 paired with our open quantum DSL stack "
            "(Synapse-Lang, Qubit-Flow). The loop is Apache 2.0 and runs "
            "end-to-end against synthetic traces today.\n\n"
            "Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint\n\n"
            "Quantinuum's H-series ion trap hardware with its long coherence "
            "times and high fidelities is exactly the kind of platform where "
            "a calibration agent can compound value: fewer manual "
            "recalibrations, more effective qubit time per shift, faster "
            "iteration on experiments.\n\n"
            "What is the right way to test this against an H-series system? "
            "Research collaboration via the Quantinuum Nexus program, or "
            "something else?\n\n"
            "Michael Crowe\n"
            "Founder, Crowe Logic, Inc.\n"
            "https://crowelogic.com\n"
            "github.com/Crowe-OS\n"
            "mike@southwestmushrooms.com\n"
        ),
    ),
    Vendor(
        key="pasqal",
        company="Pasqal",
        to="contact@pasqal.com",
        subject="Agentic calibration loop for Pasqal neutral-atom QPUs, using NVIDIA Ising",
        body=(
            "Hi Pasqal team,\n\n"
            "I am Michael Crowe, founder of Crowe Logic. We published an "
            "open agentic calibration loop last week combining NVIDIA Ising "
            "Calibration 1 with our open quantum DSL stack (Synapse-Lang, "
            "Qubit-Flow on PyPI).\n\n"
            "Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint\n\n"
            "Ising Calibration was trained on neutral-atom data, among other "
            "modalities. Pasqal's architecture feels like a particularly "
            "clean target for the loop shape. The blueprint is running on "
            "synthetic superconducting traces today; I would like to test it "
            "against real Pasqal data.\n\n"
            "Is there a path for research collaboration or via the Pasqal "
            "Cloud? Also happy to chat about what primitives you would want "
            "to see in the open layer to make this easier to integrate with "
            "Pulser.\n\n"
            "Michael Crowe\n"
            "Founder, Crowe Logic, Inc.\n"
            "https://crowelogic.com\n"
            "github.com/Crowe-OS\n"
            "mike@southwestmushrooms.com\n"
        ),
    ),
    Vendor(
        key="rigetti",
        company="Rigetti",
        to="sales@rigetti.com",
        subject="Agentic calibration loop for Rigetti Ankaa, using NVIDIA Ising + open stack",
        body=(
            "Hi Rigetti team,\n\n"
            "I am Michael Crowe, founder of Crowe Logic. We published an "
            "Apache 2.0 agentic QPU calibration loop using NVIDIA Ising "
            "Calibration 1 plus our open quantum DSL stack (Synapse-Lang and "
            "Qubit-Flow on PyPI).\n\n"
            "Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint\n\n"
            "Calibration stability is one of the hardest superconducting-"
            "qubit problems, and one of the biggest costs. This loop aims to "
            "drop human-in-the-loop time per experiment by closing the "
            "trace-to-circuit-to-execute cycle with an agent. Today it runs "
            "on synthetic traces; I would like to validate it against the "
            "Ankaa-3 system via QCS.\n\n"
            "What is the right path? QCS research access, a research "
            "collaboration, or a direct pilot?\n\n"
            "Michael Crowe\n"
            "Founder, Crowe Logic, Inc.\n"
            "https://crowelogic.com\n"
            "github.com/Crowe-OS\n"
            "mike@southwestmushrooms.com\n"
        ),
    ),
    Vendor(
        key="atom",
        company="Atom Computing",
        to="info@atom-computing.com",
        subject="Agentic calibration loop for Atom Computing, using NVIDIA Ising + open stack",
        body=(
            "Hi Atom Computing team,\n\n"
            "I am Michael Crowe, founder of Crowe Logic. We published an "
            "open agentic QPU calibration blueprint combining NVIDIA Ising "
            "Calibration 1 with Synapse-Lang, Qubit-Flow, and an "
            "orchestrator pattern for iteration and operator escalation.\n\n"
            "Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint\n\n"
            "Atom Computing's scale target (thousands of qubits in a system) "
            "is exactly the regime where human-in-the-loop calibration stops "
            "being viable and closed-loop agent calibration becomes "
            "necessary infrastructure.\n\n"
            "Is there a path to test this against your platform, via "
            "research collaboration or early access? Also happy to discuss "
            "what you would want to see in the open layer to make it "
            "production-viable for your scale.\n\n"
            "Michael Crowe\n"
            "Founder, Crowe Logic, Inc.\n"
            "https://crowelogic.com\n"
            "github.com/Crowe-OS\n"
            "mike@southwestmushrooms.com\n"
        ),
    ),
    Vendor(
        key="riverlane",
        company="Riverlane",
        to="info@riverlane.com",
        subject="Open agentic calibration loop, overlap with your decoder work",
        body=(
            "Hi Riverlane team,\n\n"
            "I am Michael Crowe, founder of Crowe Logic. We published an "
            "Apache 2.0 agentic QPU calibration blueprint last week using "
            "NVIDIA Ising Calibration 1 plus our open quantum DSL stack.\n\n"
            "Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint\n\n"
            "The reason I am reaching out to Riverlane specifically: the "
            "blueprint is currently calibration-side, but the natural next "
            "step is to add Ising Decoding (the 3D CNN QEC decoders NVIDIA "
            "shipped alongside) into the same orchestrator. Riverlane has "
            "deep expertise in real-time decoding and the DeltaFlow-on-ASIC "
            "story is complementary rather than competitive with an open "
            "agentic top-layer.\n\n"
            "Curious whether there is a collaboration shape where our open "
            "orchestrator pattern meets your production decoder "
            "infrastructure.\n\n"
            "Michael Crowe\n"
            "Founder, Crowe Logic, Inc.\n"
            "https://crowelogic.com\n"
            "github.com/Crowe-OS\n"
            "mike@southwestmushrooms.com\n"
        ),
    ),
]


def load_sent_log() -> dict[str, dict]:
    if not LOG_PATH.exists():
        return {}
    records: dict[str, dict] = {}
    for line in LOG_PATH.read_text().splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
            if rec.get("status") == "sent":
                records[rec["key"]] = rec
        except Exception:
            continue
    return records


def append_sent_log(record: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(record) + "\n")


def build_message(vendor: Vendor, from_addr: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = vendor.to
    msg["Subject"] = vendor.subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=from_addr.split("@")[-1])
    msg["Reply-To"] = from_addr
    msg.set_content(vendor.body)
    return msg


def send_one(vendor: Vendor, from_addr: str, user: str, password: str,
             dry_run: bool) -> dict:
    msg = build_message(vendor, from_addr)
    if dry_run:
        return {
            "key": vendor.key,
            "company": vendor.company,
            "to": vendor.to,
            "subject": vendor.subject,
            "from": from_addr,
            "status": "dry_run",
            "timestamp": formatdate(localtime=False),
        }
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)
    return {
        "key": vendor.key,
        "company": vendor.company,
        "to": vendor.to,
        "subject": vendor.subject,
        "from": from_addr,
        "status": "sent",
        "timestamp": formatdate(localtime=False),
    }


def confirm(prompt: str) -> bool:
    try:
        answer = input(prompt).strip().lower()
    except EOFError:
        return False
    return answer in ("y", "yes")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true",
                       help="Send to every vendor")
    group.add_argument("--only", type=str,
                       help="Comma-separated vendor keys, e.g. ibm,ionq")
    group.add_argument("--list", action="store_true",
                       help="List vendor keys and exit")
    p.add_argument("--dry-run", action="store_true",
                   help="Print each message header but send nothing")
    p.add_argument("--yes", action="store_true",
                   help="Skip per-email confirmation prompts")
    p.add_argument("--resend", action="store_true",
                   help="Ignore the sent log and resend")
    p.add_argument("--spacing", type=int, default=MIN_SPACING_SECONDS,
                   help=f"Seconds between sends (min {MIN_SPACING_SECONDS})")
    args = p.parse_args()

    if args.list:
        for v in VENDORS:
            print(f"  {v.key:<12}  {v.company:<20}  {v.to}")
        return 0

    if args.spacing < MIN_SPACING_SECONDS:
        print(f"Spacing of {args.spacing}s is below the {MIN_SPACING_SECONDS}s "
              f"safety floor. Refusing to run.", file=sys.stderr)
        return 2

    selected: list[Vendor]
    if args.all:
        selected = list(VENDORS)
    else:
        keys = [k.strip().lower() for k in args.only.split(",")]
        by_key = {v.key: v for v in VENDORS}
        unknown = [k for k in keys if k not in by_key]
        if unknown:
            print(f"Unknown vendor keys: {unknown}. Use --list.", file=sys.stderr)
            return 2
        selected = [by_key[k] for k in keys]

    sent = load_sent_log() if not args.resend else {}
    pending = [v for v in selected if v.key not in sent]
    skipped = [v for v in selected if v.key in sent]
    if skipped:
        print(f"Skipping already-sent: {[v.key for v in skipped]} "
              f"(use --resend to override)")
    if not pending:
        print("Nothing to send.")
        return 0

    user = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    from_addr = os.environ.get("GMAIL_FROM") or user or "dry-run@example.com"

    if not args.dry_run:
        if not user or not password:
            print("Error: set GMAIL_USER and GMAIL_APP_PASSWORD env vars.",
                  file=sys.stderr)
            print("  Create app password: https://myaccount.google.com/apppasswords",
                  file=sys.stderr)
            return 2

    print(f"\nWill process {len(pending)} email(s):")
    for v in pending:
        print(f"  - {v.key:<12} -> {v.to}")
    print(f"\nFrom: {from_addr or '(dry-run)'}")
    print(f"Spacing: {args.spacing}s between sends")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    if not args.yes and not args.dry_run:
        if not confirm("\nProceed? [y/N]: "):
            print("Aborted.")
            return 1

    for i, vendor in enumerate(pending):
        print(f"\n--- [{i+1}/{len(pending)}] {vendor.key}: {vendor.company} ---")
        print(f"To:      {vendor.to}")
        print(f"Subject: {vendor.subject}")
        print(f"Body preview (first 160 chars):")
        print(f"  {vendor.body[:160].strip()}...")
        if not args.yes and not args.dry_run:
            if not confirm("Send this one? [y/N]: "):
                print("Skipped.")
                continue
        try:
            record = send_one(vendor, from_addr or user, user, password, args.dry_run)
            append_sent_log(record)
            print(f"  {record['status']} at {record['timestamp']}")
        except smtplib.SMTPAuthenticationError as e:
            print(f"\nSMTP auth error: {e}", file=sys.stderr)
            print("Common causes:\n"
                  "  - 2FA not enabled on the Google account\n"
                  "  - GMAIL_APP_PASSWORD is an account password, not an app password\n"
                  "  - App password was created for the wrong scope", file=sys.stderr)
            return 3
        except Exception as e:
            print(f"  Failed: {e}", file=sys.stderr)
            append_sent_log({
                "key": vendor.key,
                "company": vendor.company,
                "status": "error",
                "error": str(e),
                "timestamp": formatdate(localtime=False),
            })
            if not confirm("Continue with remaining sends? [y/N]: "):
                return 4

        if i < len(pending) - 1 and not args.dry_run:
            print(f"  Sleeping {args.spacing}s (anti-abuse pacing)...")
            time.sleep(args.spacing)

    print("\nDone. Sent log: launch/sent.log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
