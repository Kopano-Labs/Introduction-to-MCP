# Start local API + Studio so Training page shows seeded KC store (146+ promoted).
# First run can take ~30-60s while kopano.api imports.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path "kopano-core\.kc\context_store.json")) {
    python scripts/kc_apprenticeship_activate.py --replace
    python scripts/kc_apprenticeship_steward.py --max-phase 10 --promote
}
if (-not (Test-Path "kopano-core\studio\dist\index.html")) {
    Push-Location kopano-core\studio
    npm run build
    Pop-Location
}
Write-Host "Starting API on http://127.0.0.1:8000 — open Training (CRUD) in Studio."
python main.py serve api --no-open
