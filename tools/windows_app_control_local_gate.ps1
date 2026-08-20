<#
.SYNOPSIS
    APL-WIN-014 real App Control for Business local acceptance gate.
.DESCRIPTION
    Runs only on a disposable/isolated Windows 11 acceptance VM/host.

    Prepare phase:
      - verifies the exact Russian production release;
      - installs the exact Setup as an isolated reference installation;
      - generates a ReferenceFullHash supplemental trust pack;
      - removes the reference installation;
      - DOES NOT deploy or weaken App Control policy.

    Enforced phase:
      - proves the requested base policy is actually enforced;
      - proves the generated supplemental policy is actually active/on-disk;
      - installs the exact Setup under enforcement;
      - proves GUI process creation, proxy core start, PAC serving and Windows
        system-proxy activation;
      - proves explicit rollback restores the network state;
      - runs the canonical signed-set repair/corruption/uninstall lifecycle
        acceptance while App Control remains enforced;
      - records Code Integrity evidence and fails on Arvectum 3077 block events.

    This script never calls CiTool --update-policy or --remove-policy and never
    disables Smart App Control, App Control for Business, Defender or any other
    Windows protection.
#>
[CmdletBinding()]
param(
    [ValidateSet('Prepare','Enforced')]
    [string]$Phase = 'Enforced',

    [Parameter(Mandatory = $true)]
    [Guid]$BasePolicyId,

    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$TrustPackDirectory = 'C:\Arvectum\Evidence\APL-WIN-014\trust-pack',
    [string]$EvidenceDirectory = 'C:\Arvectum\Evidence\APL-WIN-014',

    [switch]$IsolatedAcceptanceEnvironment
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ExpectedVersion = '0.2.3'
$ExpectedTag = 'v0.2.3-ru.2'
$ExpectedSetupSha256 = '5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414'
$ExpectedApplicationSha256 = 'f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a'
$ExpectedTrustSchema = 'arvectum.proxy.windows-app-control-enterprise-trust-pack.v1'
$AppKeyName = '{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}_is1'
$RunKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'

function Normalize-GuidText([object]$Value) {
    if ($null -eq $Value) { return '' }
    $text = ([string]$Value).Trim().Trim('{}')
    try { return ([Guid]$text).ToString('D').ToLowerInvariant() } catch { return $text.ToLowerInvariant() }
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'APL-WIN-014 local gate requires an elevated Administrator PowerShell session.'
    }
}

function Assert-IsolatedWindows11 {
    if ($env:OS -ne 'Windows_NT') { throw 'APL-WIN-014 local gate must run on Windows.' }
    if (-not $IsolatedAcceptanceEnvironment) {
        throw 'SAFETY BLOCK: pass -IsolatedAcceptanceEnvironment only on a disposable/isolated Windows 11 VM or dedicated acceptance host.'
    }
    $os = Get-CimInstance Win32_OperatingSystem
    $version = [Version]([string]$os.Version)
    if ($version.Major -lt 10 -or $version.Build -lt 22000) {
        throw "Windows 11 is required. Detected: $($os.Caption) $($os.Version)"
    }
    return $os
}

function Get-CiToolPath {
    $candidates = @(
        (Join-Path $env:SystemRoot 'System32\CiTool.exe'),
        (Join-Path $env:SystemRoot 'System32\citool.exe')
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    throw 'CiTool.exe is required for real App Control for Business acceptance.'
}

function Get-AppControlPolicies([string]$CiTool) {
    $raw = & $CiTool -lp -json 2>&1
    if ($LASTEXITCODE -ne 0) { throw "CiTool -lp -json failed: $($raw -join ' ')" }
    $parsed = ($raw -join [Environment]::NewLine) | ConvertFrom-Json
    $items = @()
    if ($parsed.PSObject.Properties['Policies']) { $items = @($parsed.Policies) }
    elseif ($parsed -is [System.Collections.IEnumerable]) { $items = @($parsed) }
    foreach ($policy in $items) {
        [pscustomobject]@{
            policy_id = Normalize-GuidText $policy.PolicyID
            base_policy_id = Normalize-GuidText $policy.BasePolicyID
            friendly_name = [string]$policy.FriendlyName
            is_enforced = [bool]$policy.IsEnforced
            is_on_disk = [bool]$policy.IsOnDisk
            is_signed = [bool]$policy.IsSignedPolicy
        }
    }
}

function Invoke-CheckedProcess {
    param(
        [Parameter(Mandatory = $true)] [string]$FilePath,
        [string[]]$ArgumentList = @(),
        [Parameter(Mandatory = $true)] [string]$Label
    )
    $p = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -PassThru -Wait
    if ($p.ExitCode -ne 0) { throw "$Label failed with exit code $($p.ExitCode)." }
    return $p.ExitCode
}

function Get-RegisteredInstallKeys {
    @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
    ) | Where-Object { Test-Path -LiteralPath $_ }
}

function Assert-CleanAcceptanceState {
    $documents = [Environment]::GetFolderPath('MyDocuments')
    $installRoot = Join-Path $documents 'ArvectumProxyLauncher'
    $stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
    $registered = @(Get-RegisteredInstallKeys)
    $processes = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    if ($registered.Count -gt 0 -or (Test-Path -LiteralPath $installRoot) -or (Test-Path -LiteralPath $stateRoot) -or $processes.Count -gt 0) {
        throw 'Acceptance VM is not clean. Revert to the dedicated pre-gate snapshot instead of mutating an existing/owner installation.'
    }
}

function Invoke-ReleaseAssessment([string]$Suffix) {
    $script = Join-Path $PSScriptRoot 'windows_app_control_assess.ps1'
    if (-not (Test-Path -LiteralPath $script -PathType Leaf)) { throw "Assessment script is missing: $script" }
    $path = Join-Path $EvidenceDirectory ("assessment-$Suffix.json")
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -ReleaseDirectory $ReleaseDirectory -EvidencePath $path
    if ($LASTEXITCODE -ne 0) { throw "App Control assessment failed ($Suffix)." }
    return $path
}

function Install-ExactRelease([string]$LogPath) {
    $setup = Join-Path $ReleaseDirectory 'ArvectumProxyLauncher-Setup-0.2.3.exe'
    if (-not (Test-Path -LiteralPath $setup -PathType Leaf)) { throw "Setup is missing: $setup" }
    if ((Get-Sha256 $setup) -ne $ExpectedSetupSha256) { throw 'Setup SHA256 does not match the sealed production release.' }
    Invoke-CheckedProcess -FilePath $setup -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',("/LOG=$LogPath")) -Label 'exact production Setup' | Out-Null

    $installRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'ArvectumProxyLauncher'
    $exe = Join-Path $installRoot 'Arvectum Proxy Launcher.exe'
    $repair = Join-Path $installRoot 'Arvectum Proxy Launcher Repair.exe'
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'Installed application EXE is missing.' }
    if (-not (Test-Path -LiteralPath $repair -PathType Leaf)) { throw 'Cached repair installer is missing.' }
    if ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256) { throw 'Installed application EXE is not the sealed production binary.' }
    if ((Get-Sha256 $repair) -ne $ExpectedSetupSha256) { throw 'Cached repair installer does not match the sealed Setup.' }
    return [pscustomobject]@{ root = $installRoot; exe = $exe; repair = $repair; uninstaller = (Join-Path $installRoot 'unins000.exe') }
}

function Uninstall-ExactRelease([object]$Installed, [string]$LogPath) {
    if (-not (Test-Path -LiteralPath $Installed.uninstaller -PathType Leaf)) { throw 'Uninstaller is missing.' }
    Invoke-CheckedProcess -FilePath $Installed.uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',("/LOG=$LogPath")) -Label 'exact release uninstall' | Out-Null
    if (Test-Path -LiteralPath $Installed.exe) { throw 'Uninstall left the application EXE behind.' }
}

function Stop-ExactGui([string]$ExePath) {
    $expected = [IO.Path]::GetFullPath($ExePath)
    $all = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    foreach ($item in $all) {
        $path = [string]$item.ExecutablePath
        if (-not $path -or [IO.Path]::GetFullPath($path) -ine $expected) {
            throw "Foreign or unverifiable same-named process detected: PID=$($item.ProcessId) PATH=$path"
        }
        $cmd = [string]$item.CommandLine
        if ($cmd -match '(?i)(^|\s)--start(\s|$)') { continue }
        Stop-Process -Id ([int]$item.ProcessId) -Force -ErrorAction Stop
    }
}

function Invoke-RuntimeAcceptance([object]$Installed) {
    $result = [ordered]@{}

    $gui = Start-Process -FilePath $Installed.exe -WorkingDirectory $Installed.root -PassThru
    Start-Sleep -Seconds 3
    if ($gui.HasExited) { throw "First GUI launch was blocked/failed; exit code $($gui.ExitCode)." }
    $observed = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue | Where-Object {
        [string]$_.ExecutablePath -and ([IO.Path]::GetFullPath([string]$_.ExecutablePath) -ieq [IO.Path]::GetFullPath($Installed.exe))
    })
    if ($observed.Count -lt 1) { throw 'First GUI process was not observed under App Control enforcement.' }
    $result.first_gui_launch = 'PASS'
    Stop-ExactGui -ExePath $Installed.exe

    $stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
    New-Item -ItemType Directory -Path $stateRoot -Force | Out-Null
    $settings = [ordered]@{
        config_version = 1
        local_http_port = 8080
        local_socks_port = 1080
        local_pac_port = 8082
        pac_path = '/proxy.pac'
        upstream = @([ordered]@{ host = '127.0.0.1'; port = 65534 })
    }
    $settings | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $stateRoot 'proxy_settings.json') -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $stateRoot 'no_proxy.txt') -Value "app-control-gate.invalid`r`n" -Encoding UTF8

    $core = Start-Process -FilePath $Installed.exe -ArgumentList @('--start') -WorkingDirectory $Installed.root -PassThru
    Start-Sleep -Seconds 3
    if ($core.HasExited) { throw "Proxy core was blocked/failed; exit code $($core.ExitCode)." }

    $statusOutput = (& $Installed.exe --status 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0 -or $statusOutput -notmatch 'RUNNING' -or $statusOutput -notmatch 'system proxy:\s*ENABLED') {
        throw "Runtime status did not prove active core + system proxy. Output: $statusOutput"
    }
    $result.proxy_core = 'PASS'
    $result.system_proxy = 'PASS'

    $pac = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8082/proxy.pac' -TimeoutSec 5
    if ($pac.StatusCode -ne 200 -or [string]$pac.Content -notmatch 'FindProxyForURL') { throw 'PAC endpoint validation failed.' }
    $result.pac = 'PASS'

    $internetSettings = Get-ItemProperty -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
    if (-not $internetSettings.PSObject.Properties['AutoConfigURL'] -or [string]$internetSettings.AutoConfigURL -ne 'http://127.0.0.1:8082/proxy.pac') {
        throw 'Windows AutoConfigURL does not point to the governed local PAC endpoint.'
    }
    $result.windows_pac_binding = 'PASS'

    $rollbackOutput = (& $Installed.exe --rollback 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0 -or $rollbackOutput -notmatch 'network settings restored') {
        throw "Explicit rollback failed. Output: $rollbackOutput"
    }
    Start-Sleep -Seconds 1
    $statusAfter = (& $Installed.exe --status 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0 -or $statusAfter -notmatch 'STOPPED') { throw "Core remained active after rollback. Output: $statusAfter" }
    foreach ($name in @('proxy_internet_backup.json','proxy_env_backup.json','proxy_core.pid')) {
        if (Test-Path -LiteralPath (Join-Path $stateRoot $name)) { throw "Rollback left recovery/runtime artifact: $name" }
    }
    $result.rollback = 'PASS'

    return $result
}

function Get-CodeIntegrityRecordId {
    try {
        $event = Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 1 -ErrorAction Stop
        return [long]$event.RecordId
    } catch { return [long]0 }
}

function Get-NewCodeIntegrityEvents([long]$AfterRecordId) {
    try {
        return @(Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -ErrorAction Stop | Where-Object { [long]$_.RecordId -gt $AfterRecordId } | Select-Object TimeCreated, Id, RecordId, LevelDisplayName, Message)
    } catch { return @() }
}

$os = Assert-IsolatedWindows11
Assert-Administrator
$ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
New-Item -ItemType Directory -Path $EvidenceDirectory -Force | Out-Null
$ciTool = Get-CiToolPath
$baseId = Normalize-GuidText $BasePolicyId
$policies = @(Get-AppControlPolicies -CiTool $ciTool)
$basePolicy = @($policies | Where-Object { $_.policy_id -eq $baseId })
if ($basePolicy.Count -ne 1) { throw "Requested App Control base policy is not uniquely present: $($BasePolicyId.ToString('B'))" }

$evidence = [ordered]@{
    schema = 'arvectum.proxy.apl-win-014-local-gate.v1'
    task = 'APL-WIN-014'
    phase = $Phase
    host = $env:COMPUTERNAME
    os_caption = [string]$os.Caption
    os_version = [string]$os.Version
    release_tag = $ExpectedTag
    release_version = $ExpectedVersion
    release_directory = $ReleaseDirectory
    base_policy_id = $BasePolicyId.ToString('B')
    started_utc = [DateTime]::UtcNow.ToString('o')
    result = 'BLOCK'
    phases = [ordered]@{}
}

try {
    Assert-CleanAcceptanceState
    $evidence.phases.clean_isolated_state = 'PASS'
    $evidence.assessment_before = Invoke-ReleaseAssessment -Suffix ($Phase.ToLowerInvariant() + '-before')
    $evidence.phases.exact_release_verification = 'PASS'

    if ($Phase -eq 'Prepare') {
        $installed = Install-ExactRelease -LogPath (Join-Path $EvidenceDirectory 'prepare-install.log')
        try {
            $generator = Join-Path $PSScriptRoot 'windows_app_control_enterprise_trust_pack.ps1'
            if (-not (Test-Path -LiteralPath $generator -PathType Leaf)) { throw "Trust-pack generator is missing: $generator" }
            if (Test-Path -LiteralPath $TrustPackDirectory) { Remove-Item -LiteralPath $TrustPackDirectory -Recurse -Force }
            & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $generator -ReleaseDirectory $ReleaseDirectory -BasePolicyId $BasePolicyId -Mode ReferenceFullHash -InstalledRoot $installed.root -OutputDirectory $TrustPackDirectory
            if ($LASTEXITCODE -ne 0) { throw 'ReferenceFullHash trust-pack generation failed.' }
            $manifestPath = Join-Path $TrustPackDirectory 'trust-pack.json'
            if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw 'Generated trust-pack manifest is missing.' }
            $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ([string]$manifest.schema -ne $ExpectedTrustSchema -or [string]$manifest.mode -ne 'ReferenceFullHash') { throw 'Generated trust pack is not the required ReferenceFullHash profile.' }
            if ((Normalize-GuidText $manifest.base_policy_id) -ne $baseId) { throw 'Generated trust pack targets a different base policy.' }
            $evidence.supplemental_policy_id = [string]$manifest.supplemental_policy_id
            $evidence.trust_pack_manifest = $manifestPath
            $evidence.phases.reference_full_hash_trust_pack = 'PASS'
        }
        finally {
            if (Test-Path -LiteralPath $installed.uninstaller -PathType Leaf) {
                Uninstall-ExactRelease -Installed $installed -LogPath (Join-Path $EvidenceDirectory 'prepare-uninstall.log')
            }
        }
        $stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
        Remove-Item -LiteralPath $stateRoot -Recurse -Force -ErrorAction SilentlyContinue
        $evidence.phases.reference_cleanup = 'PASS'
        $evidence.policy_deployment = 'NOT_PERFORMED'
        $evidence.result = 'PREPARED'
    }
    else {
        $manifestPath = Join-Path $TrustPackDirectory 'trust-pack.json'
        if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw "Trust-pack manifest is missing: $manifestPath" }
        $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ([string]$manifest.schema -ne $ExpectedTrustSchema) { throw 'Unexpected trust-pack schema.' }
        if ([string]$manifest.mode -ne 'ReferenceFullHash') { throw 'Enforced acceptance requires ReferenceFullHash trust.' }
        if ([string]$manifest.russian_release_verification -ne 'PASS') { throw 'Trust pack does not bind a verified Russian release.' }
        if ((Normalize-GuidText $manifest.base_policy_id) -ne $baseId) { throw 'Trust pack targets a different base policy.' }
        if (([string]$manifest.release.installer_sha256).ToLowerInvariant() -ne $ExpectedSetupSha256 -or ([string]$manifest.release.application_exe_sha256).ToLowerInvariant() -ne $ExpectedApplicationSha256) {
            throw 'Trust pack does not bind the sealed 0.2.3 release bytes.'
        }

        $supplementalId = Normalize-GuidText $manifest.supplemental_policy_id
        $policies = @(Get-AppControlPolicies -CiTool $ciTool)
        $basePolicy = @($policies | Where-Object { $_.policy_id -eq $baseId })
        if ($basePolicy.Count -ne 1 -or -not $basePolicy[0].is_enforced -or -not $basePolicy[0].is_on_disk) {
            throw 'Requested base policy is not actively enforced/on-disk. No simulated App Control acceptance is allowed.'
        }
        $supplemental = @($policies | Where-Object { $_.policy_id -eq $supplementalId })
        if ($supplemental.Count -ne 1 -or -not $supplemental[0].is_on_disk) {
            throw 'Required supplemental policy is not active/on-disk. Deploy it through the lab/customer policy-management path first.'
        }
        if ($supplemental[0].base_policy_id -and $supplemental[0].base_policy_id -ne $baseId) {
            throw 'Active supplemental policy reports a different base-policy binding.'
        }
        $evidence.supplemental_policy_id = [string]$manifest.supplemental_policy_id
        $evidence.phases.base_policy_enforced = 'PASS'
        $evidence.phases.supplemental_policy_active = 'PASS'

        $ciStart = Get-CodeIntegrityRecordId
        $installed = $null
        try {
            $installed = Install-ExactRelease -LogPath (Join-Path $EvidenceDirectory 'enforced-install.log')
            $evidence.phases.setup_under_enforcement = 'PASS'
            $runtime = Invoke-RuntimeAcceptance -Installed $installed
            foreach ($entry in $runtime.GetEnumerator()) { $evidence.phases[$entry.Key] = $entry.Value }
            Uninstall-ExactRelease -Installed $installed -LogPath (Join-Path $EvidenceDirectory 'enforced-runtime-uninstall.log')
            $installed = $null
            $evidence.phases.runtime_smoke_uninstall = 'PASS'

            $stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
            Remove-Item -LiteralPath $stateRoot -Recurse -Force -ErrorAction SilentlyContinue
            Remove-ItemProperty -LiteralPath $RunKey -Name 'ArvectumProxyLauncher' -ErrorAction SilentlyContinue
            Remove-ItemProperty -LiteralPath $RunKey -Name 'ArvectumProxyLauncherRecovery' -ErrorAction SilentlyContinue

            $lifecycle = Join-Path $PSScriptRoot 'windows_signed_set_lifecycle_acceptance.ps1'
            if (-not (Test-Path -LiteralPath $lifecycle -PathType Leaf)) { throw "Canonical lifecycle script is missing: $lifecycle" }
            $lifecycleEvidence = Join-Path $EvidenceDirectory 'signed-set-lifecycle.json'
            & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $lifecycle -ReleaseDirectory $ReleaseDirectory -EvidencePath $lifecycleEvidence
            if ($LASTEXITCODE -ne 0) { throw 'Canonical signed-set lifecycle acceptance failed under App Control enforcement.' }
            $life = Get-Content -LiteralPath $lifecycleEvidence -Raw -Encoding UTF8 | ConvertFrom-Json
            if ([string]$life.result -ne 'PASS' -or -not [bool]$life.environment_restored) { throw 'Lifecycle evidence is not PASS/restored.' }
            $evidence.lifecycle_evidence = $lifecycleEvidence
            $evidence.phases.repair_corruption_uninstall_lifecycle = 'PASS'
        }
        finally {
            if ($installed) {
                try { & $installed.exe --rollback | Out-Null } catch {}
                try { if (Test-Path -LiteralPath $installed.uninstaller -PathType Leaf) { Uninstall-ExactRelease -Installed $installed -LogPath (Join-Path $EvidenceDirectory 'emergency-uninstall.log') } } catch {}
            }
        }

        $events = @(Get-NewCodeIntegrityEvents -AfterRecordId $ciStart)
        $ciEventPath = Join-Path $EvidenceDirectory 'code-integrity-events.json'
        $events | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ciEventPath -Encoding UTF8
        $blocked = @($events | Where-Object { [int]$_.Id -eq 3077 -and [string]$_.Message -match '(?i)Arvectum' })
        $evidence.code_integrity_events = $ciEventPath
        $evidence.arvectum_3077_block_events = $blocked.Count
        if ($blocked.Count -gt 0) { throw "Code Integrity recorded $($blocked.Count) Arvectum 3077 enforcement block event(s)." }
        $evidence.phases.no_arvectum_enforcement_blocks = 'PASS'

        $evidence.assessment_after = Invoke-ReleaseAssessment -Suffix 'enforced-after'
        $policiesAfter = @(Get-AppControlPolicies -CiTool $ciTool)
        $baseAfter = @($policiesAfter | Where-Object { $_.policy_id -eq $baseId })
        $suppAfter = @($policiesAfter | Where-Object { $_.policy_id -eq $supplementalId })
        if ($baseAfter.Count -ne 1 -or -not $baseAfter[0].is_enforced -or $suppAfter.Count -ne 1 -or -not $suppAfter[0].is_on_disk) {
            throw 'App Control enforcement/trust policy state changed during acceptance.'
        }
        $evidence.phases.app_control_remained_enforced = 'PASS'
        $evidence.result = 'PASS'
    }
}
finally {
    $evidence.finished_utc = [DateTime]::UtcNow.ToString('o')
    $out = Join-Path $EvidenceDirectory ("apl-win-014-$($Phase.ToLowerInvariant())-result.json")
    $evidence | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $out -Encoding UTF8
    Write-Host "Evidence: $out"
}

if ($Phase -eq 'Prepare') {
    Write-Host 'APL-WIN-014 preparation: PREPARED'
    Write-Host "Trust pack: $TrustPackDirectory"
    Write-Host 'Policy deployment: NOT PERFORMED'
    Write-Host 'Next: deploy the generated supplemental .cip through the isolated lab/customer App Control management path, make the base policy enforced, reboot if required, then run -Phase Enforced.'
}
elseif ($evidence.result -eq 'PASS') {
    Write-Host 'APL-WIN-014 real App Control for Business acceptance: PASS'
    Write-Host 'Setup / first launch / core / PAC / rollback / repair / corruption recovery / uninstall: PASS'
    Write-Host 'App Control remained enforced: PASS'
}
else {
    throw 'APL-WIN-014 local gate: BLOCK'
}
