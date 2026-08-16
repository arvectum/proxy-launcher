<# Canonical APL-REL-006 / APL-WIN-010..012 installer build. Requires Inno Setup 6.7.1. #>
[CmdletBinding()]
param(
    [string]$PythonExecutable = 'python',
    [string]$IsccPath,
    [switch]$SyntheticPredecessor
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Windows installer build must run on Windows.' }
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root

$canonicalVersion = (Get-Content VERSION -Raw).Trim()
$semver = [regex]::Match($canonicalVersion, '^(?<major>0|[1-9]\d*)\.(?<minor>0|[1-9]\d*)\.(?<patch>0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$')
if (-not $semver.Success) { throw "Invalid canonical VERSION: $canonicalVersion" }

$version = $canonicalVersion
$synthetic = $false
if ($SyntheticPredecessor) {
    if ($canonicalVersion -match '[-+]') { throw 'Synthetic predecessor generation requires a stable numeric canonical VERSION.' }
    $major = [int]$semver.Groups['major'].Value
    $minor = [int]$semver.Groups['minor'].Value
    $patch = [int]$semver.Groups['patch'].Value
    if ($patch -gt 0) {
        $version = "$major.$minor.$($patch - 1)"
    } elseif ($minor -gt 0) {
        $version = "$major.$($minor - 1).0"
    } else {
        throw "Cannot derive a synthetic predecessor for $canonicalVersion"
    }
    $synthetic = $true
}

$versionCore = ($version -split '[-+]')[0]
$versionInfoVersion = "$versionCore.0"
$exe = Join-Path $root 'dist\Arvectum Proxy Launcher.exe'
if (-not (Test-Path -LiteralPath $exe)) {
    & (Join-Path $root 'tools\clean_build_windows.ps1') -PythonExecutable $PythonExecutable
    if ($LASTEXITCODE) { throw 'portable build failed' }
}
if (-not (Test-Path -LiteralPath $exe)) { throw 'dist\\Arvectum Proxy Launcher.exe is required' }

$payload = Join-Path $root 'out\installer-payload'
Remove-Item -LiteralPath $payload -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $payload -Force | Out-Null
Copy-Item -LiteralPath $exe -Destination (Join-Path $payload 'Arvectum Proxy Launcher.exe')
Copy-Item -LiteralPath (Join-Path $root 'installer\upgrade_helper.ps1') -Destination $payload
Copy-Item -LiteralPath (Join-Path $root 'installer\uninstall_helper.ps1') -Destination $payload
function Hash([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }

$manifest = [ordered]@{
    product='Arvectum Proxy Launcher'
    company='ООО «Арвектум»'
    version=$version
    canonical_version=$canonicalVersion
    synthetic_lifecycle_fixture=$synthetic
    platform='windows-x64'
    format='setup'
    source_commit=(git rev-parse HEAD).Trim()
    application_sha256=(Hash (Join-Path $payload 'Arvectum Proxy Launcher.exe'))
    upgrade_helper_sha256=(Hash (Join-Path $payload 'upgrade_helper.ps1'))
    uninstall_helper_sha256=(Hash (Join-Path $payload 'uninstall_helper.ps1'))
}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $payload 'build_manifest.json') -Encoding utf8

if (-not $IsccPath) {
    $IsccPath = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe") |
        Where-Object { Test-Path -LiteralPath $_ } |
        Select-Object -First 1
}
if (-not $IsccPath) { throw 'Inno Setup 6.7.1 ISCC.exe was not found.' }

$isccArgs = @(
    "/DAppVersion=$version",
    "/DVersionInfoVersion=$versionInfoVersion",
    "/DPayloadDir=$payload"
)
if ($SyntheticPredecessor) { $isccArgs += '/DSyntheticLifecycleFixture=1' }
$isccArgs += 'installer\ArvectumProxyLauncher.iss'
& $IsccPath @isccArgs
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup compilation failed' }

$suffix = if ($SyntheticPredecessor) { '-synthetic-predecessor' } else { '' }
$setup = Join-Path $root "out\installer\Arvectum-Proxy-Launcher-$version-windows-x64-setup$suffix.exe"
if (-not (Test-Path -LiteralPath $setup)) { throw "Expected setup EXE was not produced: $setup" }
$setupHash = Hash $setup

$setupInfo = (Get-Item -LiteralPath $setup).VersionInfo
if ([string]$setupInfo.CompanyName -cne 'ООО «Арвектум»') { throw "Setup CompanyName mismatch: $($setupInfo.CompanyName)" }
if ([string]$setupInfo.ProductName -cne 'Arvectum Proxy Launcher') { throw "Setup ProductName mismatch: $($setupInfo.ProductName)" }
if ([string]$setupInfo.FileDescription -cne 'Arvectum Proxy Launcher Windows Installer') { throw "Setup FileDescription mismatch: $($setupInfo.FileDescription)" }
if ([string]$setupInfo.FileVersion -cne $versionInfoVersion) { throw "Setup FileVersion mismatch: $($setupInfo.FileVersion) != $versionInfoVersion" }

if ($env:GITHUB_OUTPUT) {
    if ($SyntheticPredecessor) {
        "predecessor_setup_path=$setup" >> $env:GITHUB_OUTPUT
        "predecessor_version=$version" >> $env:GITHUB_OUTPUT
    } else {
        "setup_path=$setup" >> $env:GITHUB_OUTPUT
        "setup_name=$(Split-Path $setup -Leaf)" >> $env:GITHUB_OUTPUT
        "setup_sha256=$setupHash" >> $env:GITHUB_OUTPUT
    }
}
Write-Host "Installer build PASS: $setup SHA256=$setupHash synthetic=$synthetic"
