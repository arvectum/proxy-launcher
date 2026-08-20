<#
.SYNOPSIS
    Owner-host wrapper for APL-REL-014 when Arvectum Proxy Launcher is already installed.
.DESCRIPTION
    If no registered installation exists, this wrapper delegates directly to the canonical lifecycle acceptance script.
    If an exact registered 0.2.3 production installation exists, it snapshots the installation, app state,
    Run values, uninstall registration and shortcuts, removes them from the active host, runs the canonical
    exact signed-set lifecycle acceptance, then restores the original snapshot.

    Any non-exact, machine-wide or ambiguous registered installation fails closed before the first mutation.
#>
[CmdletBinding()]
param(
    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$EvidencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Owner-host lifecycle acceptance must run on Windows.' }

$ExpectedVersion = '0.2.3'
$ExpectedApplicationSha256 = 'f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a'
$ExpectedSetupSha256 = '5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414'
$AppKeyName = '{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}_is1'
$UserUninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$MachineUninstallKey = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$MachineWowUninstallKey = "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$NativeUserUninstallKey = "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"

$ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
if (-not $EvidencePath) { $EvidencePath = $ReleaseDirectory + '.lifecycle-acceptance.json' }
$baseScript = Join-Path $PSScriptRoot 'windows_signed_set_lifecycle_acceptance.ps1'
if (-not (Test-Path -LiteralPath $baseScript -PathType Leaf)) { throw "Canonical lifecycle script is missing: $baseScript" }

function Get-Sha256([string]$Path) {
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-ExactPath([string]$Candidate, [string]$Expected) {
    if (-not $Candidate -or -not $Expected) { return $false }
    try { return [IO.Path]::GetFullPath($Candidate).TrimEnd('\') -ieq [IO.Path]::GetFullPath($Expected).TrimEnd('\') } catch { return $false }
}

function Invoke-NativeChecked {
    param([string]$FilePath, [string[]]$ArgumentList = @(), [string]$Label)
    $p = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -PassThru -Wait
    if ($p.ExitCode -ne 0) { throw "$Label failed with exit code $($p.ExitCode)" }
}

function Get-RunValue([string]$Name) {
    $runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    $item = Get-ItemProperty -Path $runPath -ErrorAction SilentlyContinue
    if ($null -eq $item) { return $null }
    $property = $item.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    [string]$property.Value
}

function Set-RunValue([string]$Name, [AllowNull()][string]$Value) {
    $runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    New-Item -Path $runPath -Force | Out-Null
    if ($null -eq $Value) {
        Remove-ItemProperty -Path $runPath -Name $Name -ErrorAction SilentlyContinue
    } else {
        New-ItemProperty -Path $runPath -Name $Name -Value $Value -PropertyType String -Force | Out-Null
    }
}

function Assert-NoRunningLauncher {
    $running = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    if ($running.Count -gt 0) {
        $details = @($running | ForEach-Object { "PID=$($_.ProcessId) PATH=$($_.ExecutablePath)" }) -join '; '
        throw "Arvectum Proxy Launcher is currently running. Close it and rerun acceptance. $details"
    }
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

$registered = @()
foreach ($path in @($UserUninstallKey, $MachineUninstallKey, $MachineWowUninstallKey)) {
    if (Test-Path -LiteralPath $path) { $registered += $path }
}

if ($registered.Count -eq 0) {
    Write-Host 'No registered installer installation detected; running canonical lifecycle acceptance directly.'
    Invoke-BaseAcceptance
    exit 0
}

if ($registered.Count -ne 1 -or $registered[0] -cne $UserUninstallKey) {
    throw "Registered installation is ambiguous or machine-wide. Refusing mutation: $($registered -join '; ')"
}

Assert-NoRunningLauncher

$documents = [Environment]::GetFolderPath('MyDocuments')
$installRoot = Join-Path $documents 'ArvectumProxyLauncher'
$exe = Join-Path $installRoot 'Arvectum Proxy Launcher.exe'
$repair = Join-Path $installRoot 'Arvectum Proxy Launcher Repair.exe'
$uninstaller = Join-Path $installRoot 'unins000.exe'
$manifestPath = Join-Path $installRoot 'build_manifest.json'
$ownerMarker = Join-Path $installRoot '.arvectum-install-owner'
$stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$mainRunName = 'ArvectumProxyLauncher'
$recoveryRunName = 'ArvectumProxyLauncherRecovery'

foreach ($required in @($exe, $repair, $uninstaller, $manifestPath, $ownerMarker)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Registered installation is incomplete and cannot be snapshotted safely: $required"
    }
}

if ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256) {
    throw 'Registered installation EXE does not match the exact sealed 0.2.3 application.'
}
if ((Get-Sha256 $repair) -ne $ExpectedSetupSha256) {
    throw 'Registered installation cached repair installer does not match the exact production installer.'
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ([string]$manifest.version -ne $ExpectedVersion) { throw 'Registered installation manifest version is not 0.2.3.' }
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

foreach ($recoveryFile in @('proxy_internet_backup.json','proxy_env_backup.json')) {
    $candidate = Join-Path $stateRoot $recoveryFile
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        throw "Active network recovery backup exists; acceptance is blocked until normal rollback is complete: $candidate"
    }
}

$sessionId = [guid]::NewGuid().ToString('N')
$workRoot = Join-Path $env:TEMP ("ArvectumOwnerHostAcceptance-$sessionId")
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

Invoke-NativeChecked -FilePath 'reg.exe' -ArgumentList @('export', $NativeUserUninstallKey, ('"' + $registryBackup + '"'), '/y') -Label 'export existing uninstall registration'
if (-not (Test-Path -LiteralPath $registryBackup -PathType Leaf)) { throw 'Registry snapshot was not created.' }

$restoreArmed = $true
$basePassed = $false
$baseError = $null
$restoreWarnings = @()

Write-Host 'Exact registered 0.2.3 installation detected and validated.'
Write-Host 'Creating reversible owner-host snapshot before lifecycle acceptance.'

try {
    Move-Item -LiteralPath $installRoot -Destination $installBackup
    if ($hadStateRoot) { Move-Item -LiteralPath $stateRoot -Destination $stateBackup }
    Set-RunValue $mainRunName $null
    Set-RunValue $recoveryRunName $null
    foreach ($shortcut in $shortcutPaths) { Remove-Item -LiteralPath $shortcut -Force -ErrorAction SilentlyContinue }
    Remove-Item -LiteralPath $UserUninstallKey -Recurse -Force

    if (Test-Path -LiteralPath $UserUninstallKey) { throw 'Failed to isolate existing uninstall registration.' }
    if (Test-Path -LiteralPath $installRoot) { throw 'Failed to isolate existing install root.' }

    Invoke-BaseAcceptance
    $basePassed = $true
}
catch {
    $baseError = $_.Exception.Message
}
finally {
    if ($restoreArmed) {
        try {
            $testUninstaller = Join-Path $installRoot 'unins000.exe'
            if (Test-Path -LiteralPath $testUninstaller -PathType Leaf) {
                $p = Start-Process -FilePath $testUninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -PassThru -Wait -ErrorAction SilentlyContinue
                if ($p -and $p.ExitCode -ne 0) { $restoreWarnings += "test cleanup uninstaller exit=$($p.ExitCode)" }
            }
        } catch { $restoreWarnings += "test cleanup uninstall: $($_.Exception.Message)" }

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
        } catch { $restoreWarnings += "restore state root: $($_.Exception.Message)" }
        try { Set-RunValue $mainRunName $oldMainRun } catch { $restoreWarnings += "restore main Run: $($_.Exception.Message)" }
        try { Set-RunValue $recoveryRunName $oldRecoveryRun } catch { $restoreWarnings += "restore recovery Run: $($_.Exception.Message)" }
        try { Invoke-NativeChecked -FilePath 'reg.exe' -ArgumentList @('import', ('"' + $registryBackup + '"')) -Label 'restore uninstall registration' } catch { $restoreWarnings += "restore uninstall registration: $($_.Exception.Message)" }
        foreach ($snapshot in $shortcutSnapshots) {
            try {
                New-Item -ItemType Directory -Path (Split-Path -Parent $snapshot.Original) -Force | Out-Null
                Copy-Item -LiteralPath $snapshot.Backup -Destination $snapshot.Original -Force
            } catch { $restoreWarnings += "restore shortcut: $($snapshot.Original): $($_.Exception.Message)" }
        }
    }
}

if ($restoreWarnings.Count -eq 0) {
    if (-not (Test-Path -LiteralPath $UserUninstallKey)) { $restoreWarnings += 'restored uninstall registration is missing' }
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { $restoreWarnings += 'restored executable is missing' }
    elseif ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256) { $restoreWarnings += 'restored executable hash mismatch' }
    if (-not (Test-Path -LiteralPath $repair -PathType Leaf)) { $restoreWarnings += 'restored cached repair installer is missing' }
    elseif ((Get-Sha256 $repair) -ne $ExpectedSetupSha256) { $restoreWarnings += 'restored cached repair installer hash mismatch' }
}

if (Test-Path -LiteralPath $EvidencePath -PathType Leaf) {
    try {
        $evidence = Get-Content -LiteralPath $EvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $evidence | Add-Member -NotePropertyName preexisting_registered_install -NotePropertyValue $true -Force
        $evidence | Add-Member -NotePropertyName preexisting_registered_install_exact -NotePropertyValue 'PASS' -Force
        $evidence | Add-Member -NotePropertyName owner_host_snapshot_restored -NotePropertyValue ($restoreWarnings.Count -eq 0) -Force
        if ($restoreWarnings.Count -gt 0) {
            $evidence.result = 'BLOCK'
            $evidence | Add-Member -NotePropertyName owner_host_restore_warnings -NotePropertyValue @($restoreWarnings) -Force
        }
        $evidence | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
    } catch {
        $restoreWarnings += "update owner-host evidence: $($_.Exception.Message)"
    }
}

Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue

if ($restoreWarnings.Count -gt 0) {
    throw "Owner-host snapshot restoration BLOCK: $($restoreWarnings -join '; ')"
}
if (-not $basePassed) {
    throw "Canonical lifecycle acceptance failed, but the pre-existing registered installation was restored: $baseError"
}

Write-Host ''
Write-Host 'APL-REL-014 owner-host wrapper: PASS'
Write-Host 'Pre-existing exact registered installation: VALIDATED'
Write-Host 'Canonical signed-set lifecycle acceptance: PASS'
Write-Host 'Pre-existing registered installation restored: PASS'
Write-Host "Evidence: $EvidencePath"
