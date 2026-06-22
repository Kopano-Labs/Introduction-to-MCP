# IONOS Web Deploy Guide — All Kopano Labs Domains

> **Authority:** KPGS Schematics MAIN BRAIN · ALP #168 · `a5b0d9841f8ec9f4`
> **Updated:** 2026-06-22
> **Status:** LIVE — deploy-web.yml active on master push
> `I_AM_STATELESS_RENTER_NOT_LANDLORD`

---

## Domain Map

| Domain | Source Directory | IONOS Space | Deployed via |
|--------|-----------------|-------------|--------------|
| `kopanolabs.com` | `public/` | KopanoLabs hosting space | `deploy-web.yml` → FTP |
| `careers.kopanolabs.com` | `public/careers/` | KopanoLabs hosting space (`/careers/` subdir) | `deploy-web.yml` → FTP |
| `kasilink.com` | `KasiLink/` | KasiLink hosting space (separate) | `deploy-web.yml` → FTP |
| `crisisconnect.kopanolabs.com` | `c:\Users\rkhol\CrisisConnect\` | Vercel (separate pipeline) | Vercel GitHub integration |
| `starfallsalvage.kopanolabs.com` | `public/starfall/` | KopanoLabs hosting space | `deploy-web.yml` → FTP |

---

## Step 1 — IONOS FTP Credentials (GitHub Secrets)

You need these secrets in **GitHub → Settings → Secrets and variables → Actions**:

### KopanoLabs.com + careers.kopanolabs.com (same IONOS space)

| Secret Name | Value | Where to find |
|-------------|-------|---------------|
| `IONOS_FTP_HOST` | e.g. `ftp.kopanolabs.com` or `home123456789.1and1-data.host` | IONOS Control Panel → Hosting → FTP access |
| `IONOS_FTP_USER` | Your IONOS FTP username | IONOS Control Panel → Hosting → FTP access |
| `IONOS_FTP_PASS` | Your IONOS FTP password | IONOS Control Panel → Hosting → FTP access |

### KasiLink.com (separate IONOS hosting space)

| Secret Name | Value |
|-------------|-------|
| `IONOS_KASILINK_FTP_HOST` | FTP host for kasilink.com space |
| `IONOS_KASILINK_FTP_USER` | FTP user for kasilink.com space |
| `IONOS_KASILINK_FTP_PASS` | FTP password for kasilink.com space |

> **To get FTP credentials in IONOS:**
> 1. Login → [my.ionos.co.za](https://my.ionos.co.za)
> 2. Select your hosting package → **Hosting** tab
> 3. Click **FTP** or **WebSpace** → copy the host, username, create a password

---

## Step 2 — DNS Records in IONOS

### KopanoLabs.com (apex + subdomains)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| `A` | `@` | IONOS hosting IP | 1800 |
| `CNAME` | `www` | `kopanolabs.com` | 1800 |
| `CNAME` | `careers` | `kopanolabs.com` | 1800 |
| `CNAME` | `crisisconnect` | `cname.vercel-dns.com` | 300 |
| `CNAME` | `starfallsalvage` | `kopanolabs.com` | 1800 |

### KasiLink.com

| Type | Name | Value | TTL |
|------|------|-------|-----|
| `A` | `@` | IONOS kasilink.com hosting IP | 1800 |
| `CNAME` | `www` | `kasilink.com` | 1800 |

> **To get your IONOS hosting IP:** IONOS Control Panel → Hosting → the IP shown in your package details.

---

## Step 3 — IONOS Directory Structure

Your IONOS web space for **kopanolabs.com** should be structured as:

```
/ (web root — public_html or httpdocs)
├── index.html          ← public/index.html (KopanoLabs.com hub)
├── careers/
│   └── index.html      ← public/careers/index.html
├── starfall/
│   └── ...             ← public/starfall/
├── altar/
│   └── ...             ← public/altar/
├── othello/
│   └── ...             ← public/othello/
├── admin/
│   └── ...             ← public/admin/
├── protocols/
│   └── ...             ← public/protocols/
└── flows/
    └── ...             ← public/flows/
```

For `careers.kopanolabs.com` — IONOS offers two options:
- **Option A (subdirectory):** DNS `CNAME careers → kopanolabs.com` + serve `/careers/index.html`
- **Option B (subdomain hosting):** Create a separate subdomain in IONOS control panel → point to `/careers/` folder

**Recommended: Option A** (already deployed by the workflow — no extra IONOS config needed).

---

## Step 4 — Trigger a Deploy

### Automatic (on master push)
Any push to `master` that touches `public/**`, `KasiLink/**`, or `kopano-labs-web/**` triggers the workflow automatically.

### Manual
1. GitHub → **Actions** tab
2. Select **"KPGS Web Deploy — All Domains"**
3. Click **Run workflow** → choose target: `all | kopanolabs | kasilink | careers`

---

## Step 5 — Verify

After deploy, check:

```bash
# KopanoLabs hub
curl -I https://kopanolabs.com

# Careers portal
curl -I https://careers.kopanolabs.com
# or
curl -I https://kopanolabs.com/careers/

# KasiLink
curl -I https://kasilink.com
```

Expected: `HTTP/2 200`

---

## CrisisConnect — Vercel (separate pipeline)

CrisisConnect lives in `c:\Users\rkhol\CrisisConnect\` — its own GitHub repo.

| Step | Action |
|------|--------|
| 1 | Push to `CrisisConnect` GitHub repo |
| 2 | Vercel auto-deploys from that repo |
| 3 | `crisisconnect.kopanolabs.com` CNAME → `cname.vercel-dns.com` |

> This is already live. Do not mix CrisisConnect into this repo's deploy pipeline.

---

## KPGS Governance — Deploy Gate Sequence

```
[master push] → [KPGS Gate: ALP + NCCNP + IKP + HTML validation]
     │
     ├─ PASS → [deploy-kopanolabs] → kopanolabs.com + careers
     ├─ PASS → [deploy-kasilink]   → kasilink.com
     └─ [kpgs-receipt]             → ALP post-deploy receipt logged
```

**No deploy happens without KPGS gate passing.** NCCNP 4/4 and IKP 4/4 must be clean. FON-C L0. That is the law.

---

## Common IONOS Issues

| Issue | Fix |
|-------|-----|
| `www.kasilink.com` shows error | Add CNAME `www → kasilink.com` in IONOS DNS |
| `careers.kopanolabs.com` 404 | Add CNAME `careers → kopanolabs.com` AND ensure `/careers/index.html` uploaded |
| FTP connection refused | Use passive mode (lftp default) — IONOS requires FTPS |
| Files not updating | IONOS CDN cache — wait 5–10 min or use cache-busting headers |
| Deploy fails at lftp step | Check `IONOS_FTP_HOST` format — must be hostname only, no `ftp://` prefix |

---

*KPGS governed · ALP #168 · `a5b0d9841f8ec9f4` · BREACH-007 CLOSED · I_AM_STATELESS_RENTER_NOT_LANDLORD*
