<#
.SYNOPSIS
    Canonical owner-operated Russian-first Windows production signing ceremony.
.DESCRIPTION
    Binds the already-proven Windows 0.2.3 portable ZIP and Inno Setup installer
    to their exact production-build evidence, stages the canonical customer
    release set outside the repository, adds end-user verification UX, creates
    qualified detached CryptoPro/Rutoken release evidence, and runs the
    fail-closed production publication gate.

    This script deliberately does NOT rebuild artifacts and does NOT perform
    embedded PE/Authenticode signing. The governed certificate is used for
    qualified release-evidence signing only until a separately approved domestic
    code-signing identity and embedded-signing POC exist.

    The script never accepts or stores a token PIN, password, PFX, or private-key
    material. CryptoPro may request the Rutoken PIN interactively.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PortableZipPath,

    [Parameter(Mandatory = $true)]
    [string]$InstallerPath,

    [Parameter(Mandatory = $true)]
    [string]$ReleaseDirectory,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$')]
    [string]$GitTag,

    [string]$CertificateThumbprint = 'EE1CFA955BA22F03C39C76B183D94CD37494582E',

    [ValidateSet('CurrentUser', 'LocalMachine')]
    [string]$CertificateStoreLocation = 'CurrentUser'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'Windows Russian-first production signing must run on the owner-operated Windows signing station.'
}

function Invoke-Git([string[]]$Arguments) {
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code ${exitCode}: $($output -join ' ')"
    }
    return (($output | ForEach-Object { $_.ToString() }) -join "`n").Trim()
}

function Normalize-PathForComparison([string]$Path) {
    return ([System.IO.Path]::GetFullPath($Path)).TrimEnd('\')
}

function Assert-ReleaseOnlyDelta([string]$BuildCommit, [string]$ReleaseCommit) {
    & git merge-base --is-ancestor $BuildCommit $ReleaseCommit 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Artifact build commit $BuildCommit is not an ancestor of release commit $ReleaseCommit."
    }

    $changed = @(Invoke-Git @('diff', '--name-only', "$BuildCommit..$ReleaseCommit") -split "`n" | Where-Object { $_ })
    $releaseOnlyPatterns = @(
        '^docs/',
        '^release/',
        '^tests/',
        '^\.github/',
        '^tools/windows_russian_production_signing\.ps1$',
        '^tools/russian_signed_release\.ps1$',
        '^tools/prepare_russian_release_verification_ux\.ps1$',
        '^tools/verify_russian_release\.ps1$',
        '^tools/VERIFY_RUSSIAN_RELEASE\.cmd$',
        '^tools/russian_production_release_gate\.ps1$'
    )

    $forbidden = @()
    foreach ($path in $changed) {
        $allowed = $false
        foreach ($pattern in $releaseOnlyPatterns) {
            if ($path -match $pattern) {
                $allowed = $true
                break
            }
        }
        if (-not $allowed) { $forbidden += $path }
    }

    if ($forbidden.Count -gt 0) {
        throw ("Product/build-input drift exists after the sealed artifact build. Rebuild is required before signing. Forbidden changed paths: " + ($forbidden -join ', '))
    }
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Push-Location $repoRoot
try {
    if ((Invoke-Git @('rev-parse', '--is-inside-work-tree')) -ne 'true') {
        throw 'Signing ceremony must run from the canonical Proxy Launcher Git worktree.'
    }

    $branch = Invoke-Git @('branch', '--show-current')
    if ($branch -ne 'main') {
        throw "Signing ceremony requires canonical branch main. Current branch: $branch"
    }

    if (Invoke-Git @('status', '--porcelain')) {
        throw 'Git worktree must be clean before production signing.'
    }

    $releaseCommit = (Invoke-Git @('rev-parse', 'HEAD')).ToLowerInvariant()
    $tagCommit = (Invoke-Git @('rev-parse', "$GitTag^{commit}")).ToLowerInvariant()
    if ($tagCommit -ne $releaseCommit) {
        throw "Release tag must resolve to current canonical HEAD before signing. Tag=$tagCommit HEAD=$releaseCommit"
    }

    $version = (Get-Content -LiteralPath (Join-Path $repoRoot 'VERSION') -Raw).Trim()
    if ($GitTag -notmatch ('^v' + [regex]::Escape($version) + '(?:$|[-+])')) {
        throw "Version/tag mismatch: VERSION=$version GitTag=$GitTag"
    }

    $buildEvidencePath = Join-Path $repoRoot 'docs\evidence\WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json'
    if (-not (Test-Path -LiteralPath $buildEvidencePath -PathType Leaf)) {
        throw "Canonical Windows production-build evidence is missing: $buildEvidencePath"
    }
    $buildEvidence = Get-Content -LiteralPath $buildEvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json

    if ([string]$buildEvidence.verification_status -ne 'PASS' -or [string]$buildEvidence.closure_status -ne 'CLOSED') {
        throw 'Canonical Windows production-build evidence is not PASS/CLOSED.'
    }
    if ([string]$buildEvidence.product_version -ne $version) {
        throw "Build-evidence version does not match VERSION. Evidence=$($buildEvidence.product_version) VERSION=$version"
    }

    $buildCommit = ([string]$buildEvidence.repository.source_commit).ToLowerInvariant()
    if ($buildCommit -notmatch '^[0-9a-f]{40}$') {
        throw "Invalid artifact build commit in evidence: $buildCommit"
    }
    Assert-ReleaseOnlyDelta -BuildCommit $buildCommit -ReleaseCommit $releaseCommit

    $portableSource = (Resolve-Path -LiteralPath $PortableZipPath).Path
    $installerSource = (Resolve-Path -LiteralPath $InstallerPath).Path
    $expectedPortableName = "Arvectum-Proxy-Launcher-$version-windows-x64-portable.zip"
    $expectedInstallerName = [string]$buildEvidence.installer_build.filename

    if ((Split-Path -Leaf $portableSource) -cne $expectedPortableName) {
        throw "Portable filename mismatch. Actual=$(Split-Path -Leaf $portableSource) Expected=$expectedPortableName"
    }
    if ((Split-Path -Leaf $installerSource) -cne $expectedInstallerName) {
        throw "Installer filename mismatch. Actual=$(Split-Path -Leaf $installerSource) Expected=$expectedInstallerName"
    }

    $portableHash = (Get-FileHash -LiteralPath $portableSource -Algorithm SHA256).Hash.ToLowerInvariant()
    $installerHash = (Get-FileHash -LiteralPath $installerSource -Algorithm SHA256).Hash.ToLowerInvariant()
    $expectedPortableHash = ([string]$buildEvidence.portable_build.zip_sha256).ToLowerInvariant()
    $expectedInstallerHash = ([string]$buildEvidence.installer_build.sha256).ToLowerInvariant()
    if ($portableHash -ne $expectedPortableHash) {
        throw "Portable ZIP is not the sealed production artifact. Actual=$portableHash Expected=$expectedPortableHash"
    }
    if ($installerHash -ne $expectedInstallerHash) {
        throw "Installer is not the sealed production artifact. Actual=$installerHash Expected=$expectedInstallerHash"
    }

    $installerBytes = (Get-Item -LiteralPath $installerSource).Length
    if ($installerBytes -ne [int64]$buildEvidence.installer_build.bytes) {
        throw "Installer size mismatch. Actual=$installerBytes Expected=$($buildEvidence.installer_build.bytes)"
    }

    $releaseFullPath = Normalize-PathForComparison $ReleaseDirectory
    $repoFullPath = Normalize-PathForComparison $repoRoot
    if ($releaseFullPath.StartsWith($repoFullPath + '\', [System.StringComparison]::OrdinalIgnoreCase) -or $releaseFullPath -eq $repoFullPath) {
        throw 'ReleaseDirectory must be outside the Git worktree so production evidence cannot dirty the exact release checkout.'
    }

    if (Test-Path -LiteralPath $releaseFullPath) {
        $existing = @(Get-ChildItem -LiteralPath $releaseFullPath -Force)
        if ($existing.Count -gt 0) {
            throw "ReleaseDirectory already exists and is not empty: $releaseFullPath"
        }
    }
    else {
        New-Item -ItemType Directory -Path $releaseFullPath -Force | Out-Null
    }

    $requiredRepoFiles = @(
        'THIRD_PARTY_NOTICES.txt',
        'LICENSE',
        'tools\prepare_russian_release_verification_ux.ps1',
        'tools\russian_signed_release.ps1',
        'tools\russian_production_release_gate.ps1'
    )
    foreach ($relative in $requiredRepoFiles) {
        $candidate = Join-Path $repoRoot $relative
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            throw "Required governed release file is missing: $relative"
        }
    }

    Copy-Item -LiteralPath $portableSource -Destination (Join-Path $releaseFullPath $expectedPortableName)
    Copy-Item -LiteralPath $installerSource -Destination (Join-Path $releaseFullPath $expectedInstallerName)
    Copy-Item -LiteralPath (Join-Path $repoRoot 'THIRD_PARTY_NOTICES.txt') -Destination (Join-Path $releaseFullPath 'THIRD_PARTY_NOTICES.txt')
    Copy-Item -LiteralPath (Join-Path $repoRoot 'LICENSE') -Destination (Join-Path $releaseFullPath 'LICENSE.txt')
    Copy-Item -LiteralPath $buildEvidencePath -Destination (Join-Path $releaseFullPath 'WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json')

    $buildEvidenceHash = (Get-FileHash -LiteralPath $buildEvidencePath -Algorithm SHA256).Hash.ToLowerInvariant()
    $provenance = [ordered]@{
        schema_version = 1
        task = 'WINDOWS_RUSSIAN_FIRST_PRODUCTION_SIGNING'
        product = 'Arvectum Proxy Launcher'
        version = $version
        release_tag = $GitTag
        artifact_build_commit = $buildCommit
        release_policy_commit = $releaseCommit
        artifact_identity_rule = 'sealed-build-artifacts-with-release-only-delta'
        build_evidence = [ordered]@{
            filename = 'WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json'
            sha256 = $buildEvidenceHash
            verification_status = [string]$buildEvidence.verification_status
            closure_status = [string]$buildEvidence.closure_status
        }
        portable = [ordered]@{
            filename = $expectedPortableName
            sha256 = $portableHash
            executable_sha256 = ([string]$buildEvidence.portable_build.exe_sha256).ToLowerInvariant()
        }
        installer = [ordered]@{
            filename = $expectedInstallerName
            size_bytes = $installerBytes
            sha256 = $installerHash
            pre_signing_authenticode_status = [string]$buildEvidence.installer_build.authenticode_status
        }
        trust_model = [ordered]@{
            russian_qualified_release_evidence = $true
            embedded_pe_authenticode = $false
            microsoft_smartscreen_trust_claimed = $false
            governed_certificate_thumbprint = ($CertificateThumbprint -replace '\s', '').ToUpperInvariant()
            governed_certificate_classification = 'RELEASE-EVIDENCE-ONLY'
        }
    }
    $provenance | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $releaseFullPath 'WINDOWS_BUILD_PROVENANCE.json') -Encoding UTF8

    $readme = @"
Arvectum Proxy Launcher $version — Windows Russian-first release

This package is protected by a Russian qualified detached release signature over SHA256SUMS.txt.
Run VERIFY_RUSSIAN_RELEASE.cmd before installation or use verify_russian_release.ps1 directly.

Important trust boundary:
- the detached CryptoPro/Rutoken signature authenticates the release manifest and all listed files;
- the current release-evidence certificate is not claimed as Microsoft Authenticode/SmartScreen trust;
- do not publish or install the package if the bundled verifier reports failure.

Release tag: $GitTag
Artifact build commit: $buildCommit
Release policy commit: $releaseCommit
"@
    $readme | Set-Content -LiteralPath (Join-Path $releaseFullPath 'README_RUSSIAN_RELEASE.txt') -Encoding UTF8

    & (Join-Path $repoRoot 'tools\prepare_russian_release_verification_ux.ps1') -ReleaseDirectory $releaseFullPath
    if ($LASTEXITCODE -ne 0) { throw 'REL-012 verification UX staging failed.' }

    Write-Host ''
    Write-Host '=== Physical signing boundary ==='
    Write-Host "Exact portable SHA256: $portableHash"
    Write-Host "Exact installer SHA256: $installerHash"
    Write-Host "Artifact build commit: $buildCommit"
    Write-Host "Release policy commit: $releaseCommit"
    Write-Host 'CryptoPro may now ask for the Rutoken PIN interactively; the PIN is never passed to this script.'

    & (Join-Path $repoRoot 'tools\russian_signed_release.ps1') `
        -ReleaseDirectory $releaseFullPath `
        -Version $version `
        -GitTag $GitTag `
        -GitCommit $releaseCommit `
        -CertificateThumbprint $CertificateThumbprint `
        -CertificateStoreLocation $CertificateStoreLocation
    if ($LASTEXITCODE -ne 0) { throw 'APL-REL-011 signing failed.' }

    $decisionPath = $releaseFullPath + '.production-release-gate.json'
    & (Join-Path $repoRoot 'tools\russian_production_release_gate.ps1') `
        -ReleaseDirectory $releaseFullPath `
        -Version $version `
        -GitTag $GitTag `
        -GitCommit $releaseCommit `
        -ExpectedSignerThumbprint $CertificateThumbprint `
        -DecisionOutputPath $decisionPath
    if ($LASTEXITCODE -ne 0) { throw 'APL-REL-013 production publication gate failed.' }

    $decision = Get-Content -LiteralPath $decisionPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]$decision.decision -ne 'PUBLISH') {
        throw "Production gate did not issue PUBLISH: $($decision.decision)"
    }

    Write-Host ''
    Write-Host 'Windows Russian-first production signing ceremony: PASS'
    Write-Host "Canonical release directory: $releaseFullPath"
    Write-Host "Publication decision: $decisionPath"
    Write-Host 'Qualified detached release evidence: PRESENT AND VERIFIED'
    Write-Host 'Embedded Authenticode/SmartScreen trust claimed: NO'
}
finally {
    Pop-Location
}
