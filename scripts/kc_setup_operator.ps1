# One-time local Super God operator bootstrap (NOT committed).
# Usage: .\scripts\kc_setup_operator.ps1 -Email you@kopanolabs.com -Password (Read-Host -AsSecureString)
param(
    [Parameter(Mandatory = $true)]
    [string]$Email,
    [Parameter(Mandatory = $true)]
    [string]$Password
)

$dir = Join-Path $env:LOCALAPPDATA "KopanoContext"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$path = Join-Path $dir "operator.bootstrap.json"
@{ email = $Email.Trim().ToLower(); password = $Password } | ConvertTo-Json | Set-Content -Path $path -Encoding UTF8
Write-Host "Wrote $path"
Write-Host "Restart KopanoContext.exe — Swarm Console will auto-bind Super God Mode for this account."
