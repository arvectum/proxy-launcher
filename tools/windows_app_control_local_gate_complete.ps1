<#
.SYNOPSIS
    Canonical completion wrapper for the APL-WIN-014 real local gate.
.DESCRIPTION
    A final APL-WIN-014 PASS is emitted only when BOTH are proven on the same
    dedicated/isolated Windows 11 acceptance host while App Control remains enforced:
      1. real cross-version upgrade from a distinct sealed baseline build to 0.2.3;
      2. exact 0.2.3 Setup / first launch / GUI / core / PAC / rollback /
         repair / corruption recovery / uninstall acceptance.

    For the current project workflow the abandoned Windows VM path is out of scope.
    Policy deployment is intentionally outside this wrapper.
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
    [string]$TrustPackDirectory = 'C:\Arvectum\Evidence\APL-WIN-014\trust-pack',
    [string]$EvidenceDirectory = 'C:\Arvectum\Evidence\APL-WIN-014',
    [switch]$IsolatedAcceptanceEnvironment
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $IsolatedAcceptanceEnvironment) {
    throw 'SAFETY BLOCK: final APL-WIN-014 acceptance is allowed only on the dedicated/isolated Windows 11 acceptance host.'
}

$upgradeScript = Join-Path $PSScriptRoot 'windows_app_control_upgrade_acceptance.ps1'
$currentScript = Join-Path $PSScriptRoot 'windows_app_control_local_gate.ps1'
foreach ($required in @($upgradeScript, $currentScript)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Required acceptance script is missing: $required" }
}

New-Item -ItemType Directory -Path $EvidenceDirectory -Force | Out-Null
$final = [ordered]@{
    schema = 'arvectum.proxy.apl-win-014-final-local-gate.v1'
    task = 'APL-WIN-014'
    host = $env:COMPUTERNAME
    base_policy_id = $BasePolicyId.ToString('B')
    baseline_version = $BaselineVersion
    current_version = '0.2.3'
    started_utc = [DateTime]::UtcNow.ToString('o')
    result = 'BLOCK'
    upgrade_gate = 'NOT_RUN'
    current_release_gate = 'NOT_RUN'
}

try {
    & $upgradeScript `
        -BasePolicyId $BasePolicyId `
        -BaselineSupplementalPolicyId $BaselineSupplementalPolicyId `
        -BaselineSetupPath $BaselineSetupPath `
        -BaselineSetupSha256 $BaselineSetupSha256 `
        -BaselineApplicationSha256 $BaselineApplicationSha256 `
        -BaselineVersion $BaselineVersion `
        -ReleaseDirectory $ReleaseDirectory `
        -CurrentTrustPackDirectory $TrustPackDirectory `
        -EvidenceDirectory $EvidenceDirectory `
        -IsolatedAcceptanceEnvironment

    $upgradeEvidencePath = Join-Path $EvidenceDirectory 'apl-win-014-upgrade-result.json'
    if (-not (Test-Path -LiteralPath $upgradeEvidencePath -PathType Leaf)) { throw 'Upgrade sub-gate evidence is missing.' }
    $upgrade = Get-Content -LiteralPath $upgradeEvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]$upgrade.result -ne 'PASS') { throw 'Real cross-version upgrade sub-gate did not PASS.' }
    $final.upgrade_gate = 'PASS'
    $final.upgrade_evidence = $upgradeEvidencePath

    # Inno Setup should remove its owned tree. A truly empty residual directory
    # is harmless acceptance residue; remove only that empty directory before
    # the clean current-release sub-gate. Never delete a non-empty tree here.
    $installRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'ArvectumProxyLauncher'
    if (Test-Path -LiteralPath $installRoot -PathType Container) {
        $remaining = @(Get-ChildItem -LiteralPath $installRoot -Force -ErrorAction Stop)
        if ($remaining.Count -eq 0) { Remove-Item -LiteralPath $installRoot -Force }
    }

    & $currentScript `
        -Phase Enforced `
        -BasePolicyId $BasePolicyId `
        -ReleaseDirectory $ReleaseDirectory `
        -TrustPackDirectory $TrustPackDirectory `
        -EvidenceDirectory $EvidenceDirectory `
        -IsolatedAcceptanceEnvironment

    $currentEvidencePath = Join-Path $EvidenceDirectory 'apl-win-014-enforced-result.json'
    if (-not (Test-Path -LiteralPath $currentEvidencePath -PathType Leaf)) { throw 'Current-release enforced evidence is missing.' }
    $current = Get-Content -LiteralPath $currentEvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]$current.result -ne 'PASS') { throw 'Exact 0.2.3 enforced sub-gate did not PASS.' }
    $final.current_release_gate = 'PASS'
    $final.current_release_evidence = $currentEvidencePath

    $final.result = 'PASS'
}
finally {
    $final.finished_utc = [DateTime]::UtcNow.ToString('o')
    $finalPath = Join-Path $EvidenceDirectory 'apl-win-014-final-result.json'
    $final | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $finalPath -Encoding UTF8
    Write-Host "Final evidence: $finalPath"
}

if ($final.result -ne 'PASS') { throw 'APL-WIN-014 real App Control for Business local gate: BLOCK' }
Write-Host 'APL-WIN-014 real App Control for Business local gate: PASS'
Write-Host 'Cross-version upgrade: PASS'
Write-Host 'Setup / first launch / GUI / core / PAC / rollback / repair / corruption recovery / uninstall: PASS'
Write-Host 'Windows App Control remained enforced: PASS'
