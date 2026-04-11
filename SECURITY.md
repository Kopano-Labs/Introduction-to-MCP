# Security Policy — Kopano Context

## Zero-Secret Commit Policy

Kopano Context enforces a zero-tolerance policy for secrets in source control.

- **Do not commit `.env` files.** All environment variables must be set locally or via your CI/CD secrets manager.
- **Do not commit `node_modules/`.** Install dependencies locally using `npm install`. The `node_modules/` directory is excluded via `.gitignore`.
- **Do not commit API keys, tokens, or credentials** of any kind — Anthropic, Azure, Clerk, MongoDB Atlas, RapidAPI, GitHub PATs, or otherwise.
- **Do not commit database files** (`.db`, `.sqlite`) that may contain user data.

## If a Secret Is Accidentally Committed

1. **Immediately revoke or rotate** the exposed credential. Do not wait. Assume it is already compromised.
2. Remove the secret from all commits using `git filter-repo` or BFG Repo-Cleaner.
3. Force-push the cleaned history (after team coordination).
4. Log the incident in `Schematics/11-AI HALLUCINATION - CRITICAL/` if an AI agent was involved.
5. Notify RobynAwesome immediately.

## Vendor and Dependency Rules

- **Do not commit `node_modules/`** — this is enforced by `.gitignore`.
- **Do not commit Python virtual environments** (`.venv/`, `venv/`, `env/`).
- **Do not commit compiled binaries** (`dist/`, `*.exe`) unless they are specifically demo artifacts tracked intentionally.
- Keep `pip-audit` and `npm audit` clean before every demo.

## Reporting a Vulnerability

Contact: [rkholofelo@context.kopanolabs.com](mailto:rkholofelo@context.kopanolabs.com)

Do not open a public GitHub issue for security vulnerabilities.
