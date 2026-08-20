<#
.SYNOPSIS
    Migration-style owner-host wrapper for APL-REL-014 when the registered
    0.2.3 installation is not byte-identical to the sealed production EXE.
.DESCRIPTION
    The pre-existing installation is treated as opaque legacy host state.
    This wrapper never executes legacy support files and never uses the legacy
    EXE to prove the release. It verifies the exact signed v0.2.3-ru.2 release,
    records the legacy EXE hash and metadata, creates an independent rescue
    snapshot, quiesces only path-verified legacy launcher processes via Windows
    process control, isolates the old installation, runs canonical exact signed-
    set lifecycle acceptance, restores the old host byte-for-byte, and restores
    the original GUI/core runtime shape.
#>
[CmdletBinding()]
param(
    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$EvidencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Migration lifecycle acceptance must run on Windows.' }

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
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Required migration input is missing: $required" }
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
    finally { $sha.Dispose() }
}

function Get-TreeFingerprint([string]$Root) {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return $null }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    $lines = @(
        Get-ChildItem -LiteralPath $Root -File -Recurse -Force | ForEach-Object {
            $full = [IO.Path]::GetFullPath($_.FullName)
            $relative = $full.Substring($rootFull.Length).TrimStart('\')
            "$relative`t$($_.Length)`t$(Get-Sha256 $_.FullName)"
        } | Sort-Object
    )
    return [pscustomobject]@{ FileCount = $lines.Count; Sha256 = (Get-TextSha256 ($lines -join "`n")) }
}

function Test-ExactPath([string]$Candidate, [string]$Expected) {
    if (-not $Candidate -or -not $Expected) { return $false }
    try { return [IO.Path]::GetFullPath($Candidate).TrimEnd('\') -ieq [IO.Path]::GetFullPath($Expected).TrimEnd('\') }
    catch { return $false }
}

function Invoke-NativeChecked {
    param([string]$FilePath, [string[]]$ArgumentList = @(), [string]$Label)
    $p = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -PassThru -Wait
    if ($p.ExitCode -ne 0) { throw "$Label failed with exit code $($p.ExitCode)" }
}

function Invoke-ReleaseVerifier {
    $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $verifier + '"'),'-ReleaseDirectory',('"' + $ReleaseDirectory + '"'),'-ExpectedSignerThumbprint',$ExpectedSignerThumbprint)
    Invoke-NativeChecked -FilePath 'powershell.exe' -ArgumentList $args -Label 'signed release verification'
}

function Invoke-BaseAcceptance {
    $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $baseScript + '"'),'-ReleaseDirectory',('"' + $ReleaseDirectory + '"'),'-EvidencePath',('"' + $EvidencePath + '"'))
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
    if ($null -eq $Value) {
        if (Test-Path -LiteralPath $runPath) { Remove-ItemProperty -Path $runPath -Name $Name -ErrorAction SilentlyContinue }
    }
    else {
        New-Item -Path $runPath -Force | Out-Null
        New-ItemProperty -Path $runPath -Name $Name -Value $Value -PropertyType String -Force | Out-Null
    }
}

function Get-LegacyProcesses {
    $running = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    foreach ($process in $running) {
        $path = [string]$process.ExecutablePath
        if (-not $path) { throw "A running launcher process cannot be path-verified: PID=$($process.ProcessId)" }
        if (-not (Test-ExactPath $path $exe)) { throw "A same-named foreign launcher process is running and will not be touched: PID=$($process.ProcessId) PATH=$path" }
        if (-not [string]$process.CommandLine) { throw "A registered launcher process cannot be classified safely: PID=$($process.ProcessId)" }
        if ([string]$process.CommandLine -match '(?i)(^|\s)--(stop|status|rollback|doctor|doctor-json)(\s|$)') {
            throw "A maintenance launcher command is already running: PID=$($process.ProcessId) CMD=$($process.CommandLine)"
        }
    }
    return $running
}

function Test-CoreProcess([object]$Process) {
    return ([string]$Process.CommandLine -match '(?i)(^|\s)--start(\s|$)')
}

function Stop-LegacyProcesses([object[]]$Processes) {
    foreach ($process in $Processes) {
        try {
            $live = Get-Process -Id ([int]$process.ProcessId) -ErrorAction Stop
            [void]$live.CloseMainWindow()
        }
        catch { }
    }
    Start-Sleep -Seconds 2
    foreach ($process in @(Get-LegacyProcesses)) {
        Stop-Process -Id ([int]$process.ProcessId) -Force -ErrorAction Stop
    }
    Start-Sleep -Milliseconds 500
    if (@(Get-LegacyProcesses).Count -gt 0) { throw 'Registered legacy runtime did not quiesce.' }
}

function Start-LegacyRuntime([int]$CoreCount, [int]$GuiCount) {
    for ($i = 0; $i -lt $CoreCount; $i++) { Start-Process -FilePath $exe -ArgumentList @('--start') -WorkingDirectory $installRoot | Out-Null }
    if ($CoreCount -gt 0) { Start-Sleep -Seconds 2 }
    for ($i = 0; $i -lt $GuiCount; $i++) { Start-Process -FilePath $exe -WorkingDirectory $installRoot | Out-Null }
    if ($GuiCount -gt 0) { Start-Sleep -Seconds 2 }
}

$registered = @()
foreach ($path in @($UserUninstallKey, $MachineUninstallKey, $MachineWowUninstallKey)) {
    if (Test-Path -LiteralPath $path) { $registered += $path }
}
if ($registered.Count -ne 1 -or $registered[0] -cne $UserUninstallKey) {
    throw "Registered installation is absent, ambiguous or machine-wide: $($registered -join '; ')"
}
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "Registered executable is missing: $exe" }

$registration = Get-ItemProperty -LiteralPath $UserUninstallKey
$legacyDisplayName = if ($registration.PSObject.Properties['DisplayName']) { [string]$registration.DisplayName } else { $null }
if ([string]$registration.DisplayVersion -ne $ExpectedVersion) { throw 'Registered DisplayVersion mismatch.' }
if ($registration.PSObject.Properties['InstallLocation']) {
    $registeredLocation = [string]$registration.InstallLocation
    if ($registeredLocation -and -not (Test-ExactPath $registeredLocation $installRoot)) { throw "Registered InstallLocation mismatch: $registeredLocation" }
}

$legacyInfo = (Get-Item -LiteralPath $exe).VersionInfo
$legacyProductName = [string]$legacyInfo.ProductName
$legacyProductVersion = [string]$legacyInfo.ProductVersion
$legacyFileVersion = [string]$legacyInfo.FileVersion
$legacyExeSha256 = Get-Sha256 $exe
$legacyMatchesSealed = ($legacyExeSha256 -eq $ExpectedApplicationSha256)
$setupSha256 = Get-Sha256 $setup
if ($setupSha256 -ne $ExpectedSetupSha256) { throw 'Signed production installer hash mismatch.' }

Write-Host '=== Migration preflight: signed production release ==='
Invoke-ReleaseVerifier

$runtimeBefore = @(Get-LegacyProcesses)
$coreBefore = @($runtimeBefore | Where-Object { Test-CoreProcess $_ })
$guiBefore = @($runtimeBefore | Where-Object { -not (Test-CoreProcess $_) })
$treeBefore = Get-TreeFingerprint $installRoot
$hadStateRoot = Test-Path -LiteralPath $stateRoot -PathType Container
$stateBefore = if ($hadStateRoot) { Get-TreeFingerprint $stateRoot } else { $null }
$oldMainRun = Get-RunValue $mainRunName
$oldRecoveryRun = Get-RunValue $recoveryRunName

Write-Host "Legacy registered name  : $legacyDisplayName"
Write-Host "Legacy EXE SHA256       : $legacyExeSha256"
Write-Host "Legacy matches sealed   : $legacyMatchesSealed"
Write-Host "Legacy product name     : $legacyProductName"
Write-Host "Legacy file version     : $legacyFileVersion"
Write-Host "Legacy product version  : $legacyProductVersion"
Write-Host "Legacy process count    : $($runtimeBefore.Count)"
Write-Host "Legacy core count       : $($coreBefore.Count)"
Write-Host "Legacy GUI count        : $($guiBefore.Count)"
Write-Host "Legacy install tree     : $($treeBefore.Sha256) files=$($treeBefore.FileCount)"

$sessionId = [guid]::NewGuid().ToString('N')
$rescueRoot = Join-Path 'C:\Arvectum\Recovery' ("APL-REL-014-$sessionId")
$rescueInstall = Join-Path $rescueRoot 'install-root'
$rescueState = Join-Path $rescueRoot 'state-root'
$rescueRegistry = Join-Path $rescueRoot 'uninstall-registration.reg'
$rescueShortcuts = Join-Path $rescueRoot 'shortcuts'
New-Item -ItemType Directory -Path $rescueRoot -Force | Out-Null
New-Item -ItemType Directory -Path $rescueShortcuts -Force | Out-Null

Copy-Item -LiteralPath $installRoot -Destination $rescueInstall -Recurse -Force
$rescueTree = Get-TreeFingerprint $rescueInstall
if ($rescueTree.Sha256 -ne $treeBefore.Sha256 -or $rescueTree.FileCount -ne $treeBefore.FileCount) { throw 'Independent rescue install-tree copy verification failed.' }
if ($hadStateRoot) {
    Copy-Item -LiteralPath $stateRoot -Destination $rescueState -Recurse -Force
    $rescueStateFp = Get-TreeFingerprint $rescueState
    if ($rescueStateFp.Sha256 -ne $stateBefore.Sha256 -or $rescueStateFp.FileCount -ne $stateBefore.FileCount) { throw 'Independent rescue state-tree copy verification failed.' }
}
Invoke-NativeChecked -FilePath 'reg.exe' -ArgumentList @('export',$NativeUserUninstallKey,('"' + $rescueRegistry + '"'),'/y') -Label 'export rescue uninstall registration'

$shortcutPaths = @(
    (Join-Path ([Environment]::GetFolderPath('Programs')) 'Arvectum Proxy Launcher.lnk'),
    (Join-Path ([Environment]::GetFolderPath('Programs')) 'Repair Arvectum Proxy Launcher.lnk'),
    (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Arvectum Proxy Launcher.lnk')
)
$shortcutSnapshots = @()
$shortcutIndex = 0
foreach ($shortcut in $shortcutPaths) {
    if (Test-Path -LiteralPath $shortcut -PathType Leaf) {
        $backup = Join-Path $rescueShortcuts ("shortcut-$shortcutIndex.lnk")
        Copy-Item -LiteralPath $shortcut -Destination $backup -Force
        $shortcutSnapshots += [pscustomobject]@{ Original = $shortcut; Backup = $backup }
        $shortcutIndex += 1
    }
}

$rescueMeta = [ordered]@{
    created_utc = [DateTime]::UtcNow.ToString('o')
    legacy_registered_display_name = $legacyDisplayName
    legacy_exe_sha256 = $legacyExeSha256
    legacy_matches_sealed = $legacyMatchesSealed
    legacy_product_name = $legacyProductName
    legacy_file_version = $legacyFileVersion
    legacy_product_version = $legacyProductVersion
    install_tree_sha256 = $treeBefore.Sha256
    install_tree_files = $treeBefore.FileCount
    had_state_root = $hadStateRoot
    state_tree_sha256 = $(if ($stateBefore) { $stateBefore.Sha256 } else { $null })
    main_run = $oldMainRun
    recovery_run = $oldRecoveryRun
    core_count = $coreBefore.Count
    gui_count = $guiBefore.Count
}
$rescueMeta | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $rescueRoot 'rescue.json') -Encoding UTF8
Write-Host "Independent rescue armed: $rescueRoot"

$workRoot = Join-Path $env:TEMP ("ArvectumMigrationAcceptance-$sessionId")
$workInstall = Join-Path $workRoot 'install-root'
$workState = Join-Path $workRoot 'state-root'
New-Item -ItemType Directory -Path $workRoot -Force | Out-Null

$installIsolated = $false
$stateIsolated = $false
$registryRestoreArmed = $false
$runRestoreArmed = $false
$shortcutsRestoreArmed = $false
$runtimeQuiesced = $false
$baseStarted = $false
$basePassed = $false
$baseError = $null
$restoreWarnings = @()
$rescueUsed = $false

try {
    if ($runtimeBefore.Count -gt 0) { Stop-LegacyProcesses -Processes $runtimeBefore }
    $runtimeQuiesced = $true

    Move-Item -LiteralPath $installRoot -Destination $workInstall
    $installIsolated = $true
    if ($hadStateRoot) {
        Move-Item -LiteralPath $stateRoot -Destination $workState
        $stateIsolated = $true
    }

    $runRestoreArmed = $true
    Set-RunValue $mainRunName $null
    Set-RunValue $recoveryRunName $null

    $shortcutsRestoreArmed = $true
    foreach ($shortcut in $shortcutPaths) { Remove-Item -LiteralPath $shortcut -Force -ErrorAction SilentlyContinue }

    $registryRestoreArmed = $true
    Remove-Item -LiteralPath $UserUninstallKey -Recurse -Force

    $baseStarted = $true
    Invoke-BaseAcceptance
    $basePassed = $true
}
catch { $baseError = $_.Exception.Message }
finally {
    if ($installIsolated) {
        if ($baseStarted) {
            try { Remove-Item -LiteralPath $installRoot -Recurse -Force -ErrorAction SilentlyContinue } catch { $restoreWarnings += "remove test install: $($_.Exception.Message)" }
        }
        try { Move-Item -LiteralPath $workInstall -Destination $installRoot } catch { $restoreWarnings += "restore install: $($_.Exception.Message)" }
    }

    if ($baseStarted) {
        try { Remove-Item -LiteralPath $stateRoot -Recurse -Force -ErrorAction SilentlyContinue } catch { $restoreWarnings += "remove test state: $($_.Exception.Message)" }
    }
    if ($stateIsolated) {
        try {
            New-Item -ItemType Directory -Path (Split-Path -Parent $stateRoot) -Force | Out-Null
            Move-Item -LiteralPath $workState -Destination $stateRoot
        }
        catch { $restoreWarnings += "restore state: $($_.Exception.Message)" }
    }

    if ($runRestoreArmed) {
        try { Set-RunValue $mainRunName $oldMainRun } catch { $restoreWarnings += "restore main Run: $($_.Exception.Message)" }
        try { Set-RunValue $recoveryRunName $oldRecoveryRun } catch { $restoreWarnings += "restore recovery Run: $($_.Exception.Message)" }
    }

    if ($registryRestoreArmed) {
        try { Remove-Item -LiteralPath $UserUninstallKey -Recurse -Force -ErrorAction SilentlyContinue } catch { $restoreWarnings += "remove test registration: $($_.Exception.Message)" }
        try { Invoke-NativeChecked -FilePath 'reg.exe' -ArgumentList @('import',('"' + $rescueRegistry + '"')) -Label 'restore legacy uninstall registration' } catch { $restoreWarnings += "restore registration: $($_.Exception.Message)" }
    }

    if ($shortcutsRestoreArmed) {
        foreach ($shortcut in $shortcutPaths) {
            try { Remove-Item -LiteralPath $shortcut -Force -ErrorAction SilentlyContinue } catch { $restoreWarnings += "remove test shortcut: $shortcut" }
        }
        foreach ($snapshot in $shortcutSnapshots) {
            try {
                New-Item -ItemType Directory -Path (Split-Path -Parent $snapshot.Original) -Force | Out-Null
                Copy-Item -LiteralPath $snapshot.Backup -Destination $snapshot.Original -Force
            }
            catch { $restoreWarnings += "restore shortcut: $($snapshot.Original)" }
        }
    }
}

$treeRestored = $false
$stateRestored = $false
try {
    $treeAfter = Get-TreeFingerprint $installRoot
    $treeRestored = ($treeAfter -and $treeAfter.Sha256 -eq $treeBefore.Sha256 -and $treeAfter.FileCount -eq $treeBefore.FileCount)
    if ($hadStateRoot) {
        $stateAfter = Get-TreeFingerprint $stateRoot
        $stateRestored = ($stateAfter -and $stateAfter.Sha256 -eq $stateBefore.Sha256 -and $stateAfter.FileCount -eq $stateBefore.FileCount)
    }
    else { $stateRestored = -not (Test-Path -LiteralPath $stateRoot) }
}
catch { $restoreWarnings += "validate restored trees: $($_.Exception.Message)" }

if (-not $treeRestored -or -not $stateRestored -or $restoreWarnings.Count -gt 0) {
    $rescueUsed = $true
    try {
        foreach ($p in @(Get-LegacyProcesses)) { Stop-Process -Id ([int]$p.ProcessId) -Force -ErrorAction SilentlyContinue }
        Remove-Item -LiteralPath $installRoot -Recurse -Force -ErrorAction SilentlyContinue
        Copy-Item -LiteralPath $rescueInstall -Destination $installRoot -Recurse -Force
        Remove-Item -LiteralPath $stateRoot -Recurse -Force -ErrorAction SilentlyContinue
        if ($hadStateRoot) {
            New-Item -ItemType Directory -Path (Split-Path -Parent $stateRoot) -Force | Out-Null
            Copy-Item -LiteralPath $rescueState -Destination $stateRoot -Recurse -Force
        }
        Set-RunValue $mainRunName $oldMainRun
        Set-RunValue $recoveryRunName $oldRecoveryRun
        Remove-Item -LiteralPath $UserUninstallKey -Recurse -Force -ErrorAction SilentlyContinue
        Invoke-NativeChecked -FilePath 'reg.exe' -ArgumentList @('import',('"' + $rescueRegistry + '"')) -Label 'rescue restore uninstall registration'
        foreach ($shortcut in $shortcutPaths) { Remove-Item -LiteralPath $shortcut -Force -ErrorAction SilentlyContinue }
        foreach ($snapshot in $shortcutSnapshots) {
            New-Item -ItemType Directory -Path (Split-Path -Parent $snapshot.Original) -Force | Out-Null
            Copy-Item -LiteralPath $snapshot.Backup -Destination $snapshot.Original -Force
        }
        $treeAfter = Get-TreeFingerprint $installRoot
        $treeRestored = ($treeAfter.Sha256 -eq $treeBefore.Sha256 -and $treeAfter.FileCount -eq $treeBefore.FileCount)
        if ($hadStateRoot) {
            $stateAfter = Get-TreeFingerprint $stateRoot
            $stateRestored = ($stateAfter.Sha256 -eq $stateBefore.Sha256 -and $stateAfter.FileCount -eq $stateBefore.FileCount)
        }
        else { $stateRestored = -not (Test-Path -LiteralPath $stateRoot) }
        $restoreWarnings = @()
    }
    catch { $restoreWarnings = @("independent rescue restore failed: $($_.Exception.Message)") }
}

$runtimeRestored = $false
if ($treeRestored -and $stateRestored -and $restoreWarnings.Count -eq 0) {
    try {
        $runtimeNow = @(Get-LegacyProcesses)
        $coreNow = @($runtimeNow | Where-Object { Test-CoreProcess $_ })
        $guiNow = @($runtimeNow | Where-Object { -not (Test-CoreProcess $_) })
        if ($coreNow.Count -ne $coreBefore.Count -or $guiNow.Count -ne $guiBefore.Count) {
            foreach ($p in $runtimeNow) { Stop-Process -Id ([int]$p.ProcessId) -Force -ErrorAction Stop }
            Start-Sleep -Milliseconds 500
            Start-LegacyRuntime -CoreCount $coreBefore.Count -GuiCount $guiBefore.Count
        }
        $runtimeAfter = @(Get-LegacyProcesses)
        $coreAfter = @($runtimeAfter | Where-Object { Test-CoreProcess $_ })
        $guiAfter = @($runtimeAfter | Where-Object { -not (Test-CoreProcess $_) })
        $runtimeRestored = ($coreAfter.Count -eq $coreBefore.Count -and $guiAfter.Count -eq $guiBefore.Count)
    }
    catch { $restoreWarnings += "restore legacy runtime: $($_.Exception.Message)" }
}

if (Test-Path -LiteralPath $EvidencePath -PathType Leaf) {
    try {
        $evidence = Get-Content -LiteralPath $EvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $evidence | Add-Member -NotePropertyName preexisting_registered_runtime_exact -NotePropertyValue 'LEGACY_REGISTERED_0.2.3' -Force
        $evidence | Add-Member -NotePropertyName preexisting_registered_install_exact -NotePropertyValue 'LEGACY_NONSEALED_RUNTIME' -Force
        $evidence | Add-Member -NotePropertyName preexisting_registered_display_name -NotePropertyValue $legacyDisplayName -Force
        $evidence | Add-Member -NotePropertyName preexisting_exe_sha256 -NotePropertyValue $legacyExeSha256 -Force
        $evidence | Add-Member -NotePropertyName preexisting_exe_matches_sealed -NotePropertyValue $legacyMatchesSealed -Force
        $evidence | Add-Member -NotePropertyName preexisting_exe_product_name -NotePropertyValue $legacyProductName -Force
        $evidence | Add-Member -NotePropertyName preexisting_exe_file_version -NotePropertyValue $legacyFileVersion -Force
        $evidence | Add-Member -NotePropertyName preexisting_exe_product_version -NotePropertyValue $legacyProductVersion -Force
        $evidence | Add-Member -NotePropertyName preexisting_install_tree_sha256 -NotePropertyValue $treeBefore.Sha256 -Force
        $evidence | Add-Member -NotePropertyName preexisting_install_tree_files -NotePropertyValue $treeBefore.FileCount -Force
        $evidence | Add-Member -NotePropertyName owner_host_install_tree_restored_exact -NotePropertyValue $treeRestored -Force
        $evidence | Add-Member -NotePropertyName owner_host_state_tree_restored_exact -NotePropertyValue $stateRestored -Force
        $evidence | Add-Member -NotePropertyName owner_host_runtime_was_running -NotePropertyValue ($runtimeBefore.Count -gt 0) -Force
        $evidence | Add-Member -NotePropertyName owner_host_core_was_running -NotePropertyValue ($coreBefore.Count -gt 0) -Force
        $evidence | Add-Member -NotePropertyName owner_host_gui_was_running -NotePropertyValue ($guiBefore.Count -gt 0) -Force
        $evidence | Add-Member -NotePropertyName owner_host_runtime_quiesced -NotePropertyValue ($(if ($runtimeQuiesced) { 'PASS' } else { 'BLOCK' })) -Force
        $evidence | Add-Member -NotePropertyName owner_host_runtime_restored -NotePropertyValue $runtimeRestored -Force
        $evidence | Add-Member -NotePropertyName owner_host_rescue_armed -NotePropertyValue $true -Force
        $evidence | Add-Member -NotePropertyName owner_host_rescue_used -NotePropertyValue $rescueUsed -Force
        $evidence | Add-Member -NotePropertyName owner_host_rescue_restored -NotePropertyValue ($treeRestored -and $stateRestored -and $restoreWarnings.Count -eq 0) -Force
        $evidence | Add-Member -NotePropertyName owner_host_snapshot_restored -NotePropertyValue ($treeRestored -and $stateRestored -and $restoreWarnings.Count -eq 0) -Force
        if (-not $runtimeRestored -or $restoreWarnings.Count -gt 0) {
            $evidence.result = 'BLOCK'
            $evidence | Add-Member -NotePropertyName owner_host_restore_warnings -NotePropertyValue @($restoreWarnings) -Force
        }
        $evidence | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
    }
    catch { $restoreWarnings += "evidence update failed: $($_.Exception.Message)" }
}

Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue

if ($restoreWarnings.Count -gt 0) { throw "Owner-host restoration BLOCK: $($restoreWarnings -join '; ')" }
if (-not $treeRestored -or -not $stateRestored) { throw 'Owner-host byte-exact restoration BLOCK.' }
if (-not $runtimeRestored) { throw 'Owner-host runtime restoration BLOCK.' }
if (-not $basePassed) { throw "Canonical signed-set lifecycle acceptance failed after safe legacy isolation: $baseError" }

Remove-Item -LiteralPath $rescueRoot -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ''
Write-Host 'APL-REL-014 migration-style legacy-host wrapper: PASS'
Write-Host "Legacy registered name: $legacyDisplayName"
Write-Host "Legacy EXE SHA256: $legacyExeSha256"
Write-Host "Legacy matches sealed EXE: $legacyMatchesSealed"
Write-Host "Legacy ProductName: $legacyProductName"
Write-Host "Legacy ProductVersion: $legacyProductVersion"
Write-Host 'Canonical exact signed-set lifecycle acceptance: PASS'
Write-Host 'Legacy install tree restoration: BYTE-EXACT'
Write-Host 'Legacy state tree restoration: PASS'
Write-Host 'Original runtime restoration: PASS'
Write-Host "Independent rescue used: $rescueUsed"
Write-Host "Evidence: $EvidencePath"
