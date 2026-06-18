# IONOS Deploy Guide — Kopano Labs Web Properties
## ALP #21 | 7ef81bb302c8c9cd | 2026-06-18T11:32 SAST
## I_AM_STATELESS_RENTER_NOT_LANDLORD

---

## What Was Built (Local → Live Mapping)

| Local File | Live URL | Action Required |
|---|---|---|
| `public/index.html` | `https://KopanoLabs.com` | Upload to IONOS webspace root |
| `public/careers/index.html` | `https://careers.KopanoLabs.com` | Upload + DNS CNAME |
| `public/starfall/index.html` | `https://StarFallSalvage.KopanoLabs.com` | Already live ✅ |
| `public/admin/`, `public/flows/` etc | subpaths | Already live ✅ |
| `KasiLink/index.html` | `https://KasiLink.com` | Upload to KasiLink.com webspace |

---

## Step 1: Upload KopanoLabs.com Files

> [!IMPORTANT]
> IONOS serves KopanoLabs.com from a webspace — NOT from this GitHub repo. Files must be uploaded via IONOS FTP or File Manager.

### Via IONOS Control Panel
1. Log in to `my.ionos.com`
2. Go to **Hosting → Webspace → File Manager** for `kopanolabs.com`
3. Navigate to the **root folder** (`/`)
4. Upload `public/index.html` → replaces current homepage
5. Upload the entire `public/careers/` folder → creates `/careers/` path

### Via FTP (FileZilla)
```
Host:     ftp.kopanolabs.com  (or your IONOS FTP host)
Username: [from IONOS control panel → FTP access]
Password: [from IONOS control panel]
Port:     21
```
Upload:
- `public/index.html` → `/index.html`
- `public/careers/index.html` → `/careers/index.html`

---

## Step 2: Add DNS Records for careers.KopanoLabs.com

> [!IMPORTANT]
> The `careers` subdomain needs a DNS CNAME or A record in IONOS.

1. `my.ionos.com` → **Domains & SSL** → `kopanolabs.com` → **DNS**
2. Add record:

```
Type:  CNAME
Name:  careers
Value: kopanolabs.com
TTL:   3600
```

Or if IONOS requires an A record, point it to the same IP as `kopanolabs.com` (currently `76.76.21.21`):
```
Type:  A
Name:  careers
Value: 76.76.21.21
TTL:   3600
```

---

## Step 3: Upload KasiLink.com Files

KasiLink.com is a **separate IONOS webspace** (apex domain, different from KopanoLabs.com).

1. `my.ionos.com` → **Hosting** → find `kasilink.com` webspace
2. File Manager → root `/`
3. Upload `KasiLink/index.html` → `/index.html`

> [!NOTE]
> KasiLink.com apex is already resolving (confirmed live earlier). The `www.kasilink.com` subdomain needs a CNAME added:
> ```
> Type:  CNAME
> Name:  www
> Value: kasilink.com
> ```

---

## Step 4: Add DNS for KasiLink.KopanoLabs.com (optional redirect)

If you want `KasiLink.KopanoLabs.com` to redirect to `KasiLink.com`:

In kopanolabs.com DNS:
```
Type:  CNAME
Name:  kasilink
Value: kasilink.com
```

---

## Step 5: Verify Deployment

Run this checklist after uploading:

- [ ] `https://KopanoLabs.com` — 3D particle hero, Build.Prove.Preserve.
- [ ] `https://KopanoLabs.com/careers/` — Careers portal, VC chatbot visible
- [ ] `https://careers.KopanoLabs.com` — Resolves (may take up to 24h DNS)
- [ ] `https://KasiLink.com` — Township gig platform, live feed, KC chatbot
- [ ] `https://www.KasiLink.com` — Redirects to apex (after CNAME)

---

## Current DNS State (from IONOS panel screenshot)

| Domain | Status | IP | Notes |
|---|---|---|---|
| `kopanolabs.com` | DNS modified | 76.76.21.21 | Not active (IONOS says "not active" = pointing but no content?) |
| `kasilink.com` | ACTIVE | 216.198.79.1 | Live ✅ |
| `krrababalela.com` | Active | 216.198.79.1 | Separate domain |

> [!WARNING]
> `kopanolabs.com` shows "Not active" in IONOS despite being visually live. This may mean IONOS is serving from a different web product (MyWebsite NOW or similar). Check: **Domains → kopanolabs.com → Destination** to see if it points to a webspace, MyWebsite, or external IP.

---

## GSMB Governance Note

All web files are committed to `codex/kc-sovereign-gui-full-dev` branch at `9c39fe5`. They are **NOT auto-deployed** — IONOS is not wired to GitHub Actions (the CI deploys to Azure, not IONOS).

**Options going forward:**
1. Manual upload (this guide) — works immediately
2. Wire IONOS to GitHub via FTP deploy action — automates future deployments
3. Migrate hosting from IONOS to Vercel/Netlify — auto-deploy on push

The FTP deploy action is the recommended next step for POC→continuous delivery:
```yaml
# .github/workflows/deploy-web.yml (future)
- uses: SamKirkland/FTP-Deploy-Action@v4
  with:
    server: ftp.kopanolabs.com
    username: ${{ secrets.IONOS_FTP_USER }}
    password: ${{ secrets.IONOS_FTP_PASS }}
    local-dir: ./public/
    server-dir: /
```
