# QPU vendor outreach emails

**Send from:** mike@southwestmushrooms.com
**When:** 2-3 days after the GitHub repo and HF Space are public, so recipients can verify the work is real.
**Subject template:** `Agentic calibration loop for <company>, using NVIDIA Ising + open quantum stack`

Each email is ~150 words. Long emails to strangers don't get read.

---

## IBM Quantum

**To:** research-collaborations@us.ibm.com (also worth direct-pinging Blake Johnson or Jay Gambetta on LinkedIn after sending)
**Subject:** `Agentic calibration loop for IBM Quantum, using NVIDIA Ising + open quantum stack`

```
Hi IBM Quantum team,

I am Michael Crowe, founder of Crowe Logic. We just published an
Apache 2.0 reference implementation of an end-to-end agentic QPU
calibration loop: NVIDIA Ising Calibration 1 for physical-layer
interpretation, plus our open quantum DSL stack (Synapse-Lang and
Qubit-Flow on PyPI) for authoring and executing corrective circuits,
plus an orchestrator pattern that handles iteration and operator
escalation.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Today it runs against synthetic superconducting-qubit traces. To matter,
it needs to run against real devices. I would love to test this against
an IBM Quantum backend, ideally one of the Eagle or Heron systems via
Qiskit Runtime.

What is the right path to do that? Research collaboration, IBM Quantum
Network access, or something else? Happy to share more detail on the
orchestrator pattern, or to jump on a call.

Michael Crowe
Crowe Logic, Inc.
mike@southwestmushrooms.com
```

---

## IonQ

**To:** partnerships@ionq.com (backup: info@ionq.com)
**Subject:** `Agentic calibration loop for IonQ, using NVIDIA Ising + open quantum stack`

```
Hi IonQ team,

I am Michael Crowe, founder of Crowe Logic. We published an Apache 2.0
agentic QPU calibration loop last week combining NVIDIA Ising Calibration
1 with an open quantum DSL stack (Synapse-Lang and Qubit-Flow on PyPI) and
an orchestrator pattern that drives iteration and operator escalation.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Ising Calibration was trained across multiple qubit modalities, including
trapped ions, so IonQ is one of the most interesting targets to validate
this against. The blueprint currently runs on synthetic traces; I would
like to test it against real IonQ calibration data.

Is there a path to test this via IonQ Cloud or through a research
collaboration? Also interested in how your calibration workflow handles
drift across long jobs, since that is exactly where this loop shape
earns its keep.

Michael Crowe
Crowe Logic, Inc.
```

---

## Quantinuum

**To:** info@quantinuum.com (backup: LinkedIn message to Ilyas Khan or Rajeeb Hazra)
**Subject:** `Agentic calibration loop for Quantinuum H-series, using NVIDIA Ising + open quantum stack`

```
Hi Quantinuum team,

I am Michael Crowe, founder of Crowe Logic. We just published an open
agentic QPU calibration blueprint using NVIDIA Ising Calibration 1
paired with our open quantum DSL stack (Synapse-Lang, Qubit-Flow). The
loop is Apache 2.0 and runs end-to-end against synthetic traces today.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Quantinuum's H-series ion trap hardware with its long coherence times
and high fidelities is exactly the kind of platform where a calibration
agent can compound value: fewer manual recalibrations, more effective
qubit time per shift, faster iteration on experiments.

What is the right way to test this against an H-series system? Research
collaboration via the Quantinuum Nexus program, or something else?

Michael Crowe
Crowe Logic, Inc.
```

---

## Pasqal

**To:** contact@pasqal.com
**Subject:** `Agentic calibration loop for Pasqal neutral-atom QPUs, using NVIDIA Ising`

```
Hi Pasqal team,

I am Michael Crowe, founder of Crowe Logic. We published an open
agentic calibration loop last week combining NVIDIA Ising Calibration 1
with our open quantum DSL stack (Synapse-Lang, Qubit-Flow on PyPI).

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Ising Calibration was trained on neutral-atom data, among other
modalities. Pasqal's architecture feels like a particularly clean target
for the loop shape. The blueprint is running on synthetic superconducting
traces today; I would like to test it against real Pasqal data.

Is there a path for research collaboration or via the Pasqal Cloud? Also
happy to chat about what primitives you would want to see in the open
layer to make this easier to integrate with Pulser.

Michael Crowe
Crowe Logic, Inc.
```

---

## Rigetti

**To:** sales@rigetti.com (backup: partnerships@rigetti.com)
**Subject:** `Agentic calibration loop for Rigetti Ankaa, using NVIDIA Ising + open stack`

```
Hi Rigetti team,

I am Michael Crowe, founder of Crowe Logic. We published an Apache 2.0
agentic QPU calibration loop using NVIDIA Ising Calibration 1 plus our
open quantum DSL stack (Synapse-Lang and Qubit-Flow on PyPI).

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Calibration stability is one of the hardest superconducting-qubit
problems, and one of the biggest costs. This loop aims to drop human-in-
the-loop time per experiment by closing the trace-to-circuit-to-execute
cycle with an agent. Today it runs on synthetic traces; I would like to
validate it against the Ankaa-3 system via QCS.

What is the right path? QCS research access, a research collaboration,
or a direct pilot?

Michael Crowe
Crowe Logic, Inc.
```

---

## Atom Computing

**To:** info@atom-computing.com
**Subject:** `Agentic calibration loop for Atom Computing, using NVIDIA Ising + open stack`

```
Hi Atom Computing team,

I am Michael Crowe, founder of Crowe Logic. We published an open
agentic QPU calibration blueprint combining NVIDIA Ising Calibration 1
with Synapse-Lang, Qubit-Flow, and an orchestrator pattern for iteration
and operator escalation.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

Atom Computing's scale target (thousands of qubits in a system) is
exactly the regime where human-in-the-loop calibration stops being
viable and closed-loop agent calibration becomes necessary infrastructure.

Is there a path to test this against your platform, via research
collaboration or early access? Also happy to discuss what you would want
to see in the open layer to make it production-viable for your scale.

Michael Crowe
Crowe Logic, Inc.
```

---

## Riverlane

**To:** info@riverlane.com (backup: LinkedIn message to Steve Brierley or Earl Campbell)
**Subject:** `Open agentic calibration loop, overlap with your decoder work`

```
Hi Riverlane team,

I am Michael Crowe, founder of Crowe Logic. We published an Apache 2.0
agentic QPU calibration blueprint last week using NVIDIA Ising
Calibration 1 plus our open quantum DSL stack.

Repo: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint

The reason I am reaching out to Riverlane specifically: the blueprint is
currently calibration-side, but the natural next step is to add Ising
Decoding (the 3D CNN QEC decoders NVIDIA shipped alongside) into the
same orchestrator. Riverlane has deep expertise in real-time decoding
and the DeltaFlow-on-ASIC story is complementary rather than competitive
with an open agentic top-layer.

Curious whether there is a collaboration shape where our open
orchestrator pattern meets your production decoder infrastructure.

Michael Crowe
Crowe Logic, Inc.
```

## Rules for all of these

- Send one at a time, a few per day. Batch-sending identical-shaped emails flags as outbound marketing.
- Customize the second paragraph for each company's specific hardware or product name. Generic pitches get ignored.
- If you get a response, reply within 24 hours. Momentum dies fast.
- Track responses in a simple spreadsheet: company, contact, date sent, status, follow-up date.
