"""One-shot local git estate audit for CF reconciliation."""
import json
import subprocess
from pathlib import Path

PATHS = [
    r"C:\Users\rkhol\5s-Arena-Blog",
    r"C:\Users\rkhol\amaphu-app",
    r"C:\Users\rkhol\ayakha-ai",
    r"C:\Users\rkhol\Bookit-5s-Arena",
    r"C:\Users\rkhol\cape-campass",
    r"C:\Users\rkhol\cars4mars-landingpage",
    r"C:\Users\rkhol\cars4mars-project",
    r"C:\Users\rkhol\crisis-connect",
    r"C:\Users\rkhol\CrisisConnect",
    r"C:\Users\rkhol\freddy-nw-alfalfa",
    r"C:\Users\rkhol\Harvest-4-All",
    r"C:\Users\rkhol\Introduction to MCP",
    r"C:\Users\rkhol\kasi-link",
    r"C:\Users\rkhol\kasi-link-clean",
    r"C:\Users\rkhol\Kopano-Labs-Interns",
    r"C:\Users\rkhol\Kopano-Labs-Website",
    r"C:\Users\rkhol\kopano-sovereign-hub",
    r"C:\Users\rkhol\KopanoContext",
    r"C:\Users\rkhol\kpgs-morning-engine-core--kmec-",
    r"C:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP",
    r"C:\Users\rkhol\Partial-Knowable-Algebra",
    r"C:\Users\rkhol\paws-and-potjie",
    r"C:\Users\rkhol\Portfolio",
    r"C:\Users\rkhol\Portfolio-client-MBR",
    r"C:\Users\rkhol\Project-Jennifer",
    r"C:\Users\rkhol\Search-Entity-Architecture",
    r"C:\Users\rkhol\Starfall Salvage",
    r"C:\Users\rkhol\starfall-salvage",
    r"C:\Users\rkhol\starfall-salvage-temp",
    r"C:\Users\rkhol\Top-AI-repos",
]


def run(cmd, cwd):
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as exc:
        return 1, "", str(exc)


def audit(path_str: str):
    p = Path(path_str)
    if not (p / ".git").exists():
        return None
    rc, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], p)
    if rc != 0:
        return None
    _, head, _ = run(["git", "rev-parse", "HEAD"], p)
    _, remote, _ = run(["git", "remote", "get-url", "origin"], p)
    _, porcelain, _ = run(["git", "status", "--porcelain"], p)
    dirty = "dirty" if porcelain else "clean"
    run(["git", "fetch", "origin"], p)
    rc_u, upstream, _ = run(["git", "rev-parse", "--abbrev-ref", "@{u}"], p)
    ahead = behind = None
    if rc_u == 0 and upstream:
        _, ahead, _ = run(["git", "rev-list", "--count", f"{upstream}..HEAD"], p)
        _, behind, _ = run(["git", "rev-list", "--count", f"HEAD..{upstream}"], p)
    _, last_line, _ = run(["git", "log", "-1", "--format=%ci|%h|%s"], p)
    parts = last_line.split("|", 2) if last_line else ["", "", ""]
    return {
        "path": str(p),
        "branch": branch,
        "head": head,
        "remote": remote or None,
        "worktree": dirty,
        "upstream": upstream if rc_u == 0 else None,
        "ahead": int(ahead) if ahead and ahead.isdigit() else None,
        "behind": int(behind) if behind and behind.isdigit() else None,
        "last_commit_at": parts[0] if parts else None,
        "last_commit_short": parts[1] if len(parts) > 1 else None,
        "last_commit_subject": parts[2] if len(parts) > 2 else None,
    }


rows = [r for r in (audit(x) for x in PATHS) if r]
print(json.dumps(rows, indent=2))
