<#
.SYNOPSIS
    Real cross-version upgrade sub-gate for APL-WIN-014.
.DESCRIPTION
    Installs a separately sealed previous Windows build under active App Control,
    upgrades it in-place to the exact 0.2.3 Russian production release, verifies
    state preservation and exact post-upgrade bytes, then uninstalls cleanly.

    This is acceptance tooling for a disposable/isolated Windows 11 VM/host.
    It never deploys/removes App Control policies and never weakens Windows protection.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [Guid]$BasePolicyId,
    [Parameter(Mandatory = $true)] [Guid]$BaselineSupplementalPolicyId,
    [Parameter(Mandatory = $true)] [string]$BaselineSetupPath,
    [Parameter(Mandatory = $true)] [string]$BaselineSetupSha256,
    [Parameter(Mandatory = $true)] [string]$BaselineApplicationSha256,
    [Parameter(Mandatory = $true)] [string]$BaselineVersion,
    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$CurrentTrustPackDirectory = 'C:\Arvectum\Evidence\APL-WIN-014\trust-pack',
    [string]$EvidenceDirectory = 'C:\Arvectum\Evidence\APL-WIN-014',
    [switch]$IsolatedAcceptanceEnvironment
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ExpectedVersion = '0.2.3'
$ExpectedSetupSha256 = '5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414'
$ExpectedApplicationSha256 = 'f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a'
$AppKeyName = '{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}_is1'
$UserUninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"

function Normalize-GuidText([object]$Value) {
    if ($null -eq $Value) { return '' }
    $text = ([string]$Value).Trim().Trim('{}')
    try { return ([Guid]$text).ToString('D').ToLowerInvariant() } catch { return $text.ToLowerInvariant() }
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-AdminAndIsolation {
    if ($env:OS -ne 'Windows_NT') { throw 'Upgrade acceptance must run on Windows.' }
    if (-not $IsolatedAcceptanceEnvironment) { throw 'SAFETY BLOCK: isolated/disposable Windows 11 acceptance environment is required.' }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Elevated Administrator PowerShell is required.' }
    $os = Get-CimInstance Win32_OperatingSystem
    $version = [Version]([string]$os.Version)
    if ($version.Build -lt 22000) { throw "Windows 11 is required. Detected: $($os.Caption) $($os.Version)" }
    return $os
}

function Get-CiToolPath {
    $path = Join-Path $env:SystemRoot 'System32\CiTool.exe'
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw 'CiTool.exe is required.' }
    return $path
}

function Get-Policies([string]$CiTool) {
    $raw = & $CiTool -lp -json 2>&1
    if ($LASTEXITCODE -ne 0) { throw "CiTool -lp -json failed: $($raw -join ' ')" }
    $parsed = ($raw -join [Environment]::NewLine) | ConvertFrom-Json
    $items = if ($parsed.PSObject.Properties['Policies']) { @($parsed.Policies) } else { @($parsed) }
    foreach ($p in $items) {
        [pscustomobject]@{
            policy_id = Normalize-GuidText $p.PolicyID
            base_policy_id = Normalize-GuidText $p.BasePolicyID
            is_enforced = [bool]$p.IsEnforced
            is_on_disk = [bool]$p.IsOnDisk
            friendly_name = [string]$p.FriendlyName
        }
    }
}

function Assert-CleanState {
    $installRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'ArvectumProxyLauncher'
    $stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
    $processes = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    if ((Test-Path -LiteralPath $installRoot) -or (Test-Path -LiteralPath $stateRoot) -or (Test-Path -LiteralPath $UserUninstallKey) -or $processes.Count -gt 0) {
        throw 'Upgrade acceptance requires a clean isolated snapshot.'
    }
}

function Invoke-Setup([string]$Path, [string]$LogPath, [string]$Label) {
    $p = Start-Process -FilePath $Path -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',("/LOG=$LogPath")) -PassThru -Wait
    if ($p.ExitCode -ne 0) { throw "$Label failed with exit code $($p.ExitCode)." }
}

function Get-InstallInfo {
    $root = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'ArvectumProxyLauncher'
    return [pscustomobject]@{
        root = $root
        exe = Join-Path $root 'Arvectum Proxy Launcher.exe'
        repair = Join-Path $root 'Arvectum Proxy Launcher Repair.exe'
        uninstaller = Join-Path $root 'unins000.exe'
    }
}

function Assert-RegisteredVersion([string]$Expected) {
    if (-not (Test-Path -LiteralPath $UserUninstallKey)) { throw 'Expected per-user uninstall registration is missing.' }
    $reg = Get-ItemProperty -LiteralPath $UserUninstallKey
    if ([string]$reg.DisplayName -ne 'Arvectum Proxy Launcher') { throw 'Unexpected registered DisplayName.' }
    if ([string]$reg.DisplayVersion -ne $Expected) { throw "Registered version mismatch. Expected=$Expected actual=$($reg.DisplayVersion)" }
}

function Get-CodeIntegrityRecordId {
    try { return [long](Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 1 -ErrorAction Stop).RecordId } catch { return [long]0 }
}

function Get-NewCodeIntegrityEvents([long]$After) {
    try { return @(Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -ErrorAction Stop | Where-Object { [long]$_.RecordId -gt $After } | Select-Object TimeCreated, Id, RecordId, LevelDisplayName, Message) } catch { return @() }
}

$os = Assert-AdminAndIsolation
$BaselineSetupPath = (Resolve-Path -LiteralPath $BaselineSetupPath).Path
$ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
New-Item -ItemType Directory -Path $EvidenceDirectory -Force | Out-Null
Assert-CleanState

$baselineSetupHash = (Get-Sha256 $BaselineSetupPath)
if ($baselineSetupHash -ne $BaselineSetupSha256.ToLowerInvariant()) { throw 'Baseline Setup SHA256 mismatch.' }
if ($BaselineApplicationSha256.Length -ne 64 -or $BaselineApplicationSha256 -notmatch '^[0-9a-fA-F]{64}$') { throw 'BaselineApplicationSha256 must be a full SHA256.' }
if ($BaselineVersion -eq $ExpectedVersion) { throw 'Upgrade baseline must be a distinct previous version; same-version repair is not accepted as upgrade evidence.' }

$currentSetup = Join-Path $ReleaseDirectory 'ArvectumProxyLauncher-Setup-0.2.3.exe'
if ((Get-Sha256 $currentSetup) -ne $ExpectedSetupSha256) { throw 'Current Setup is not the sealed production installer.' }

$currentManifestPath = Join-Path $CurrentTrustPackDirectory 'trust-pack.json'
if (-not (Test-Path -LiteralPath $currentManifestPath -PathType Leaf)) { throw 'Current ReferenceFullHash trust-pack manifest is missing.' }
$currentManifest = Get-Content -LiteralPath $currentManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ([string]$currentManifest.mode -ne 'ReferenceFullHash') { throw 'Current release must use ReferenceFullHash trust.' }
if ((Normalize-GuidText $currentManifest.base_policy_id) -ne (Normalize-GuidText $BasePolicyId)) { throw 'Current trust pack targets another base policy.' }
$currentSupplementalId = Normalize-GuidText $currentManifest.supplemental_policy_id

$ciTool = Get-CiToolPath
$policies = @(Get-Policies -CiTool $ciTool)
$baseId = Normalize-GuidText $BasePolicyId
$baselinePolicyId = Normalize-GuidText $BaselineSupplementalPolicyId
$base = @($policies | Where-Object { $_.policy_id -eq $baseId })
$baselinePolicy = @($policies | Where-Object { $_.policy_id -eq $baselinePolicyId })
$currentPolicy = @($policies | Where-Object { $_.policy_id -eq $currentSupplementalId })
if ($base.Count -ne 1 -or -not $base[0].is_enforced -or -not $base[0].is_on_disk) { throw 'Base App Control policy is not enforced/on-disk.' }
if ($baselinePolicy.Count -ne 1 -or -not $baselinePolicy[0].is_on_disk) { throw 'Baseline supplemental policy is not active/on-disk.' }
if ($currentPolicy.Count -ne 1 -or -not $currentPolicy[0].is_on_disk) { throw 'Current supplemental policy is not active/on-disk.' }

$evidence = [ordered]@{
    schema = 'arvectum.proxy.apl-win-014-upgrade-gate.v1'
    task = 'APL-WIN-014'
    host = $env:COMPUTERNAME
    os = "$($os.Caption) $($os.Version)"
    base_policy_id = $BasePolicyId.ToString('B')
    baseline_supplemental_policy_id = $BaselineSupplementalPolicyId.ToString('B')
    current_supplemental_policy_id = [string]$currentManifest.supplemental_policy_id
    baseline_version = $BaselineVersion
    current_version = $ExpectedVersion
    baseline_setup_sha256 = $baselineSetupHash
    baseline_application_sha256 = $BaselineApplicationSha256.ToLowerInvariant()
    current_setup_sha256 = $ExpectedSetupSha256
    current_application_sha256 = $ExpectedApplicationSha256
    started_utc = [DateTime]::UtcNow.ToString('o')
    result = 'BLOCK'
    phases = [ordered]@{}
}

$installed = Get-InstallInfo
$stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$ciStart = Get-CodeIntegrityRecordId
try {
    Invoke-Setup -Path $BaselineSetupPath -LogPath (Join-Path $EvidenceDirectory 'upgrade-baseline-install.log') -Label 'baseline Setup'
    Assert-RegisteredVersion -Expected $BaselineVersion
    if (-not (Test-Path -LiteralPath $installed.exe -PathType Leaf)) { throw 'Baseline application EXE is missing.' }
    if ((Get-Sha256 $installed.exe) -ne $BaselineApplicationSha256.ToLowerInvariant()) { throw 'Installed baseline application SHA256 mismatch.' }
    $evidence.phases.baseline_install_under_enforcement = 'PASS'

    New-Item -ItemType Directory -Path $stateRoot -Force | Out-Null
    $marker = Join-Path $stateRoot 'apl-win-014-upgrade-marker.txt'
    Set-Content -LiteralPath $marker -Value 'preserve-across-upgrade' -Encoding ASCII

    Invoke-Setup -Path $currentSetup -LogPath (Join-Path $EvidenceDirectory 'upgrade-to-0.2.3.log') -Label '0.2.3 upgrade Setup'
    Assert-RegisteredVersion -Expected $ExpectedVersion
    if ((Get-Sha256 $installed.exe) -ne $ExpectedApplicationSha256) { throw 'Post-upgrade application is not the exact sealed 0.2.3 EXE.' }
    if ((Get-Sha256 $installed.repair) -ne $ExpectedSetupSha256) { throw 'Post-upgrade cached repair installer is not the exact sealed 0.2.3 Setup.' }
    if (-not (Test-Path -LiteralPath $marker -PathType Leaf) -or (Get-Content -LiteralPath $marker -Raw).Trim() -ne 'preserve-across-upgrade') { throw 'Per-user state marker was not preserved across upgrade.' }
    $status = (& $installed.exe --status 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0 -or $status -notmatch 'STOPPED') { throw "Post-upgrade status smoke failed: $status" }
    $evidence.phases.real_cross_version_upgrade = 'PASS'
    $evidence.phases.state_preserved = 'PASS'
    $evidence.phases.post_upgrade_exact_bytes = 'PASS'

    if (-not (Test-Path -LiteralPath $installed.uninstaller -PathType Leaf)) { throw 'Post-upgrade uninstaller is missing.' }
    $un = Start-Process -FilePath $installed.uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',("/LOG=" + (Join-Path $EvidenceDirectory 'upgrade-uninstall.log'))) -PassThru -Wait
    if ($un.ExitCode -ne 0) { throw "Post-upgrade uninstall failed with exit code $($un.ExitCode)." }
    if (Test-Path -LiteralPath $installed.exe) { throw 'Post-upgrade uninstall left the application EXE behind.' }
    $evidence.phases.post_upgrade_uninstall = 'PASS'

    $events = @(Get-NewCodeIntegrityEvents -After $ciStart)
    $eventsPath = Join-Path $EvidenceDirectory 'upgrade-code-integrity-events.json'
    $events | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $eventsPath -Encoding UTF8
    $blocks = @($events | Where-Object { [int]$_.Id -eq 3077 -and [string]$_.Message -match '(?i)Arvectum' })
    $evidence.code_integrity_events = $eventsPath
    $evidence.arvectum_3077_block_events = $blocks.Count
    if ($blocks.Count -gt 0) { throw "Code Integrity recorded $($blocks.Count) Arvectum 3077 block event(s) during upgrade." }
    $evidence.phases.no_upgrade_enforcement_blocks = 'PASS'

    $policiesAfter = @(Get-Policies -CiTool $ciTool)
    $baseAfter = @($policiesAfter | Where-Object { $_.policy_id -eq $baseId })
    if ($baseAfter.Count -ne 1 -or -not $baseAfter[0].is_enforced) { throw 'Base App Control enforcement changed during upgrade acceptance.' }
    $evidence.phases.app_control_remained_enforced = 'PASS'
    $evidence.result = 'PASS'
}
finally {
    try { if (Test-Path -LiteralPath $installed.exe) { & $installed.exe --rollback | Out-Null } } catch {}
    try {
        if (Test-Path -LiteralPath $installed.uninstaller -PathType Leaf) {
            Start-Process -FilePath $installed.uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -Wait | Out-Null
        }
    } catch {}
    Remove-Item -LiteralPath $stateRoot -Recurse -Force -ErrorAction SilentlyContinue
    $evidence.finished_utc = [DateTime]::UtcNow.ToString('o')
    $path = Join-Path $EvidenceDirectory 'apl-win-014-upgrade-result.json'
    $evidence | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $path -Encoding UTF8
    Write-Host "Evidence: $path"
}

if ($evidence.result -ne 'PASS') { throw 'APL-WIN-014 real cross-version upgrade sub-gate: BLOCK' }
Write-Host 'APL-WIN-014 real cross-version upgrade under App Control: PASS'
