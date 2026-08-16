<#
.SYNOPSIS
    Adds the APL-REL-012 consumer verification UX to a final release directory.
.DESCRIPTION
    Run this BEFORE tools/russian_signed_release.ps1. The copied verification
    files then become ordinary release assets and are covered by SHA256SUMS.txt
    and the qualified detached signature.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ReleaseDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $ReleaseDirectory -PathType Container)) {
    throw "Release directory does not exist: $ReleaseDirectory"
}

$releasePath = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
$verifierSource = Join-Path $PSScriptRoot 'verify_russian_release.ps1'
$launcherSource = Join-Path $PSScriptRoot 'VERIFY_RUSSIAN_RELEASE.cmd'

foreach ($source in @($verifierSource, $launcherSource)) {
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Required REL-012 source file is missing: $source"
    }
}

Copy-Item -LiteralPath $verifierSource -Destination (Join-Path $releasePath 'verify_russian_release.ps1') -Force
Copy-Item -LiteralPath $launcherSource -Destination (Join-Path $releasePath 'VERIFY_RUSSIAN_RELEASE.cmd') -Force

Write-Host 'APL-REL-012 verification UX added to release directory.'
Write-Host 'Next: run tools/russian_signed_release.ps1 so both verifier files are included in SHA256SUMS.txt.'
