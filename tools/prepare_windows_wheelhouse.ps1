<#
.SYNOPSIS
    Acquire and verify the exact APL-IP-002-WIN Windows x64 build wheelhouse.
.DESCRIPTION
    This is the only network-acquisition step for the Python build toolchain.
    pip downloads only binary wheels named by requirements-build.windows-x64.hashes.txt
    and verifies every file against the committed SHA256 hashes. The resulting directory
    can then be copied to Arvectum-controlled storage and consumed by clean_build_windows.ps1
    with -WheelhousePath, where package-index access is disabled.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$PythonExecutable = "python.exe",

    [Parameter(Mandatory = $false)]
    [string]$OutputDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$HashLock = Join-Path $RepoRoot "requirements-build.windows-x64.hashes.txt"
if (-not (Test-Path -LiteralPath $HashLock)) {
    throw "Missing hash lock: $HashLock"
}

$Python = (Get-Command $PythonExecutable -ErrorAction Stop).Source
$VersionCheck = & $Python -c "import sys,platform; print('.'.join(map(str,sys.version_info[:3]))); print(platform.machine()); print(platform.architecture()[0])"
if ($LASTEXITCODE -ne 0 -or $VersionCheck.Count -lt 3) {
    throw "Unable to inspect Python toolchain"
}
$ExpectedVersion = (Get-Content -LiteralPath (Join-Path $RepoRoot "BUILD_PYTHON_VERSION") -Raw).Trim()
if ($VersionCheck[0].Trim() -ne $ExpectedVersion -or $VersionCheck[2].Trim() -ne "64bit") {
    throw "Wheelhouse acquisition requires CPython $ExpectedVersion 64-bit; got $($VersionCheck -join ' / ')"
}

if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $RepoRoot "artifact\windows-wheelhouse"
}
$Wheelhouse = [System.IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $Wheelhouse) {
    Remove-Item -LiteralPath $Wheelhouse -Recurse -Force
}
New-Item -ItemType Directory -Path $Wheelhouse -Force | Out-Null

Write-Host "Downloading exact hash-locked Windows x64 wheels to $Wheelhouse..."
& $Python -m pip download `
    --dest $Wheelhouse `
    --only-binary=:all: `
    --no-deps `
    --require-hashes `
    -r $HashLock
if ($LASTEXITCODE -ne 0) {
    throw "Hash-verified wheelhouse acquisition failed"
}

$Wheels = @(Get-ChildItem -LiteralPath $Wheelhouse -File -Filter "*.whl" | Sort-Object Name)
if ($Wheels.Count -ne 8) {
    throw "Expected exactly 8 approved wheels; found $($Wheels.Count)"
}

$ExpectedNames = @(
    'altgraph-0.17.5-py2.py3-none-any.whl',
    'packaging-26.3-py3-none-any.whl',
    'pefile-2024.8.26-py3-none-any.whl',
    'pip-26.1.2-py3-none-any.whl',
    'pyinstaller-6.22.0-py3-none-win_amd64.whl',
    'pyinstaller_hooks_contrib-2026.6-py3-none-any.whl',
    'pywin32_ctypes-0.2.3-py3-none-any.whl',
    'setuptools-84.0.0-py3-none-any.whl'
)
$ActualNames = @($Wheels | Select-Object -ExpandProperty Name)
foreach ($name in $ExpectedNames) {
    if ($ActualNames -notcontains $name) { throw "Missing approved wheel: $name" }
}
foreach ($name in $ActualNames) {
    if ($ExpectedNames -notcontains $name) { throw "Unexpected wheel in controlled wheelhouse: $name" }
}

$Files = foreach ($wheel in $Wheels) {
    [ordered]@{
        name   = $wheel.Name
        bytes  = $wheel.Length
        sha256 = (Get-FileHash -LiteralPath $wheel.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$GitCommit = "unknown"
try {
    $candidate = (git -C $RepoRoot rev-parse HEAD 2>$null)
    if ($candidate) { $GitCommit = $candidate.Trim() }
} catch {}

$Manifest = [ordered]@{
    schema_version      = 1
    purpose             = "APL-IP-002-WIN-R1/R2 controlled Windows x64 Python build wheelhouse"
    source_channel      = "PyPI acquisition verified by committed SHA256 requirements"
    python_version      = $ExpectedVersion
    python_architecture = "64bit"
    target_platform     = "windows-x64"
    hash_lock_sha256    = (Get-FileHash -LiteralPath $HashLock -Algorithm SHA256).Hash.ToLowerInvariant()
    source_commit       = $GitCommit
    wheel_count         = $Wheels.Count
    wheels              = @($Files)
}
$ManifestPath = Join-Path $Wheelhouse "wheelhouse-manifest.json"
$Manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ManifestPath -Encoding utf8

Write-Host "Wheelhouse verification PASS: $($Wheels.Count) exact wheels"
Write-Host "Manifest: $ManifestPath"
Write-Output $Wheelhouse
