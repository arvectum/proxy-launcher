<#
.SYNOPSIS
    Legacy-owner-host compatibility wrapper for APL-REL-014.
.DESCRIPTION
    Validates the exact sealed 0.2.3 executable and the exact HKCU product
    registration before touching runtime state. The pre-existing install tree
    is treated as opaque legacy host state: support files may be missing or
    differ because they are never executed by this wrapper.

    The wrapper verifies the exact signed production release, safely quiesces
    only the exact governed executable, snapshots the complete legacy install
    tree/state/registration/shortcuts, runs canonical APL-REL-014 against the
    signed release, restores the legacy snapshot, proves the install tree was
    restored byte-for-byte, and restores the original runtime shape.
#>
[CmdletBinding()]
param(
    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$EvidencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Legacy-host lifecycle acceptance must run on Windows.' }

$ExpectedVersion = '0.2.3'
$ExpectedApplicationSha256 = 'f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a'
$ExpectedSetupSha256 = '5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414'
$ExpectedSignerThumbprint = 'EE1CFA955BA22F03C39C76B183D94CD37494582E'
$SetupName = 'Arvectum-Proxy-Launcher-0.2.3-windows-x64-setup.exe'
$AppKeyName = '{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}_is1'
$UserUninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$MachineUninstallKey = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$MachineWowUninstallKey = "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$NativeUserUninstallKey = "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"

$ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
if (-not $EvidencePath) { $EvidencePath = $ReleaseDirectory + '.lifecycle-acceptance.json' }
$setup = Join-Path $ReleaseDirectory $SetupName
$verifier = Join-Path $ReleaseDirectory 'verify_russian_release.ps1'
$baseScript = Join-Path $PSScriptRoot 'windows_signed_set_lifecycle_acceptance.ps1'

foreach ($required in @($setup, $verifier, $baseScript)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required legacy-host input is missing: $required"
    }
}

$documents = [Environment]::GetFolderPath('MyDocuments')
$installRoot = Join-Path $documents 'ArvectumProxyLauncher'
$exe = Join-Path $installRoot 'Arvectum Proxy Launcher.exe'
$stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$mainRunName = 'ArvectumProxyLauncher'
$recoveryRunName = 'ArvectumProxyLauncherRecovery'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-TextSha256([string]$Text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        $hash = $sha.ComputeHash($bytes)
        return (-join ($hash | ForEach-Object { $_.ToString('x2') }))
    }
    finally {
        $sha.Dispose()
    }
}

function Get-InstallTreeFingerprint([string]$Root) {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        throw "Install tree is missing while fingerprinting: $Root"
    }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    $lines = @(
        Get-ChildItem -LiteralPath $Root -File -Recurse | ForEach-Object {
            $full = [IO.Path]::GetFullPath($_.FullName)
            $relative = $full.Substring($rootFull.Length).TrimStart('\')
            $hash = Get-Sha256 $_.FullName
            "$relative`t$($_.Length)`t$hash"
        } | Sort-Object
    )
    $body = $lines -join "`n"
    return [pscustomobject]@{
        FileCount = $lines.Count
        Sha256 = (Get-TextSha256 $body)
    }
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
    if ($exitCode -ne 0) { throw "$Label failed with exit code $exitCode" }
}

function Invoke-ReleaseVerifier {
    $args = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', ('"' + $verifier + '"'),
        '-ReleaseDirectory', ('"' + $ReleaseDirectory + '"'),
        '-ExpectedSignerThumbprint', $ExpectedSignerThumbprint
    )
    Invoke-NativeChecked -FilePath 'powershell.exe' -ArgumentList $args -Label 'signed release verification'
}

function Invoke-BaseAcceptance {
    $args = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', ('"' + $baseScript + '"'),
        '-ReleaseDirectory', ('"' + $ReleaseDirectory + '"'),
        '-EvidencePath', ('"' + $EvidencePath + '"')
    )
    Invoke-NativeChecked -FilePath 'powershell.exe' -ArgumentList $args -Label 'canonical signed-set lifecycle acceptance'
}

function Get-RunValue([string]$Name) {
    $runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    $item = Get-ItemProperty -Path $runPath -ErrorAction SilentlyContinue
    if ($null -eq $item) { return $null }
    $property = $item.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return [string]$property.Value
}

function Set-RunValue([string]$Name, [AllowNull()][string]$Value) {
    $runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    New-Item -Path $runPath -Force | Out-Null
    if ($null -eq $Value) {
        Remove-ItemProperty -Path $runPath -Name $Name -ErrorAction SilentlyContinue
    }
    else {
        New-ItemProperty -Path $runPath -Name $Name -Value $Value -PropertyType String -Force | Out-Null
    }
}

function Get-ExactLauncherProcesses([string]$ExpectedExe) {
    $running = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    foreach ($process in $running) {
        $path = [string]$process.ExecutablePath
        if (-not $path) {
            throw "A running launcher process cannot be path-verified: PID=$($process.ProcessId)"
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
        throw 'Exact governed runtime did not quiesce completely.'
    }

    $recoveryFiles = @(Get-RecoveryFiles)
    if ($recoveryFiles.Count -gt 0) {
        $rollbackExit = Invoke-NativeExitCode -FilePath $ExpectedExe -ArgumentList @('--rollback')
        if ($rollbackExit -ne 0) { throw "Final rollback failed with exit code $rollbackExit" }
        $recoveryFiles = @(Get-RecoveryFiles)
    }
    if ($recoveryFiles.Count -gt 0) {
        throw "Network recovery state remains after runtime quiesce: $($recoveryFiles -join '; ')"
    }
}

function Start-OriginalRuntime {
    param([bool]$CoreWasRunning, [bool]$GuiWasRunning)

    if ($CoreWasRunning) {
        Write-Host 'Restoring original proxy-core running state.'
        $coreProcess = Start-Process -FilePath $exe -ArgumentList @('--start') -WorkingDirectory $installRoot -PassThru
        Start-Sleep -Seconds 2
        if ($coreProcess.HasExited) { throw "Restored proxy-core exited unexpectedly with code $($coreProcess.ExitCode)" }
        $runtime = @(Get-ExactLauncherProcesses -ExpectedExe $exe)
        if (@($runtime | Where-Object { Test-CoreProcess $_ }).Count -lt 1) {
            throw 'Restored proxy-core process was not observed.'
        }
    }

    if ($GuiWasRunning) {
        Write-Host 'Restoring original GUI running state.'
        $guiProcess = Start-Process -FilePath $exe -WorkingDirectory $installRoot -PassThru
        Start-Sleep -Seconds 2
        if ($guiProcess.HasExited) { throw "Restored GUI exited unexpectedly with code $($guiProcess.ExitCode)" }
        $runtime = @(Get-ExactLauncherProcesses -ExpectedExe $exe)
        $guiMatches = @($runtime | Where-Object { -not (Test-CoreProcess $_) -and -not (Test-MaintenanceProcess $_) })
        if ($guiMatches.Count -lt 1) { throw 'Restored GUI process was not observed.' }
    }
}

$setupHash = Get-Sha256 $setup
if ($setupHash -ne $ExpectedSetupSha256) { throw 'Signed production installer hash mismatch.' }

Write-Host '=== Legacy-host preflight: exact signed release verification ==='
Invoke-ReleaseVerifier

$registered = @()
foreach ($path in @($UserUninstallKey, $MachineUninstallKey, $MachineWowUninstallKey)) {
    if (Test-Path -LiteralPath $path) { $registered += $path }
}

if ($registered.Count -eq 0) {
    Write-Host 'No registered legacy installation detected; running canonical lifecycle acceptance directly.'
    Invoke-BaseAcceptance
    exit 0
}
if ($registered.Count -ne 1 -or $registered[0] -cne $UserUninstallKey) {
    throw "Registered installation is ambiguous or machine-wide. Refusing mutation: $($registered -join '; ')"
}

if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw "Registered installation does not contain the governed executable: $exe"
}
if ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256) {
    throw 'Registered installation EXE is not the exact sealed 0.2.3 application.'
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

$supportPaths = [ordered]@{
    repair_installer = (Join-Path $installRoot 'Arvectum Proxy Launcher Repair.exe')
    build_manifest = (Join-Path $installRoot 'build_manifest.json')
    owner_marker = (Join-Path $installRoot '.arvectum-install-owner')
    inno_uninstaller = (Join-Path $installRoot 'unins000.exe')
    upgrade_helper = (Join-Path $installRoot 'upgrade_helper.ps1')
    uninstall_helper = (Join-Path $installRoot 'uninstall_helper.ps1')
}
$supportStates = [ordered]@{}
$missingSupport = @()
foreach ($entry in $supportPaths.GetEnumerator()) {
    $present = Test-Path -LiteralPath $entry.Value -PathType Leaf
    $supportStates[$entry.Key] = $(if ($present) { 'PRESENT' } else { 'MISSING' })
    if (-not $present) { $missingSupport += $entry.Key }
}

$runtimeBefore = @(Get-ExactLauncherProcesses -ExpectedExe $exe)
$maintenanceBefore = @($runtimeBefore | Where-Object { Test-MaintenanceProcess $_ })
if ($maintenanceBefore.Count -gt 0) {
    throw 'A launcher maintenance command is already running; retry after it exits.'
}
$coreBefore = @($runtimeBefore | Where-Object { Test-CoreProcess $_ })
$guiBefore = @($runtimeBefore | Where-Object { -not (Test-CoreProcess $_) -and -not (Test-MaintenanceProcess $_) })
$wasRuntimeRunning = ($runtimeBefore.Count -gt 0)
$wasCoreRunning = ($coreBefore.Count -gt 0)
$wasGuiRunning = ($guiBefore.Count -gt 0)

Write-Host "Exact governed running processes: $($runtimeBefore.Count)"
Write-Host "Original proxy-core running     : $wasCoreRunning"
Write-Host "Original GUI running            : $wasGuiRunning"
Write-Host "Missing legacy support files    : $($missingSupport -join ', ')"

$quiescePassed = $false
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

$treeBefore = Get-InstallTreeFingerprint -Root $installRoot
Write-Host "Legacy install tree files       : $($treeBefore.FileCount)"
Write-Host "Legacy install tree SHA256      : $($treeBefore.Sha256)"

$sessionId = [guid]::NewGuid().ToString('N')
$workRoot = Join-Path $env:TEMP ("ArvectumLegacyHostAcceptance-$sessionId")
$backupRoot = Join-Path $workRoot 'snapshot'
$installBackup = Join-Path $backupRoot 'install-root'
$stateBackup = Join-Path $backupRoot 'state-root'
$registryBackup = Join-Path $backupRoot 'uninstall-registration.reg'
$shortcutBackupRoot = Join-Path $backupRoot 'shortcuts'
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
New-Item -ItemType Directory -Path $shortcutBackupRoot -Force | Out-Null

$oldMainRun = Get-RunValue $mainRunName
$oldRecoveryRun = Get-RunValue $recoveryRunName
$hadStateRoot = Test-Path -LiteralPath $stateRoot
$shortcutPaths = @(
    (Join-Path ([Environment]::GetFolderPath('Programs')) 'Arvectum Proxy Launcher.lnk'),
    (Join-Path ([Environment]::GetFolderPath('Programs')) 'Repair Arvectum Proxy Launcher.lnk'),
    (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Arvectum Proxy Launcher.lnk')
)
$shortcutSnapshots = @()
$shortcutIndex = 0
foreach ($shortcut in $shortcutPaths) {
    if (Test-Path -LiteralPath $shortcut -PathType Leaf) {
        $backup = Join-Path $shortcutBackupRoot ("shortcut-$shortcutIndex.lnk")
        Copy-Item -LiteralPath $shortcut -Destination $backup -Force
        $shortcutSnapshots += [pscustomobject]@{ Original = $shortcut; Backup = $backup }
        $shortcutIndex += 1
    }
}

Invoke-NativeChecked -FilePath 'reg.exe' -ArgumentList @('export', $NativeUserUninstallKey, ('"' + $registryBackup + '"'), '/y') -Label 'export legacy uninstall registration'
if (-not (Test-Path -LiteralPath $registryBackup -PathType Leaf)) { throw 'Registry snapshot was not created.' }

$basePassed = $false
$baseError = $null
$restoreWarnings = @()
$treeRestored = $false

try {
    Move-Item -LiteralPath $installRoot -Destination $installBackup
    if ($hadStateRoot) { Move-Item -LiteralPath $stateRoot -Destination $stateBackup }
    Set-RunValue $mainRunName $null
    Set-RunValue $recoveryRunName $null
    foreach ($shortcut in $shortcutPaths) { Remove-Item -LiteralPath $shortcut -Force -ErrorAction SilentlyContinue }
    Remove-Item -LiteralPath $UserUninstallKey -Recurse -Force

    if (Test-Path -LiteralPath $UserUninstallKey) { throw 'Failed to isolate legacy uninstall registration.' }
    if (Test-Path -LiteralPath $installRoot) { throw 'Failed to isolate legacy install root.' }

    Invoke-BaseAcceptance
    $basePassed = $true
}
catch {
    $baseError = $_.Exception.Message
}
finally {
    try {
        $testUninstaller = Join-Path $installRoot 'unins000.exe'
        if (Test-Path -LiteralPath $testUninstaller -PathType Leaf) {
            $p = Start-Process -FilePath $testUninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -PassThru -Wait -ErrorAction SilentlyContinue
            if ($p -and $p.ExitCode -ne 0) { $restoreWarnings += "test cleanup uninstaller exit=$($p.ExitCode)" }
        }
    }
    catch { $restoreWarnings += "test cleanup uninstall: $($_.Exception.Message)" }

    try { Remove-Item -LiteralPath $installRoot -Recurse -Force -ErrorAction SilentlyContinue } catch { $restoreWarnings += "remove test install root: $($_.Exception.Message)" }
    try { Remove-Item -LiteralPath $stateRoot -Recurse -Force -ErrorAction SilentlyContinue } catch { $restoreWarnings += "remove test state root: $($_.Exception.Message)" }
    try { Remove-Item -LiteralPath $UserUninstallKey -Recurse -Force -ErrorAction SilentlyContinue } catch { $restoreWarnings += "remove test uninstall registration: $($_.Exception.Message)" }
    foreach ($shortcut in $shortcutPaths) {
        try { Remove-Item -LiteralPath $shortcut -Force -ErrorAction SilentlyContinue } catch { $restoreWarnings += "remove test shortcut: $shortcut" }
    }

    try { Move-Item -LiteralPath $installBackup -Destination $installRoot } catch { $restoreWarnings += "restore install root: $($_.Exception.Message)" }
    try {
        if ($hadStateRoot -and (Test-Path -LiteralPath $stateBackup)) {
            New-Item -ItemType Directory -Path (Split-Path -Parent $stateRoot) -Force | Out-Null
            Move-Item -LiteralPath $stateBackup -Destination $stateRoot
        }
    }
    catch { $restoreWarnings += "restore state root: $($_.Exception.Message)" }
    try { Set-RunValue $mainRunName $oldMainRun } catch { $restoreWarnings += "restore main Run: $($_.Exception.Message)" }
    try { Set-RunValue $recoveryRunName $oldRecoveryRun } catch { $restoreWarnings += "restore recovery Run: $($_.Exception.Message)" }
    try { Invoke-NativeChecked -FilePath 'reg.exe' -ArgumentList @('import', ('"' + $registryBackup + '"')) -Label 'restore legacy uninstall registration' } catch { $restoreWarnings += "restore uninstall registration: $($_.Exception.Message)" }
    foreach ($snapshot in $shortcutSnapshots) {
        try {
            New-Item -ItemType Directory -Path (Split-Path -Parent $snapshot.Original) -Force | Out-Null
            Copy-Item -LiteralPath $snapshot.Backup -Destination $snapshot.Original -Force
        }
        catch { $restoreWarnings += "restore shortcut: $($snapshot.Original): $($_.Exception.Message)" }
    }

    try {
        $treeAfter = Get-InstallTreeFingerprint -Root $installRoot
        $treeRestored = (
            $treeAfter.FileCount -eq $treeBefore.FileCount -and
            $treeAfter.Sha256 -eq $treeBefore.Sha256
        )
        if (-not $treeRestored) {
            $restoreWarnings += "legacy install tree fingerprint mismatch after restore: before=$($treeBefore.Sha256) after=$($treeAfter.Sha256)"
        }
    }
    catch {
        $restoreWarnings += "legacy install tree fingerprint after restore: $($_.Exception.Message)"
    }
}

$runtimeRestoreWarnings = @()
if ($restoreWarnings.Count -eq 0 -and $quiescePassed -and $wasRuntimeRunning) {
    try {
        Start-OriginalRuntime -CoreWasRunning $wasCoreRunning -GuiWasRunning $wasGuiRunning
    }
    catch {
        $runtimeRestoreWarnings += $_.Exception.Message
    }
}
$runtimeRestored = ($runtimeRestoreWarnings.Count -eq 0)

if ($treeRestored -and $runtimeRestored) {
    try {
        $treeAfterRuntime = Get-InstallTreeFingerprint -Root $installRoot
        if ($treeAfterRuntime.FileCount -ne $treeBefore.FileCount -or $treeAfterRuntime.Sha256 -ne $treeBefore.Sha256) {
            $treeRestored = $false
            $restoreWarnings += 'legacy install tree changed while restoring runtime shape.'
        }
    }
    catch {
        $treeRestored = $false
        $restoreWarnings += "post-runtime install tree verification: $($_.Exception.Message)"
    }
}

$restorePassed = ($restoreWarnings.Count -eq 0 -and $runtimeRestoreWarnings.Count -eq 0 -and $treeRestored)

if (Test-Path -LiteralPath $EvidencePath -PathType Leaf) {
    try {
        $evidence = Get-Content -LiteralPath $EvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $evidence | Add-Member -NotePropertyName preexisting_registered_install -NotePropertyValue $true -Force
        $evidence | Add-Member -NotePropertyName preexisting_registered_runtime_exact -NotePropertyValue 'PASS' -Force
        $evidence | Add-Member -NotePropertyName preexisting_registered_install_exact -NotePropertyValue 'RUNTIME_EXACT_SUPPORT_DRIFT' -Force
        $evidence | Add-Member -NotePropertyName legacy_support_drift_accepted -NotePropertyValue $true -Force
        $evidence | Add-Member -NotePropertyName preexisting_support_files -NotePropertyValue ([pscustomobject]$supportStates) -Force
        $evidence | Add-Member -NotePropertyName preexisting_support_missing -NotePropertyValue @($missingSupport) -Force
        $evidence | Add-Member -NotePropertyName preexisting_install_tree_sha256 -NotePropertyValue $treeBefore.Sha256 -Force
        $evidence | Add-Member -NotePropertyName preexisting_install_tree_file_count -NotePropertyValue $treeBefore.FileCount -Force
        $evidence | Add-Member -NotePropertyName owner_host_install_tree_restored_exact -NotePropertyValue $treeRestored -Force
        $evidence | Add-Member -NotePropertyName owner_host_snapshot_restored -NotePropertyValue $restorePassed -Force
        $evidence | Add-Member -NotePropertyName owner_host_runtime_was_running -NotePropertyValue $wasRuntimeRunning -Force
        $evidence | Add-Member -NotePropertyName owner_host_core_was_running -NotePropertyValue $wasCoreRunning -Force
        $evidence | Add-Member -NotePropertyName owner_host_gui_was_running -NotePropertyValue $wasGuiRunning -Force
        $evidence | Add-Member -NotePropertyName owner_host_runtime_quiesced -NotePropertyValue ($(if ($quiescePassed) { 'PASS' } else { 'BLOCK' })) -Force
        $evidence | Add-Member -NotePropertyName owner_host_runtime_restored -NotePropertyValue $runtimeRestored -Force
        if (-not $restorePassed) {
            $evidence.result = 'BLOCK'
            $evidence | Add-Member -NotePropertyName legacy_host_restore_warnings -NotePropertyValue @($restoreWarnings + $runtimeRestoreWarnings) -Force
        }
        $evidence | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
    }
    catch {
        $restoreWarnings += "legacy-host evidence update failed: $($_.Exception.Message)"
        $restorePassed = $false
    }
}

Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue

if (-not $restorePassed) {
    throw "Legacy owner-host restoration BLOCK: $($restoreWarnings + $runtimeRestoreWarnings -join '; ')"
}
if (-not $basePassed) {
    throw "Canonical signed-set lifecycle acceptance failed after reversible legacy snapshot: $baseError"
}

Write-Host ''
Write-Host 'APL-REL-014 legacy-owner-host compatibility wrapper: PASS'
Write-Host 'Exact installed runtime identity: PASS'
Write-Host "Legacy support files missing: $($missingSupport -join ', ')"
Write-Host "Legacy install tree SHA256: $($treeBefore.Sha256)"
Write-Host 'Legacy install tree byte-exact restoration: PASS'
Write-Host "Original runtime running: $wasRuntimeRunning"
Write-Host "Original proxy-core running: $wasCoreRunning"
Write-Host "Original GUI running: $wasGuiRunning"
Write-Host 'Runtime quiesce: PASS'
Write-Host 'Runtime restoration: PASS'
Write-Host 'Canonical exact signed-set lifecycle acceptance: PASS'
Write-Host "Evidence: $EvidencePath"
