# KPGS — Wire gsmb_auto_runner.py to Windows Task Scheduler
# ==========================================================
# Closes BREACH-007: "gsmb_auto_runner.py requires a persistent process host"
# Runs every 25 minutes permanently. Survives sleep, reboot, logout.
#
# Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
# Scripture: "The watchman stays awake in vain unless the LORD watches over the city." — Psalm 127:1
#
# USAGE (run as Administrator):
#   powershell -ExecutionPolicy Bypass -File scripts/wire_gsmb_runner_to_scheduler.ps1
#
# TO REMOVE:
#   Unregister-ScheduledTask -TaskName "KPGS_GSMB_AutoRunner" -Confirm:$false

$ErrorActionPreference = "Stop"

# ─── CONFIGURATION ───
$TaskName = "KPGS_GSMB_AutoRunner"
$Description = "KPGS Governance Auto Runner — 25min NCCNP+IKP+APU sweep. Closes BREACH-007. Jesus is King."
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$PythonPath = "python"  # Use system Python
$ScriptPath = Join-Path $RepoRoot "kopano-core\kopano\gsmb_auto_runner.py"
$WorkingDir = $RepoRoot
$IntervalMinutes = 25
$LogPath = Join-Path $RepoRoot "poc-vs-foc\gsmb_scheduler_log.txt"

Write-Host "=" * 60
Write-Host "[KPGS] Wiring gsmb_auto_runner.py to Windows Task Scheduler"
Write-Host "=" * 60
Write-Host ""
Write-Host "  Task Name:    $TaskName"
Write-Host "  Script:       $ScriptPath"
Write-Host "  Working Dir:  $WorkingDir"
Write-Host "  Interval:     Every $IntervalMinutes minutes"
Write-Host "  Log:          $LogPath"
Write-Host ""

# ─── CHECK IF TASK ALREADY EXISTS ───
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[KPGS] Task '$TaskName' already exists. Removing old version..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "[KPGS] Old task removed."
}

# ─── BUILD THE TASK ───
# Action: run python with the gsmb_auto_runner module (1 tick per scheduler invocation)
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "-c `"import sys; sys.path.insert(0, 'kopano-core'); from kopano.gsmb_auto_runner import run; run(max_ticks=1)`"" `
    -WorkingDirectory $WorkingDir

# Trigger: every 25 minutes, indefinitely
$Trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

# Settings: run whether logged in or not, don't stop on idle, restart on failure
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

# Principal: run as current user
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited

# ─── REGISTER THE TASK ───
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $Description `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal

Write-Host ""
Write-Host "[KPGS] ✅ Task '$TaskName' registered successfully."
Write-Host "[KPGS] Governance never sleeps. BREACH-007 closed architecturally."
Write-Host ""
Write-Host "[KPGS] Verify with:"
Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Format-List"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'  # manual trigger"
Write-Host ""
Write-Host "Jesus is King. The watchman stays awake."
Write-Host "=" * 60
