# Kopano Context — Unified Launcher
# Starts: FastAPI backend (port 8000), Vite Studio (port 5173), MAO validation
# Usage: .\launch.ps1

$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$coreDir = Join-Path $root "kopano-core"
$studioDir = Join-Path $coreDir "studio"
$cliDir = Join-Path $root "CLI"

Write-Host "`n=== KOPANO CONTEXT — UNIFIED LAUNCHER ===" -ForegroundColor Cyan
Write-Host "Root: $root" -ForegroundColor DarkGray

# Kill stale processes on ports 8000 and 5173
$staleBackend = Get-NetTCPConnection -LocalPort 8000 -State Listen 2>$null
if ($staleBackend) {
    Write-Host "[CLEANUP] Killing stale process on port 8000..." -ForegroundColor Yellow
    Stop-Process -Id $staleBackend.OwningProcess -Force 2>$null
    Start-Sleep -Seconds 1
}

$staleStudio = Get-NetTCPConnection -LocalPort 5173 -State Listen 2>$null
if ($staleStudio) {
    Write-Host "[CLEANUP] Killing stale process on port 5173..." -ForegroundColor Yellow
    Stop-Process -Id $staleStudio.OwningProcess -Force 2>$null
    Start-Sleep -Seconds 1
}

# 1. Start FastAPI Backend
Write-Host "`n[1/3] Starting FastAPI backend on :8000..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & python -c "from kopano.api import start_api; start_api()"
} -ArgumentList $coreDir

Start-Sleep -Seconds 3

# Verify backend
$backendUp = Get-NetTCPConnection -LocalPort 8000 -State Listen 2>$null
if ($backendUp) {
    Write-Host "  [OK] FastAPI backend LISTENING on :8000 (PID $($backendUp.OwningProcess))" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Backend may still be starting..." -ForegroundColor Yellow
}

# 2. Start Vite Studio
Write-Host "`n[2/3] Starting Vite Studio on :5173..." -ForegroundColor Green
$studioJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & npm run dev
} -ArgumentList $studioDir

Start-Sleep -Seconds 4

$studioUp = Get-NetTCPConnection -LocalPort 5173 -State Listen 2>$null
if ($studioUp) {
    Write-Host "  [OK] Vite Studio LISTENING on :5173 (PID $($studioUp.OwningProcess))" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Studio may still be starting..." -ForegroundColor Yellow
}

# 3. Validate MAO
Write-Host "`n[3/3] Validating MAO server import..." -ForegroundColor Green
$maoCheck = & python -c "import sys; sys.path.insert(0, r'$cliDir'); from mao_server import mao_swarm_status; s = mao_swarm_status(); print(f'MAO OK: {s[\"total_agents\"]} agents registered')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] $maoCheck" -ForegroundColor Green
} else {
    Write-Host "  [WARN] MAO validation: $maoCheck" -ForegroundColor Yellow
}

Write-Host "`n=== ALL SYSTEMS GO ===" -ForegroundColor Cyan
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Studio:   http://localhost:5173" -ForegroundColor White
Write-Host "  Console:  http://localhost:5173/#/console" -ForegroundColor White
Write-Host "  MAO mode: http://localhost:5173/#/console (select MAO tab)" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop all services.`n" -ForegroundColor DarkGray

try {
    while ($true) {
        Start-Sleep -Seconds 10
        $be = Get-NetTCPConnection -LocalPort 8000 -State Listen 2>$null
        $fe = Get-NetTCPConnection -LocalPort 5173 -State Listen 2>$null
        if (-not $be) { Write-Host "[HEARTBEAT] Backend DOWN — restarting..." -ForegroundColor Red }
        if (-not $fe) { Write-Host "[HEARTBEAT] Studio DOWN — check terminal." -ForegroundColor Red }
    }
} finally {
    Write-Host "`n[SHUTDOWN] Stopping background jobs..." -ForegroundColor Yellow
    Stop-Job $backendJob 2>$null; Remove-Job $backendJob 2>$null
    Stop-Job $studioJob 2>$null; Remove-Job $studioJob 2>$null
}
