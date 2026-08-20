<#
.SYNOPSIS
    Owner-operated exact signed-set lifecycle acceptance for Windows 0.2.3.
#>
[CmdletBinding()]
param(
    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$EvidencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Signed-set lifecycle acceptance must run on Windows.' }

$ExpectedVersion = '0.2.3'
$ExpectedTag = 'v0.2.3-ru.2'
$ExpectedCommit = '47823585c42da54ab51dc2246583dc24d74d4ba6'
$ExpectedSignerThumbprint = 'EE1CFA955BA22F03C39C76B183D94CD37494582E'
$ExpectedPortableSha256 = '62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801'
$ExpectedSetupSha256 = '5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414'
$PortableName = 'Arvectum-Proxy-Launcher-0.2.3-windows-x64-portable.zip'
$SetupName = 'Arvectum-Proxy-Launcher-0.2.3-windows-x64-setup.exe'
$VerifierName = 'verify_russian_release.ps1'

$ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
if (-not $EvidencePath) { $EvidencePath = $ReleaseDirectory + '.lifecycle-acceptance.json' }
$portable = Join-Path $ReleaseDirectory $PortableName
$setup = Join-Path $ReleaseDirectory $SetupName
$verifier = Join-Path $ReleaseDirectory $VerifierName
$decisionPath = $ReleaseDirectory + '.production-release-gate.json'
foreach ($required in @($portable, $setup, $verifier, $decisionPath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Required production-release file is missing: $required" }
}

function Get-Sha256([string]$Path) {
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Invoke-NativeChecked {
    param([string]$FilePath, [string[]]$ArgumentList = @(), [string]$Label)
    $p = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -PassThru -Wait
    if ($p.ExitCode -ne 0) { throw "$Label failed with exit code $($p.ExitCode)" }
}

function Invoke-ReleaseVerifier([string]$Label) {
    $args = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', ('"' + $verifier + '"'),
        '-ReleaseDirectory', ('"' + $ReleaseDirectory + '"'),
        '-ExpectedSignerThumbprint', $ExpectedSignerThumbprint
    )
    Invoke-NativeChecked -FilePath 'powershell.exe' -ArgumentList $args -Label $Label
}

function Get-RunValue([string]$Name) {
    $runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    $item = Get-ItemProperty -Path $runPath -ErrorAction SilentlyContinue
    if ($null -eq $item) { return $null }
    $property = $item.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    [string]$property.Value
}

function Set-RunValue([string]$Name, [AllowNull()][string]$Value) {
    $runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    New-Item -Path $runPath -Force | Out-Null
    if ($null -eq $Value) {
        Remove-ItemProperty -Path $runPath -Name $Name -ErrorAction SilentlyContinue
    } else {
        New-ItemProperty -Path $runPath -Name $Name -Value $Value -PropertyType String -Force | Out-Null
    }
}

function Assert-NoRegisteredInstall {
    $appKey = '{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}_is1'
    $paths = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$appKey",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$appKey",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\$appKey"
    )
    foreach ($path in $paths) {
        if (Test-Path -LiteralPath $path) {
            throw "A registered Arvectum Proxy Launcher installation already exists: $path. Refusing destructive acceptance over an installed instance."
        }
    }
}

function Assert-NoRunningLauncher {
    $running = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    if ($running.Count -gt 0) {
        $details = @($running | ForEach-Object { "PID=$($_.ProcessId) PATH=$($_.ExecutablePath)" }) -join '; '
        throw "Arvectum Proxy Launcher is currently running. Close it and rerun acceptance. $details"
    }
}

function Invoke-Setup([string]$Path, [string]$Label, [string]$LogRoot) {
    $log = Join-Path $LogRoot ($Label + '.log')
    Invoke-NativeChecked -FilePath $Path -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',("/LOG=$log")) -Label $Label
    $log
}

function Invoke-Status([string]$Exe, [string]$Label) {
    Invoke-NativeChecked -FilePath $Exe -ArgumentList @('--status') -Label $Label
}

function Assert-InstallMode([string]$InstallLog, [string]$Mode) {
    if (-not (Test-Path -LiteralPath $InstallLog -PathType Leaf)) { throw "install.log is missing while checking $Mode" }
    $raw = Get-Content -LiteralPath $InstallLog -Raw
    if ($raw -notmatch [regex]::Escape("PASS ($Mode)")) { throw "install.log does not prove PASS ($Mode)" }
}

function Assert-InstalledMetadata([string]$Exe) {
    if (-not (Test-Path -LiteralPath $Exe -PathType Leaf)) { throw 'Installed executable is missing.' }
    $info = (Get-Item -LiteralPath $Exe).VersionInfo
    if ([string]$info.ProductName -cne 'Arvectum Proxy Launcher') { throw "Installed ProductName mismatch: $($info.ProductName)" }
    if ([string]$info.ProductVersion -cne $ExpectedVersion) { throw "Installed ProductVersion mismatch: $($info.ProductVersion)" }
}

function Invoke-Uninstall([string]$Uninstaller, [string]$Label, [string]$LogRoot) {
    if (-not (Test-Path -LiteralPath $Uninstaller -PathType Leaf)) { throw "${Label}: uninstaller is missing" }
    $log = Join-Path $LogRoot ($Label + '.log')
    Invoke-NativeChecked -FilePath $Uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',("/LOG=$log")) -Label $Label
    $log
}

$decision = Get-Content -LiteralPath $decisionPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ([string]$decision.decision -ne 'PUBLISH') { throw 'Production release gate is not PUBLISH.' }
if ([string]$decision.version -ne $ExpectedVersion) { throw 'Production release version mismatch.' }
if ([string]$decision.git_tag -ne $ExpectedTag) { throw 'Production release tag mismatch.' }
if (([string]$decision.git_commit).ToLowerInvariant() -ne $ExpectedCommit) { throw 'Production release commit mismatch.' }
if (([string]$decision.signer_thumbprint).ToUpperInvariant() -ne $ExpectedSignerThumbprint) { throw 'Production release signer mismatch.' }

$portableHash = Get-Sha256 $portable
$setupHash = Get-Sha256 $setup
if ($portableHash -ne $ExpectedPortableSha256) { throw 'Portable ZIP hash mismatch.' }
if ($setupHash -ne $ExpectedSetupSha256) { throw 'Installer hash mismatch.' }

Write-Host '=== Signed-set lifecycle acceptance preflight ==='
Write-Host "Release: $ExpectedTag"
Write-Host "Commit : $ExpectedCommit"
Write-Host "Setup  : $setupHash"
Invoke-ReleaseVerifier 'preflight signed-set verification'
Assert-NoRegisteredInstall
Assert-NoRunningLauncher

$documents = [Environment]::GetFolderPath('MyDocuments')
$installRoot = Join-Path $documents 'ArvectumProxyLauncher'
$exe = Join-Path $installRoot 'Arvectum Proxy Launcher.exe'
$repair = Join-Path $installRoot 'Arvectum Proxy Launcher Repair.exe'
$uninstaller = Join-Path $installRoot 'unins000.exe'
$stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$installLog = Join-Path $stateRoot 'install.log'
$mainRunName = 'ArvectumProxyLauncher'
$recoveryRunName = 'ArvectumProxyLauncherRecovery'

$sessionId = [guid]::NewGuid().ToString('N')
$workRoot = Join-Path $env:TEMP ("ArvectumSignedSetAcceptance-$sessionId")
$backupRoot = Join-Path $workRoot 'backup'
$logRoot = Join-Path $workRoot 'logs'
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
$installBackup = Join-Path $backupRoot 'install-root'
$stateBackup = Join-Path $backupRoot 'state-root'
$hadInstallRoot = Test-Path -LiteralPath $installRoot
$hadStateRoot = Test-Path -LiteralPath $stateRoot
$oldMainRun = Get-RunValue $mainRunName
$oldRecoveryRun = Get-RunValue $recoveryRunName
$testEnvironmentActive = $true
$cleanupWarnings = @()

$evidence = [ordered]@{
    schema_version = 1
    task = 'APL-REL-014'
    product = 'Arvectum Proxy Launcher'
    version = $ExpectedVersion
    release_tag = $ExpectedTag
    release_commit = $ExpectedCommit
    signer_thumbprint = $ExpectedSignerThumbprint
    portable_sha256 = $portableHash
    installer_sha256 = $setupHash
    production_gate = 'PUBLISH'
    preflight_release_verification = 'PASS'
    phases = [ordered]@{}
    environment_restored = $false
    result = 'BLOCK'
}

try {
    if ($hadInstallRoot) { Move-Item -LiteralPath $installRoot -Destination $installBackup }
    if ($hadStateRoot) { Move-Item -LiteralPath $stateRoot -Destination $stateBackup }
    Set-RunValue $mainRunName $null
    Set-RunValue $recoveryRunName $null

    Write-Host '=== Phase 1: fresh install and smoke ==='
    Invoke-Setup -Path $setup -Label 'fresh-install' -LogRoot $logRoot | Out-Null
    if (-not (Test-Path -LiteralPath $repair -PathType Leaf)) { throw 'Cached repair installer is missing after fresh install.' }
    if ((Get-Sha256 $repair) -ne $ExpectedSetupSha256) { throw 'Cached repair installer does not match the signed production installer.' }
    Assert-InstalledMetadata $exe
    Invoke-Status $exe 'fresh-install status smoke'
    Assert-InstallMode $installLog 'INSTALL'
    $evidence.phases.fresh_install = 'PASS'
    $evidence.phases.status_smoke = 'PASS'

    New-Item -ItemType Directory -Path $stateRoot -Force | Out-Null
    $settings = Join-Path $stateRoot 'proxy_settings.json'
    $noProxy = Join-Path $stateRoot 'no_proxy.txt'
    Set-Content -LiteralPath $settings -Value '{"config_version":1,"acceptance_canary":true}' -Encoding UTF8
    Set-Content -LiteralPath $noProxy -Value 'signed-set-acceptance.invalid' -Encoding UTF8
    $settingsHash = Get-Sha256 $settings
    $noProxyHash = Get-Sha256 $noProxy

    Write-Host '=== Phase 2: same-version repair path ==='
    Invoke-Setup -Path $setup -Label 'same-version-repair' -LogRoot $logRoot | Out-Null
    Assert-InstallMode $installLog 'REPAIR'
    Assert-InstalledMetadata $exe
    Invoke-Status $exe 'same-version repair status smoke'
    if ((Get-Sha256 $settings) -ne $settingsHash) { throw 'Same-version repair modified proxy settings.' }
    if ((Get-Sha256 $noProxy) -ne $noProxyHash) { throw 'Same-version repair modified no-proxy rules.' }
    $evidence.phases.same_version_repair = 'PASS'

    Write-Host '=== Phase 3: corruption recovery through cached repair ==='
    Set-Content -LiteralPath (Join-Path $stateRoot 'proxy_core.pid') -Value '2147483646' -Encoding ASCII
    Set-Content -LiteralPath ($exe + '.new') -Value 'stale-new' -Encoding ASCII
    Set-Content -LiteralPath ($exe + '.old') -Value 'stale-old' -Encoding ASCII
    $ownedStart = '"' + $exe + '" --start'
    Set-RunValue $recoveryRunName $ownedStart
    Set-Content -LiteralPath $exe -Value 'damaged-binary-for-production-lifecycle-acceptance' -Encoding ASCII
    if ((Get-Sha256 $repair) -ne $ExpectedSetupSha256) { throw 'Cached repair installer changed before recovery.' }
    Invoke-Setup -Path $repair -Label 'cached-repair-recovery' -LogRoot $logRoot | Out-Null
    Assert-InstallMode $installLog 'REPAIR'
    Assert-InstalledMetadata $exe
    Invoke-Status $exe 'recovered status smoke'
    if (Test-Path -LiteralPath ($exe + '.new')) { throw 'Recovery left stale .new artifact.' }
    if (Test-Path -LiteralPath ($exe + '.old')) { throw 'Recovery left stale .old artifact.' }
    if (Test-Path -LiteralPath (Join-Path $stateRoot 'proxy_core.pid')) { throw 'Recovery left stale PID file.' }
    if (Get-RunValue $recoveryRunName) { throw 'Recovery left stale owned recovery autostart.' }
    if ((Get-Sha256 $settings) -ne $settingsHash) { throw 'Recovery modified proxy settings.' }
    if ((Get-Sha256 $noProxy) -ne $noProxyHash) { throw 'Recovery modified no-proxy rules.' }
    $evidence.phases.corruption_recovery = 'PASS'

    Write-Host '=== Phase 4: uninstall ownership boundaries ==='
    Set-RunValue $mainRunName $ownedStart
    $foreignRecovery = '"' + $env:SystemRoot + '\System32\cmd.exe" /c echo arvectum-foreign-canary'
    Set-RunValue $recoveryRunName $foreignRecovery
    Invoke-Uninstall -Uninstaller $uninstaller -Label 'final-uninstall' -LogRoot $logRoot | Out-Null
    if (Test-Path -LiteralPath $exe) { throw 'Uninstall left installed executable.' }
    if (Test-Path -LiteralPath $repair) { throw 'Uninstall left cached repair installer.' }
    if (Get-RunValue $mainRunName) { throw 'Uninstall left owned main autostart.' }
    if ((Get-RunValue $recoveryRunName) -ne $foreignRecovery) { throw 'Uninstall modified foreign recovery autostart.' }
    if ((Get-Sha256 $settings) -ne $settingsHash) { throw 'Uninstall modified proxy settings.' }
    if ((Get-Sha256 $noProxy) -ne $noProxyHash) { throw 'Uninstall modified no-proxy rules.' }
    $evidence.phases.uninstall = 'PASS'
    $evidence.phases.user_configuration_preservation = 'PASS'
    $evidence.phases.foreign_autostart_preservation = 'PASS'

    Write-Host '=== Phase 5: post-lifecycle signed-set re-verification ==='
    Invoke-ReleaseVerifier 'post-lifecycle signed-set verification'
    if ((Get-Sha256 $portable) -ne $ExpectedPortableSha256) { throw 'Portable ZIP changed during lifecycle acceptance.' }
    if ((Get-Sha256 $setup) -ne $ExpectedSetupSha256) { throw 'Installer changed during lifecycle acceptance.' }
    $evidence.phases.post_lifecycle_release_verification = 'PASS'
    $evidence.result = 'PASS'
}
finally {
    if ($testEnvironmentActive) {
        try {
            if (Test-Path -LiteralPath $uninstaller -PathType Leaf) {
                $p = Start-Process -FilePath $uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -PassThru -Wait -ErrorAction SilentlyContinue
                if ($p -and $p.ExitCode -ne 0) { $cleanupWarnings += "cleanup uninstaller exit=$($p.ExitCode)" }
            }
        } catch { $cleanupWarnings += "cleanup uninstall: $($_.Exception.Message)" }
        try { Remove-Item -LiteralPath $installRoot -Recurse -Force -ErrorAction SilentlyContinue } catch { $cleanupWarnings += "cleanup install root: $($_.Exception.Message)" }
        try { Remove-Item -LiteralPath $stateRoot -Recurse -Force -ErrorAction SilentlyContinue } catch { $cleanupWarnings += "cleanup state root: $($_.Exception.Message)" }
        try { Set-RunValue $mainRunName $oldMainRun } catch { $cleanupWarnings += "restore main Run: $($_.Exception.Message)" }
        try { Set-RunValue $recoveryRunName $oldRecoveryRun } catch { $cleanupWarnings += "restore recovery Run: $($_.Exception.Message)" }
        try {
            if ($hadInstallRoot -and (Test-Path -LiteralPath $installBackup)) { Move-Item -LiteralPath $installBackup -Destination $installRoot }
        } catch { $cleanupWarnings += "restore install root: $($_.Exception.Message)" }
        try {
            if ($hadStateRoot -and (Test-Path -LiteralPath $stateBackup)) {
                New-Item -ItemType Directory -Path (Split-Path -Parent $stateRoot) -Force | Out-Null
                Move-Item -LiteralPath $stateBackup -Destination $stateRoot
            }
        } catch { $cleanupWarnings += "restore state root: $($_.Exception.Message)" }
    }

    if ($cleanupWarnings.Count -eq 0) {
        $evidence.environment_restored = $true
    } else {
        $evidence.environment_restored = $false
        $evidence.cleanup_warnings = @($cleanupWarnings)
        $evidence.result = 'BLOCK'
    }
    $evidence.generated_utc = [DateTime]::UtcNow.ToString('o')
    $evidence.host = $env:COMPUTERNAME
    $evidenceDir = Split-Path -Parent $EvidencePath
    if ($evidenceDir) { New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null }
    $evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
    Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
}

if ($evidence.result -ne 'PASS' -or -not $evidence.environment_restored) { throw "Signed-set lifecycle acceptance BLOCK. Evidence: $EvidencePath" }
Write-Host ''
Write-Host 'APL-REL-014 Windows signed-set lifecycle acceptance: PASS'
Write-Host "Release tag: $ExpectedTag"
Write-Host "Installer SHA256: $ExpectedSetupSha256"
Write-Host 'Fresh install: PASS'
Write-Host 'Status smoke: PASS'
Write-Host 'Same-version repair: PASS'
Write-Host 'Corruption recovery: PASS'
Write-Host 'Uninstall: PASS'
Write-Host 'User configuration preservation: PASS'
Write-Host 'Foreign autostart preservation: PASS'
Write-Host 'Post-lifecycle signed-set verification: PASS'
Write-Host 'Host environment restored: PASS'
Write-Host "Evidence: $EvidencePath"
