param(
  [int]$Port = 9222,
  [string]$UserDataDir = "$env:LOCALAPPDATA\KPGS\BrowserMCP\Profile",
  [string]$ChromePath = ""
)

$ErrorActionPreference = "Stop"

if (-not $ChromePath) {
  $candidates = @(
    "$env:PROGRAMFILES\Google\Chrome\Application\chrome.exe",
    "${env:PROGRAMFILES(X86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
    "$env:PROGRAMFILES\Microsoft\Edge\Application\msedge.exe",
    "${env:PROGRAMFILES(X86)}\Microsoft\Edge\Application\msedge.exe"
  )
  $ChromePath = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
}

if (-not $ChromePath -or -not (Test-Path $ChromePath)) {
  throw "Could not find Chrome/Edge. Pass -ChromePath explicitly."
}

New-Item -ItemType Directory -Path $UserDataDir -Force | Out-Null

Write-Host "KPGS Browser MCP"
Write-Host "Browser: $ChromePath"
Write-Host "Profile: $UserDataDir"
Write-Host "CDP: http://127.0.0.1:$Port"
Write-Host "This is a dedicated persistent KPGS browser profile. Log in manually when needed."

$args = @(
  "--remote-debugging-port=$Port",
  "--remote-debugging-address=127.0.0.1",
  "--user-data-dir=$UserDataDir",
  "--no-first-run",
  "--no-default-browser-check",
  "about:blank"
)

Start-Process -FilePath $ChromePath -ArgumentList $args
