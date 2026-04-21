# Hugging Face Space upload

The Space is fully scaffolded under `hf_space/` in the repo. Uploading requires a one-time `hf auth login` because the HF CLI needs your token.

## One-time setup

Create a write token at: https://huggingface.co/settings/tokens (type: **Write**)

Then:

```bash
hf auth login
# paste the Write token when prompted
```

## Upload command

From the repository root:

```bash
# Create the Space (first time only)
hf repo create CroweLogic/ising-calibration-blueprint --repo-type space --space-sdk gradio

# Push everything in hf_space/ to the Space
hf upload CroweLogic/ising-calibration-blueprint hf_space/ --repo-type space
```

The Space will build automatically on free CPU hardware and be live in ~3 minutes at:
**https://huggingface.co/spaces/CroweLogic/ising-calibration-blueprint**

## Enabling live mode (optional)

After the Space is up, add `NVIDIA_API_KEY` as a Space secret via the Space Settings page. The live-mode checkbox will become interactive automatically. Get a key at https://build.nvidia.com (free tier available).

## Promoting the Space

Once the Space is live, do two things:

1. On the [Ising Calibration 1 model card](https://huggingface.co/nvidia/ising-calibration-1) Community tab, post a short note: "Built a reproducible agentic calibration loop using this model. Apache 2.0, runs in mock mode with no credentials: [link to Space]." This is how the Ising team discovers you organically.

2. Add the Space link to the GitHub README under Quickstart as an alternative to local install.

## Note on org name

`CroweLogic` as the HF namespace matches the brand. If it is unavailable or already taken by someone else, fall back to `Crowe-OS` (matching GitHub) or `MichaelCrowe11` (personal).
