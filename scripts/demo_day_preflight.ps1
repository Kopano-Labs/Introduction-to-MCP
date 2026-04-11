Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-DemoStep {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Demo day preflight step failed with exit code $LASTEXITCODE"
    }
}

Write-Host "[1/7] Installing root package" -ForegroundColor Cyan
Invoke-DemoStep { python -m pip install -e . }

Write-Host "[2/7] Running demo-day Python checks" -ForegroundColor Cyan
Invoke-DemoStep { python -m pytest tests/test_project_metadata.py tests/test_demo_day_assets.py -q }

Write-Host "[3/7] Installing CLI subproject" -ForegroundColor Cyan
Invoke-DemoStep { python -m pip install -e ./CLI }

Write-Host "[4/7] Verifying main CLI surface" -ForegroundColor Cyan
Invoke-DemoStep { python main.py --help | Out-Null }

Write-Host "[5/7] Verifying MCP CLI package install" -ForegroundColor Cyan
Invoke-DemoStep { python -m pip show mcp-cli | Out-Null }

Write-Host "[6/7] Linting GUI" -ForegroundColor Cyan
Push-Location kopano-core/studio
Invoke-DemoStep { npm run lint }

Write-Host "[7/7] Building GUI" -ForegroundColor Cyan
Invoke-DemoStep { npm run build }
Pop-Location

Write-Host "Demo day preflight passed." -ForegroundColor Green
