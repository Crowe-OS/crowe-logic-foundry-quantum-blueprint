# Quantum trade publication pitches

**When to send:** after GitHub is public and HF Space is live. Ideally after HN or NVIDIA forum activity so you have a signal-of-interest in the subject line.

**General rule:** quantum trade pubs prefer exclusivity. Pitch one at a time. Wait for a response before pitching the next one. If you get declined, pitch the next one.

**Suggested order (highest-fit first):**
1. The Quantum Insider (thequantuminsider.com)
2. Inside Quantum Technology (insidequantumtechnology.com)
3. Quantum Zeitgeist (quantumzeitgeist.com)
4. Global Quantum Intelligence (gqintel.com)

---

## Email template (customize per outlet)

**Subject:** `Pitch: open agentic QPU calibration loop using NVIDIA Ising`

```
Hi <editor first name>,

I am Michael Crowe, founder of Crowe Logic. Quick pitch.

Last month NVIDIA open-sourced Ising Calibration 1, the first open
vision-language model for quantum processor calibration. Important
launch, but on its own Ising is a single-shot inference, not a
workflow.

We just published an Apache 2.0 reference implementation that closes
the loop end-to-end: Ising interprets the trace, our open quantum DSL
stack (Synapse-Lang and Qubit-Flow) authors and executes the corrective
circuit, and an orchestrator pattern handles iteration and operator
escalation.

- GitHub: https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint
- Live demo: https://huggingface.co/spaces/CroweLogic/ising-calibration-blueprint

Story angles that I think fit <outlet name>:

  1. Why the interesting problem in quantum AI right now is not bigger
     models, it is closing the perception-to-action loop against real
     hardware.

  2. How open-source quantum tooling (Synapse-Lang, Qubit-Flow, Ising)
     is starting to assemble into full workflows without any one vendor
     owning the stack.

  3. The vendor-partnership gap: blueprints like this one need QPU
     vendors to test against real devices, and we are openly asking for
     that collaboration.

Happy to write a guest post, be interviewed, or just hand over the repo
for an independent writeup. I would prefer to work with <outlet name>
on this story; let me know if there is interest.

Michael Crowe
Crowe Logic, Inc.
michael@crowelogic.com
```

## Outlet-specific notes

### The Quantum Insider
**Contact:** editors@thequantuminsider.com (backup: LinkedIn to Matt Swayne, the senior writer)
**Preferred angle:** "ecosystem moves" and partnership stories. Lead with the Apache 2.0 framing and the vendor-collaboration ask.
**Lead time:** ~1 week from pitch to publication if accepted.

### Inside Quantum Technology
**Contact:** editor@insidequantumtechnology.com
**Preferred angle:** more business-oriented. Emphasize the operational-cost story (QPU time, recalibration frequency) over the technical architecture.
**Lead time:** ~1-2 weeks.

### Quantum Zeitgeist
**Contact:** contact@quantumzeitgeist.com
**Preferred angle:** accepts community bylines directly. Lowest editorial friction; good for getting the story out even if the higher-tier pubs pass.
**Lead time:** often same-week if you submit a ready-to-publish draft.

### Global Quantum Intelligence
**Contact:** through gqintel.com contact form
**Preferred angle:** paywalled industry intelligence. Different readership (industry analysts, enterprise buyers). Pitch only if Crowe Logic has an enterprise go-to-market angle to share.

## If one of these accepts

- Deliver clean copy, no em dashes, no marketing fluff.
- Include 1-2 images: the loop diagram, a Space screenshot.
- Cite NVIDIA, Hugging Face, the Qiskit/PennyLane/Cirq ecosystem by name.
- Link to the GitHub repo and the HF Space.
- Do not expect a "brand mention alongside Claude Code" from these. That comes later. Their job in this launch is to establish quantum-community credibility that the NVIDIA blog pitch can then reference.
