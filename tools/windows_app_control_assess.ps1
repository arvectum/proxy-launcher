<#
.SYNOPSIS
    Read-only Windows application-control assessment for APL-WIN-014.
.DESCRIPTION
    Observes Smart App Control/App Control state, effective Code Integrity policies,
    release provenance verification and Authenticode status. This script never
    changes Windows security policy, registry policy state, proxy settings or app files.
#>
[CmdletBinding()]
param(
    [string]$ReleaseDirectory = '',
    [string]$InstalledExe = '',
    [string]$EvidencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'APL-WIN-014 assessment must run on Windows.'
}

$ExpectedVersion = '0.2.3'
$ExpectedTag = 'v0.2.3-ru.2'
$ExpectedSetupSha256 = '5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414'
$ExpectedPortableSha256 = '62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801'
$ExpectedAppSha256 = 'f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a'
$ExpectedSignerThumbprint = 'EE1CFA955BA22F03C39C76B183D94CD37494582E'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-SignatureRecord([string]$Path) {
    if (-not $Path -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    $sig = Get-AuthenticodeSignature -LiteralPath $Path
    return [ordered]@{
        path = $Path
        status = [string]$sig.Status
        status_message = [string]$sig.StatusMessage
        signer_subject = $(if ($sig.SignerCertificate) { [string]$sig.SignerCertificate.Subject } else { $null })
        signer_thumbprint = $(if ($sig.SignerCertificate) { [string]$sig.SignerCertificate.Thumbprint } else { $null })
        signature_type = [string]$sig.SignatureType
    }
}

$os = Get-CimInstance Win32_OperatingSystem
$computerSystem = Get-CimInstance Win32_ComputerSystem
$ciPolicyKey = 'HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy'
$verifiedState = $null
$verifiedStateName = 'UNKNOWN'

if (Test-Path -LiteralPath $ciPolicyKey) {
    $ciPolicy = Get-ItemProperty -LiteralPath $ciPolicyKey -ErrorAction SilentlyContinue
    if ($ciPolicy -and $ciPolicy.PSObject.Properties['VerifiedAndReputablePolicyState']) {
        $verifiedState = [int]$ciPolicy.VerifiedAndReputablePolicyState
        switch ($verifiedState) {
            0 { $verifiedStateName = 'OFF' }
            1 { $verifiedStateName = 'ENFORCE' }
            2 { $verifiedStateName = 'EVALUATION' }
            default { $verifiedStateName = 'UNKNOWN_VALUE' }
        }
    }
}

$ciTool = Join-Path $env:WINDIR 'System32\CiTool.exe'
$ciToolAvailable = Test-Path -LiteralPath $ciTool -PathType Leaf
$effectivePolicies = @()
$ciToolError = $null

if ($ciToolAvailable) {
    try {
        $raw = & $ciTool -lp -json 2>&1
        if ($LASTEXITCODE -eq 0) {
            $parsed = ($raw -join "`n") | ConvertFrom-Json
            if ($parsed.Policies) {
                $effectivePolicies = @(
                    $parsed.Policies | ForEach-Object {
                        [ordered]@{
                            policy_id = [string]$_.PolicyID
                            base_policy_id = [string]$_.BasePolicyID
                            friendly_name = [string]$_.FriendlyName
                            is_enforced = [string]$_.IsEnforced
                            is_on_disk = [string]$_.IsOnDisk
                            is_signed_policy = [string]$_.IsSignedPolicy
                        }
                    }
                )
            }
        }
        else {
            $ciToolError = "CiTool exited with code $LASTEXITCODE"
        }
    }
    catch {
        $ciToolError = $_.Exception.Message
    }
}

if (-not $InstalledExe) {
    $documents = [Environment]::GetFolderPath('MyDocuments')
    $candidate = Join-Path $documents 'ArvectumProxyLauncher\Arvectum Proxy Launcher.exe'
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        $InstalledExe = $candidate
    }
}

$releaseVerification = 'NOT_REQUESTED'
$releaseVerificationExit = $null
$setupRecord = $null
$portableRecord = $null

if ($ReleaseDirectory) {
    $ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
    $setup = Join-Path $ReleaseDirectory 'Arvectum-Proxy-Launcher-0.2.3-windows-x64-setup.exe'
    $portable = Join-Path $ReleaseDirectory 'Arvectum-Proxy-Launcher-0.2.3-windows-x64-portable.zip'
    $verifier = Join-Path $ReleaseDirectory 'verify_russian_release.ps1'

    foreach ($required in @($setup, $portable, $verifier)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
            throw "Required release input is missing: $required"
        }
    }

    $setupHash = Get-Sha256 $setup
    $portableHash = Get-Sha256 $portable
    if ($setupHash -ne $ExpectedSetupSha256) { throw 'Production installer SHA256 mismatch.' }
    if ($portableHash -ne $ExpectedPortableSha256) { throw 'Production portable ZIP SHA256 mismatch.' }

    $oldEap = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $verifier -ReleaseDirectory $ReleaseDirectory -ExpectedSignerThumbprint $ExpectedSignerThumbprint | Out-Host
        $releaseVerificationExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $oldEap
    }
    $releaseVerification = $(if ($releaseVerificationExit -eq 0) { 'PASS' } else { 'BLOCK' })
    $setupRecord = Get-SignatureRecord $setup
    $portableRecord = [ordered]@{ path = $portable; sha256 = $portableHash }
}

$installedSignature = Get-SignatureRecord $InstalledExe
$installedHash = $null
$installedMatchesSealed = $null
if ($InstalledExe -and (Test-Path -LiteralPath $InstalledExe -PathType Leaf)) {
    $installedHash = Get-Sha256 $InstalledExe
    $installedMatchesSealed = ($installedHash -eq $ExpectedAppSha256)
}

$enforcedPolicies = @($effectivePolicies | Where-Object { [string]$_.is_enforced -eq 'True' })
$classification = if ($verifiedState -eq 1) {
    'SMART_APP_CONTROL_ENFORCED'
}
elseif ($enforcedPolicies.Count -gt 0) {
    'APP_CONTROL_FOR_BUSINESS_DETECTED'
}
elseif ($verifiedState -eq 2) {
    'SMART_APP_CONTROL_EVALUATION'
}
elseif ($verifiedState -eq 0) {
    'SMART_APP_CONTROL_OFF_OR_ENTERPRISE_POLICY_ONLY'
}
else {
    'APPLICATION_CONTROL_STATE_UNRESOLVED'
}

$recommendedPath = if ($classification -eq 'SMART_APP_CONTROL_ENFORCED') {
    'DO_NOT_CHANGE_SAC_ON_OWNER_HOST; use trusted source/developer mode until a SAC-trusted embedded signature exists'
}
elseif ($classification -eq 'APP_CONTROL_FOR_BUSINESS_DETECTED') {
    'ENTERPRISE_TRUST_PACK_CANDIDATE; customer IT must approve and deploy supplemental hash or managed-installer policy'
}
else {
    'VERIFY_TARGET_ORGANIZATION_POLICY_BEFORE_DEPLOYMENT'
}

$evidence = [ordered]@{
    schema = 'arvectum.proxy.windows-app-control-assessment.v1'
    task = 'APL-WIN-014'
    created_utc = [DateTime]::UtcNow.ToString('o')
    expected_version = $ExpectedVersion
    expected_release_tag = $ExpectedTag
    os_caption = [string]$os.Caption
    os_version = [string]$os.Version
    os_build = [string]$os.BuildNumber
    domain = [string]$computerSystem.Domain
    part_of_domain = [bool]$computerSystem.PartOfDomain
    verified_and_reputable_policy_state = $verifiedState
    verified_and_reputable_policy_state_name = $verifiedStateName
    ci_tool_available = $ciToolAvailable
    ci_tool_error = $ciToolError
    effective_policies = $effectivePolicies
    classification = $classification
    recommended_path = $recommendedPath
    release_verification = $releaseVerification
    release_verification_exit_code = $releaseVerificationExit
    setup_authenticode = $setupRecord
    portable = $portableRecord
    installed_exe = $(if ($InstalledExe) { [ordered]@{
        path = $InstalledExe
        sha256 = $installedHash
        matches_sealed_release_exe = $installedMatchesSealed
        authenticode = $installedSignature
    }} else { $null })
    security_invariants = @(
        'assessment is read-only',
        'Smart App Control is never disabled or bypassed',
        'detached Russian release signature is not represented as Authenticode execution trust'
    )
}

if ($EvidencePath) {
    $parent = Split-Path -Parent $EvidencePath
    if ($parent) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    $evidence | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
}

$evidence | ConvertTo-Json -Depth 12
