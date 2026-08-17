<#
.SYNOPSIS
    Acquire and Sigstore-verify the exact CPython bootstrap used by Windows builds.
.DESCRIPTION
    Downloads the locked CPython installer and its official Sigstore bundle from
    python.org, verifies the release-manager identity, then emits a manifest with
    the exact SHA256 for controlled archival. This is an acquisition step, not a
    runtime dependency of Arvectum Proxy Launcher.

    Bundle verification is explicitly performed with Sigstore's --offline mode.
    This preserves cryptographic identity/bundle verification while preventing a
    separate TUF metadata refresh from becoming a release-recovery network gate.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$VerifierPython = "python.exe",

    [Parameter(Mandatory = $false)]
    [string]$OutputDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$LockPath = Join-Path $RepoRoot "tools\python-windows-base.lock"
if (-not (Test-Path -LiteralPath $LockPath)) { throw "Missing CPython base lock: $LockPath" }

$Lock = @{}
foreach ($line in Get-Content -LiteralPath $LockPath) {
    $value = $line.Trim()
    if (-not $value -or $value.StartsWith('#')) { continue }
    $parts = $value.Split('=', 2)
    if ($parts.Count -ne 2) { throw "Invalid CPython base lock line: $value" }
    $Lock[$parts[0]] = $parts[1]
}

$RequiredKeys = @(
    'PYTHON_VERSION','PYTHON_ARCH','PYTHON_INSTALLER','PYTHON_INSTALLER_URL',
    'PYTHON_INSTALLER_SIZE','PYTHON_SIGSTORE_BUNDLE_URL',
    'PYTHON_SIGSTORE_CERT_IDENTITY','PYTHON_SIGSTORE_OIDC_ISSUER',
    'SIGSTORE_VERIFIER_VERSION'
)
foreach ($key in $RequiredKeys) {
    if (-not $Lock.ContainsKey($key) -or -not $Lock[$key]) { throw "Missing lock key: $key" }
}
if ($Lock['PYTHON_VERSION'] -ne (Get-Content -LiteralPath (Join-Path $RepoRoot 'BUILD_PYTHON_VERSION') -Raw).Trim()) {
    throw 'CPython base lock version does not match BUILD_PYTHON_VERSION'
}
if ($Lock['PYTHON_ARCH'] -ne 'x64') { throw 'Only the governed Windows x64 bootstrap is supported here' }

if (-not $OutputDirectory) { $OutputDirectory = Join-Path $RepoRoot 'artifact\windows-cpython-base' }
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $OutputDirectory) { Remove-Item -LiteralPath $OutputDirectory -Recurse -Force }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

$Installer = Join-Path $OutputDirectory $Lock['PYTHON_INSTALLER']
$Bundle = "$Installer.sigstore"
Write-Host "Downloading locked CPython $($Lock['PYTHON_VERSION']) $($Lock['PYTHON_ARCH']) installer..."
Invoke-WebRequest -Uri $Lock['PYTHON_INSTALLER_URL'] -OutFile $Installer -UseBasicParsing
Invoke-WebRequest -Uri $Lock['PYTHON_SIGSTORE_BUNDLE_URL'] -OutFile $Bundle -UseBasicParsing

$InstallerInfo = Get-Item -LiteralPath $Installer
if ($InstallerInfo.Length -ne [int64]$Lock['PYTHON_INSTALLER_SIZE']) {
    throw "CPython installer size mismatch: $($InstallerInfo.Length) != $($Lock['PYTHON_INSTALLER_SIZE'])"
}

$Verifier = (Get-Command $VerifierPython -ErrorAction Stop).Source
$VerifierVenv = Join-Path $OutputDirectory '.sigstore-verifier'
& $Verifier -m venv $VerifierVenv
if ($LASTEXITCODE -ne 0) { throw 'Unable to create Sigstore verifier venv' }
$VerifierVenvPython = Join-Path $VerifierVenv 'Scripts\python.exe'
& $VerifierVenvPython -m pip install --disable-pip-version-check "sigstore==$($Lock['SIGSTORE_VERIFIER_VERSION'])"
if ($LASTEXITCODE -ne 0) { throw 'Unable to install pinned Sigstore verifier' }

Write-Host "Verifying CPython Sigstore identity $($Lock['PYTHON_SIGSTORE_CERT_IDENTITY']) in offline bundle mode..."
& $VerifierVenvPython -m sigstore verify identity `
    --offline `
    --cert-identity $Lock['PYTHON_SIGSTORE_CERT_IDENTITY'] `
    --cert-oidc-issuer $Lock['PYTHON_SIGSTORE_OIDC_ISSUER'] `
    --bundle $Bundle `
    $Installer
if ($LASTEXITCODE -ne 0) { throw 'CPython Sigstore verification failed' }

Remove-Item -LiteralPath $VerifierVenv -Recurse -Force

$Manifest = [ordered]@{
    schema_version        = 1
    purpose               = 'APL-IP-002-WIN-R3 controlled CPython build bootstrap'
    python_version        = $Lock['PYTHON_VERSION']
    architecture          = $Lock['PYTHON_ARCH']
    installer             = $InstallerInfo.Name
    installer_bytes       = $InstallerInfo.Length
    installer_sha256      = (Get-FileHash -LiteralPath $Installer -Algorithm SHA256).Hash.ToLowerInvariant()
    sigstore_bundle       = (Split-Path -Leaf $Bundle)
    sigstore_bundle_sha256= (Get-FileHash -LiteralPath $Bundle -Algorithm SHA256).Hash.ToLowerInvariant()
    cert_identity         = $Lock['PYTHON_SIGSTORE_CERT_IDENTITY']
    oidc_issuer           = $Lock['PYTHON_SIGSTORE_OIDC_ISSUER']
    verifier_version      = $Lock['SIGSTORE_VERIFIER_VERSION']
    verification          = 'sigstore-identity-pass'
    verification_mode     = 'offline-bundle'
    trust_root_source     = 'sigstore-python-cache-or-baked-root'
    source_url            = $Lock['PYTHON_INSTALLER_URL']
    source_bundle_url     = $Lock['PYTHON_SIGSTORE_BUNDLE_URL']
}
$ManifestPath = Join-Path $OutputDirectory 'cpython-base-manifest.json'
$Manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $ManifestPath -Encoding utf8

Write-Host "CPython bootstrap verification PASS: $($Manifest.installer_sha256)"
Write-Output $OutputDirectory
