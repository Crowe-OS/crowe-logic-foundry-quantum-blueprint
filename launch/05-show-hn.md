# Show HN

**Where:** https://news.ycombinator.com/submit
**When:** Tuesday or Wednesday, 7:30 to 9:30 AM Eastern. Avoid Monday (weekend backlog) and Friday (low traffic).

## Title options, ranked

1. `Show HN: Agentic QPU calibration loop using NVIDIA Ising and open quantum DSLs`
2. `Show HN: Open-source agentic quantum processor calibration loop`
3. `Show HN: Wiring NVIDIA's new Ising Calibration VLM into a working agent loop`

Pick #1. It is specific, names the partner, and signals the integration shape. HN rewards specificity over cleverness.

## URL

```
https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint
```

(Not the HF Space. HN readers prefer GitHub as the canonical link; Space goes in the first comment.)

## First comment (post immediately after submission)

```
Author here. Quick context that did not fit in the title:

NVIDIA shipped Ising Calibration 1 (a 35B vision-language model for QPU
calibration) a few weeks ago. It interprets measurement traces and
recommends corrective parameters. Great model. But on its own it is a
single-shot inference, not a workflow.

A real calibration loop also needs to author the corrective pulse
sequence, execute it on a backend, and decide when to iterate vs. escalate
to a human. This blueprint wires that loop end-to-end using two open PyPI
packages we wrote (Synapse-Lang for evaluation, Qubit-Flow for circuit
authoring), Trinity as the execution bridge, and a small agent pattern.

Design notes:

1. Ising's freeform VLM output is parsed into a dataclass with
   experiment_type, classification, severity, recommended_action,
   suggested_parameters, confidence, and rationale. That is the conversion
   from chat to agentic loop.

2. The agent prompt mandates operator escalation when confidence is
   below 0.6. Calibration mistakes waste QPU time at best and damage
   hardware at worst; treating low-confidence findings as a pause
   rather than proceed is the pattern real labs will want.

3. Runs in mock mode with zero credentials. Live mode flips to
   build.nvidia.com's NIM endpoint via NVIDIA_API_KEY. The split matters
   because "works on your laptop after git clone" is how research tools
   actually get adopted.

4. Converges on the synthetic sample trace in 2 iterations. That is
   contrived (the mock is iteration-aware) but the shape is real and the
   live version will behave similarly for well-posed calibration
   problems.

Happy to answer questions about: the Qubit-Flow DSL shape, why we parse
VLM output into a dataclass instead of passing strings around, the
orchestrator pattern, how this extends to the Ising Decoding path, or
why Apache 2.0 instead of more restrictive licensing.

Hugging Face Space (mock mode, no credentials needed):
https://huggingface.co/spaces/CroweLogic/ising-calibration-blueprint
```

## After submission

- Reply to every early comment within the first hour. HN ranking heavily weights author engagement early.
- If someone points out a real bug, acknowledge it in-thread and open a GitHub issue linking the comment.
- Do not ask friends to upvote. HN detects and penalizes coordinated voting rings.
- Do not resubmit if the post does not take off. One chance per story.
