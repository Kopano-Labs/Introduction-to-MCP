<#
.SYNOPSIS
    Automated Hardware Maintenance & No Malloc Margin Offload Routine
.DESCRIPTION
    Reclaims disk space, purges package manager and temp caches, optimizes NVMe SSD, and compacts git repositories.
#>

$ErrorActionPreference = 'SilentlyContinue'

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " 🚀 GSMB HARDWARE OFFLOAD & NO MALLOC MARGIN ROUTINE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Measure Initial Space
$initialDrive = Get-PSDrive -PSProvider FileSystem -Name C
$initialFree = [math]::Round($initialDrive.Free / 1GB, 2)
Write-Host "[1/5] Starting Free Space on C:: $initialFree GB" -ForegroundColor Yellow

# 2. Tier 1: Purge Package Manager & Temp Caches
Write-Host "[2/5] Purging NPM cache, User Temp, and Puppeteer cache..." -ForegroundColor Green
npm cache clean --force 2>$null

if (Test-Path "$env:LOCALAPPDATA\npm-cache") {
    Remove-Item "$env:LOCALAPPDATA\npm-cache" -Recurse -Force -ErrorAction SilentlyContinue
}

if (Test-Path "$env:LOCALAPPDATA\Temp") {
    Get-ChildItem -Path "$env:LOCALAPPDATA\Temp" -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
        try { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue } catch {}
    }
}

if (Test-Path "C:\Users\rkhol\.cache\puppeteer") {
    Remove-Item "C:\Users\rkhol\.cache\puppeteer" -Recurse -Force -ErrorAction SilentlyContinue
}

# 3. Tier 2: System Dumps & Updates
Write-Host "[3/5] Cleaning Windows Update Downloads & CrashDumps..." -ForegroundColor Green
if (Test-Path "C:\Windows\SoftwareDistribution\Download") {
    Get-ChildItem -Path "C:\Windows\SoftwareDistribution\Download" -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
        try { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue } catch {}
    }
}
if (Test-Path "$env:LOCALAPPDATA\CrashDumps") {
    Remove-Item "$env:LOCALAPPDATA\CrashDumps\*" -Recurse -Force -ErrorAction SilentlyContinue
}
ipconfig /flushdns | Out-Null

# 4. Tier 3: NVMe SSD ReTrim
Write-Host "[4/5] Running SSD ReTrim on Drive C:..." -ForegroundColor Green
try {
    Optimize-Volume -DriveLetter C -ReTrim -ErrorAction SilentlyContinue | Out-Null
} catch {}

# 5. Tier 4: Git Object Packfile Compaction
Write-Host "[5/5] Compacting git packfiles..." -ForegroundColor Green
$repos = @(
    "C:\Users\rkhol\Bookit-5s-Arena",
    "C:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP"
)
foreach ($repo in $repos) {
    if (Test-Path $repo) {
        git -C $repo gc --prune=now --quiet 2>$null
    }
}

# Final Summary
$finalDrive = Get-PSDrive -PSProvider FileSystem -Name C
$finalFree = [math]::Round($finalDrive.Free / 1GB, 2)
$gain = [math]::Round($finalFree - $initialFree, 2)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " ✅ COMPLETE: Free Space is now $finalFree GB (Gain: +$gain GB)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
