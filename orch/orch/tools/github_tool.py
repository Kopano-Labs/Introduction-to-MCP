"""
GitHub API MCP Tool for orch
============================
Capabilities unlocked:
  #3  — Smart commit message generation from staged diff
  #4  — Auto PR review (summary, risks, suggestions)

Place this file at:  orch/orch/tools/github_tool.py
Create empty file:   orch/orch/tools/__init__.py

No extra dependencies — uses only httpx (already in your venv).

Environment variables (.env):
  GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxx
  GITHUB_DEFAULT_OWNER=RobynAwesome
  GITHUB_DEFAULT_REPO=Introduction-to-MCP
"""

from __future__ import annotations

import json
import os
import re
import sys
import textwrap
from typing import Any

import httpx
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings



def _require(value: str, name: str) -> None:
    if not value:
        raise ValueError(
            f"{name} is required. Pass it directly or set "
            f"GITHUB_DEFAULT_{name.upper()} in your .env"
        )
# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class GitHubSettings(BaseSettings):
    github_token: str = Field(..., description="GitHub PAT with repo scope")
    github_default_owner: str = Field("", description="Default repo owner")
    github_default_repo: str = Field("", description="Default repo name")

    model_config = {"env_file": ".env", "extra": "ignore"}


def _settings() -> GitHubSettings:
    return GitHubSettings()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Raw HTTP client (httpx only — no PyGithub)
# ---------------------------------------------------------------------------

class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self, token: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self._diff_headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get(self, path: str, diff: bool = False) -> httpx.Response:
        headers = self._diff_headers if diff else self._headers
        url = f"{self.BASE}{path}"
        resp = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
        if resp.status_code >= 400:
            raise RuntimeError(
                f"GitHub API {resp.status_code} — {path}\n{resp.text[:400]}"
            )
        return resp

    def _post(self, path: str, body: dict) -> httpx.Response:
        url = f"{self.BASE}{path}"
        resp = httpx.post(
            url, headers=self._headers,
            content=json.dumps(body), timeout=30
        )
        if resp.status_code >= 400:
            raise RuntimeError(
                f"GitHub API {resp.status_code} — {path}\n{resp.text[:400]}"
            )
        return resp

    def get_pr(self, owner: str, repo: str, pr_number: int) -> dict:
        return self._get(f"/repos/{owner}/{repo}/pulls/{pr_number}").json()

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        return self._get(
            f"/repos/{owner}/{repo}/pulls/{pr_number}", diff=True
        ).text

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        return self._get(
            f"/repos/{owner}/{repo}/pulls/{pr_number}/files"
        ).json()

    def get_commit_diff(self, owner: str, repo: str, sha: str) -> str:
        return self._get(
            f"/repos/{owner}/{repo}/commits/{sha}", diff=True
        ).text

    def list_open_prs(self, owner: str, repo: str) -> list[dict]:
        return self._get(f"/repos/{owner}/{repo}/pulls?state=open").json()

    def post_pr_comment(
        self, owner: str, repo: str, pr_number: int, body: str
    ) -> str:
        resp = self._post(
            f"/repos/{owner}/{repo}/issues/{pr_number}/comments",
            {"body": body}
        )
        return resp.json().get("html_url", "")


# ---------------------------------------------------------------------------
# Capability #4 — PR Review
# ---------------------------------------------------------------------------

class PRReviewResult(BaseModel):
    pr_number: int
    title: str
    author: str
    summary: str
    risk_level: str
    risks: list[str]
    suggestions: list[str]
    changed_files: int
    additions: int
    deletions: int
    diff_preview: str


def review_pull_request(
    pr_number: int,
    owner: str = "",
    repo: str = "",
    post_comment: bool = False,
) -> PRReviewResult:
    """
    Capability #4 — Auto PR Review.

    Args:
        pr_number:    GitHub PR number to review.
        owner:        Repo owner (falls back to GITHUB_DEFAULT_OWNER).
        repo:         Repo name  (falls back to GITHUB_DEFAULT_REPO).
        post_comment: If True, posts the review as a PR comment on GitHub.
    """
    cfg = _settings()
    owner = owner or cfg.github_default_owner
    repo  = repo  or cfg.github_default_repo
    _require(owner, "owner")
    _require(repo,  "repo")

    client = GitHubClient(cfg.github_token)
    pr   = client.get_pr(owner, repo, pr_number)
    diff = client.get_pr_diff(owner, repo, pr_number)

    additions     = pr.get("additions", 0)
    deletions     = pr.get("deletions", 0)
    changed_files = pr.get("changed_files", 0)

    risk_level, risks = _assess_risk(additions, deletions, changed_files, diff)
    suggestions       = _build_suggestions(pr, diff)
    summary           = _summarise_pr(pr, client, owner, repo, pr_number)

    result = PRReviewResult(
        pr_number     = pr["number"],
        title         = pr["title"],
        author        = pr["user"]["login"],
        summary       = summary,
        risk_level    = risk_level,
        risks         = risks,
        suggestions   = suggestions,
        changed_files = changed_files,
        additions     = additions,
        deletions     = deletions,
        diff_preview  = diff[:3000],
    )

    if post_comment:
        body = _format_review_comment(result)
        url  = client.post_pr_comment(owner, repo, pr_number, body)
        print(f"Review posted: {url}")

    return result


def _assess_risk(
    additions: int, deletions: int, changed_files: int, diff: str
) -> tuple[str, list[str]]:
    risks: list[str] = []
    total = additions + deletions

    if total > 1000:
        risks.append(f"Large changeset: +{additions} / -{deletions} lines")
    elif total > 300:
        risks.append(f"Medium changeset: +{additions} / -{deletions} lines")

    if changed_files > 20:
        risks.append(f"High file churn: {changed_files} files changed")

    sensitive = [
        ".env", "secret", "token", "password", "credential",
        "auth", "key", "private", "cert", "pem", "ssh",
    ]
    diff_lower = diff.lower()
    found = [s for s in sensitive if s in diff_lower]
    if found:
        risks.append(f"Sensitive keywords in diff: {', '.join(found)}")

    if "test" not in diff_lower and additions > 50:
        risks.append("No test files in diff — coverage may be lacking")

    if any(kw in diff_lower for kw in ["migrate", "alter table", "drop table", "schema"]):
        risks.append("Database migration or schema change detected")

    if any("sensitive" in r.lower() or "migration" in r.lower() for r in risks):
        level = "CRITICAL" if len(risks) >= 3 else "HIGH"
    elif len(risks) >= 2:
        level = "MEDIUM"
    elif risks:
        level = "LOW"
    else:
        level = "LOW"

    return level, risks or ["No significant risks detected"]


def _build_suggestions(pr: dict, diff: str) -> list[str]:
    suggestions: list[str] = []
    diff_lower = diff.lower()

    if "TODO" in diff or "FIXME" in diff:
        suggestions.append("Resolve TODO/FIXME comments before merging")
    if "print(" in diff and "logger" not in diff_lower:
        suggestions.append("Replace print() with structured logging")
    if "except:" in diff or "except Exception:" in diff:
        suggestions.append("Narrow bare except clauses — catch specific exceptions")
    if "time.sleep" in diff:
        suggestions.append("Replace time.sleep() with async/await or backoff")
    if not pr.get("body") or len((pr.get("body") or "").strip()) < 30:
        suggestions.append("Add a meaningful PR description explaining the 'why'")
    if any(kw in diff for kw in ["localhost", "127.0.0.1", "http://"]):
        suggestions.append("Avoid hardcoded URLs — use config or environment vars")

    return suggestions or ["Code looks clean — no automatic suggestions triggered"]


def _summarise_pr(
    pr: dict, client: GitHubClient, owner: str, repo: str, pr_number: int
) -> str:
    try:
        files   = client.get_pr_files(owner, repo, pr_number)
        names   = [f["filename"] for f in files[:8]]
        preview = ", ".join(names)
        total   = pr.get("changed_files", 0)
        if total > 8:
            preview += f" … (+{total - 8} more)"
    except Exception:
        preview = "(could not enumerate files)"

    additions     = pr.get("additions", 0)
    deletions     = pr.get("deletions", 0)
    changed_files = pr.get("changed_files", 0)
    base          = pr.get("base", {}).get("ref", "?")
    head          = pr.get("head", {}).get("ref", "?")
    author        = pr["user"]["login"]

    return (
        f"PR #{pr['number']} by @{author} targets `{base}` from `{head}`. "
        f"Changes: +{additions} / -{deletions} lines across {changed_files} file(s). "
        f"Files touched: {preview}."
    )


def _format_review_comment(r: PRReviewResult) -> str:
    emoji   = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(r.risk_level, "⚪")
    risks   = "\n".join(f"- {x}" for x in r.risks)
    suggest = "\n".join(f"- {x}" for x in r.suggestions)
    return textwrap.dedent(f"""
        ## 🤖 orch Auto-Review — PR #{r.pr_number}

        **{emoji} Risk level:** `{r.risk_level}`

        ### Summary
        {r.summary}

        ### Risks identified
        {risks}

        ### Suggestions
        {suggest}

        ---
        *Posted automatically by [orch](https://github.com/RobynAwesome/Introduction-to-MCP)*
    """).strip()


# ---------------------------------------------------------------------------
# Capability #3 — Commit Message Generation
# ---------------------------------------------------------------------------

class CommitMessageResult(BaseModel):
    subject:      str
    body:         str
    full_message: str
    type:         str
    scope:        str
    breaking:     bool


def generate_commit_message(
    diff: str | None = None,
    sha:  str | None = None,
    owner: str = "",
    repo:  str = "",
    extra_context: str = "",
) -> CommitMessageResult:
    """
    Capability #3 — Smart commit message generation.

    Pass either:
      - diff : raw unified diff string (e.g. from `git diff --staged`)
      - sha  : commit SHA to fetch from GitHub
    """
    if diff is None and sha:
        cfg   = _settings()
        owner = owner or cfg.github_default_owner
        repo  = repo  or cfg.github_default_repo
        _require(owner, "owner")
        _require(repo,  "repo")
        diff  = GitHubClient(cfg.github_token).get_commit_diff(owner, repo, sha)

    if not diff:
        raise ValueError("Provide either `diff` text or a `sha` to look up.")

    commit_type, scope, breaking = _classify_diff(diff)
    subject = _build_subject(diff, commit_type, scope, breaking)
    body    = _build_body(diff, extra_context, breaking)
    full    = f"{subject}\n\n{body}" if body else subject

    return CommitMessageResult(
        subject=subject, body=body, full_message=full,
        type=commit_type, scope=scope, breaking=breaking,
    )


def _classify_diff(diff: str) -> tuple[str, str, bool]:
    diff_lower = diff.lower()
    breaking   = "breaking change" in diff_lower

    if any(kw in diff_lower for kw in ["migration", "alter table", "drop column"]):
        return "feat", _infer_scope(diff), True
    if "test_" in diff_lower or "_test.py" in diff_lower:
        return "test", _infer_scope(diff), breaking
    if any(kw in diff_lower for kw in ["readme", "docstring"]):
        return "docs", _infer_scope(diff), breaking
    if any(kw in diff_lower for kw in ["github/workflows", "dockerfile", "ci.yml"]):
        return "ci", _infer_scope(diff), breaking
    if any(kw in diff_lower for kw in ["fix", "bug", "error", "exception"]):
        return "fix", _infer_scope(diff), breaking
    if any(kw in diff_lower for kw in ["refactor", "rename", "move", "extract"]):
        return "refactor", _infer_scope(diff), breaking
    if any(kw in diff_lower for kw in ["add ", "new ", "feature", "implement"]):
        return "feat", _infer_scope(diff), breaking
    return "chore", _infer_scope(diff), breaking


def _infer_scope(diff: str) -> str:
    paths    = re.findall(r"diff --git a/(.+?) b/", diff)
    top_dirs = {p.split("/")[0] for p in paths if "/" in p}
    scope_map = {
        "orch": "orch", "tests": "tests", "cli": "cli",
        "tools": "tools", "public": "public", ".github": "ci",
    }
    for d in top_dirs:
        if d in scope_map:
            return scope_map[d]
    return sorted(top_dirs)[0] if top_dirs else ""


def _build_subject(
    diff: str, commit_type: str, scope: str, breaking: bool
) -> str:
    paths   = re.findall(r"diff --git a/(.+?) b/", diff)
    desc    = os.path.splitext(os.path.basename(paths[0]))[0].replace("_", " ") if paths else "update"
    bang    = "!" if breaking else ""
    scope_s = f"({scope})" if scope else ""
    prefix  = f"{commit_type}{scope_s}{bang}: "
    max_d   = 72 - len(prefix)

    added = [
        line[1:].strip() for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
        and len(line) > 5
        and not line[1:].strip().startswith(("#", '"""', "'''"))
    ]
    if added:
        candidate = added[0][:max_d].lower()
        for noise in ["def ", "class ", "import ", "from ", "return ", "self."]:
            candidate = candidate.replace(noise, "")
        desc = candidate.strip() or desc

    return f"{prefix}{desc[:max_d].rstrip(',. ')}"


def _build_body(diff: str, extra_context: str, breaking: bool) -> str:
    added   = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))
    lines   = [f"Changes: +{added} / -{removed} lines"]
    if breaking:
        lines += ["", "BREAKING CHANGE: review migration steps before deploying."]
    if extra_context:
        lines += ["", extra_context]
    return "\n".join(
        w for line in lines
        for w in (textwrap.wrap(line, 72) if len(line) > 72 else [line])
    )


# ---------------------------------------------------------------------------
# MCP Tool Registration
# ---------------------------------------------------------------------------

def get_mcp_tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "github_review_pr",
            "description": (
                "Review a GitHub Pull Request. Returns risk assessment, "
                "summary, and actionable suggestions. Optionally posts as a PR comment."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pr_number":    {"type": "integer", "description": "PR number to review"},
                    "owner":        {"type": "string",  "description": "GitHub repo owner"},
                    "repo":         {"type": "string",  "description": "GitHub repo name"},
                    "post_comment": {"type": "boolean", "description": "Post review as GitHub comment", "default": False},
                },
                "required": ["pr_number"],
            },
        },
        {
            "name": "github_generate_commit_message",
            "description": (
                "Generate a Conventional Commits message from a diff. "
                "Pass raw diff text or a commit SHA to look up from GitHub."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "diff":          {"type": "string", "description": "Raw unified diff text"},
                    "sha":           {"type": "string", "description": "Commit SHA"},
                    "owner":         {"type": "string", "description": "Repo owner (needed for SHA)"},
                    "repo":          {"type": "string", "description": "Repo name (needed for SHA)"},
                    "extra_context": {"type": "string", "description": "Optional hint e.g. 'Closes #42'"},
                },
                "required": [],
            },
        },
    ]


def dispatch_mcp_call(tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "github_review_pr":
        return review_pull_request(**tool_input).model_dump()
    if tool_name == "github_generate_commit_message":
        return generate_commit_message(**tool_input).model_dump()
    raise ValueError(f"Unknown tool: {tool_name}")


# ---------------------------------------------------------------------------
# CLI quick-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "review" and len(sys.argv) >= 3:
        result = review_pull_request(int(sys.argv[2]), post_comment="--post" in sys.argv)
        print(json.dumps(result.model_dump(), indent=2))

    elif cmd == "commit" and len(sys.argv) >= 3:
        arg    = sys.argv[2]
        result = generate_commit_message(sha=arg) if len(arg) == 40 else generate_commit_message(diff=arg)
        print(result.full_message)

    elif cmd == "commit-stdin":
        result = generate_commit_message(diff=sys.stdin.read())
        print(result.full_message)

    else:
        print(
            "Usage:\n"
            "  python github_tool.py review <PR_NUMBER> [--post]\n"
            "  python github_tool.py commit <SHA>\n"
            "  git diff --staged | python github_tool.py commit-stdin\n"
        )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _require(value: str, name: str) -> None:
    if not value:
        raise ValueError(
            f"`{name}` is required. Pass it directly or set "
            f"GITHUB_DEFAULT_{name.upper()} in your .env"
        )