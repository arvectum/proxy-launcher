<#
.SYNOPSIS
    Verify a P0.1 controlled Windows build-input archive without network access.
.DESCRIPTION
    Validates the archive SHA-256 sidecar, expands into a temporary directory,
    verifies every file against controlled-archive-manifest.json, re-validates
    the nested CPython and wheelhouse manifests, and optionally requires the
    governance locks in the archive to byte-match the current repository.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ArchivePath,

    [Parameter(Mandatory = $false)]
    [string]$SidecarPath,

    [Parameter(Mandatory = $false)]
    [switch]$RequireCurrentRepositoryLocks
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Archive = (Resolve-Path -LiteralPath $ArchivePath).Path
if (-not $SidecarPath) { $SidecarPath = "$Archive.sha256" }
$Sidecar = (Resolve-Path -LiteralPath $SidecarPath).Path

function Get-Sha256Lower([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-Match([string]$Path, [string]$ExpectedHash, [Nullable[Int64]]$ExpectedBytes = $null) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing required archive file: $Path" }
    $actualHash = Get-Sha256Lower $Path
    if ($actualHash -ne $ExpectedHash.ToLowerInvariant()) { throw "SHA256 mismatch for $Path" }
    if ($null -ne $ExpectedBytes -and (Get-Item -LiteralPath $Path).Length -ne [Int64]$ExpectedBytes) {
        throw "Size mismatch for $Path"
    }
}

$SidecarLine = (Get-Content -LiteralPath $Sidecar -Raw).Trim()
if ($SidecarLine -notmatch '^([0-9a-fA-F]{64})\s+(.+)$') { throw 'Invalid SHA256 sidecar format' }
$ExpectedArchiveSha = $Matches[1].ToLowerInvariant()
$SidecarArchiveName = $Matches[2].Trim().TrimStart('*')
if ($SidecarArchiveName -ne (Split-Path -Leaf $Archive)) { throw 'SHA256 sidecar archive name does not match archive filename' }
$ActualArchiveSha = Get-Sha256Lower $Archive
if ($ActualArchiveSha -ne $ExpectedArchiveSha) { throw 'Controlled archive SHA256 does not match sidecar' }

$Temp = Join-Path ([System.IO.Path]::GetTempPath()) ('apl-p0-1-verify-' + [Guid]::NewGuid().ToString('N'))
try {
    New-Item -ItemType Directory -Path $Temp -Force | Out-Null
    Expand-Archive -LiteralPath $Archive -DestinationPath $Temp -Force

    $OuterManifestPath = Join-Path $Temp 'controlled-archive-manifest.json'
    if (-not (Test-Path -LiteralPath $OuterManifestPath -PathType Leaf)) { throw 'Missing controlled-archive-manifest.json' }
    $Outer = Get-Content -LiteralPath $OuterManifestPath -Raw | ConvertFrom-Json
    if ([Int32]$Outer.schema_version -ne 1) { throw 'Unsupported controlled archive schema' }
    if ([string]$Outer.task -ne 'P0.1') { throw 'Archive is not a P0.1 evidence archive' }
    if ([string]$Outer.architecture -ne 'x64' -or [string]$Outer.target_platform -ne 'windows-x64') { throw 'Unexpected archive target' }
    if ([Int32]$Outer.wheel_count -ne 8) { throw 'Archive must contain exactly 8 governed wheels' }
    if ([string]$Outer.cpython_verification -ne 'sigstore-identity-pass') { throw 'Archive does not preserve a verified CPython bootstrap identity' }

    $ExpectedPaths = @($Outer.files | ForEach-Object { ([string]$_.path).Replace('/','\') } | Sort-Object)
    if ([Int32]$Outer.file_count -ne $ExpectedPaths.Count) { throw 'Outer manifest file_count mismatch' }
    foreach ($entry in @($Outer.files)) {
        $relative = ([string]$entry.path).Replace('/','\')
        if ([System.IO.Path]::IsPathRooted($relative) -or $relative.Contains('..')) { throw "Unsafe archive manifest path: $relative" }
        $fullPath = Join-Path $Temp $relative
        Assert-Match $fullPath ([string]$entry.sha256) ([Int64]$entry.bytes)
    }

    $ActualPayloadPaths = @(
        Get-ChildItem -LiteralPath $Temp -File -Recurse |
            Where-Object { $_.FullName -ne $OuterManifestPath } |
            ForEach-Object { [System.IO.Path]::GetRelativePath($Temp, $_.FullName) } |
            Sort-Object
    )
    if (($ExpectedPaths -join "`n") -ne ($ActualPayloadPaths -join "`n")) { throw 'Archive contains missing or unexpected payload files' }

    $CpythonManifestPath = Join-Path $Temp 'cpython\cpython-base-manifest.json'
    $Cpython = Get-Content -LiteralPath $CpythonManifestPath -Raw | ConvertFrom-Json
    if ([string]$Cpython.python_version -ne [string]$Outer.python_version) { throw 'Nested CPython manifest version mismatch' }
    if ([string]$Cpython.architecture -ne 'x64' -or [string]$Cpython.verification -ne 'sigstore-identity-pass') { throw 'Nested CPython manifest verification mismatch' }
    $InstallerPath = Join-Path (Join-Path $Temp 'cpython') ([string]$Cpython.installer)
    $BundlePath = Join-Path (Join-Path $Temp 'cpython') ([string]$Cpython.sigstore_bundle)
    Assert-Match $InstallerPath ([string]$Cpython.installer_sha256) ([Int64]$Cpython.installer_bytes)
    Assert-Match $BundlePath ([string]$Cpython.sigstore_bundle_sha256)
    if ([string]$Outer.cpython_installer_sha256 -ne [string]$Cpython.installer_sha256) { throw 'Outer/nested CPython digest mismatch' }

    $WheelhouseManifestPath = Join-Path $Temp 'wheelhouse\wheelhouse-manifest.json'
    $Wheelhouse = Get-Content -LiteralPath $WheelhouseManifestPath -Raw | ConvertFrom-Json
    if ([string]$Wheelhouse.python_version -ne [string]$Outer.python_version) { throw 'Nested wheelhouse Python version mismatch' }
    if ([string]$Wheelhouse.python_architecture -ne '64bit' -or [string]$Wheelhouse.target_platform -ne 'windows-x64') { throw 'Nested wheelhouse target mismatch' }
    if ([Int32]$Wheelhouse.wheel_count -ne 8) { throw 'Nested wheelhouse must contain exactly 8 wheels' }
    if ([string]$Wheelhouse.hash_lock_sha256 -ne [string]$Outer.wheelhouse_hash_lock_sha256) { throw 'Outer/nested wheelhouse hash-lock digest mismatch' }
    $WheelFiles = @(Get-ChildItem -LiteralPath (Join-Path $Temp 'wheelhouse') -File -Filter '*.whl' | Sort-Object Name)
    if ($WheelFiles.Count -ne 8) { throw "Expected 8 wheel files in archive; found $($WheelFiles.Count)" }
    $ManifestWheelNames = @($Wheelhouse.wheels | ForEach-Object { [string]$_.name } | Sort-Object)
    $ActualWheelNames = @($WheelFiles | ForEach-Object { $_.Name } | Sort-Object)
    if (($ManifestWheelNames -join "`n") -ne ($ActualWheelNames -join "`n")) { throw 'Archived wheels do not exactly match nested wheelhouse manifest' }
    foreach ($entry in @($Wheelhouse.wheels)) {
        Assert-Match (Join-Path (Join-Path $Temp 'wheelhouse') ([string]$entry.name)) ([string]$entry.sha256) ([Int64]$entry.bytes)
    }

    $ArchivedPythonVersion = (Get-Content -LiteralPath (Join-Path $Temp 'governance\BUILD_PYTHON_VERSION') -Raw).Trim()
    if ($ArchivedPythonVersion -ne [string]$Outer.python_version) { throw 'Archived BUILD_PYTHON_VERSION does not match archive manifest' }
    $ArchivedHashLock = Join-Path $Temp 'governance\requirements-build.windows-x64.hashes.txt'
    if ((Get-Sha256Lower $ArchivedHashLock) -ne [string]$Outer.wheelhouse_hash_lock_sha256) { throw 'Archived hash lock digest mismatch' }

    if ($RequireCurrentRepositoryLocks) {
        $Pairs = @(
            @((Join-Path $Temp 'governance\BUILD_PYTHON_VERSION'), (Join-Path $RepoRoot 'BUILD_PYTHON_VERSION')),
            @((Join-Path $Temp 'governance\requirements-build.lock.txt'), (Join-Path $RepoRoot 'requirements-build.lock.txt')),
            @((Join-Path $Temp 'governance\requirements-build.windows-x64.hashes.txt'), (Join-Path $RepoRoot 'requirements-build.windows-x64.hashes.txt')),
            @((Join-Path $Temp 'governance\python-windows-base.lock'), (Join-Path $RepoRoot 'tools\python-windows-base.lock'))
        )
        foreach ($pair in $Pairs) {
            if ((Get-Sha256Lower $pair[0]) -ne (Get-Sha256Lower $pair[1])) { throw "Archived governance lock differs from current repository: $($pair[1])" }
        }
    }

    Write-Host 'P0.1 CONTROLLED ARCHIVE VERIFICATION: PASS'
    Write-Host "Archive: $Archive"
    Write-Host "SHA256: $ActualArchiveSha"
    Write-Host "CPython: $($Outer.python_version) x64 / Sigstore identity PASS recorded"
    Write-Host 'Wheelhouse: 8/8 exact governed wheels PASS'
    if ($RequireCurrentRepositoryLocks) { Write-Host 'Current repository governance locks: BYTE-MATCH PASS' }
} finally {
    if (Test-Path -LiteralPath $Temp) { Remove-Item -LiteralPath $Temp -Recurse -Force }
}
