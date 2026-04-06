Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[1/7] Installing root package" -ForegroundColor Cyan
python -m pip install -e .

Write-Host "[2/7] Running Python tests" -ForegroundColor Cyan
python -m pytest -q

Write-Host "[3/7] Installing CLI subproject" -ForegroundColor Cyan
python -m pip install -e ./CLI

Write-Host "[4/7] Verifying main CLI surface" -ForegroundColor Cyan
python -m orch --help | Out-Null

Write-Host "[5/7] Verifying MCP CLI package install" -ForegroundColor Cyan
python -m pip show mcp-cli | Out-Null

Write-Host "[6/7] Linting GUI" -ForegroundColor Cyan
Push-Location orch/gui
npm run lint

Write-Host "[7/7] Building GUI" -ForegroundColor Cyan
npm run build
Pop-Location

Write-Host "Demo day preflight passed." -ForegroundColor Green
