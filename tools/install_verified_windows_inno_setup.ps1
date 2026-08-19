<#
.SYNOPSIS
    Install an already verified Inno Setup 6.7.1 input on a disposable Windows recovery host.
.DESCRIPTION
    Re-validates the acquisition manifest, exact installer bytes and ancillary
    evidence without network access, then installs into an explicit isolated path.
    The installed ISCC.exe must report the exact three-part version 6.7.1.

    This script intentionally does not perform Authenticode trust/revocation
    discovery in the endpoint-denied VM. Trust is established during connected
    acquisition and then carried into recovery by the immutable locked SHA-256.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$VerifiedBaseDirectory,

    [Parameter(Mandatory = $true)]
    [string]$TargetDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Inno Setup recovery installation must run on Windows.' }

$Base = (Resolve-Path -LiteralPath $VerifiedBaseDirectory).Path
$ManifestPath = Join-Path $Base 'inno-setup-base-manifest.json'
if (-not (Test-Path -LiteralPath $ManifestPath)) { throw 'Missing Inno Setup base manifest.' }
$Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json

if ([string]$Manifest.inno_setup_version -ne '6.7.1') { throw 'Unexpected Inno Setup version in manifest.' }
if ([string]$Manifest.release_tag -ne 'is-6_7_1') { throw 'Unexpected Inno Setup release tag in manifest.' }
if ([string]$Manifest.verification -ne 'locked-sha256+authenticode-pass') {
    throw 'Inno Setup acquisition manifest does not record the required verification result.'
}
if ([string]$Manifest.recovery_install_mode -ne 'offline-from-controlled-copy') {
    throw 'Inno Setup base is not marked for controlled offline recovery installation.'
}

$Installer = Join-Path $Base ([string]$Manifest.installer)
if (-not (Test-Path -LiteralPath $Installer)) { throw "Missing verified Inno Setup installer: $Installer" }
$InstallerInfo = Get-Item -LiteralPath $Installer
$InstallerHash = (Get-FileHash -LiteralPath $Installer -Algorithm SHA256).Hash.ToLowerInvariant()
if ($InstallerHash -ne [string]$Manifest.installer_sha256) { throw 'Verified Inno Setup installer SHA-256 changed after acquisition.' }
if ($InstallerInfo.Length -ne [int64]$Manifest.installer_bytes) { throw 'Verified Inno Setup installer size changed after acquisition.' }

$EvidenceFiles = @(
    [pscustomobject]@{ Name = [string]$Manifest.issig; Sha256 = [string]$Manifest.issig_sha256 },
    [pscustomobject]@{ Name = [string]$Manifest.public_key; Sha256 = [string]$Manifest.public_key_sha256 },
    [pscustomobject]@{ Name = [string]$Manifest.license; Sha256 = [string]$Manifest.license_sha256 }
)
foreach ($item in $EvidenceFiles) {
    $Path = Join-Path $Base $item.Name
    if (-not (Test-Path -LiteralPath $Path)) { throw "Missing controlled Inno Setup evidence file: $Path" }
    $Observed = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Observed -ne $item.Sha256) { throw "Controlled Inno Setup evidence hash mismatch: $($item.Name)" }
}

$Target = [System.IO.Path]::GetFullPath($TargetDirectory)
if (Test-Path -LiteralPath $Target) { Remove-Item -LiteralPath $Target -Recurse -Force }
$Log = Join-Path $Base 'inno-setup-install.log'

$Arguments = @(
    '/PORTABLE=1',
    '/VERYSILENT',
    '/SUPPRESSMSGBOXES',
    '/NORESTART',
    '/SP-',
    '/CURRENTUSER',
    '/NOICONS',
    "/DIR=`"$Target`"",
    "/LOG=`"$Log`""
)
$Process = Start-Process -FilePath $Installer -ArgumentList $Arguments -Wait -PassThru
if ($Process.ExitCode -ne 0) {
    throw "Inno Setup installer failed with exit code $($Process.ExitCode). Installer log: $Log"
}

$Iscc = Join-Path $Target 'ISCC.exe'
if (-not (Test-Path -LiteralPath $Iscc)) { throw "Installed ISCC.exe not found: $Iscc" }

function Get-ThreePartVersion([string]$Value) {
    $match = [regex]::Match(([string]$Value).Trim(), '^(?<major>\d+)\.(?<minor>\d+)\.(?<patch>\d+)')
    if (-not $match.Success) { return $null }
    return "$($match.Groups['major'].Value).$($match.Groups['minor'].Value).$($match.Groups['patch'].Value)"
}

$VersionInfo = (Get-Item -LiteralPath $Iscc).VersionInfo
$ObservedVersion = Get-ThreePartVersion ([string]$VersionInfo.FileVersion)
if (-not $ObservedVersion) { $ObservedVersion = Get-ThreePartVersion ([string]$VersionInfo.ProductVersion) }
if ($ObservedVersion -ne '6.7.1') {
    throw "Installed ISCC.exe version mismatch: '$ObservedVersion' != '6.7.1'"
}

$Evidence = [ordered]@{
    schema_version       = 1
    inno_setup_version   = $ObservedVersion
    iscc_path            = $Iscc
    iscc_sha256          = (Get-FileHash -LiteralPath $Iscc -Algorithm SHA256).Hash.ToLowerInvariant()
    source_installer     = $InstallerInfo.Name
    source_sha256        = $InstallerHash
    install_mode         = 'offline-portable-from-controlled-copy'
    upstream_access_used = $false
}
$EvidencePath = Join-Path $Base 'inno-setup-install-evidence.json'
$Evidence | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $EvidencePath -Encoding utf8

Write-Host "Verified Inno Setup $ObservedVersion installed in portable recovery mode: $Iscc"
Write-Output $Iscc
