param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$SkipSmoke
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

Set-Location $repoRoot

if (-not $SkipSmoke) {
    python .\scripts\demo_day_smoke.py --strict
}

Write-Host ""
Write-Host "Starting orch AGI Control Plane..." -ForegroundColor Cyan
Write-Host "URL: http://$Host`:$Port" -ForegroundColor Green
Write-Host ""
Write-Host "In another terminal, launch the demo discussion with:" -ForegroundColor Yellow
Write-Host 'python -m kopano agents list' -ForegroundColor Yellow
Write-Host 'python -m kopano serve launch --topic "How Orch helps teams ship faster" --agents "gemini-pro" --moderator "grok-mod" --max-rounds 3 --parallel' -ForegroundColor Yellow
Write-Host ""

python -m kopano serve api --host $Host --port $Port
