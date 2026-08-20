<#
.SYNOPSIS
    Drift-compatible outer wrapper for APL-REL-014 on the real owner Windows host.
.DESCRIPTION
    Handles one narrowly-defined pre-existing host drift: the governed registered 0.2.3
    installation may be missing the cached repair installer even though the exact sealed
    application, manifest, owner marker and registration are otherwise valid.

    The wrapper verifies the exact signed production release before staging anything,
    stages the sealed setup only as a temporary repair cache, delegates to the unchanged
    runtime-aware owner-host acceptance chain, then removes the staged file so the original
    owner-host state is restored exactly.
#>
[CmdletBinding()]
param(
    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$EvidencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Drift-compatible lifecycle acceptance must run on Windows.' }

$ExpectedVersion = '0.2.3'
$ExpectedApplicationSha256 = 'f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a'
$ExpectedSetupSha256 = '5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414'
$ExpectedSignerThumbprint = 'EE1CFA955BA22F03C39C76B183D94CD37494582E'
$SetupName = 'Arvectum-Proxy-Launcher-0.2.3-windows-x64-setup.exe'
$AppKeyName = '{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}_is1'
$UserUninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$MachineUninstallKey = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$MachineWowUninstallKey = "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$ExpectedOwnerMarker = 'ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER'

$ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
if (-not $EvidencePath) { $EvidencePath = $ReleaseDirectory + '.lifecycle-acceptance.json' }
$setup = Join-Path $ReleaseDirectory $SetupName
$verifier = Join-Path $ReleaseDirectory 'verify_russian_release.ps1'
$runtimeScript = Join-Path $PSScriptRoot 'windows_signed_set_lifecycle_acceptance_runtime.ps1'

foreach ($required in @($setup, $verifier, $runtimeScript)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required drift-wrapper input is missing: $required"
    }
}

$documents = [Environment]::GetFolderPath('MyDocuments')
$installRoot = Join-Path $documents 'ArvectumProxyLauncher'
$exe = Join-Path $installRoot 'Arvectum Proxy Launcher.exe'
$repair = Join-Path $installRoot 'Arvectum Proxy Launcher Repair.exe'
$uninstaller = Join-Path $installRoot 'unins000.exe'
$manifestPath = Join-Path $installRoot 'build_manifest.json'
$ownerMarker = Join-Path $installRoot '.arvectum-install-owner'
$temporaryRepair = $repair + '.apl-rel-014-stage'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-ExactPath([string]$Candidate, [string]$Expected) {
    if (-not $Candidate -or -not $Expected) { return $false }
    try {
        return [IO.Path]::GetFullPath($Candidate).TrimEnd('\') -ieq [IO.Path]::GetFullPath($Expected).TrimEnd('\')
    }
    catch {
        return $false
    }
}

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory = $true)] [string]$FilePath,
        [string[]]$ArgumentList = @(),
        [Parameter(Mandatory = $true)] [string]$Label
    )
    $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -PassThru -Wait
    if ($process.ExitCode -ne 0) {
        throw "$Label failed with exit code $($process.ExitCode)"
    }
}

function Invoke-ReleaseVerifier {
    $args = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', ('"' + $verifier + '"'),
        '-ReleaseDirectory', ('"' + $ReleaseDirectory + '"'),
        '-ExpectedSignerThumbprint', $ExpectedSignerThumbprint
    )
    Invoke-NativeChecked -FilePath 'powershell.exe' -ArgumentList $args -Label 'signed release verification before repair-cache staging'
}

function Invoke-RuntimeAcceptance {
    $args = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', ('"' + $runtimeScript + '"'),
        '-ReleaseDirectory', ('"' + $ReleaseDirectory + '"'),
        '-EvidencePath', ('"' + $EvidencePath + '"')
    )
    Invoke-NativeChecked -FilePath 'powershell.exe' -ArgumentList $args -Label 'runtime-aware owner-host lifecycle acceptance'
}

$registered = @()
foreach ($path in @($UserUninstallKey, $MachineUninstallKey, $MachineWowUninstallKey)) {
    if (Test-Path -LiteralPath $path) { $registered += $path }
}
if ($registered.Count -ne 1 -or $registered[0] -cne $UserUninstallKey) {
    throw "Registered installation is absent, ambiguous or machine-wide. Drift compatibility is not applicable: $($registered -join '; ')"
}

foreach ($required in @($exe, $uninstaller, $manifestPath, $ownerMarker)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Registered installation is incomplete beyond the supported repair-cache drift: $required"
    }
}

if ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256) {
    throw 'Registered installation EXE is not the exact sealed 0.2.3 application.'
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ([string]$manifest.version -ne $ExpectedVersion) {
    throw 'Registered installation manifest version is not 0.2.3.'
}
if (([string]$manifest.application_sha256).ToLowerInvariant() -ne $ExpectedApplicationSha256) {
    throw 'Registered installation manifest does not bind the exact sealed application hash.'
}

$markerValue = (Get-Content -LiteralPath $ownerMarker -Raw -Encoding ASCII).Trim()
if ($markerValue -cne $ExpectedOwnerMarker) {
    throw 'Registered installation owner marker is not governed.'
}

$registration = Get-ItemProperty -LiteralPath $UserUninstallKey
if ([string]$registration.DisplayName -ne 'Arvectum Proxy Launcher') { throw 'Registered DisplayName mismatch.' }
if ([string]$registration.DisplayVersion -ne $ExpectedVersion) { throw 'Registered DisplayVersion mismatch.' }
if ($registration.PSObject.Properties['InstallLocation']) {
    $registeredLocation = [string]$registration.InstallLocation
    if ($registeredLocation -and -not (Test-ExactPath $registeredLocation $installRoot)) {
        throw "Registered InstallLocation mismatch: $registeredLocation"
    }
}

$setupHash = Get-Sha256 $setup
if ($setupHash -ne $ExpectedSetupSha256) {
    throw 'Signed release installer hash mismatch before drift handling.'
}

Write-Host '=== Drift preflight: exact signed release verification ==='
Invoke-ReleaseVerifier

$repairWasMissing = -not (Test-Path -LiteralPath $repair -PathType Leaf)
if (-not $repairWasMissing -and (Get-Sha256 $repair) -ne $ExpectedSetupSha256) {
    throw 'Existing repair cache is present but does not match the exact signed production installer.'
}

$stagePerformed = $false
$runtimePassed = $false
$runtimeError = $null
$restoreError = $null

try {
    if ($repairWasMissing) {
        Write-Host 'Pre-existing repair cache: MISSING'
        Write-Host 'Staging exact signed installer transactionally for acceptance only.'
        Remove-Item -LiteralPath $temporaryRepair -Force -ErrorAction SilentlyContinue
        Copy-Item -LiteralPath $setup -Destination $temporaryRepair -Force
        if ((Get-Sha256 $temporaryRepair) -ne $ExpectedSetupSha256) {
            throw 'Temporary repair-cache staging hash mismatch.'
        }
        Move-Item -LiteralPath $temporaryRepair -Destination $repair
        if ((Get-Sha256 $repair) -ne $ExpectedSetupSha256) {
            throw 'Staged repair cache does not match the exact signed installer.'
        }
        $stagePerformed = $true
    }
    else {
        Write-Host 'Pre-existing repair cache: PRESENT_EXACT'
    }

    Invoke-RuntimeAcceptance
    $runtimePassed = $true
}
catch {
    $runtimeError = $_.Exception.Message
}
finally {
    Remove-Item -LiteralPath $temporaryRepair -Force -ErrorAction SilentlyContinue
    if ($repairWasMissing -and (Test-Path -LiteralPath $repair -PathType Leaf)) {
        try {
            if ((Get-Sha256 $repair) -ne $ExpectedSetupSha256) {
                throw 'Cannot restore original missing repair-cache state because the staged path no longer has the governed hash.'
            }
            Remove-Item -LiteralPath $repair -Force
        }
        catch {
            $restoreError = $_.Exception.Message
        }
    }
}

$repairOriginalStateRestored = $true
if ($repairWasMissing) {
    $repairOriginalStateRestored = -not (Test-Path -LiteralPath $repair)
}
else {
    $repairOriginalStateRestored = (
        (Test-Path -LiteralPath $repair -PathType Leaf) -and
        ((Get-Sha256 $repair) -eq $ExpectedSetupSha256)
    )
}

if (-not $repairOriginalStateRestored -and -not $restoreError) {
    $restoreError = 'Pre-existing repair-cache state was not restored exactly.'
}

if (Test-Path -LiteralPath $EvidencePath -PathType Leaf) {
    try {
        $evidence = Get-Content -LiteralPath $EvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $evidence | Add-Member -NotePropertyName preexisting_repair_installer_state -NotePropertyValue ($(if ($repairWasMissing) { 'MISSING' } else { 'PRESENT_EXACT' })) -Force
        $evidence | Add-Member -NotePropertyName repair_cache_staged_for_acceptance -NotePropertyValue $stagePerformed -Force
        $evidence | Add-Member -NotePropertyName repair_cache_original_state_restored -NotePropertyValue $repairOriginalStateRestored -Force
        if (-not $repairOriginalStateRestored) {
            $evidence.result = 'BLOCK'
            $evidence | Add-Member -NotePropertyName repair_cache_restore_error -NotePropertyValue $restoreError -Force
        }
        $evidence | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
    }
    catch {
        if (-not $restoreError) { $restoreError = "drift evidence update failed: $($_.Exception.Message)" }
    }
}

if ($restoreError) {
    throw "Repair-cache drift restoration BLOCK: $restoreError"
}
if (-not $runtimePassed) {
    throw "Runtime-aware lifecycle acceptance failed after transactional repair-cache staging: $runtimeError"
}

Write-Host ''
Write-Host 'APL-REL-014 repair-cache drift wrapper: PASS'
Write-Host "Pre-existing repair-cache state: $(if ($repairWasMissing) { 'MISSING' } else { 'PRESENT_EXACT' })"
Write-Host "Temporary repair cache staged: $stagePerformed"
Write-Host 'Runtime-aware signed-set lifecycle acceptance: PASS'
Write-Host 'Original repair-cache state restored: PASS'
Write-Host "Evidence: $EvidencePath"
