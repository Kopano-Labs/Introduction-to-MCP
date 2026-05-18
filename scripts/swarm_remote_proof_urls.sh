#!/usr/bin/env bash
# Swarm remote proof — print GitHub URLs + optional curl probes (no gh auth).
# Requires: git, curl. Run from repo root or anywhere inside the clone.
#
# Usage:
#   bash scripts/swarm_remote_proof_urls.sh
#   bash scripts/swarm_remote_proof_urls.sh --probe
# Override owner/repo if origin is not GitHub HTTPS/SSH:
#   GITHUB_OWNER=RobynAwesome GITHUB_REPO=Introduction-to-MCP bash scripts/swarm_remote_proof_urls.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${ROOT}" ]]; then
  echo "error: not inside a git repository" >&2
  exit 2
fi
cd "${ROOT}"

ORIGIN="$(git remote get-url origin 2>/dev/null || true)"
BRANCH="$(git branch --show-current 2>/dev/null || echo "")"
FULL_SHA="$(git rev-parse HEAD 2>/dev/null || echo "")"
SHORT_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo "")"

OWNER="${GITHUB_OWNER:-}"
REPO="${GITHUB_REPO:-}"

if [[ -z "${OWNER}" || -z "${REPO}" ]]; then
  if [[ "${ORIGIN}" =~ github\.com[:/]([^/]+)/([^/]+)$ ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]%.git}"
  fi
fi

if [[ -z "${OWNER}" || -z "${REPO}" ]]; then
  echo "error: could not parse owner/repo from origin: ${ORIGIN}" >&2
  echo "Set GITHUB_OWNER and GITHUB_REPO, or use a github.com HTTPS/SSH remote." >&2
  exit 1
fi

PROBE=0
if [[ "${1:-}" == "--probe" ]]; then
  PROBE=1
fi

BASE="https://github.com/${OWNER}/${REPO}"

echo "=== Swarm remote proof checklist (open in browser) ==="
echo ""
echo "Repo:           ${BASE}"
echo "Branch tree:    ${BASE}/tree/${BRANCH}"
echo "Commit (short): ${BASE}/commit/${SHORT_SHA}"
echo "Commit (full):  ${BASE}/commit/${FULL_SHA}"
echo "Actions (CI):   ${BASE}/actions"
echo "Compare to upstream (adjust branches):"
echo "  ${BASE}/compare/master...${BRANCH}?expand=1"
echo ""
echo "Git (local facts)"
echo "  origin: ${ORIGIN}"
echo "  branch: ${BRANCH}"
echo "  HEAD:   ${FULL_SHA}"
echo ""

if [[ "${PROBE}" -eq 1 ]]; then
  echo "=== curl probes (public API, unauthenticated) ==="
  api_repo="https://api.github.com/repos/${OWNER}/${REPO}"
  api_commit="https://api.github.com/repos/${OWNER}/${REPO}/commits/${FULL_SHA}"
  code_repo="$(curl -sS -H "Accept: application/vnd.github+json" -o /dev/null -w "%{http_code}" "${api_repo}" || echo "000")"
  code_commit="$(curl -sS -H "Accept: application/vnd.github+json" -o /dev/null -w "%{http_code}" "${api_commit}" || echo "000")"
  echo "  GET ${api_repo}  -> HTTP ${code_repo}  (200 = repo visible to anonymous API)"
  echo "  GET ${api_commit} -> HTTP ${code_commit} (200 = commit reachable on GitHub for that owner/repo)"
  if [[ "${code_repo}" != "200" ]]; then
    echo "  Note: 403/404 here often means the repo is private without a token, or the path is wrong." >&2
  fi
  if [[ "${code_commit}" != "200" ]]; then
    echo ""
    echo "  If commit is 404: object is not on ${OWNER}/${REPO} (unpushed, wrong remote, or wrong fork)." >&2
  fi
  echo ""
  echo "=== Kopano host probes (public HTTPS) ==="
  for u in \
    "https://context.kopanolabs.com/" \
    "https://kopanolabs.com/" \
    "https://kopanocontext.kopanolabs.com/"; do
    code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 10 "${u}" || echo "000")"
    echo "  GET ${u} -> HTTP ${code}"
  done
  echo "  See docs/swarm-ops/VERIFIED_ENDPOINTS.md for interpretation (000 often = DNS failure)."
  echo ""
fi

echo "Tip: if your public fork is RobynAwesome but origin is Kopano-Labs, re-run with:"
echo "  GITHUB_OWNER=RobynAwesome GITHUB_REPO=Introduction-to-MCP bash scripts/swarm_remote_proof_urls.sh --probe"
