<#
.SYNOPSIS
    Install an already Sigstore-verified CPython bootstrap into an isolated path.
.DESCRIPTION
    This script is intended for a clean Windows recovery/build host. The traditional
    python.org full installer does not provide reliable side-by-side installation of
    the same registered Python feature version. If a conflicting registered Python
    installation is detected, fail explicitly instead of entering an ambiguous
    maintenance/modify path.
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

$Base = (Resolve-Path -LiteralPath $VerifiedBaseDirectory).Path
$ManifestPath = Join-Path $Base 'cpython-base-manifest.json'
if (-not (Test-Path -LiteralPath $ManifestPath)) { throw 'Missing CPython base manifest' }
$Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if ($Manifest.verification -ne 'sigstore-identity-pass') { throw 'CPython base was not Sigstore identity verified' }
if ($Manifest.architecture -ne 'x64') { throw 'Unexpected CPython architecture' }

$Installer = Join-Path $Base $Manifest.installer
if (-not (Test-Path -LiteralPath $Installer)) { throw "Missing verified installer: $Installer" }
$Hash = (Get-FileHash -LiteralPath $Installer -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Hash -ne [string]$Manifest.installer_sha256) { throw 'Verified CPython installer SHA256 changed after acquisition' }
if ((Get-Item -LiteralPath $Installer).Length -ne [int64]$Manifest.installer_bytes) { throw 'Verified CPython installer size changed after acquisition' }

$Target = [System.IO.Path]::GetFullPath($TargetDirectory)

# The traditional python.org installer is a registered product installer, not a
# portable extractor. A previously registered install of the same feature version
# can force the bootstrapper into maintenance/modify mode and ignore TargetDir.
# Detect that state before touching the requested isolated target.
$VersionParts = ([string]$Manifest.python_version).Split('.')
if ($VersionParts.Count -lt 2) { throw 'Invalid CPython version in acquisition manifest' }
$FeatureVersion = "$($VersionParts[0]).$($VersionParts[1])"
$RegistryPaths = @(
    "Registry::HKEY_CURRENT_USER\Software\Python\PythonCore\$FeatureVersion\InstallPath",
    "Registry::HKEY_LOCAL_MACHINE\Software\Python\PythonCore\$FeatureVersion\InstallPath"
)
$RegisteredInstalls = @()
foreach ($RegistryPath in $RegistryPaths) {
    if (-not (Test-Path -LiteralPath $RegistryPath)) { continue }
    try {
        $RawPath = (Get-Item -LiteralPath $RegistryPath).GetValue('')
        if ($RawPath) {
            $RegisteredInstalls += [ordered]@{
                registry = $RegistryPath
                path     = [System.IO.Path]::GetFullPath([string]$RawPath)
            }
        }
    } catch {
        throw "Unable to inspect existing CPython registration at ${RegistryPath}: $($_.Exception.Message)"
    }
}
foreach ($Registered in $RegisteredInstalls) {
    if (-not [string]::Equals($Registered.path.TrimEnd('\'), $Target.TrimEnd('\'), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Existing CPython $FeatureVersion registration detected at '$($Registered.path)' ($($Registered.registry)). The traditional python.org installer does not reliably support an isolated side-by-side install of the same registered version. Run this recovery-install step on a clean Windows host. P0.1 archive preparation itself does not require installing CPython on the acquisition laptop."
    }
}

if (Test-Path -LiteralPath $Target) { Remove-Item -LiteralPath $Target -Recurse -Force }
$Log = Join-Path $Base 'cpython-install.log'

$Arguments = @(
    '/quiet',
    "TargetDir=$Target",
    'InstallAllUsers=0',
    'Include_launcher=0',
    'Include_test=0',
    'Include_doc=0',
    'Shortcuts=0',
    'AssociateFiles=0',
    'PrependPath=0',
    'AppendPath=0',
    'Include_pip=1',
    'Include_tcltk=1',
    "/log", $Log
)
$Process = Start-Process -FilePath $Installer -ArgumentList $Arguments -Wait -PassThru
if ($Process.ExitCode -ne 0) {
    $UnsignedExitCode = [BitConverter]::ToUInt32([BitConverter]::GetBytes([int]$Process.ExitCode), 0)
    $ExitCodeHex = '0x{0:X8}' -f $UnsignedExitCode
    throw "CPython installer failed with exit code $($Process.ExitCode) ($ExitCodeHex). Installer log: $Log"
}

$Python = Join-Path $Target 'python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Installed CPython python.exe not found' }
$Observed = & $Python -c "import json,platform,sys; print(json.dumps({'version':'.'.join(map(str,sys.version_info[:3])),'bits':platform.architecture()[0],'machine':platform.machine()}))"
if ($LASTEXITCODE -ne 0) { throw 'Installed CPython runtime probe failed' }
$Runtime = $Observed | ConvertFrom-Json
if ($Runtime.version -ne [string]$Manifest.python_version) { throw "Installed CPython version mismatch: $($Runtime.version)" }
if ($Runtime.bits -ne '64bit') { throw "Installed CPython is not 64-bit: $($Runtime.bits)" }

Write-Host "Verified CPython installed: $Python"
Write-Output $Python
