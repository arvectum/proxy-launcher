<#
.SYNOPSIS
    Runtime-aware owner-host wrapper for APL-REL-014.
.DESCRIPTION
    Validates the exact governed installed 0.2.3 instance before touching any running process.
    If the exact installed launcher/core is running, this script records the runtime shape,
    restores network state through the product --stop/--rollback path, quiesces only processes
    whose executable path exactly matches the governed installation, delegates to the proven
    owner-host snapshot wrapper, then restores the original core/GUI running state.

    Foreign, ambiguous, modified or unverifiable processes fail closed before process mutation.
#>
[CmdletBinding()]
param(
    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$EvidencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Runtime-aware lifecycle acceptance must run on Windows.' }

$ExpectedVersion = '0.2.3'
$ExpectedApplicationSha256 = 'f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a'
$ExpectedSetupSha256 = '5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414'
$AppKeyName = '{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}_is1'
$UserUninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$MachineUninstallKey = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$MachineWowUninstallKey = "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"

$ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
if (-not $EvidencePath) { $EvidencePath = $ReleaseDirectory + '.lifecycle-acceptance.json' }
$ownerHostScript = Join-Path $PSScriptRoot 'windows_signed_set_lifecycle_acceptance_owner_host.ps1'
if (-not (Test-Path -LiteralPath $ownerHostScript -PathType Leaf)) {
    throw "Owner-host lifecycle wrapper is missing: $ownerHostScript"
}

$documents = [Environment]::GetFolderPath('MyDocuments')
$installRoot = Join-Path $documents 'ArvectumProxyLauncher'
$exe = Join-Path $installRoot 'Arvectum Proxy Launcher.exe'
$repair = Join-Path $installRoot 'Arvectum Proxy Launcher Repair.exe'
$uninstaller = Join-Path $installRoot 'unins000.exe'
$manifestPath = Join-Path $installRoot 'build_manifest.json'
$ownerMarker = Join-Path $installRoot '.arvectum-install-owner'
$stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-ExactPath([string]$Candidate, [string]$Expected) {
    if (-not $Candidate -or -not $Expected) { return $false }
    try {
        return [IO.Path]::GetFullPath($Candidate).TrimEnd('\') -ieq [IO.Path]::GetFullPath($Expected).TrimEnd('\')
    }
    catch {
        return $false
    }
}

function Invoke-NativeExitCode {
    param(
        [Parameter(Mandatory = $true)] [string]$FilePath,
        [string[]]$ArgumentList = @()
    )
    $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -PassThru -Wait
    return [int]$process.ExitCode
}

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory = $true)] [string]$FilePath,
        [string[]]$ArgumentList = @(),
        [Parameter(Mandatory = $true)] [string]$Label
    )
    $exitCode = Invoke-NativeExitCode -FilePath $FilePath -ArgumentList $ArgumentList
    if ($exitCode -ne 0) {
        throw "$Label failed with exit code $exitCode"
    }
}

function Get-ExactLauncherProcesses([string]$ExpectedExe) {
    $running = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    foreach ($process in $running) {
        $path = [string]$process.ExecutablePath
        if (-not $path) {
            throw "A running Arvectum Proxy Launcher process cannot be path-verified: PID=$($process.ProcessId)"
        }
        if (-not (Test-ExactPath $path $ExpectedExe)) {
            throw "A same-named foreign launcher process is running and will not be touched: PID=$($process.ProcessId) PATH=$path"
        }
        if (-not [string]$process.CommandLine) {
            throw "A governed launcher process cannot be command-line classified safely: PID=$($process.ProcessId)"
        }
    }
    return $running
}

function Test-CoreProcess([object]$Process) {
    return ([string]$Process.CommandLine -match '(?i)(^|\s)--start(\s|$)')
}

function Test-MaintenanceProcess([object]$Process) {
    return ([string]$Process.CommandLine -match '(?i)(^|\s)--(stop|status|rollback|doctor|doctor-json)(\s|$)')
}

function Get-RecoveryFiles {
    $result = @()
    foreach ($name in @('proxy_internet_backup.json','proxy_env_backup.json')) {
        $candidate = Join-Path $stateRoot $name
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { $result += $candidate }
    }
    return $result
}

function Stop-ExactRuntime([string]$ExpectedExe) {
    Write-Host 'Quiescing exact governed runtime through product recovery paths.'

    $stopExit = Invoke-NativeExitCode -FilePath $ExpectedExe -ArgumentList @('--stop')
    if ($stopExit -ne 0) {
        Write-Host "Product --stop returned $stopExit; attempting explicit --rollback."
        $rollbackExit = Invoke-NativeExitCode -FilePath $ExpectedExe -ArgumentList @('--rollback')
        if ($rollbackExit -ne 0) {
            throw "Runtime quiesce failed: --stop exit=$stopExit; --rollback exit=$rollbackExit"
        }
    }

    Start-Sleep -Milliseconds 600
    $remaining = @(Get-ExactLauncherProcesses -ExpectedExe $ExpectedExe)

    foreach ($process in $remaining) {
        try {
            $live = Get-Process -Id ([int]$process.ProcessId) -ErrorAction Stop
            [void]$live.CloseMainWindow()
        }
        catch {
        }
    }

    Start-Sleep -Seconds 2
    $remaining = @(Get-ExactLauncherProcesses -ExpectedExe $ExpectedExe)
    foreach ($process in $remaining) {
        Stop-Process -Id ([int]$process.ProcessId) -Force -ErrorAction Stop
    }

    Start-Sleep -Milliseconds 600
    $remaining = @(Get-ExactLauncherProcesses -ExpectedExe $ExpectedExe)
    if ($remaining.Count -gt 0) {
        $details = @($remaining | ForEach-Object { "PID=$($_.ProcessId) PATH=$($_.ExecutablePath)" }) -join '; '
        throw "Exact governed runtime did not quiesce: $details"
    }

    $recoveryFiles = @(Get-RecoveryFiles)
    if ($recoveryFiles.Count -gt 0) {
        Write-Host 'Recovery evidence remains after --stop; attempting final explicit --rollback.'
        $rollbackExit = Invoke-NativeExitCode -FilePath $ExpectedExe -ArgumentList @('--rollback')
        if ($rollbackExit -ne 0) {
            throw "Final rollback failed with exit code $rollbackExit"
        }
        $recoveryFiles = @(Get-RecoveryFiles)
    }

    if ($recoveryFiles.Count -gt 0) {
        throw "Network recovery state remains after runtime quiesce: $($recoveryFiles -join '; ')"
    }
}

function Start-OriginalRuntime {
    param(
        [bool]$CoreWasRunning,
        [bool]$GuiWasRunning
    )

    if ($CoreWasRunning) {
        Write-Host 'Restoring original proxy-core running state.'
        $coreProcess = Start-Process -FilePath $exe -ArgumentList @('--start') -WorkingDirectory $installRoot -PassThru
        Start-Sleep -Seconds 2
        if ($coreProcess.HasExited) {
            throw "Restored proxy-core exited unexpectedly with code $($coreProcess.ExitCode)"
        }
        $runtime = @(Get-ExactLauncherProcesses -ExpectedExe $exe)
        $coreMatches = @($runtime | Where-Object { Test-CoreProcess $_ })
        if ($coreMatches.Count -lt 1) {
            throw 'Restored proxy-core process was not observed.'
        }
    }

    if ($GuiWasRunning) {
        Write-Host 'Restoring original GUI running state.'
        $guiProcess = Start-Process -FilePath $exe -WorkingDirectory $installRoot -PassThru
        Start-Sleep -Seconds 2
        if ($guiProcess.HasExited) {
            throw "Restored GUI exited unexpectedly with code $($guiProcess.ExitCode)"
        }
        $runtime = @(Get-ExactLauncherProcesses -ExpectedExe $exe)
        $guiMatches = @($runtime | Where-Object { -not (Test-CoreProcess $_) -and -not (Test-MaintenanceProcess $_) })
        if ($guiMatches.Count -lt 1) {
            throw 'Restored GUI process was not observed.'
        }
    }
}

function Invoke-OwnerHostAcceptance {
    $args = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', ('"' + $ownerHostScript + '"'),
        '-ReleaseDirectory', ('"' + $ReleaseDirectory + '"'),
        '-EvidencePath', ('"' + $EvidencePath + '"')
    )
    Invoke-NativeChecked -FilePath 'powershell.exe' -ArgumentList $args -Label 'owner-host lifecycle acceptance'
}

$registered = @()
foreach ($path in @($UserUninstallKey, $MachineUninstallKey, $MachineWowUninstallKey)) {
    if (Test-Path -LiteralPath $path) { $registered += $path }
}

if ($registered.Count -eq 0) {
    Write-Host 'No registered installer installation detected; delegating to owner-host lifecycle wrapper.'
    Invoke-OwnerHostAcceptance
    exit 0
}

if ($registered.Count -ne 1 -or $registered[0] -cne $UserUninstallKey) {
    throw "Registered installation is ambiguous or machine-wide. Refusing runtime mutation: $($registered -join '; ')"
}

foreach ($required in @($exe, $repair, $uninstaller, $manifestPath, $ownerMarker)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Registered installation is incomplete and runtime mutation is blocked: $required"
    }
}

if ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256) {
    throw 'Registered installation EXE is not the exact sealed 0.2.3 application.'
}
if ((Get-Sha256 $repair) -ne $ExpectedSetupSha256) {
    throw 'Registered cached repair installer is not the exact production installer.'
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ([string]$manifest.version -ne $ExpectedVersion) {
    throw 'Registered installation manifest version is not 0.2.3.'
}
if (([string]$manifest.application_sha256).ToLowerInvariant() -ne $ExpectedApplicationSha256) {
    throw 'Registered installation manifest does not bind the exact sealed application hash.'
}

$registration = Get-ItemProperty -LiteralPath $UserUninstallKey
if ([string]$registration.DisplayName -ne 'Arvectum Proxy Launcher') { throw 'Registered DisplayName mismatch.' }
if ([string]$registration.DisplayVersion -ne $ExpectedVersion) { throw 'Registered DisplayVersion mismatch.' }
if ($registration.PSObject.Properties['InstallLocation']) {
    $registeredLocation = [string]$registration.InstallLocation
    if ($registeredLocation -and -not (Test-ExactPath $registeredLocation $installRoot)) {
        throw "Registered InstallLocation mismatch: $registeredLocation"
    }
}

$runtimeBefore = @(Get-ExactLauncherProcesses -ExpectedExe $exe)
$maintenanceBefore = @($runtimeBefore | Where-Object { Test-MaintenanceProcess $_ })
if ($maintenanceBefore.Count -gt 0) {
    $details = @($maintenanceBefore | ForEach-Object { "PID=$($_.ProcessId) CMD=$($_.CommandLine)" }) -join '; '
    throw "A launcher maintenance command is already running; retry after it exits: $details"
}

$coreBefore = @($runtimeBefore | Where-Object { Test-CoreProcess $_ })
$guiBefore = @($runtimeBefore | Where-Object { -not (Test-CoreProcess $_) -and -not (Test-MaintenanceProcess $_) })
$wasRuntimeRunning = ($runtimeBefore.Count -gt 0)
$wasCoreRunning = ($coreBefore.Count -gt 0)
$wasGuiRunning = ($guiBefore.Count -gt 0)

Write-Host "Exact governed running processes: $($runtimeBefore.Count)"
Write-Host "Original proxy-core running     : $wasCoreRunning"
Write-Host "Original GUI running            : $wasGuiRunning"

$quiescePassed = $false
$ownerPassed = $false
$ownerError = $null
$runtimeRestoreWarnings = @()

try {
    if ($wasRuntimeRunning) {
        Stop-ExactRuntime -ExpectedExe $exe
        $quiescePassed = $true
    }
    else {
        $recoveryFiles = @(Get-RecoveryFiles)
        if ($recoveryFiles.Count -gt 0) {
            throw "Unresolved network recovery state exists while runtime is stopped: $($recoveryFiles -join '; ')"
        }
        $quiescePassed = $true
    }

    Invoke-OwnerHostAcceptance
    $ownerPassed = $true
}
catch {
    $ownerError = $_.Exception.Message
}
finally {
    if ($quiescePassed -and $wasRuntimeRunning) {
        try {
            Start-OriginalRuntime -CoreWasRunning $wasCoreRunning -GuiWasRunning $wasGuiRunning
        }
        catch {
            $runtimeRestoreWarnings += $_.Exception.Message
        }
    }
}

$runtimeRestored = ($runtimeRestoreWarnings.Count -eq 0)

if (Test-Path -LiteralPath $EvidencePath -PathType Leaf) {
    try {
        $evidence = Get-Content -LiteralPath $EvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $evidence | Add-Member -NotePropertyName owner_host_runtime_was_running -NotePropertyValue $wasRuntimeRunning -Force
        $evidence | Add-Member -NotePropertyName owner_host_core_was_running -NotePropertyValue $wasCoreRunning -Force
        $evidence | Add-Member -NotePropertyName owner_host_gui_was_running -NotePropertyValue $wasGuiRunning -Force
        $evidence | Add-Member -NotePropertyName owner_host_runtime_quiesced -NotePropertyValue ($(if ($quiescePassed) { 'PASS' } else { 'BLOCK' })) -Force
        $evidence | Add-Member -NotePropertyName owner_host_runtime_restored -NotePropertyValue $runtimeRestored -Force
        if (-not $runtimeRestored) {
            $evidence.result = 'BLOCK'
            $evidence | Add-Member -NotePropertyName owner_host_runtime_restore_warnings -NotePropertyValue @($runtimeRestoreWarnings) -Force
        }
        $evidence | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
    }
    catch {
        $runtimeRestoreWarnings += "runtime evidence update failed: $($_.Exception.Message)"
        $runtimeRestored = $false
    }
}

if (-not $runtimeRestored) {
    throw "Owner-host runtime restoration BLOCK: $($runtimeRestoreWarnings -join '; ')"
}
if (-not $ownerPassed) {
    throw "Owner-host lifecycle acceptance failed after safe runtime handling: $ownerError"
}

Write-Host ''
Write-Host 'APL-REL-014 runtime-aware owner-host wrapper: PASS'
Write-Host 'Exact installed instance validation: PASS'
Write-Host "Original runtime running: $wasRuntimeRunning"
Write-Host "Original proxy-core running: $wasCoreRunning"
Write-Host "Original GUI running: $wasGuiRunning"
Write-Host 'Runtime quiesce: PASS'
Write-Host 'Owner-host signed-set lifecycle acceptance: PASS'
Write-Host 'Original runtime state restored: PASS'
Write-Host "Evidence: $EvidencePath"
