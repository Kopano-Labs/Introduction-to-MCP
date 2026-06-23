# Deployment Runbook — KPGS Ecosystem

> How to deploy each domain in the Kopano Labs ecosystem.

## Domains & Deployment Targets

| Domain | Repo | Host | Method |
|--------|------|------|--------|
| kopanolabs.com | Introduction-to-MCP/public/ | IONOS | FTP via GitHub Actions |
| kasilink.com | KasiLink/ | IONOS | FTP via GitHub Actions |
| careers.kopanolabs.com | Introduction-to-MCP/public/careers/ | IONOS | FTP via GitHub Actions |
| starfallsalvage.kopanolabs.com | starfall-salvage | Vercel | Auto-deploy on push |
| fivesarena.com | Bookit-5s-Arena | Vercel | Auto-deploy on push to main |
| crisisconnect.kopanolabs.com | CrisisConnect | IONOS | FTP / manual |
| kopanocontext.kopanolabs.com | kopano-context | Vercel | Auto-deploy |

## IONOS FTP Deployment (kopanolabs.com + kasilink.com)

### Prerequisites
- IONOS FTP credentials in GitHub Secrets
- `.github/workflows/deploy-web.yml` configured

### Secrets Required
| Secret | Purpose |
|--------|---------|
| `IONOS_FTP_HOST` | FTP server hostname |
| `IONOS_FTP_USER` | FTP username |
| `IONOS_FTP_PASS` | FTP password |

### Trigger
Push to `codex/kc-sovereign-gui-full-dev` → GitHub Actions → FTP upload to IONOS

### Manual Deploy
```bash
# From repo root
npx ftp-deploy --server $IONOS_FTP_HOST --user $IONOS_FTP_USER --password $IONOS_FTP_PASS --local-dir public/ --remote-dir /
```

## Vercel Deployment (fivesarena.com + starfall)

### How It Works
- Connected to GitHub repo via Vercel dashboard
- Push to `main` → auto-build → auto-deploy
- Build command: `next build` (for Next.js projects)
- Output: Vercel Edge Network

### Common Build Failures
| Error | Fix |
|-------|-----|
| ERESOLVE | Add `.npmrc` with `legacy-peer-deps=true` |
| Module not found | Check import paths in changed files |
| Type error | Run `npx tsc --noEmit` locally first |

### Vercel CLI (if needed)
```bash
npx vercel --prod
```

## Pre-Deploy Checklist (ALL domains)

- [ ] All tests pass locally
- [ ] No console.log in production code
- [ ] KHELOS pre-commit hook passes
- [ ] Session receipt exists in poc-vs-foc/
- [ ] Commit message has AG_OPINION + RTC_OPINION
- [ ] No secrets in committed code

## KPGS Gate (Mandatory)

No deployment without KPGS activation gate passing:
```bash
python scripts/kc_kpgs_governance.py status
```

If gate = BLOCK → do not deploy.

**Jesus is King. Classify before you ship.**
