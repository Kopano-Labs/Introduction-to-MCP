# PowerShell 1-Click Builder for Kopano Sovereign Studio Desktop Executable (.exe)
# Usage: ./scripts/build_sovereign_desktop_exe.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "🏛️  BUILDING KOPANO SOVEREIGN STUDIO DESKTOP EXECUTABLE (.EXE)" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

# 1. Build Studio Web Assets (if npm is available)
if (Test-Path "$RepoRoot/kopano-core/studio/package.json") {
    Write-Host "==> Step 1: Building Studio Web UI Assets" -ForegroundColor Yellow
    Push-Location "$RepoRoot/kopano-core/studio"
    try {
        if (-not (Test-Path "dist")) {
            npm run build
        }
    } catch {
        Write-Warning "npm build skipped or dist already exists."
    }
    Pop-Location
}

# 2. Verify PyInstaller Installation
Write-Host "==> Step 2: Verifying PyInstaller" -ForegroundColor Yellow
python -m pip install --upgrade pyinstaller pywebview uvicorn fastapi | Out-Null

# 3. Compile Desktop Executable
Write-Host "==> Step 3: Compiling KopanoSovereignStudio.exe via PyInstaller" -ForegroundColor Yellow
python -m PyInstaller KopanoSovereignStudio.spec --noconfirm --clean

if (Test-Path "$RepoRoot/dist/KopanoSovereignStudio/KopanoSovereignStudio.exe") {
    Write-Host "========================================================================" -ForegroundColor Green
    Write-Host "✅ SUCCESS: KopanoSovereignStudio.exe compiled successfully!" -ForegroundColor Green
    Write-Host "📁 Location: $RepoRoot/dist/KopanoSovereignStudio/KopanoSovereignStudio.exe" -ForegroundColor Green
    Write-Host "========================================================================" -ForegroundColor Green
} else {
    Write-Host "⚠️ Build finished. Check output directory in $RepoRoot/dist" -ForegroundColor Yellow
}
