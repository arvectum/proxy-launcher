<#
.SYNOPSIS
    Acquire and verify the exact Inno Setup 6.7.1 compiler input for P0.2 recovery.
.DESCRIPTION
    Downloads the locked upstream Inno Setup installer plus its detached ISSig
    signature, release public key and license. The executable is accepted only if
    its exact byte size and SHA-256 match the repository lock and Windows reports
    a valid Authenticode signature from the pinned publisher.

    This is a connected acquisition step. The resulting directory is intended to
    be archived under Arvectum control and later moved into an endpoint-denied
    recovery VM. The installer is never executed by this script.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$OutputDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Inno Setup acquisition verification must run on Windows.' }

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$LockPath = Join-Path $RepoRoot 'tools\inno-setup-windows.lock'
if (-not (Test-Path -LiteralPath $LockPath)) { throw "Missing Inno Setup lock: $LockPath" }

$Lock = @{}
foreach ($line in Get-Content -LiteralPath $LockPath) {
    $value = $line.Trim()
    if (-not $value -or $value.StartsWith('#')) { continue }
    $parts = $value.Split('=', 2)
    if ($parts.Count -ne 2) { throw "Invalid Inno Setup lock line: $value" }
    $Lock[$parts[0]] = $parts[1]
}

$RequiredKeys = @(
    'INNO_VERSION','INNO_RELEASE_TAG','INNO_RELEASE_COMMIT_SHORT',
    'INNO_INSTALLER','INNO_INSTALLER_URL','INNO_INSTALLER_SIZE','INNO_INSTALLER_SHA256',
    'INNO_AUTHENTICODE_PUBLISHER','INNO_ISSIG','INNO_ISSIG_URL',
    'INNO_PUBLIC_KEY','INNO_PUBLIC_KEY_URL','INNO_PUBLIC_KEY_ID',
    'INNO_LICENSE','INNO_LICENSE_URL'
)
foreach ($key in $RequiredKeys) {
    if (-not $Lock.ContainsKey($key) -or -not $Lock[$key]) { throw "Missing lock key: $key" }
}
if ($Lock['INNO_VERSION'] -ne '6.7.1') { throw 'P0.2-B requires exact Inno Setup 6.7.1.' }
if ($Lock['INNO_RELEASE_TAG'] -ne 'is-6_7_1') { throw 'Unexpected Inno Setup release tag.' }
if ($Lock['INNO_INSTALLER_SHA256'] -notmatch '^[0-9a-f]{64}$') { throw 'Invalid locked Inno Setup SHA-256.' }

if (-not $OutputDirectory) { $OutputDirectory = Join-Path $RepoRoot 'artifact\windows-inno-setup-base' }
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $OutputDirectory) { Remove-Item -LiteralPath $OutputDirectory -Recurse -Force }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

$Installer = Join-Path $OutputDirectory $Lock['INNO_INSTALLER']
$Issig = Join-Path $OutputDirectory $Lock['INNO_ISSIG']
$PublicKey = Join-Path $OutputDirectory $Lock['INNO_PUBLIC_KEY']
$License = Join-Path $OutputDirectory $Lock['INNO_LICENSE']

Write-Host "Downloading locked Inno Setup $($Lock['INNO_VERSION']) release input..."
Invoke-WebRequest -Uri $Lock['INNO_INSTALLER_URL'] -OutFile $Installer -UseBasicParsing
Invoke-WebRequest -Uri $Lock['INNO_ISSIG_URL'] -OutFile $Issig -UseBasicParsing
Invoke-WebRequest -Uri $Lock['INNO_PUBLIC_KEY_URL'] -OutFile $PublicKey -UseBasicParsing
Invoke-WebRequest -Uri $Lock['INNO_LICENSE_URL'] -OutFile $License -UseBasicParsing

$InstallerInfo = Get-Item -LiteralPath $Installer
if ($InstallerInfo.Length -ne [int64]$Lock['INNO_INSTALLER_SIZE']) {
    throw "Inno Setup installer size mismatch: $($InstallerInfo.Length) != $($Lock['INNO_INSTALLER_SIZE'])"
}
$InstallerHash = (Get-FileHash -LiteralPath $Installer -Algorithm SHA256).Hash.ToLowerInvariant()
if ($InstallerHash -ne $Lock['INNO_INSTALLER_SHA256']) {
    throw "Inno Setup SHA-256 mismatch: $InstallerHash != $($Lock['INNO_INSTALLER_SHA256'])"
}

$Signature = Get-AuthenticodeSignature -LiteralPath $Installer
if ($Signature.Status -ne 'Valid') {
    throw "Inno Setup Authenticode verification failed: $($Signature.Status) $($Signature.StatusMessage)"
}
$SignerSubject = [string]$Signature.SignerCertificate.Subject
if ($SignerSubject -notlike "*$($Lock['INNO_AUTHENTICODE_PUBLISHER'])*") {
    throw "Inno Setup signer mismatch: '$SignerSubject' does not contain '$($Lock['INNO_AUTHENTICODE_PUBLISHER'])'"
}

$PublicKeyText = (Get-Content -LiteralPath $PublicKey -Raw).Trim()
if ($PublicKeyText -notmatch [regex]::Escape("key-id $($Lock['INNO_PUBLIC_KEY_ID'])")) {
    throw 'Inno Setup release public-key id does not match the repository lock.'
}

function FileHash([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$Manifest = [ordered]@{
    schema_version                 = 1
    purpose                        = '[Win] P0.2-B Inno Setup sovereignty preparation'
    inno_setup_version             = $Lock['INNO_VERSION']
    release_tag                    = $Lock['INNO_RELEASE_TAG']
    release_commit_short           = $Lock['INNO_RELEASE_COMMIT_SHORT']
    release_repository             = 'jrsoftware/issrc'
    release_immutable              = $true
    installer                      = $InstallerInfo.Name
    installer_bytes                = $InstallerInfo.Length
    installer_sha256               = $InstallerHash
    authenticode_status            = [string]$Signature.Status
    authenticode_publisher         = $Lock['INNO_AUTHENTICODE_PUBLISHER']
    authenticode_signer_subject    = $SignerSubject
    authenticode_signer_thumbprint = [string]$Signature.SignerCertificate.Thumbprint
    issig                          = (Split-Path -Leaf $Issig)
    issig_sha256                   = FileHash $Issig
    public_key                     = (Split-Path -Leaf $PublicKey)
    public_key_id                  = $Lock['INNO_PUBLIC_KEY_ID']
    public_key_sha256              = FileHash $PublicKey
    license                        = (Split-Path -Leaf $License)
    license_sha256                 = FileHash $License
    verification                   = 'locked-sha256+authenticode-pass'
    acquisition_mode               = 'connected-upstream'
    recovery_install_mode          = 'offline-from-controlled-copy'
    installer_source_url           = $Lock['INNO_INSTALLER_URL']
    issig_source_url               = $Lock['INNO_ISSIG_URL']
    public_key_source_url          = $Lock['INNO_PUBLIC_KEY_URL']
    license_source_url             = $Lock['INNO_LICENSE_URL']
    github_release_attestation     = "optional-defense-in-depth: gh release verify-asset $($Lock['INNO_INSTALLER']) --repo jrsoftware/issrc"
}
$ManifestPath = Join-Path $OutputDirectory 'inno-setup-base-manifest.json'
$Manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $ManifestPath -Encoding utf8

Write-Host "Inno Setup acquisition verification PASS: $InstallerHash"
Write-Host 'No upstream executable was run. Archive this verified directory under Arvectum control before recovery use.'
Write-Output $OutputDirectory
