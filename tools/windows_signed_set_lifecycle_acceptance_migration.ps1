<#
.SYNOPSIS
    Historical APL-REL-014 owner-host migration entry point, now fail-closed.
.DESCRIPTION
    A 2026-08-20 owner-workstation incident proved that a destructive lifecycle
    drill can successfully restore files and state yet still fail to restart a
    previously working unsigned executable when Windows application-control
    policy evaluates the new process creation.

    Owner-host migration acceptance is therefore prohibited. This entry point
    remains only to turn old instructions/scripts into an explicit safety BLOCK.
    Use the canonical lifecycle acceptance script only in a disposable/isolated
    Windows acceptance environment.
#>
[CmdletBinding()]
param(
    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$EvidencePath = '',
    [switch]$IsolatedAcceptanceEnvironment
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'APL-REL-014 lifecycle acceptance must run on Windows.'
}

if (-not $IsolatedAcceptanceEnvironment) {
    throw @'
APL-REL-014 OWNER-HOST SAFETY BLOCK.
Destructive lifecycle acceptance is prohibited on a normal owner workstation after the 2026-08-20 application-control incident.
Do not disable Smart App Control or other Windows protection to make an unsigned executable restart.
Run acceptance only in a disposable/isolated Windows VM or dedicated clean acceptance host.
See docs/evidence/APL_REL_014_OWNER_HOST_INCIDENT_2026-08-20.md.
'@
}

$baseScript = Join-Path $PSScriptRoot 'windows_signed_set_lifecycle_acceptance.ps1'
if (-not (Test-Path -LiteralPath $baseScript -PathType Leaf)) {
    throw "Canonical APL-REL-014 script is missing: $baseScript"
}

$ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
if (-not $EvidencePath) {
    $EvidencePath = $ReleaseDirectory + '.lifecycle-acceptance.json'
}

Write-Host 'APL-REL-014 isolated-environment gate: PASS'
Write-Host 'Owner-host migration behavior: DISABLED'
Write-Host 'Delegating to canonical exact signed-set lifecycle acceptance.'

$arguments = @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', ('"' + $baseScript + '"'),
    '-ReleaseDirectory', ('"' + $ReleaseDirectory + '"'),
    '-EvidencePath', ('"' + $EvidencePath + '"')
)

$process = Start-Process `
    -FilePath 'powershell.exe' `
    -ArgumentList $arguments `
    -PassThru `
    -Wait

if ($process.ExitCode -ne 0) {
    throw "Canonical isolated APL-REL-014 acceptance failed with exit code $($process.ExitCode)."
}

Write-Host 'APL-REL-014 isolated-environment acceptance: PASS'
