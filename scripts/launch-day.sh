#!/usr/bin/env bash
#
# launch-day.sh
#
# Orchestrates the manual portions of the launch by opening every target
# URL in your default browser with fields pre-filled wherever the target
# supports it (HN, X, HF Space creation, NVIDIA forum new-topic).
#
# Call with a step name, or "all" to walk the full sequence with pauses.
# All steps are idempotent; re-running only re-opens tabs.
#
# Usage:
#   ./scripts/launch-day.sh hn
#   ./scripts/launch-day.sh x
#   ./scripts/launch-day.sh forum
#   ./scripts/launch-day.sh hf-space
#   ./scripts/launch-day.sh hf-blog-fork
#   ./scripts/launch-day.sh inception
#   ./scripts/launch-day.sh all

set -euo pipefail

REPO_URL="https://github.com/Crowe-OS/crowe-logic-foundry-quantum-blueprint"
SPACE_URL="https://huggingface.co/spaces/CroweLogic/ising-calibration-blueprint"

open_url() {
    # macOS uses `open`, Linux uses `xdg-open`.
    if command -v open >/dev/null 2>&1; then
        open "$1"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$1"
    else
        echo "Open this URL manually: $1"
    fi
}

# urlencode via python3 (available on all supported platforms)
urlencode() {
    python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=''))" "$1"
}

pause() {
    read -r -p "--> Press ENTER when that step is done (or ctrl-c to stop): " _
}

###############################################################################
# Step: Show HN submission
###############################################################################

step_hn() {
    local title="Show HN: Agentic QPU calibration loop using NVIDIA Ising and open quantum DSLs"
    local url="${REPO_URL}"
    local hn_url="https://news.ycombinator.com/submitlink?t=$(urlencode "$title")&u=$(urlencode "$url")"
    echo ""
    echo "=== Show HN ==="
    echo "Opening HN submit page with title and URL pre-filled."
    echo ""
    echo "After submission, immediately paste this as the first comment:"
    echo "  launch/05-show-hn.md (search for 'First comment')"
    echo ""
    # Also copy the first comment to clipboard so pasting is one command.
    if command -v pbcopy >/dev/null 2>&1; then
        awk '/^## First comment/{flag=1; next} /^##/{flag=0} flag' launch/05-show-hn.md \
            | sed -n '/^```$/,/^```$/p' \
            | sed '1d;$d' \
            | pbcopy
        echo "(First comment has been copied to clipboard.)"
    fi
    open_url "$hn_url"
}

###############################################################################
# Step: X thread
###############################################################################

step_x() {
    echo ""
    echo "=== X thread ==="
    echo "Opening X compose with post 1 pre-filled."
    echo "After posting, reply to your own post to thread posts 2-7."
    echo "Full thread copy is in launch/06-x-thread.md"
    echo ""
    local post1="We built an open-source agentic loop that uses NVIDIA's new Ising Calibration 1 VLM to drive a complete quantum processor calibration workflow end to end.

Trace in. Corrective circuit out. Executed. Iterated until within spec.

Apache 2.0.

${REPO_URL}"
    local intent="https://x.com/intent/post?text=$(urlencode "$post1")"
    open_url "$intent"
    if command -v pbcopy >/dev/null 2>&1; then
        awk '/^### Post 2/{flag=1; next} /^### Post 3/{exit} flag' launch/06-x-thread.md \
            | sed -n '/^```$/,/^```$/p' \
            | sed '1d;$d' \
            | pbcopy
        echo "(Post 2 is now on your clipboard. After sending post 1, reply to it and paste.)"
    fi
}

###############################################################################
# Step: NVIDIA Developer Forum
###############################################################################

step_forum() {
    echo ""
    echo "=== NVIDIA Developer Forum ==="
    echo "Opening the NeMo category new-topic page."
    echo "Body is in launch/03-nvidia-forum-post.md (between ## Body fences)"
    if command -v pbcopy >/dev/null 2>&1; then
        awk '/^## Body/{flag=1; next} /^## After/{exit} flag' launch/03-nvidia-forum-post.md \
            | sed -n '/^```$/,/^```$/p' \
            | sed '1d;$d' \
            | pbcopy
        echo "(Post body copied to clipboard.)"
    fi
    open_url "https://forums.developer.nvidia.com/c/ai-data-science/nemo/65"
}

###############################################################################
# Step: Hugging Face Space upload
###############################################################################

step_hf_space() {
    echo ""
    echo "=== Hugging Face Space ==="
    echo ""
    if ! command -v hf >/dev/null 2>&1; then
        echo "hf CLI not found. Install with: pip install -U huggingface_hub"
        return 1
    fi
    if ! hf auth whoami >/dev/null 2>&1; then
        echo "Not logged in to Hugging Face."
        echo "Create a Write token at: https://huggingface.co/settings/tokens"
        open_url "https://huggingface.co/settings/tokens"
        echo ""
        echo "Then run:  hf auth login"
        echo "Then re-run this script:  ./scripts/launch-day.sh hf-space"
        return 1
    fi
    echo "Logged in as: $(hf auth whoami 2>/dev/null | head -1)"
    echo "Creating Space (idempotent; ok if already exists)..."
    hf repo create CroweLogic/ising-calibration-blueprint \
        --repo-type space --space-sdk gradio 2>&1 | tail -3 || true
    echo "Uploading hf_space/ contents..."
    hf upload CroweLogic/ising-calibration-blueprint hf_space/ --repo-type space
    echo ""
    echo "Space live at: ${SPACE_URL}"
    open_url "${SPACE_URL}"
}

###############################################################################
# Step: Fork huggingface/blog and stage the blog PR branch
###############################################################################

step_hf_blog_fork() {
    echo ""
    echo "=== Hugging Face Blog PR staging ==="
    if ! command -v gh >/dev/null 2>&1; then
        echo "gh CLI not found."
        return 1
    fi
    local fork_dir="${HOME}/Projects/hf-blog-fork"
    if [ ! -d "${fork_dir}" ]; then
        echo "Forking huggingface/blog to your account and cloning to ${fork_dir}..."
        gh repo fork huggingface/blog --clone=false
        git clone "git@github.com:$(gh api user --jq .login)/blog.git" "${fork_dir}"
    fi
    cd "${fork_dir}"
    git fetch origin
    git checkout -b crowe-logic-ising-blueprint 2>/dev/null || git checkout crowe-logic-ising-blueprint
    local dest="_blog/2026-04-22-agentic-qpu-calibration-ising.md"
    # Extract the body (between the two ```markdown fences) from our draft.
    awk '/^## Submission body/{flag=1; next} /^## Submission steps/{exit} flag' \
        "${OLDPWD:-${HOME}/Projects/crowe-logic-foundry-quantum-blueprint}/launch/04-hf-blog-draft.md" \
        | sed -n '/^```markdown$/,/^```$/p' \
        | sed '1d;$d' > "${dest}"
    git add "${dest}"
    git commit -m "Add blog post: Closing the Quantum Calibration Loop" 2>&1 | tail -2 || true
    echo ""
    echo "Branch staged at ${fork_dir} on branch crowe-logic-ising-blueprint."
    echo "To open the PR (review the diff first):"
    echo "  cd ${fork_dir}"
    echo "  git push -u origin crowe-logic-ising-blueprint"
    echo "  gh pr create --repo huggingface/blog --title 'Add blog post: Closing the Quantum Calibration Loop' --body 'Submitting a community blog post on agentic QPU calibration using NVIDIA Ising Calibration 1 paired with open quantum DSLs (Synapse-Lang, Qubit-Flow). Repo: ${REPO_URL}  Space: ${SPACE_URL}'"
}

###############################################################################
# Step: NVIDIA Inception application
###############################################################################

step_inception() {
    echo ""
    echo "=== NVIDIA Inception ==="
    echo "Opening Inception application page."
    echo "All form answers are in launch/10-inception-application.md"
    open_url "https://www.nvidia.com/en-us/startups/"
}

###############################################################################
# Step: email drafts in Mail.app
###############################################################################

step_emails() {
    echo ""
    echo "=== Vendor email drafts ==="
    echo "Creating 7 draft emails in Mail.app. Review and send individually."
    bash "$(dirname "$0")/email-drafts.sh"
}

###############################################################################
# Dispatcher
###############################################################################

usage() {
    cat <<EOF
Usage: $(basename "$0") <step>

Steps:
  hn              Open Show HN submission page with title+url pre-filled
  x               Open X compose with post 1 pre-filled; copy post 2 to clipboard
  forum           Open NVIDIA Developer Forum new-topic; copy body to clipboard
  hf-space        Upload the Hugging Face Space (requires 'hf auth login' first)
  hf-blog-fork    Fork huggingface/blog and stage the community PR branch
  inception       Open the NVIDIA Inception application page
  emails          Create 7 vendor email drafts in Mail.app
  all             Walk the full sequence in order, pausing between each step
EOF
}

case "${1:-}" in
    hn) step_hn ;;
    x) step_x ;;
    forum) step_forum ;;
    hf-space) step_hf_space ;;
    hf-blog-fork) step_hf_blog_fork ;;
    inception) step_inception ;;
    emails) step_emails ;;
    all)
        step_hf_space; pause
        step_forum;    pause
        step_hn;       pause
        step_x;        pause
        step_emails;   pause
        step_hf_blog_fork; pause
        step_inception
        ;;
    *) usage; exit 1 ;;
esac
