<#
.SYNOPSIS
    Owner-operated Rutoken/CryptoPro proof-of-concept for APL-REL-010.
.DESCRIPTION
    Inventories the selected certificate, checks its EKUs, creates a disposable
    SHA256SUMS.txt manifest, produces a detached CMS/PKCS#7 signature through
    CryptoPro CSP csptest, verifies that signature, exports the public signer
    certificate, and writes non-secret JSON evidence.

    The script never accepts or stores a token PIN and never exports a private key.
    If CryptoPro/Rutoken needs authentication, the provider is expected to prompt
    the owner interactively.
#>

[CmdletBinding()]
param(
    [ValidateSet('Inspect', 'Run')]
    [string]$Mode = 'Inspect',

    [string]$CertificateThumbprint,

    [ValidateSet('CurrentUser', 'LocalMachine')]
    [string]$CertificateStoreLocation = 'CurrentUser',

    [string]$OutputDirectory = (Join-Path $env:TEMP 'Arvectum\APL-REL-010'),

    [string]$ExpectedSubjectPattern = 'Арвектум'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'APL-REL-010 owner-operated POC must run on Windows.'
}

$codeSigningOid = '1.3.6.1.5.5.7.3.3'

function Normalize-Thumbprint([string]$Thumbprint) {
    if ([string]::IsNullOrWhiteSpace($Thumbprint)) {
        return $null
    }
    return ($Thumbprint -replace '\s', '').ToUpperInvariant()
}

function Resolve-CspTest {
    if ($env:CRYPTO_PRO_CSPTEST_PATH) {
        if (-not (Test-Path -LiteralPath $env:CRYPTO_PRO_CSPTEST_PATH -PathType Leaf)) {
            throw "CRYPTO_PRO_CSPTEST_PATH does not exist: $env:CRYPTO_PRO_CSPTEST_PATH"
        }
        return (Resolve-Path -LiteralPath $env:CRYPTO_PRO_CSPTEST_PATH).Path
    }

    $command = Get-Command 'csptest.exe' -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @(
        (Join-Path $env:ProgramFiles 'Crypto Pro\CSP\csptest.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'Crypto Pro\CSP\csptest.exe')
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) }

    $candidate = $candidates | Select-Object -First 1
    if ($candidate) {
        return (Resolve-Path -LiteralPath $candidate).Path
    }

    throw 'CryptoPro CSP csptest.exe was not found. Install/repair CryptoPro CSP or set CRYPTO_PRO_CSPTEST_PATH.'
}

function Get-EkuInfo([System.Security.Cryptography.X509Certificates.X509Certificate2]$Certificate) {
    $ekus = @()
    foreach ($extension in $Certificate.Extensions) {
        if ($extension.Oid.Value -ne '2.5.29.37') {
            continue
        }
        $ekuExtension = [System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]$extension
        foreach ($oid in $ekuExtension.EnhancedKeyUsages) {
            $ekus += [pscustomobject]@{
                oid  = $oid.Value
                name = $oid.FriendlyName
            }
        }
    }
    return @($ekus)
}

function Get-ProviderName([System.Security.Cryptography.X509Certificates.X509Certificate2]$Certificate) {
    try {
        $privateKey = $Certificate.PrivateKey
        if ($privateKey -and $privateKey.CspKeyContainerInfo) {
            return $privateKey.CspKeyContainerInfo.ProviderName
        }
    } catch {
        return $null
    }
    return $null
}

function Get-CertificateInventory {
    $storePath = "Cert:\$CertificateStoreLocation\My"
    if (-not (Test-Path -LiteralPath $storePath)) {
        throw "Certificate store does not exist: $storePath"
    }

    $items = Get-ChildItem -LiteralPath $storePath | Where-Object { $_ -is [System.Security.Cryptography.X509Certificates.X509Certificate2] }
    foreach ($certificate in $items) {
        $ekus = @(Get-EkuInfo $certificate)
        [pscustomobject]@{
            thumbprint               = $certificate.Thumbprint
            subject                  = $certificate.Subject
            issuer                   = $certificate.Issuer
            serial                   = $certificate.SerialNumber
            not_before               = $certificate.NotBefore.ToUniversalTime().ToString('o')
            not_after                = $certificate.NotAfter.ToUniversalTime().ToString('o')
            has_private_key          = [bool]$certificate.HasPrivateKey
            provider                 = Get-ProviderName $certificate
            eku_oids                 = @($ekus | ForEach-Object { $_.oid })
            eku_names                = @($ekus | ForEach-Object { $_.name })
            code_signing_eku_present = [bool](@($ekus | Where-Object { $_.oid -eq $codeSigningOid }).Count -gt 0)
        }
    }
}

function Resolve-SelectedCertificate([object[]]$Inventory) {
    $normalized = Normalize-Thumbprint $CertificateThumbprint
    if ($normalized) {
        $match = @($Inventory | Where-Object { (Normalize-Thumbprint $_.thumbprint) -eq $normalized })
        if ($match.Count -ne 1) {
            throw "Certificate $normalized was not found exactly once in Cert:\$CertificateStoreLocation\My."
        }
        return $match[0]
    }

    $privateKeyCandidates = @($Inventory | Where-Object { $_.has_private_key })
    if (-not [string]::IsNullOrWhiteSpace($ExpectedSubjectPattern)) {
        $subjectMatches = @($privateKeyCandidates | Where-Object { $_.subject -match [regex]::Escape($ExpectedSubjectPattern) })
        if ($subjectMatches.Count -eq 1) {
            return $subjectMatches[0]
        }
        if ($subjectMatches.Count -gt 1) {
            throw "Multiple private-key certificates match '$ExpectedSubjectPattern'. Re-run with -CertificateThumbprint."
        }
    }

    if ($privateKeyCandidates.Count -eq 1) {
        return $privateKeyCandidates[0]
    }

    throw 'Unable to choose a unique private-key certificate automatically. Re-run with -CertificateThumbprint.'
}

function Invoke-CspTest([string[]]$Arguments) {
    $output = & $script:CspTest @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }
    if ($exitCode -ne 0) {
        throw "csptest failed with exit code $exitCode."
    }
    return @($output | ForEach-Object { $_.ToString() })
}

$script:CspTest = Resolve-CspTest
$cspVersion = (Get-Item -LiteralPath $script:CspTest).VersionInfo.FileVersion
$inventory = @(Get-CertificateInventory)

Write-Host "CryptoPro csptest: $script:CspTest"
Write-Host "CryptoPro file version: $cspVersion"
Write-Host "Certificates in Cert:\$CertificateStoreLocation\My: $($inventory.Count)"
$inventory | Format-Table thumbprint, has_private_key, code_signing_eku_present, subject -AutoSize

if ($Mode -eq 'Inspect') {
    return
}

$selected = Resolve-SelectedCertificate $inventory
if (-not $selected.has_private_key) {
    throw 'Selected certificate does not expose an accessible private key.'
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$outputPath = (Resolve-Path -LiteralPath $OutputDirectory).Path
$payloadPath = Join-Path $outputPath 'poc-artifact.txt'
$manifestPath = Join-Path $outputPath 'SHA256SUMS.txt'
$signaturePath = Join-Path $outputPath 'SHA256SUMS.txt.sig'
$certificatePath = Join-Path $outputPath 'signer-certificate.cer'
$evidencePath = Join-Path $outputPath 'signing-evidence.json'

$nonce = [guid]::NewGuid().ToString('N')
$utcNow = [DateTime]::UtcNow.ToString('o')
@(
    'Arvectum Proxy Launcher — APL-REL-010 disposable signing POC'
    "generated_utc=$utcNow"
    "nonce=$nonce"
) | Set-Content -LiteralPath $payloadPath -Encoding UTF8

$payloadHash = (Get-FileHash -LiteralPath $payloadPath -Algorithm SHA256).Hash.ToLowerInvariant()
"$payloadHash  poc-artifact.txt" | Set-Content -LiteralPath $manifestPath -Encoding ASCII

$certPath = "Cert:\$CertificateStoreLocation\My\$($selected.thumbprint)"
$certificate = Get-Item -LiteralPath $certPath
Export-Certificate -Cert $certificate -FilePath $certificatePath -Type CERT | Out-Null

if (Test-Path -LiteralPath $signaturePath) {
    Remove-Item -LiteralPath $signaturePath -Force
}

Write-Host 'Creating detached CMS/PKCS#7 signature. CryptoPro/Rutoken may prompt for the token PIN interactively.'
$signOutput = Invoke-CspTest @(
    '-sfsign', '-sign', '-detached', '-add',
    '-in', $manifestPath,
    '-out', $signaturePath,
    '-my', $selected.thumbprint
)

if (-not (Test-Path -LiteralPath $signaturePath -PathType Leaf)) {
    throw 'csptest returned success but detached signature file was not created.'
}

$verifyOutput = Invoke-CspTest @(
    '-sfsign', '-verify', '-detached',
    '-in', $manifestPath,
    '-signature', $signaturePath
)

$verifiedText = ($verifyOutput -join "`n")
$signatureVerified = ($verifiedText -match 'verified\s+OK') -or ($verifiedText -match 'ErrorCode:\s*0x00000000')
if (-not $signatureVerified) {
    throw 'Detached signature verification output did not contain a positive CryptoPro success marker.'
}

$manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
$signatureHash = (Get-FileHash -LiteralPath $signaturePath -Algorithm SHA256).Hash.ToLowerInvariant()
$subjectMatchesExpected = if ([string]::IsNullOrWhiteSpace($ExpectedSubjectPattern)) { $true } else { $selected.subject -match [regex]::Escape($ExpectedSubjectPattern) }

$codeSigningAssessment = if ($selected.code_signing_eku_present) {
    'candidate-profile-only; issuer policy, timestamping and real PE signing still require separate proof'
} else {
    'not-a-code-signing-certificate; Code Signing EKU is absent'
}

$evidence = [ordered]@{
    task                           = 'APL-REL-010'
    generated_utc                  = $utcNow
    host                           = $env:COMPUTERNAME
    os                             = [System.Environment]::OSVersion.VersionString
    powershell                     = $PSVersionTable.PSVersion.ToString()
    cryptopro_csptest_path         = $script:CspTest
    cryptopro_file_version         = $cspVersion
    certificate_store              = $CertificateStoreLocation
    signer_subject                 = $selected.subject
    signer_subject_matches_expected = [bool]$subjectMatchesExpected
    signer_issuer                  = $selected.issuer
    signer_thumbprint              = $selected.thumbprint
    certificate_serial             = $selected.serial
    certificate_not_before         = $selected.not_before
    certificate_not_after          = $selected.not_after
    certificate_has_private_key    = [bool]$selected.has_private_key
    private_key_export_attempted   = $false
    provider                       = $selected.provider
    eku_oids                       = @($selected.eku_oids)
    eku_names                      = @($selected.eku_names)
    code_signing_eku_oid           = $codeSigningOid
    code_signing_eku_present       = [bool]$selected.code_signing_eku_present
    code_signing_assessment        = $codeSigningAssessment
    manifest                       = 'SHA256SUMS.txt'
    manifest_sha256                = $manifestHash
    manifest_signature             = 'SHA256SUMS.txt.sig'
    manifest_signature_sha256      = $signatureHash
    detached_signature_verified    = [bool]$signatureVerified
    signer_certificate_exported    = 'signer-certificate.cer'
    authenticode_probe_attempted   = $false
    production_signing_activated   = $false
    pin_stored                     = $false
}

$evidence | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $evidencePath -Encoding UTF8

Write-Host ''
Write-Host 'APL-REL-010 detached signing POC PASS'
Write-Host "Signer: $($selected.subject)"
Write-Host "Thumbprint: $($selected.thumbprint)"
Write-Host "Code Signing EKU present: $($selected.code_signing_eku_present)"
Write-Host "Evidence directory: $outputPath"
Write-Host "Evidence: $evidencePath"
