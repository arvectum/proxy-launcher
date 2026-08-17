<#
.SYNOPSIS
    Package the verified Windows CPython bootstrap and hash-locked wheelhouse into
    one self-contained controlled archive for P0.1.
.DESCRIPTION
    This script performs no network access. It accepts the outputs produced by
    prepare_windows_cpython_base.ps1 and prepare_windows_wheelhouse.ps1, verifies
    their manifests and bytes again, copies only governed files into a staging
    tree, emits a top-level manifest, creates a ZIP archive and writes a SHA-256
    sidecar. The resulting archive is suitable for transfer into an
    Arvectum/Russian-controlled artifact perimeter.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$CpythonBaseDirectory,

    [Parameter(Mandatory = $true)]
    [string]$WheelhouseDirectory,

    [Parameter(Mandatory = $false)]
    [string]$OutputDirectory,

    [Parameter(Mandatory = $false)]
    [string]$ArchiveName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ExpectedPythonVersion = (Get-Content -LiteralPath (Join-Path $RepoRoot 'BUILD_PYTHON_VERSION') -Raw).Trim()
$HashLockPath = Join-Path $RepoRoot 'requirements-build.windows-x64.hashes.txt'
$BuildLockPath = Join-Path $RepoRoot 'requirements-build.lock.txt'
$PythonBaseLockPath = Join-Path $RepoRoot 'tools\python-windows-base.lock'
foreach ($path in @($HashLockPath, $BuildLockPath, $PythonBaseLockPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing governed input: $path" }
}

function Get-Sha256Lower([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-FileMatches([string]$Path, [string]$ExpectedHash, [Nullable[Int64]]$ExpectedBytes = $null) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing required file: $Path" }
    $actualHash = Get-Sha256Lower $Path
    if ($actualHash -ne $ExpectedHash.ToLowerInvariant()) {
        throw "SHA256 mismatch for $Path`: $actualHash != $ExpectedHash"
    }
    if ($null -ne $ExpectedBytes) {
        $actualBytes = (Get-Item -LiteralPath $Path).Length
        if ($actualBytes -ne [Int64]$ExpectedBytes) {
            throw "Size mismatch for $Path`: $actualBytes != $ExpectedBytes"
        }
    }
}

$CpythonBase = (Resolve-Path -LiteralPath $CpythonBaseDirectory).Path
$Wheelhouse = (Resolve-Path -LiteralPath $WheelhouseDirectory).Path

# Re-verify the controlled CPython acquisition output.
$CpythonManifestPath = Join-Path $CpythonBase 'cpython-base-manifest.json'
if (-not (Test-Path -LiteralPath $CpythonManifestPath -PathType Leaf)) { throw 'Missing CPython base manifest' }
$CpythonManifest = Get-Content -LiteralPath $CpythonManifestPath -Raw | ConvertFrom-Json
if ([string]$CpythonManifest.python_version -ne $ExpectedPythonVersion) { throw 'CPython manifest version does not match BUILD_PYTHON_VERSION' }
if ([string]$CpythonManifest.architecture -ne 'x64') { throw 'CPython manifest architecture is not x64' }
if ([string]$CpythonManifest.verification -ne 'sigstore-identity-pass') { throw 'CPython bootstrap is not recorded as Sigstore identity verified' }
$CpythonInstaller = Join-Path $CpythonBase ([string]$CpythonManifest.installer)
$CpythonBundle = Join-Path $CpythonBase ([string]$CpythonManifest.sigstore_bundle)
Assert-FileMatches $CpythonInstaller ([string]$CpythonManifest.installer_sha256) ([Int64]$CpythonManifest.installer_bytes)
Assert-FileMatches $CpythonBundle ([string]$CpythonManifest.sigstore_bundle_sha256)

# Re-verify the controlled wheelhouse acquisition output.
$WheelhouseManifestPath = Join-Path $Wheelhouse 'wheelhouse-manifest.json'
if (-not (Test-Path -LiteralPath $WheelhouseManifestPath -PathType Leaf)) { throw 'Missing wheelhouse manifest' }
$WheelhouseManifest = Get-Content -LiteralPath $WheelhouseManifestPath -Raw | ConvertFrom-Json
if ([string]$WheelhouseManifest.python_version -ne $ExpectedPythonVersion) { throw 'Wheelhouse manifest Python version mismatch' }
if ([string]$WheelhouseManifest.python_architecture -ne '64bit') { throw 'Wheelhouse manifest architecture is not 64bit' }
if ([string]$WheelhouseManifest.target_platform -ne 'windows-x64') { throw 'Wheelhouse target platform is not windows-x64' }
if ([Int32]$WheelhouseManifest.wheel_count -ne 8) { throw 'Wheelhouse manifest must contain exactly 8 wheels' }
$ExpectedHashLockSha = Get-Sha256Lower $HashLockPath
if ([string]$WheelhouseManifest.hash_lock_sha256 -ne $ExpectedHashLockSha) { throw 'Wheelhouse manifest hash-lock digest does not match repository governance lock' }

$ManifestWheelNames = @($WheelhouseManifest.wheels | ForEach-Object { [string]$_.name } | Sort-Object)
$ActualWheels = @(Get-ChildItem -LiteralPath $Wheelhouse -File -Filter '*.whl' | Sort-Object Name)
if ($ActualWheels.Count -ne 8) { throw "Expected exactly 8 wheel files; found $($ActualWheels.Count)" }
$ActualWheelNames = @($ActualWheels | ForEach-Object { $_.Name } | Sort-Object)
if (($ManifestWheelNames -join "`n") -ne ($ActualWheelNames -join "`n")) { throw 'Wheelhouse files do not exactly match wheelhouse manifest' }
foreach ($entry in @($WheelhouseManifest.wheels)) {
    $wheelPath = Join-Path $Wheelhouse ([string]$entry.name)
    Assert-FileMatches $wheelPath ([string]$entry.sha256) ([Int64]$entry.bytes)
}

if (-not $OutputDirectory) { $OutputDirectory = Join-Path $RepoRoot 'artifact\controlled-windows-build-inputs' }
$OutputRoot = [System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
if (-not $ArchiveName) { $ArchiveName = "arvectum-windows-build-inputs-cpython-$ExpectedPythonVersion-x64.zip" }
if (-not $ArchiveName.EndsWith('.zip', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'ArchiveName must end with .zip' }
$ArchivePath = Join-Path $OutputRoot $ArchiveName
$SidecarPath = "$ArchivePath.sha256"
$EvidencePath = "$ArchivePath.evidence.json"
foreach ($path in @($ArchivePath, $SidecarPath, $EvidencePath)) {
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
}

$Stage = Join-Path $OutputRoot ('.p0_1_stage_' + [Guid]::NewGuid().ToString('N'))
try {
    $CpythonStage = Join-Path $Stage 'cpython'
    $WheelhouseStage = Join-Path $Stage 'wheelhouse'
    $GovernanceStage = Join-Path $Stage 'governance'
    New-Item -ItemType Directory -Path $CpythonStage, $WheelhouseStage, $GovernanceStage -Force | Out-Null

    Copy-Item -LiteralPath $CpythonInstaller -Destination (Join-Path $CpythonStage (Split-Path -Leaf $CpythonInstaller))
    Copy-Item -LiteralPath $CpythonBundle -Destination (Join-Path $CpythonStage (Split-Path -Leaf $CpythonBundle))
    Copy-Item -LiteralPath $CpythonManifestPath -Destination (Join-Path $CpythonStage 'cpython-base-manifest.json')

    foreach ($wheel in $ActualWheels) { Copy-Item -LiteralPath $wheel.FullName -Destination (Join-Path $WheelhouseStage $wheel.Name) }
    Copy-Item -LiteralPath $WheelhouseManifestPath -Destination (Join-Path $WheelhouseStage 'wheelhouse-manifest.json')

    Copy-Item -LiteralPath (Join-Path $RepoRoot 'BUILD_PYTHON_VERSION') -Destination (Join-Path $GovernanceStage 'BUILD_PYTHON_VERSION')
    Copy-Item -LiteralPath $BuildLockPath -Destination (Join-Path $GovernanceStage 'requirements-build.lock.txt')
    Copy-Item -LiteralPath $HashLockPath -Destination (Join-Path $GovernanceStage 'requirements-build.windows-x64.hashes.txt')
    Copy-Item -LiteralPath $PythonBaseLockPath -Destination (Join-Path $GovernanceStage 'python-windows-base.lock')

    $FileEntries = @()
    foreach ($file in @(Get-ChildItem -LiteralPath $Stage -File -Recurse | Sort-Object FullName)) {
        $relative = [System.IO.Path]::GetRelativePath($Stage, $file.FullName).Replace('\','/')
        $FileEntries += [ordered]@{
            path = $relative
            bytes = $file.Length
            sha256 = Get-Sha256Lower $file.FullName
        }
    }

    $GitCommit = 'unknown'
    try {
        $candidate = (git -C $RepoRoot rev-parse HEAD 2>$null)
        if ($candidate) { $GitCommit = $candidate.Trim() }
    } catch {}

    $ArchiveManifest = [ordered]@{
        schema_version = 1
        task = 'P0.1'
        purpose = 'Controlled Windows CPython and wheelhouse archive'
        python_version = $ExpectedPythonVersion
        architecture = 'x64'
        target_platform = 'windows-x64'
        source_commit = $GitCommit
        cpython_verification = [string]$CpythonManifest.verification
        cpython_installer_sha256 = [string]$CpythonManifest.installer_sha256
        wheelhouse_hash_lock_sha256 = $ExpectedHashLockSha
        wheel_count = 8
        file_count = $FileEntries.Count
        files = $FileEntries
    }
    $ArchiveManifestPath = Join-Path $Stage 'controlled-archive-manifest.json'
    $ArchiveManifest | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $ArchiveManifestPath -Encoding utf8

    Compress-Archive -Path (Join-Path $Stage '*') -DestinationPath $ArchivePath -CompressionLevel Optimal -Force
} finally {
    if (Test-Path -LiteralPath $Stage) { Remove-Item -LiteralPath $Stage -Recurse -Force }
}

$ArchiveInfo = Get-Item -LiteralPath $ArchivePath
$ArchiveSha = Get-Sha256Lower $ArchivePath
"$ArchiveSha  $ArchiveName" | Set-Content -LiteralPath $SidecarPath -Encoding ascii
$Evidence = [ordered]@{
    schema_version = 1
    task = 'P0.1'
    result = 'ARCHIVE_PREPARED_NOT_YET_CONTROLLED_PERIMETER_PROVEN'
    archive = $ArchiveName
    archive_bytes = $ArchiveInfo.Length
    archive_sha256 = $ArchiveSha
    sha256_sidecar = (Split-Path -Leaf $SidecarPath)
    python_version = $ExpectedPythonVersion
    architecture = 'x64'
    wheel_count = 8
    next_required_boundary = 'Copy archive + sidecar into Arvectum/Russian-controlled storage and verify bytes there offline.'
}
$Evidence | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $EvidencePath -Encoding utf8

Write-Host "P0.1 controlled archive prepared: $ArchivePath"
Write-Host "SHA256: $ArchiveSha"
Write-Host 'Status: local archive prepared; controlled-perimeter copy/evidence still required.'
Write-Output $ArchivePath
