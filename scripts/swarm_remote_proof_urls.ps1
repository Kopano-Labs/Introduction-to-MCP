# Swarm remote proof — print GitHub URLs + optional curl probes (no gh auth).
# Run from repo root:  powershell -File scripts/swarm_remote_proof_urls.ps1
# Optional:  .\scripts\swarm_remote_proof_urls.ps1 -Probe
# Override:    $env:GITHUB_OWNER='RobynAwesome'; $env:GITHUB_REPO='Introduction-to-MCP'; .\scripts\...

param(
    [switch]$Probe
)

$ErrorActionPreference = 'Stop'
$root = git rev-parse --show-toplevel 2>$null
if (-not $root) {
    Write-Error "Not inside a git repository"
    exit 2
}
Set-Location $root

$origin = (git remote get-url origin 2>$null) -join ''
$branch = (git branch --show-current 2>$null) -join ''
$fullSha = (git rev-parse HEAD 2>$null) -join ''
$shortSha = (git rev-parse --short HEAD 2>$null) -join ''

$owner = $env:GITHUB_OWNER
$repo = $env:GITHUB_REPO

if (-not $owner -or -not $repo) {
    $m = [regex]::Match($origin, 'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$')
    if ($m.Success) {
        $owner = $m.Groups[1].Value
        $repo = $m.Groups[2].Value -replace '\.git$', ''
    }
}

if (-not $owner -or -not $repo) {
    Write-Error "Could not parse owner/repo from origin: $origin. Set GITHUB_OWNER and GITHUB_REPO."
    exit 1
}

$base = "https://github.com/$owner/$repo"

Write-Host "=== Swarm remote proof checklist (open in browser) ===`n"
Write-Host "Repo:           $base"
Write-Host "Branch tree:    $base/tree/$branch"
Write-Host "Commit (short): $base/commit/$shortSha"
Write-Host "Commit (full):  $base/commit/$fullSha"
Write-Host "Actions (CI):   $base/actions"
Write-Host "Compare (edit branches as needed):"
Write-Host "  $base/compare/master...$branch`?expand=1`n"
Write-Host "Git (local facts)"
Write-Host "  origin: $origin"
Write-Host "  branch: $branch"
Write-Host "  HEAD:   $fullSha`n"

if ($Probe) {
    Write-Host "=== curl probes (public API, unauthenticated) ==="
    $apiRepo = "https://api.github.com/repos/$owner/$repo"
    $apiCommit = "https://api.github.com/repos/$owner/$repo/commits/$fullSha"
    $codeRepo = (& curl.exe -sS -H "Accept: application/vnd.github+json" -o NUL -w "%{http_code}" $apiRepo) 2>$null
    if (-not $codeRepo) { $codeRepo = "000" }
    $codeCommit = (& curl.exe -sS -H "Accept: application/vnd.github+json" -o NUL -w "%{http_code}" $apiCommit) 2>$null
    if (-not $codeCommit) { $codeCommit = "000" }
    Write-Host "  GET $apiRepo  -> HTTP $codeRepo  (200 = repo visible to API)"
    Write-Host "  GET $apiCommit -> HTTP $codeCommit (200 = commit on that remote)"
    if ($codeRepo -ne "200") {
        Write-Host "  Note: 403/404 often means private repo (no token) or wrong owner/repo." -ForegroundColor DarkGray
    }
    if ($codeCommit -ne "200") {
        Write-Host "`n  If commit is 404: not on $owner/$repo (unpushed, wrong remote, or use GITHUB_OWNER/REPO for your fork)." -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "=== Kopano host probes (public HTTPS) ==="
    $kopanoHosts = @(
        "https://context.kopanolabs.com/",
        "https://kopanolabs.com/",
        "https://kopanocontext.kopanolabs.com/"
    )
    foreach ($u in $kopanoHosts) {
        $code = (& curl.exe -sS -o NUL -w "%{http_code}" --connect-timeout 10 $u) 2>$null
        if (-not $code) { $code = "000" }
        Write-Host "  GET $u -> HTTP $code"
    }
    Write-Host "  See docs/swarm-ops/VERIFIED_ENDPOINTS.md for interpretation (000 often = DNS failure)."
    Write-Host ""
}

Write-Host "Tip: if your public fork is RobynAwesome but origin is Kopano-Labs, run:"
Write-Host '  $env:GITHUB_OWNER="RobynAwesome"; $env:GITHUB_REPO="Introduction-to-MCP"; .\scripts\swarm_remote_proof_urls.ps1 -Probe'
