<#
.SYNOPSIS
    Owner-operated Russian signed-release integration for APL-REL-011.
.DESCRIPTION
    Creates the canonical final SHA256SUMS.txt for a release directory, signs it
    with the approved ООО «Арвектум» Rutoken/CryptoPro certificate, verifies the
    detached signature, exports the public signer certificate, and emits
    non-secret signing-evidence.json.

    This script deliberately does NOT perform embedded PE/Authenticode signing.
    The current APL-REL-010 certificate is RELEASE-EVIDENCE-ONLY because the
    Code Signing EKU is absent. Embedded signing remains gated on a separately
    approved ОТУЦ (or equivalent domestic code-signing) certificate and POC.

    The script never accepts or stores a token PIN and never exports a private key.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ReleaseDirectory,

    [Parameter(Mandatory = $true)]
    [string]$Version,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$')]
    [string]$GitTag,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F]{40}$')]
    [string]$GitCommit,

    [Parameter(Mandatory = $true)]
    [string]$CertificateThumbprint,

    [ValidateSet('CurrentUser', 'LocalMachine')]
    [string]$CertificateStoreLocation = 'CurrentUser',

    [switch]$OverwriteEvidence
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'APL-REL-011 signed-release integration must run on the owner-operated Windows signing station.'
}

function Normalize-Thumbprint([string]$Thumbprint) {
    return (($Thumbprint -replace '\s', '').ToUpperInvariant())
}

function Resolve-CspTest {
    if ($env:CRYPTO_PRO_CSPTEST_PATH) {
        if (-not (Test-Path -LiteralPath $env:CRYPTO_PRO_CSPTEST_PATH -PathType Leaf)) {
            throw "CRYPTO_PRO_CSPTEST_PATH does not exist: $env:CRYPTO_PRO_CSPTEST_PATH"
        }
        return (Resolve-Path -LiteralPath $env:CRYPTO_PRO_CSPTEST_PATH).Path
    }

    $command = Get-Command 'csptest.exe' -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }

    $candidates = @()
    if ($env:ProgramFiles) { $candidates += (Join-Path $env:ProgramFiles 'Crypto Pro\CSP\csptest.exe') }
    if (${env:ProgramFiles(x86)}) { $candidates += (Join-Path ${env:ProgramFiles(x86)} 'Crypto Pro\CSP\csptest.exe') }
    $candidate = $candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
    if ($candidate) { return (Resolve-Path -LiteralPath $candidate).Path }

    throw 'CryptoPro CSP csptest.exe was not found.'
}

function Invoke-CspTest([string[]]$Arguments) {
    $output = & $script:CspTest @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }
    if ($exitCode -ne 0) { throw "csptest failed with exit code $exitCode." }
    return @($output | ForEach-Object { $_.ToString() })
}

$releasePath = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
if (-not (Test-Path -LiteralPath $releasePath -PathType Container)) {
    throw "Release directory does not exist: $ReleaseDirectory"
}

if ($GitTag -notmatch ('^v' + [regex]::Escape($Version) + '(?:$|[-+])')) {
    throw "Version/tag mismatch: Version=$Version GitTag=$GitTag"
}

$manifestName = 'SHA256SUMS.txt'
$signatureName = 'SHA256SUMS.txt.sig'
$certificateName = 'signer-certificate.cer'
$evidenceName = 'signing-evidence.json'
$reserved = @($manifestName, $signatureName, $certificateName, $evidenceName)

foreach ($name in $reserved) {
    $path = Join-Path $releasePath $name
    if ((Test-Path -LiteralPath $path) -and -not $OverwriteEvidence) {
        throw "Evidence file already exists: $path. Use -OverwriteEvidence only for an intentional re-sign."
    }
}

$files = @(Get-ChildItem -LiteralPath $releasePath -File | Where-Object { $reserved -notcontains $_.Name } | Sort-Object Name)
if ($files.Count -lt 1) {
    throw 'Release directory contains no final release assets to sign.'
}

$manifestPath = Join-Path $releasePath $manifestName
$signaturePath = Join-Path $releasePath $signatureName
$certificatePath = Join-Path $releasePath $certificateName
$evidencePath = Join-Path $releasePath $evidenceName

$manifestLines = foreach ($file in $files) {
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $($file.Name)"
}
$manifestLines | Set-Content -LiteralPath $manifestPath -Encoding ASCII

# Fail closed by re-reading and verifying every manifest entry before signing.
foreach ($line in Get-Content -LiteralPath $manifestPath) {
    if ($line -notmatch '^([0-9a-f]{64})  (.+)$') { throw "Malformed manifest line: $line" }
    $expected = $Matches[1]
    $name = $Matches[2]
    $assetPath = Join-Path $releasePath $name
    if (-not (Test-Path -LiteralPath $assetPath -PathType Leaf)) { throw "Manifest asset missing: $name" }
    $actual = (Get-FileHash -LiteralPath $assetPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) { throw "SHA-256 mismatch before signing: $name" }
}

$thumbprint = Normalize-Thumbprint $CertificateThumbprint
$certPath = "Cert:\$CertificateStoreLocation\My\$thumbprint"
if (-not (Test-Path -LiteralPath $certPath)) { throw "Certificate not found: $certPath" }
$certificate = Get-Item -LiteralPath $certPath
if (-not $certificate.HasPrivateKey) { throw 'Selected certificate does not expose an accessible private key.' }

$codeSigningOid = '1.3.6.1.5.5.7.3.3'
$ekuOids = @()
foreach ($extension in $certificate.Extensions) {
    if ($extension.Oid.Value -eq '2.5.29.37') {
        $eku = [System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]$extension
        $ekuOids += @($eku.EnhancedKeyUsages | ForEach-Object { $_.Value })
    }
}
$codeSigningEkuPresent = [bool]($ekuOids -contains $codeSigningOid)

# REL-010 closed with EKU absent. Even if another cert is passed later, this task
# never silently promotes it to production PE signing.
$embeddedCodeSigningActivated = $false

Export-Certificate -Cert $certificate -FilePath $certificatePath -Type CERT | Out-Null
$script:CspTest = Resolve-CspTest
$cspVersion = (Get-Item -LiteralPath $script:CspTest).VersionInfo.FileVersion
$storeSelector = if ($CertificateStoreLocation -eq 'LocalMachine') { '-MY' } else { '-my' }

Write-Host 'Signing SHA256SUMS.txt with CryptoPro/Rutoken. The provider may prompt for the token PIN interactively.'
Invoke-CspTest @(
    '-sfsign', '-sign', '-detached', '-add',
    '-in', $manifestPath,
    '-out', $signaturePath,
    $storeSelector, $thumbprint
) | Out-Null

if (-not (Test-Path -LiteralPath $signaturePath -PathType Leaf)) {
    throw 'Detached signature was not created.'
}

$verifyOutput = Invoke-CspTest @(
    '-sfsign', '-verify', '-detached',
    '-in', $manifestPath,
    '-signature', $signaturePath
)
$verifyText = ($verifyOutput -join "`n")
$signatureVerified = ($verifyText -match 'verified\s+OK') -or ($verifyText -match 'ErrorCode:\s*0x00000000')
if (-not $signatureVerified) { throw 'Detached signature verification did not produce a positive CryptoPro success marker.' }

# Verify assets again after signing to prove that no release asset changed between
# manifest generation and evidence completion.
foreach ($line in Get-Content -LiteralPath $manifestPath) {
    $line -match '^([0-9a-f]{64})  (.+)$' | Out-Null
    $expected = $Matches[1]
    $name = $Matches[2]
    $actual = (Get-FileHash -LiteralPath (Join-Path $releasePath $name) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) { throw "Release asset changed during signing: $name" }
}

$generatedUtc = [DateTime]::UtcNow.ToString('o')
$manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
$signatureHash = (Get-FileHash -LiteralPath $signaturePath -Algorithm SHA256).Hash.ToLowerInvariant()

$assetRecords = @($files | ForEach-Object {
    [ordered]@{
        name = $_.Name
        sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        size_bytes = $_.Length
    }
})

$evidence = [ordered]@{
    schema_version                    = 1
    task                              = 'APL-REL-011'
    product                           = 'Arvectum Proxy Launcher'
    version                           = $Version
    git_tag                           = $GitTag
    git_commit                        = $GitCommit.ToLowerInvariant()
    signing_mode                      = 'russian-qualified-evidence'
    generated_utc                     = $generatedUtc
    signing_host                      = $env:COMPUTERNAME
    certificate_store                 = $CertificateStoreLocation
    signer_subject                    = $certificate.Subject
    signer_issuer                     = $certificate.Issuer
    signer_thumbprint                 = $thumbprint
    certificate_serial                = $certificate.SerialNumber
    certificate_not_after             = $certificate.NotAfter.ToUniversalTime().ToString('o')
    certificate_has_private_key       = [bool]$certificate.HasPrivateKey
    private_key_export_attempted      = $false
    pin_stored                        = $false
    cryptopro_csptest_path            = $script:CspTest
    cryptopro_file_version            = $cspVersion
    code_signing_eku_oid              = $codeSigningOid
    code_signing_eku_present          = $codeSigningEkuPresent
    current_certificate_classification = if ($codeSigningEkuPresent) { 'CODE-SIGNING-CANDIDATE-ONLY' } else { 'RELEASE-EVIDENCE-ONLY' }
    embedded_code_signing_activated   = $embeddedCodeSigningActivated
    otuc_production_certificate_used  = $false
    manifest                          = $manifestName
    manifest_sha256                   = $manifestHash
    manifest_signature                = $signatureName
    manifest_signature_sha256         = $signatureHash
    detached_signature_verified       = [bool]$signatureVerified
    signer_certificate                = $certificateName
    assets                            = $assetRecords
}

$evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $evidencePath -Encoding UTF8

Write-Host ''
Write-Host 'APL-REL-011 Russian signed-release integration: PASS'
Write-Host "Assets covered: $($files.Count)"
Write-Host "Signer: $($certificate.Subject)"
Write-Host "Certificate classification: $($evidence.current_certificate_classification)"
Write-Host "Detached signature verified: $signatureVerified"
Write-Host 'Embedded code signing activated: NO'
Write-Host "Release evidence directory: $releasePath"
