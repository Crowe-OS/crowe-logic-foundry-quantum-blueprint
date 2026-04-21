#!/usr/bin/env bash
#
# traction.sh
#
# Prints a dashboard of public traction signals for the blueprint.
# Run daily during launch week, weekly thereafter.

set -euo pipefail

REPO="Crowe-OS/crowe-logic-foundry-quantum-blueprint"
SPACE="CroweLogic/ising-calibration-blueprint"

printf "\n=== Crowe Logic Quantum Blueprint Traction ===\n\n"
printf "%-30s %s\n" "Timestamp" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# GitHub
printf "%-30s " "GitHub stars"
gh api "repos/${REPO}" --jq '.stargazers_count'
printf "%-30s " "GitHub forks"
gh api "repos/${REPO}" --jq '.forks_count'
printf "%-30s " "GitHub watchers"
gh api "repos/${REPO}" --jq '.subscribers_count'
printf "%-30s " "Open issues"
gh api "repos/${REPO}" --jq '.open_issues_count'
printf "%-30s " "Release downloads (v0.1.0)"
gh api "repos/${REPO}/releases/tags/v0.1.0" --jq '[.assets[].download_count] | add // 0' 2>/dev/null || echo "n/a"

# Recent traffic (requires push auth on repo, which we have)
echo ""
echo "Last 14 days (GitHub traffic)"
gh api "repos/${REPO}/traffic/views" --jq '"  views:       \(.count) / unique: \(.uniques)"' 2>/dev/null || echo "  n/a"
gh api "repos/${REPO}/traffic/clones" --jq '"  clones:      \(.count) / unique: \(.uniques)"' 2>/dev/null || echo "  n/a"

# Recent commits
echo ""
echo "Latest commits on main"
gh api "repos/${REPO}/commits?per_page=3" \
    --jq '.[] | "  \(.commit.committer.date[0:10])  \(.sha[0:7])  \(.commit.message | split("\n")[0])"'

# Stargazers list (top 10)
echo ""
echo "Most recent stargazers"
gh api "repos/${REPO}/stargazers" -H "Accept: application/vnd.github.star+json" --jq '.[-10:] | reverse | .[] | "  \(.starred_at[0:10])  \(.user.login)"' 2>/dev/null || echo "  none yet"

# HF Space stats
echo ""
printf "%-30s " "HF Space status"
if curl -sSL -o /dev/null -w "%{http_code}" "https://huggingface.co/spaces/${SPACE}" | grep -q "200"; then
    echo "live: https://huggingface.co/spaces/${SPACE}"
else
    echo "not yet uploaded"
fi

echo ""
echo "=============================================="
