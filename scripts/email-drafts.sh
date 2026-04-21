#!/usr/bin/env bash
#
# email-drafts.sh
#
# Creates 7 pre-filled email drafts in Mail.app for the QPU vendor
# outreach emails. Opens each one as a visible draft; you review and
# click Send individually (never in bulk).
#
# macOS only; uses osascript to drive Mail.app.

set -euo pipefail

if [[ "$(uname)" != "Darwin" ]]; then
    echo "email-drafts.sh is macOS-only (uses Mail.app via AppleScript)."
    exit 1
fi

draft() {
    local to="$1"
    local subject="$2"
    local body="$3"
    osascript <<APPLESCRIPT
tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:"${subject}", content:"${body}", visible:true}
    tell newMessage
        make new to recipient at end of to recipients with properties {address:"${to}"}
    end tell
    activate
end tell
APPLESCRIPT
}

# Bodies are kept in a single place so edits propagate. Heredocs preserve
# newlines; we strip the leading / trailing whitespace via :- defaults.

###############################################################################

IBM_BODY=$(cat <<'EOF'
Hi IBM Quantum team,

I am Michael Crowe, founder of Crowe Logic. We just published an Apache 2.0 reference implementation of an end-to-end agentic QPU calibration loop: NVIDIA Ising Calibration 1 for physical-layer interpretation, plus our open quantum DSL stack (Synapse-Lang and Qubit-Flow on PyPI) for authoring and executing corrective circuits, plus an orchestrator pattern that handles iteration and operator escalation.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Today it runs against synthetic superconducting-qubit traces. To matter, it needs to run against real devices. I would love to test this against an IBM Quantum backend, ideally one of the Eagle or Heron systems via Qiskit Runtime.

What is the right path to do that? Research collaboration, IBM Quantum Network access, or something else? Happy to share more detail on the orchestrator pattern, or to jump on a call.

Michael Crowe
Crowe Logic, Inc.
michael@crowelogic.com
EOF
)

IONQ_BODY=$(cat <<'EOF'
Hi IonQ team,

I am Michael Crowe, founder of Crowe Logic. We published an Apache 2.0 agentic QPU calibration loop last week combining NVIDIA Ising Calibration 1 with an open quantum DSL stack (Synapse-Lang and Qubit-Flow on PyPI) and an orchestrator pattern that drives iteration and operator escalation.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Ising Calibration was trained across multiple qubit modalities, including trapped ions, so IonQ is one of the most interesting targets to validate this against. The blueprint currently runs on synthetic traces; I would like to test it against real IonQ calibration data.

Is there a path to test this via IonQ Cloud or through a research collaboration? Also interested in how your calibration workflow handles drift across long jobs, since that is exactly where this loop shape earns its keep.

Michael Crowe
Crowe Logic, Inc.
EOF
)

QUANTINUUM_BODY=$(cat <<'EOF'
Hi Quantinuum team,

I am Michael Crowe, founder of Crowe Logic. We just published an open agentic QPU calibration blueprint using NVIDIA Ising Calibration 1 paired with our open quantum DSL stack (Synapse-Lang, Qubit-Flow). The loop is Apache 2.0 and runs end-to-end against synthetic traces today.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Quantinuum's H-series ion trap hardware with its long coherence times and high fidelities is exactly the kind of platform where a calibration agent can compound value: fewer manual recalibrations, more effective qubit time per shift, faster iteration on experiments.

What is the right way to test this against an H-series system? Research collaboration via the Quantinuum Nexus program, or something else?

Michael Crowe
Crowe Logic, Inc.
EOF
)

PASQAL_BODY=$(cat <<'EOF'
Hi Pasqal team,

I am Michael Crowe, founder of Crowe Logic. We published an open agentic calibration loop last week combining NVIDIA Ising Calibration 1 with our open quantum DSL stack (Synapse-Lang, Qubit-Flow on PyPI).

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Ising Calibration was trained on neutral-atom data, among other modalities. Pasqal's architecture feels like a particularly clean target for the loop shape. The blueprint is running on synthetic superconducting traces today; I would like to test it against real Pasqal data.

Is there a path for research collaboration or via the Pasqal Cloud? Also happy to chat about what primitives you would want to see in the open layer to make this easier to integrate with Pulser.

Michael Crowe
Crowe Logic, Inc.
EOF
)

RIGETTI_BODY=$(cat <<'EOF'
Hi Rigetti team,

I am Michael Crowe, founder of Crowe Logic. We published an Apache 2.0 agentic QPU calibration loop using NVIDIA Ising Calibration 1 plus our open quantum DSL stack (Synapse-Lang and Qubit-Flow on PyPI).

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Calibration stability is one of the hardest superconducting-qubit problems, and one of the biggest costs. This loop aims to drop human-in-the-loop time per experiment by closing the trace-to-circuit-to-execute cycle with an agent. Today it runs on synthetic traces; I would like to validate it against the Ankaa-3 system via QCS.

What is the right path? QCS research access, a research collaboration, or a direct pilot?

Michael Crowe
Crowe Logic, Inc.
EOF
)

ATOM_BODY=$(cat <<'EOF'
Hi Atom Computing team,

I am Michael Crowe, founder of Crowe Logic. We published an open agentic QPU calibration blueprint combining NVIDIA Ising Calibration 1 with Synapse-Lang, Qubit-Flow, and an orchestrator pattern for iteration and operator escalation.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Atom Computing's scale target (thousands of qubits in a system) is exactly the regime where human-in-the-loop calibration stops being viable and closed-loop agent calibration becomes necessary infrastructure.

Is there a path to test this against your platform, via research collaboration or early access? Also happy to discuss what you would want to see in the open layer to make it production-viable for your scale.

Michael Crowe
Crowe Logic, Inc.
EOF
)

RIVERLANE_BODY=$(cat <<'EOF'
Hi Riverlane team,

I am Michael Crowe, founder of Crowe Logic. We published an Apache 2.0 agentic QPU calibration blueprint last week using NVIDIA Ising Calibration 1 plus our open quantum DSL stack.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

The reason I am reaching out to Riverlane specifically: the blueprint is currently calibration-side, but the natural next step is to add Ising Decoding (the 3D CNN QEC decoders NVIDIA shipped alongside) into the same orchestrator. Riverlane has deep expertise in real-time decoding and the DeltaFlow-on-ASIC story is complementary rather than competitive with an open agentic top-layer.

Curious whether there is a collaboration shape where our open orchestrator pattern meets your production decoder infrastructure.

Michael Crowe
Crowe Logic, Inc.
EOF
)

# osascript content has to have quotes and newlines escaped. Build safe bodies.
escape_for_osa() {
    # Escape backslashes and double quotes, preserve newlines as \n for osascript.
    python3 -c '
import sys
s = sys.stdin.read()
s = s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
print(s, end="")
'
}

send_draft() {
    local to="$1" subject="$2" body_raw="$3"
    local body_esc
    body_esc=$(printf '%s' "$body_raw" | escape_for_osa)
    draft "$to" "$subject" "$body_esc"
    echo "  [draft] $to  |  $subject"
    sleep 1
}

echo "Creating 7 Mail.app drafts (they will open in Mail.app for review)..."
send_draft "research-collaborations@us.ibm.com" \
    "Agentic calibration loop for IBM Quantum, using NVIDIA Ising + open quantum stack" \
    "$IBM_BODY"
send_draft "partnerships@ionq.com" \
    "Agentic calibration loop for IonQ, using NVIDIA Ising + open quantum stack" \
    "$IONQ_BODY"
send_draft "info@quantinuum.com" \
    "Agentic calibration loop for Quantinuum H-series, using NVIDIA Ising + open quantum stack" \
    "$QUANTINUUM_BODY"
send_draft "contact@pasqal.com" \
    "Agentic calibration loop for Pasqal neutral-atom QPUs, using NVIDIA Ising" \
    "$PASQAL_BODY"
send_draft "sales@rigetti.com" \
    "Agentic calibration loop for Rigetti Ankaa, using NVIDIA Ising + open stack" \
    "$RIGETTI_BODY"
send_draft "info@atom-computing.com" \
    "Agentic calibration loop for Atom Computing, using NVIDIA Ising + open stack" \
    "$ATOM_BODY"
send_draft "info@riverlane.com" \
    "Open agentic calibration loop, overlap with your decoder work" \
    "$RIVERLANE_BODY"

echo ""
echo "Done. Review each draft in Mail.app and send individually."
echo "Recommended: space sends across 2-3 days; customize the second paragraph per company."
