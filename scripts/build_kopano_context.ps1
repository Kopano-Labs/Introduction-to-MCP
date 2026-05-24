# Build KopanoContext.exe (API + bundled Studio)
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "==> Studio build (Vite)"
$studio = Join-Path $RepoRoot "kopano-core\studio"
if (-not (Test-Path (Join-Path $studio "node_modules"))) {
    npm --prefix $studio ci
}
$env:VITE_KC_API_BASE_URL = ""
npm --prefix $studio run build
if (-not (Test-Path (Join-Path $studio "dist\index.html"))) {
    throw "Studio dist missing after npm run build"
}

Write-Host "==> PyInstaller"
python -m pip install --upgrade pyinstaller 2>$null | Out-Null
# Avoid --clean on Windows if a prior build left locked files under build/
python -m PyInstaller KopanoContext.spec --noconfirm

$exe = Join-Path $RepoRoot "dist\KopanoContext.exe"
if (-not (Test-Path $exe)) {
    throw "Build failed: $exe not found"
}

$item = Get-Item $exe
Write-Host "OK $($item.FullName) ($([math]::Round($item.Length / 1MB, 1)) MB)"

Write-Host @"

Smoke test (optional):
  dist\KopanoContext.exe
  # Opens http://127.0.0.1:8000 with bundled Studio

CLI mode inside the same binary:
  dist\KopanoContext.exe serve api --no-open
"@
