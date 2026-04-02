"""
GitHub API MCP Tool for orch
============================
Capabilities unlocked:
  #3  — Smart commit message generation from staged diff
  #4  — Auto PR review (summary, risks, suggestions)

Drop this file at:  orch/tools/github_tool.py
Register it in:     orch/tools/__init__.py  (see bottom of file)

Requirements (add to pyproject.toml dependencies):
  "PyGithub>=2.1.1",

Environment variables (.env):
  GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx   # classic PAT or fine-grained
  GITHUB_DEFAULT_OWNER=RobynAwesome        # optional default org/user
  GITHUB_DEFAULT_REPO=Introduction-to-MCP  # optional default repo
"""

from __future__ import annotations

import os
import textwrap
from typing import Any

import httpx
from github import Github, GithubException
from github.PullRequest import PullRequest
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class GitHubSettings(BaseSettings):
    github_token: str = Field(..., description="GitHub PAT with repo scope")
    github_default_owner: str = Field("", description="Default repo owner")
    github_default_repo: str = Field("", description="Default repo name")

    model_config = {"env_file": ".env", "extra": "ignore"}


def _settings() -> GitHubSettings:
    """Lazy-load settings so import doesn't fail if .env is missing."""
    return GitHubSettings()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Low-level GitHub client helper
# ---------------------------------------------------------------------------

class GitHubClient:
    """Thin wrapper around PyGithub + raw httpx for diff fetching."""

    def __init__(self, token: str) -> None:
        self._token = token
        self._gh = Github(token)

    def get_repo(self, owner: str, repo: str):
        return self._gh.get_repo(f"{owner}/{repo}")

    def get_pr(self, owner: str, repo: str, pr_number: int) -> PullRequest:
        return self.get_repo(owner, repo).get_pull(pr_number)

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch the raw unified diff for a PR via the GitHub API."""
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text

    def get_commit_diff(self, owner: str, repo: str, sha: str) -> str:
        """Fetch the diff for a specific commit SHA."""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text

    def list_open_prs(self, owner: str, repo: str) -> list[dict]:
        repo_obj = self.get_repo(owner, repo)
        return [
            {
                "number": pr.number,
                "title": pr.title,
                "author": pr.user.login,
                "base": pr.base.ref,
                "head": pr.head.ref,
                "created_at": pr.created_at.isoformat(),
                "changed_files": pr.changed_files,
                "additions": pr.additions,
                "deletions": pr.deletions,
            }
            for pr in repo_obj.get_pulls(state="open")
        ]

    def post_pr_comment(
        self, owner: str, repo: str, pr_number: int, body: str
    ) -> str:
        pr = self.get_pr(owner, repo, pr_number)
        comment = pr.create_issue_comment(body)
        return comment.html_url


# ---------------------------------------------------------------------------
# Capability #4 — PR Review
# ---------------------------------------------------------------------------

class PRReviewResult(BaseModel):
    pr_number: int
    title: str
    author: str
    summary: str
    risk_level: str          # LOW | MEDIUM | HIGH | CRITICAL
    risks: list[str]
    suggestions: list[str]
    changed_files: int
    additions: int
    deletions: int
    diff_preview: str        # first 3000 chars of diff for context


def review_pull_request(
    pr_number: int,
    owner: str = "",
    repo: str = "",
    post_comment: bool = False,
) -> PRReviewResult:
    """
    Capability #4 — Auto PR Review.

    Fetches the PR metadata and diff, then produces a structured review
    with a risk assessment, summary, and actionable suggestions.

    Args:
        pr_number:    GitHub PR number to review.
        owner:        Repo owner (falls back to GITHUB_DEFAULT_OWNER).
        repo:         Repo name  (falls back to GITHUB_DEFAULT_REPO).
        post_comment: If True, posts the review as a PR comment on GitHub.

    Returns:
        PRReviewResult — structured review ready to pass to agents.
    """
    cfg = _settings()
    owner = owner or cfg.github_default_owner
    repo = repo or cfg.github_default_repo
    _require(owner, "owner")
    _require(repo, "repo")

    client = GitHubClient(cfg.github_token)

    try:
        pr = client.get_pr(owner, repo, pr_number)
        diff = client.get_pr_diff(owner, repo, pr_number)
    except GithubException as exc:
        raise RuntimeError(f"GitHub API error: {exc.status} — {exc.data}") from exc

    # --- Heuristic risk scoring -------------------------------------------
    risk_level, risks = _assess_risk(pr, diff)

    # --- Build suggestions ---------------------------------------------------
    suggestions = _build_suggestions(pr, diff)

    # --- Summary -------------------------------------------------------------
    summary = _summarise_pr(pr, diff)

    result = PRReviewResult(
        pr_number=pr.number,
        title=pr.title,
        author=pr.user.login,
        summary=summary,
        risk_level=risk_level,
        risks=risks,
        suggestions=suggestions,
        changed_files=pr.changed_files,
        additions=pr.additions,
        deletions=pr.deletions,
        diff_preview=diff[:3000],
    )

    if post_comment:
        body = _format_review_comment(result)
        url = client.post_pr_comment(owner, repo, pr_number, body)
        print(f"✅ Review posted: {url}")

    return result


def _assess_risk(pr: PullRequest, diff: str) -> tuple[str, list[str]]:
    """Return (risk_level, list_of_risk_reasons) based on heuristics."""
    risks: list[str] = []

    # Size risk
    if pr.additions + pr.deletions > 1000:
        risks.append(f"Large changeset: +{pr.additions} / -{pr.deletions} lines")
    elif pr.additions + pr.deletions > 300:
        risks.append(f"Medium changeset: +{pr.additions} / -{pr.deletions} lines")

    # File count risk
    if pr.changed_files > 20:
        risks.append(f"High file churn: {pr.changed_files} files changed")

    # Sensitive paths
    sensitive = [
        ".env", "secret", "token", "password", "credential",
        "auth", "key", "private", "cert", "pem", "ssh",
    ]
    diff_lower = diff.lower()
    found_sensitive = [s for s in sensitive if s in diff_lower]
    if found_sensitive:
        risks.append(
            f"Sensitive keywords in diff: {', '.join(found_sensitive)}"
        )

    # Test coverage signal
    if "test" not in diff_lower and pr.additions > 50:
        risks.append("No test files appear in diff — coverage may be lacking")

    # Migration / schema changes
    if any(kw in diff_lower for kw in ["migrate", "alter table", "drop table", "schema"]):
        risks.append("Database migration or schema change detected")

    # Determine overall level
    if any("Sensitive" in r or "migration" in r.lower() for r in risks):
        level = "CRITICAL" if len(risks) >= 3 else "HIGH"
    elif len(risks) >= 2:
        level = "MEDIUM"
    elif risks:
        level = "LOW"
    else:
        level = "LOW"

    return level, risks or ["No significant risks detected"]


def _build_suggestions(pr: PullRequest, diff: str) -> list[str]:
    suggestions: list[str] = []
    diff_lower = diff.lower()

    if "TODO" in diff or "FIXME" in diff:
        suggestions.append("Resolve TODO/FIXME comments before merging")

    if "print(" in diff and "logger" not in diff_lower:
        suggestions.append("Replace print() statements with structured logging")

    if "except:" in diff or "except Exception:" in diff:
        suggestions.append("Narrow bare except clauses — catch specific exceptions")

    if "time.sleep" in diff:
        suggestions.append("Replace time.sleep() with async/await or exponential backoff")

    if not pr.body or len(pr.body.strip()) < 30:
        suggestions.append("Add a meaningful PR description explaining the 'why'")

    if pr.changed_files > 10 and not suggestions:
        suggestions.append("Consider splitting this PR into smaller, focused changes")

    if "hardcoded" in diff_lower or any(
        kw in diff for kw in ["localhost", "127.0.0.1", "http://"]
    ):
        suggestions.append("Avoid hardcoded URLs/IPs — use config or environment vars")

    return suggestions or ["Code looks clean — no automatic suggestions triggered"]


def _summarise_pr(pr: PullRequest, diff: str) -> str:
    files_preview = ""
    try:
        file_names = [f.filename for f in pr.get_files()][:8]
        files_preview = ", ".join(file_names)
        if pr.changed_files > 8:
            files_preview += f" … (+{pr.changed_files - 8} more)"
    except Exception:
        files_preview = "(could not enumerate files)"

    return (
        f"PR #{pr.number} by @{pr.user.login} targets `{pr.base.ref}` "
        f"from `{pr.head.ref}`. "
        f"Changes: +{pr.additions} / -{pr.deletions} lines across "
        f"{pr.changed_files} file(s). "
        f"Files touched: {files_preview}."
    )


def _format_review_comment(r: PRReviewResult) -> str:
    risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}
    emoji = risk_emoji.get(r.risk_level, "⚪")
    risks_md = "\n".join(f"- {x}" for x in r.risks)
    sugg_md = "\n".join(f"- {x}" for x in r.suggestions)
    return textwrap.dedent(f"""
        ## 🤖 orch Auto-Review — PR #{r.pr_number}

        **{emoji} Risk level:** `{r.risk_level}`

        ### Summary
        {r.summary}

        ### Risks identified
        {risks_md}

        ### Suggestions
        {sugg_md}

        ---
        *Posted automatically by [orch](https://github.com/RobynAwesome/Introduction-to-MCP)*
    """).strip()


# ---------------------------------------------------------------------------
# Capability #3 — Commit Message Generation
# ---------------------------------------------------------------------------

class CommitMessageResult(BaseModel):
    subject: str          # ≤72 chars, Conventional Commits format
    body: str             # wrapped at 72 chars
    full_message: str     # subject + blank line + body
    type: str             # feat | fix | chore | refactor | docs | test | ci
    scope: str            # inferred from changed files
    breaking: bool        # True if BREAKING CHANGE detected


def generate_commit_message(
    diff: str | None = None,
    sha: str | None = None,
    owner: str = "",
    repo: str = "",
    extra_context: str = "",
) -> CommitMessageResult:
    """
    Capability #3 — Smart commit message generation.

    Pass either:
      - `diff`: raw unified diff string (e.g. from `git diff --staged`)
      - `sha` + `owner` + `repo`: fetch diff from GitHub for an existing commit

    Args:
        diff:          Raw unified diff text.
        sha:           Commit SHA to fetch from GitHub (alternative to diff).
        owner:         Repo owner (for SHA lookup).
        repo:          Repo name  (for SHA lookup).
        extra_context: Optional hint, e.g. "This closes issue #42".

    Returns:
        CommitMessageResult with Conventional Commits-formatted message.
    """
    if diff is None and sha:
        cfg = _settings()
        owner = owner or cfg.github_default_owner
        repo = repo or cfg.github_default_repo
        _require(owner, "owner")
        _require(repo, "repo")
        client = GitHubClient(cfg.github_token)
        diff = client.get_commit_diff(owner, repo, sha)

    if not diff:
        raise ValueError("Provide either `diff` text or a `sha` to look up.")

    commit_type, scope, breaking = _classify_diff(diff)
    subject = _build_subject(diff, commit_type, scope, breaking)
    body = _build_body(diff, extra_context, breaking)
    full = f"{subject}\n\n{body}" if body else subject

    return CommitMessageResult(
        subject=subject,
        body=body,
        full_message=full,
        type=commit_type,
        scope=scope,
        breaking=breaking,
    )


def _classify_diff(diff: str) -> tuple[str, str, bool]:
    """Return (type, scope, is_breaking) from diff heuristics."""
    diff_lower = diff.lower()
    breaking = "breaking change" in diff_lower or "!breaking" in diff_lower

    # Type detection (order matters — most specific first)
    if any(kw in diff_lower for kw in ["migration", "alter table", "drop column"]):
        commit_type = "feat"
        breaking = True
    elif "test_" in diff_lower or "_test.py" in diff_lower or "spec." in diff_lower:
        commit_type = "test"
    elif any(kw in diff_lower for kw in ["readme", "docstring", "# ", "\"\"\"", "'''"]):
        commit_type = "docs"
    elif any(kw in diff_lower for kw in ["github/workflows", "dockerfile", ".yml", "ci"]):
        commit_type = "ci"
    elif any(kw in diff_lower for kw in ["fix", "bug", "error", "exception", "traceback"]):
        commit_type = "fix"
    elif any(kw in diff_lower for kw in ["refactor", "rename", "move", "extract"]):
        commit_type = "refactor"
    elif any(kw in diff_lower for kw in ["add ", "new ", "feature", "implement", "create"]):
        commit_type = "feat"
    else:
        commit_type = "chore"

    # Scope detection from file paths in diff header lines
    scope = _infer_scope(diff)

    return commit_type, scope, breaking


def _infer_scope(diff: str) -> str:
    """Extract scope from `diff --git a/x/y.py b/x/y.py` lines."""
    import re
    paths: list[str] = re.findall(r"diff --git a/(.+?) b/", diff)
    if not paths:
        return ""

    # Find common top-level directory
    parts = [p.split("/") for p in paths]
    top_dirs = {p[0] for p in parts if len(p) > 1}

    # Map known dirs to scope names
    scope_map = {
        "orch": "orch",
        "tests": "tests",
        "cli": "cli",
        "tools": "tools",
        "public": "public",
        ".github": "ci",
    }
    for d in top_dirs:
        if d in scope_map:
            return scope_map[d]

    # Fall back to first unique top dir
    return sorted(top_dirs)[0] if top_dirs else ""


def _build_subject(
    diff: str, commit_type: str, scope: str, breaking: bool
) -> str:
    """Build the subject line in Conventional Commits format."""
    import re

    # Extract most-changed file as description hint
    paths: list[str] = re.findall(r"diff --git a/(.+?) b/", diff)
    desc_hint = ""
    if paths:
        # Use filename without extension of most prominent file
        base = os.path.basename(paths[0])
        desc_hint = os.path.splitext(base)[0].replace("_", " ")

    bang = "!" if breaking else ""
    scope_str = f"({scope})" if scope else ""
    prefix = f"{commit_type}{scope_str}{bang}: "

    # Build a description (max 72 chars total)
    max_desc = 72 - len(prefix)

    # Try to extract the first meaningful added line as description
    added_lines = [
        line[1:].strip()
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
        and len(line) > 5
        and not line[1:].strip().startswith("#")
        and not line[1:].strip().startswith('"""')
    ]
    if added_lines:
        candidate = added_lines[0][:max_desc].lower()
        # Remove common noise
        for noise in ["def ", "class ", "import ", "from ", "return ", "self."]:
            candidate = candidate.replace(noise, "")
        desc = candidate.strip() or desc_hint
    else:
        desc = desc_hint or "update implementation"

    # Truncate and clean
    desc = desc[:max_desc].rstrip(",. ")
    return f"{prefix}{desc}"


def _build_body(diff: str, extra_context: str, breaking: bool) -> str:
    """Build the commit body."""
    lines: list[str] = []

    # Count changes
    added = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))
    lines.append(f"Changes: +{added} / -{removed} lines")

    if breaking:
        lines.append("")
        lines.append("BREAKING CHANGE: review migration steps before deploying.")

    if extra_context:
        lines.append("")
        lines.append(extra_context)

    # Wrap at 72 chars
    wrapped = []
    for line in lines:
        if len(line) <= 72:
            wrapped.append(line)
        else:
            wrapped.extend(textwrap.wrap(line, width=72))

    return "\n".join(wrapped)


# ---------------------------------------------------------------------------
# MCP Tool Registration helpers
# ---------------------------------------------------------------------------

def get_mcp_tool_definitions() -> list[dict[str, Any]]:
    """
    Return MCP-compatible tool definitions for both capabilities.
    Register these in your MCP server's tool registry.
    """
    return [
        {
            "name": "github_review_pr",
            "description": (
                "Review a GitHub Pull Request. Returns a structured risk assessment, "
                "summary, and actionable suggestions. Optionally posts the review "
                "as a comment on the PR."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pr_number": {
                        "type": "integer",
                        "description": "The PR number to review",
                    },
                    "owner": {
                        "type": "string",
                        "description": "GitHub repo owner (defaults to GITHUB_DEFAULT_OWNER)",
                    },
                    "repo": {
                        "type": "string",
                        "description": "GitHub repo name (defaults to GITHUB_DEFAULT_REPO)",
                    },
                    "post_comment": {
                        "type": "boolean",
                        "description": "Post the review as a GitHub comment (default: false)",
                        "default": False,
                    },
                },
                "required": ["pr_number"],
            },
        },
        {
            "name": "github_generate_commit_message",
            "description": (
                "Generate a Conventional Commits-formatted commit message from a diff. "
                "Pass raw diff text, or a commit SHA to look up from GitHub."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "diff": {
                        "type": "string",
                        "description": "Raw unified diff text (e.g. from git diff --staged)",
                    },
                    "sha": {
                        "type": "string",
                        "description": "Commit SHA to fetch diff from GitHub",
                    },
                    "owner": {
                        "type": "string",
                        "description": "GitHub repo owner (required if using sha)",
                    },
                    "repo": {
                        "type": "string",
                        "description": "GitHub repo name (required if using sha)",
                    },
                    "extra_context": {
                        "type": "string",
                        "description": "Optional hint, e.g. 'Closes #42'",
                    },
                },
                "required": [],
            },
        },
    ]


def dispatch_mcp_call(tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    """
    Route an MCP tool call to the correct function.
    Call this from your MCP server's tool handler.

    Example in your MCP server:
        result = dispatch_mcp_call(tool_use.name, tool_use.input)
        return json.dumps(result)
    """
    if tool_name == "github_review_pr":
        result = review_pull_request(**tool_input)
        return result.model_dump()

    if tool_name == "github_generate_commit_message":
        result = generate_commit_message(**tool_input)
        return result.model_dump()

    raise ValueError(f"Unknown tool: {tool_name}")


# ---------------------------------------------------------------------------
# CLI quick-test (python -m orch.tools.github_tool review 42)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "review" and len(sys.argv) >= 3:
        pr_num = int(sys.argv[2])
        post = "--post" in sys.argv
        result = review_pull_request(pr_num, post_comment=post)
        print(json.dumps(result.model_dump(), indent=2))

    elif cmd == "commit" and len(sys.argv) >= 3:
        # Pass a SHA or pipe diff via stdin
        sha_or_diff = sys.argv[2]
        if len(sha_or_diff) == 40:  # looks like a SHA
            result = generate_commit_message(sha=sha_or_diff)
        else:
            result = generate_commit_message(diff=sha_or_diff)
        print(result.full_message)

    elif cmd == "commit-stdin":
        diff_text = sys.stdin.read()
        result = generate_commit_message(diff=diff_text)
        print(result.full_message)

    else:
        print(
            "Usage:\n"
            "  python github_tool.py review <PR_NUMBER> [--post]\n"
            "  python github_tool.py commit <SHA>\n"
            "  git diff --staged | python github_tool.py commit-stdin\n"
        )


# ---------------------------------------------------------------------------
# Registration snippet — paste into orch/tools/__init__.py
# ---------------------------------------------------------------------------
# from orch.tools.github_tool import (
#     get_mcp_tool_definitions,
#     dispatch_mcp_call,
#     review_pull_request,
#     generate_commit_message,
# )
#
# TOOLS = get_mcp_tool_definitions()   # add to your MCP tool registry list
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _require(value: str, name: str) -> None:
    if not value:
        raise ValueError(
            f"`{name}` is required. Pass it directly or set the corresponding "
            f"env var (GITHUB_DEFAULT_{name.upper()})."
        )