<#
.SYNOPSIS
    Fail-closed Russian production publication gate for APL-REL-013.
.DESCRIPTION
    Proves that an exact final release set is internally consistent with the
    governed REL-011/REL-012 Russian release-evidence chain before publication.

    The gate:
      * validates version/tag/commit metadata against signing-evidence.json;
      * requires the currently governed ООО «Арвектум» release-evidence signer;
      * runs the REL-012 verifier against the untouched final directory;
      * performs a disposable negative tamper test and requires verification FAIL;
      * binds the release to the local Git tag and canonical main ancestry;
      * emits a non-secret publication decision OUTSIDE the signed release set.

    It never accepts a PIN, never exports a private key and never creates a
    production signature. The owner-operated REL-011 signing ceremony must have
    already completed successfully.
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

    [string]$ExpectedSignerThumbprint = 'EE1CFA955BA22F03C39C76B183D94CD37494582E',

    [string]$DecisionOutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'APL-REL-013 production release gate must run on Windows against the exact final Russian release set.'
}

function Normalize-Thumbprint([string]$Thumbprint) {
    return (($Thumbprint -replace '\s', '').ToUpperInvariant())
}

function Invoke-Git([string[]]$Arguments) {
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $exitCode: $($output -join ' ')"
    }
    return (($output | ForEach-Object { $_.ToString() }) -join "`n").Trim()
}

function Invoke-ReleaseVerifier([string]$Directory, [bool]$ExpectSuccess) {
    $scriptPath = Join-Path $Directory 'verify_russian_release.ps1'
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        throw "Bundled REL-012 verifier is missing: $scriptPath"
    }

    $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $scriptPath -ReleaseDirectory $Directory 2>&1
    $exitCode = $LASTEXITCODE
    $text = ($output | ForEach-Object { $_.ToString() }) -join "`n"

    if ($ExpectSuccess) {
        if ($exitCode -ne 0 -or $text -notmatch 'РЕЗУЛЬТАТ:\s*ПРОВЕРКА ПРОЙДЕНА') {
            throw "REL-012 verification did not PASS for the exact final release set. Exit=$exitCode"
        }
    }
    else {
        if ($exitCode -eq 0 -or $text -notmatch 'РЕЗУЛЬТАТ:\s*ПРОВЕРКА НЕ ПРОЙДЕНА') {
            throw 'Negative tamper test unexpectedly passed. Publication is forbidden.'
        }
    }

    return [ordered]@{
        exit_code = $exitCode
        expected_success = $ExpectSuccess
    }
}

$releasePath = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
if (-not (Test-Path -LiteralPath $releasePath -PathType Container)) {
    throw "Release directory does not exist: $ReleaseDirectory"
}

if ($GitTag -notmatch ('^v' + [regex]::Escape($Version) + '(?:$|[-+])')) {
    throw "Version/tag mismatch: Version=$Version GitTag=$GitTag"
}

$requiredEvidence = @(
    'SHA256SUMS.txt',
    'SHA256SUMS.txt.sig',
    'signer-certificate.cer',
    'signing-evidence.json',
    'verify_russian_release.ps1',
    'VERIFY_RUSSIAN_RELEASE.cmd'
)
foreach ($name in $requiredEvidence) {
    if (-not (Test-Path -LiteralPath (Join-Path $releasePath $name) -PathType Leaf)) {
        throw "Required final-release file is missing: $name"
    }
}

$evidencePath = Join-Path $releasePath 'signing-evidence.json'
$evidence = Get-Content -LiteralPath $evidencePath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($evidence.product -ne 'Arvectum Proxy Launcher') { throw 'Unexpected product in signing evidence.' }
if ($evidence.task -ne 'APL-REL-011') { throw 'Signing evidence was not produced by APL-REL-011.' }
if ($evidence.signing_mode -ne 'russian-qualified-evidence') { throw 'Unexpected signing mode.' }
if ([string]$evidence.version -ne $Version) { throw 'Version does not match signing evidence.' }
if ([string]$evidence.git_tag -ne $GitTag) { throw 'Git tag does not match signing evidence.' }
if (([string]$evidence.git_commit).ToLowerInvariant() -ne $GitCommit.ToLowerInvariant()) { throw 'Git commit does not match signing evidence.' }
if (-not [bool]$evidence.detached_signature_verified) { throw 'REL-011 evidence does not record successful detached verification.' }
if ([bool]$evidence.embedded_code_signing_activated) { throw 'Current Russia-first gate forbids an ungoverned embedded-code-signing claim.' }
if ([bool]$evidence.pin_stored) { throw 'Signing evidence reports PIN storage. Publication is forbidden.' }
if ([bool]$evidence.private_key_export_attempted) { throw 'Signing evidence reports a private-key export attempt. Publication is forbidden.' }

$expectedThumbprint = Normalize-Thumbprint $ExpectedSignerThumbprint
$evidenceThumbprint = Normalize-Thumbprint ([string]$evidence.signer_thumbprint)
if ($evidenceThumbprint -ne $expectedThumbprint) {
    throw "Signer thumbprint is not the governed ООО «Арвектум» release-evidence identity: $evidenceThumbprint"
}
if (([string]$evidence.signer_subject) -notmatch 'АРВЕКТУМ') { throw 'Signing evidence subject does not identify АРВЕКТУМ.' }

# The final download set must first pass exactly as the customer receives it.
$positive = Invoke-ReleaseVerifier -Directory $releasePath -ExpectSuccess $true

# Verify the release/tag/commit provenance from the repository containing this gate.
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Push-Location $repoRoot
try {
    $inside = Invoke-Git @('rev-parse', '--is-inside-work-tree')
    if ($inside -ne 'true') { throw 'APL-REL-013 must run from the Proxy Launcher Git worktree.' }

    $head = (Invoke-Git @('rev-parse', 'HEAD')).ToLowerInvariant()
    if ($head -ne $GitCommit.ToLowerInvariant()) {
        throw "Current HEAD is not the exact release commit. HEAD=$head expected=$($GitCommit.ToLowerInvariant())"
    }

    $tagCommit = (Invoke-Git @('rev-parse', "$GitTag^{commit}")).ToLowerInvariant()
    if ($tagCommit -ne $GitCommit.ToLowerInvariant()) {
        throw "Release tag does not resolve to the release commit. Tag=$tagCommit expected=$($GitCommit.ToLowerInvariant())"
    }

    & git merge-base --is-ancestor $GitCommit main 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw 'Release commit is not an ancestor of canonical local main.'
    }

    $dirty = Invoke-Git @('status', '--porcelain')
    if ($dirty) { throw 'Git worktree is not clean. Publication gate requires a clean exact-release checkout.' }
}
finally {
    Pop-Location
}

# Prove fail-closed behavior on a disposable copy without mutating the real release.
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('apl-rel-013-' + [Guid]::NewGuid().ToString('N'))
$tempRelease = Join-Path $tempRoot 'release'
New-Item -ItemType Directory -Path $tempRelease -Force | Out-Null
try {
    Copy-Item -LiteralPath (Join-Path $releasePath '*') -Destination $tempRelease -Recurse -Force

    $assetNames = @($evidence.assets | ForEach-Object { [string]$_.name })
    $tamperName = $assetNames | Where-Object {
        $_ -ne 'verify_russian_release.ps1' -and $_ -ne 'VERIFY_RUSSIAN_RELEASE.cmd'
    } | Select-Object -First 1
    if (-not $tamperName) {
        $tamperName = $assetNames | Select-Object -First 1
    }
    if (-not $tamperName) { throw 'No signed asset is available for the mandatory negative tamper test.' }

    $tamperPath = Join-Path $tempRelease $tamperName
    if (-not (Test-Path -LiteralPath $tamperPath -PathType Leaf)) { throw "Tamper-test asset is missing: $tamperName" }
    [System.IO.File]::AppendAllText($tamperPath, "`r`nAPL-REL-013-TAMPER-TEST", [System.Text.Encoding]::UTF8)
    $negative = Invoke-ReleaseVerifier -Directory $tempRelease -ExpectSuccess $false
}
finally {
    if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force }
}

if (-not $DecisionOutputPath) {
    $parent = Split-Path -Parent $releasePath
    $leaf = Split-Path -Leaf $releasePath
    $DecisionOutputPath = Join-Path $parent ($leaf + '.production-release-gate.json')
}
$decisionFullPath = [System.IO.Path]::GetFullPath($DecisionOutputPath)
$releasePrefix = $releasePath.TrimEnd('\') + '\'
if ($decisionFullPath.StartsWith($releasePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Decision output must be outside the signed release directory; otherwise it would invalidate REL-012 verification.'
}

$decision = [ordered]@{
    schema_version = 1
    task = 'APL-REL-013'
    product = 'Arvectum Proxy Launcher'
    version = $Version
    git_tag = $GitTag
    git_commit = $GitCommit.ToLowerInvariant()
    decision = 'PUBLISH'
    generated_utc = [DateTime]::UtcNow.ToString('o')
    release_directory = $releasePath
    signer_thumbprint = $expectedThumbprint
    signer_subject = [string]$evidence.signer_subject
    rel011_detached_signature_verified = $true
    rel012_exact_release_verification = 'PASS'
    rel012_negative_tamper_test = 'PASS_EXPECTED_FAILURE'
    git_head_exact = $true
    git_tag_exact = $true
    canonical_main_ancestry = $true
    clean_worktree = $true
    embedded_code_signing_activated = $false
    authenticode_trust_claimed = $false
    smartscreen_trust_claimed = $false
    pin_stored = $false
    private_key_export_attempted = $false
}
$decision | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $decisionFullPath -Encoding UTF8

Write-Host ''
Write-Host 'APL-REL-013 Russian production release gate: PASS'
Write-Host 'Publication decision: PUBLISH'
Write-Host "Version: $Version"
Write-Host "Git tag: $GitTag"
Write-Host "Git commit: $($GitCommit.ToLowerInvariant())"
Write-Host "Signer: $([string]$evidence.signer_subject)"
Write-Host 'REL-012 exact final set verification: PASS'
Write-Host 'Negative tamper test: PASS (tampered copy correctly rejected)'
Write-Host 'Authenticode/SmartScreen trust claimed: NO'
Write-Host "Decision evidence: $decisionFullPath"
