<#
.SYNOPSIS
    Rescue-guarded entrypoint for APL-REL-014 on the real owner Windows host.
.DESCRIPTION
    Arms an independent rescue snapshot before invoking the generalized legacy
    host compatibility wrapper. If the inner lifecycle fails or restores an
    install tree different from the pre-run fingerprint, this guard restores
    the original install tree, state, registration, Run values, shortcuts and
    runtime shape from the rescue snapshot, then returns BLOCK.
#>
[CmdletBinding()]
param(
    [string]$ReleaseDirectory = 'C:\Arvectum\Releases\0.2.3-russian-production',
    [string]$EvidencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Guarded lifecycle acceptance must run on Windows.' }

$ExpectedApplicationSha256 = 'f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a'
$AppKeyName = '{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}_is1'
$UserUninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$NativeUserUninstallKey = "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppKeyName"
$ReleaseDirectory = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
if (-not $EvidencePath) { $EvidencePath = $ReleaseDirectory + '.lifecycle-acceptance.json' }
$inner = Join-Path $PSScriptRoot 'windows_signed_set_lifecycle_acceptance_legacy_host.ps1'
if (-not (Test-Path -LiteralPath $inner -PathType Leaf)) { throw "Legacy host wrapper is missing: $inner" }

$documents = [Environment]::GetFolderPath('MyDocuments')
$installRoot = Join-Path $documents 'ArvectumProxyLauncher'
$exe = Join-Path $installRoot 'Arvectum Proxy Launcher.exe'
$stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$mainRunName = 'ArvectumProxyLauncher'
$recoveryRunName = 'ArvectumProxyLauncherRecovery'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-TextSha256([string]$Text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Text))
        return (-join ($hash | ForEach-Object { $_.ToString('x2') }))
    }
    finally { $sha.Dispose() }
}

function Get-TreeFingerprint([string]$Root) {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return $null }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    $lines = @(
        Get-ChildItem -LiteralPath $Root -File -Recurse | ForEach-Object {
            $full = [IO.Path]::GetFullPath($_.FullName)
            $relative = $full.Substring($rootFull.Length).TrimStart('\')
            "$relative`t$($_.Length)`t$(Get-Sha256 $_.FullName)"
        } | Sort-Object
    )
    return [pscustomobject]@{ FileCount=$lines.Count; Sha256=(Get-TextSha256 ($lines -join "`n")) }
}

function Same-Fingerprint($A,$B) {
    if ($null -eq $A -or $null -eq $B) { return $false }
    return ($A.FileCount -eq $B.FileCount -and $A.Sha256 -eq $B.Sha256)
}

function Get-RunValue([string]$Name) {
    $item = Get-ItemProperty -Path $runPath -ErrorAction SilentlyContinue
    if ($null -eq $item) { return $null }
    $property = $item.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return [string]$property.Value
}

function Set-RunValue([string]$Name,[AllowNull()][string]$Value) {
    New-Item -Path $runPath -Force | Out-Null
    if ($null -eq $Value) { Remove-ItemProperty -Path $runPath -Name $Name -ErrorAction SilentlyContinue }
    else { New-ItemProperty -Path $runPath -Name $Name -Value $Value -PropertyType String -Force | Out-Null }
}

function Stop-ExactPathProcesses([string]$ExpectedExe) {
    $running = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    foreach ($process in $running) {
        if (-not [string]$process.ExecutablePath) { continue }
        try {
            $actual = [IO.Path]::GetFullPath([string]$process.ExecutablePath)
            $expected = [IO.Path]::GetFullPath($ExpectedExe)
            if ($actual -ieq $expected) { Stop-Process -Id ([int]$process.ProcessId) -Force -ErrorAction SilentlyContinue }
        }
        catch {}
    }
    Start-Sleep -Milliseconds 500
}

function Get-RuntimeShape([string]$ExpectedExe) {
    $core = $false
    $gui = $false
    $running = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue)
    foreach ($process in $running) {
        if (-not [string]$process.ExecutablePath) { continue }
        try {
            if ([IO.Path]::GetFullPath([string]$process.ExecutablePath) -ine [IO.Path]::GetFullPath($ExpectedExe)) { continue }
            $cmd = [string]$process.CommandLine
            if ($cmd -match '(?i)(^|\s)--start(\s|$)') { $core = $true }
            elseif ($cmd -notmatch '(?i)(^|\s)--(stop|status|rollback|doctor|doctor-json)(\s|$)') { $gui = $true }
        }
        catch {}
    }
    return [pscustomobject]@{ Core=$core; Gui=$gui; Running=($core -or $gui) }
}

function Restore-RuntimeShape($Shape) {
    if (-not $Shape.Running) { return }
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'Rescue runtime restore EXE is missing.' }
    if ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256) { throw 'Rescue runtime restore EXE hash mismatch.' }
    if ($Shape.Core) { Start-Process -FilePath $exe -ArgumentList @('--start') -WorkingDirectory $installRoot | Out-Null; Start-Sleep -Seconds 2 }
    if ($Shape.Gui) { Start-Process -FilePath $exe -WorkingDirectory $installRoot | Out-Null; Start-Sleep -Seconds 2 }
}

if (-not (Test-Path -LiteralPath $UserUninstallKey)) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $inner -ReleaseDirectory $ReleaseDirectory -EvidencePath $EvidencePath
    exit $LASTEXITCODE
}
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'Registered owner-host EXE is missing before rescue arming.' }
if ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256) { throw 'Registered owner-host EXE is not exact before rescue arming.' }

$registration = Get-ItemProperty -LiteralPath $UserUninstallKey
if ([string]$registration.DisplayName -ne 'Arvectum Proxy Launcher') { throw 'DisplayName mismatch before rescue arming.' }
if ([string]$registration.DisplayVersion -ne '0.2.3') { throw 'DisplayVersion mismatch before rescue arming.' }

$treeBefore = Get-TreeFingerprint $installRoot
$runtimeBefore = Get-RuntimeShape $exe
$oldMainRun = Get-RunValue $mainRunName
$oldRecoveryRun = Get-RunValue $recoveryRunName
$hadState = Test-Path -LiteralPath $stateRoot -PathType Container

$sessionId = [guid]::NewGuid().ToString('N')
$rescueRoot = Join-Path $env:TEMP ("ArvectumAplRel014Rescue-$sessionId")
$rescueInstall = Join-Path $rescueRoot 'install-root'
$rescueState = Join-Path $rescueRoot 'state-root'
$rescueRegistry = Join-Path $rescueRoot 'uninstall-registration.reg'
$rescueShortcuts = Join-Path $rescueRoot 'shortcuts'
New-Item -ItemType Directory -Path $rescueRoot -Force | Out-Null
New-Item -ItemType Directory -Path $rescueShortcuts -Force | Out-Null

Copy-Item -LiteralPath $installRoot -Destination $rescueInstall -Recurse -Force
$rescueTree = Get-TreeFingerprint $rescueInstall
if (-not (Same-Fingerprint $treeBefore $rescueTree)) { throw 'Independent rescue install snapshot fingerprint mismatch.' }
if ($hadState) { Copy-Item -LiteralPath $stateRoot -Destination $rescueState -Recurse -Force }
& reg.exe export $NativeUserUninstallKey $rescueRegistry /y | Out-Null
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $rescueRegistry -PathType Leaf)) { throw 'Independent rescue registry export failed.' }

$shortcutPaths = @(
    (Join-Path ([Environment]::GetFolderPath('Programs')) 'Arvectum Proxy Launcher.lnk'),
    (Join-Path ([Environment]::GetFolderPath('Programs')) 'Repair Arvectum Proxy Launcher.lnk'),
    (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Arvectum Proxy Launcher.lnk')
)
$shortcutSnapshots = @()
$i = 0
foreach ($shortcut in $shortcutPaths) {
    if (Test-Path -LiteralPath $shortcut -PathType Leaf) {
        $backup = Join-Path $rescueShortcuts ("shortcut-$i.lnk")
        Copy-Item -LiteralPath $shortcut -Destination $backup -Force
        $shortcutSnapshots += [pscustomobject]@{ Original=$shortcut; Backup=$backup }
        $i += 1
    }
}

Write-Host 'Independent owner-host rescue snapshot: ARMED'
Write-Host "Pre-run install tree SHA256: $($treeBefore.Sha256)"

$innerPassed = $false
$innerError = $null
$rescueUsed = $false
$rescueWarnings = @()
try {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $inner -ReleaseDirectory $ReleaseDirectory -EvidencePath $EvidencePath
    if ($LASTEXITCODE -ne 0) { throw "Inner host compatibility wrapper exit=$LASTEXITCODE" }
    $after = Get-TreeFingerprint $installRoot
    if (-not (Same-Fingerprint $treeBefore $after)) { throw 'Inner wrapper returned success but owner-host install tree fingerprint changed.' }
    $innerPassed = $true
}
catch {
    $innerError = $_.Exception.Message
}
finally {
    if (-not $innerPassed) {
        $rescueUsed = $true
        Stop-ExactPathProcesses $exe
        try { Remove-Item -LiteralPath $installRoot -Recurse -Force -ErrorAction SilentlyContinue } catch { $rescueWarnings += "remove current install: $($_.Exception.Message)" }
        try { Copy-Item -LiteralPath $rescueInstall -Destination $installRoot -Recurse -Force } catch { $rescueWarnings += "restore rescue install: $($_.Exception.Message)" }

        if ($hadState) {
            try { Remove-Item -LiteralPath $stateRoot -Recurse -Force -ErrorAction SilentlyContinue } catch { $rescueWarnings += "remove current state: $($_.Exception.Message)" }
            try { Copy-Item -LiteralPath $rescueState -Destination $stateRoot -Recurse -Force } catch { $rescueWarnings += "restore rescue state: $($_.Exception.Message)" }
        }

        try { Remove-Item -LiteralPath $UserUninstallKey -Recurse -Force -ErrorAction SilentlyContinue } catch { $rescueWarnings += "remove current registration: $($_.Exception.Message)" }
        try { & reg.exe import $rescueRegistry | Out-Null; if ($LASTEXITCODE -ne 0) { throw "reg import exit=$LASTEXITCODE" } } catch { $rescueWarnings += "restore rescue registration: $($_.Exception.Message)" }
        try { Set-RunValue $mainRunName $oldMainRun; Set-RunValue $recoveryRunName $oldRecoveryRun } catch { $rescueWarnings += "restore Run values: $($_.Exception.Message)" }
        foreach ($shortcut in $shortcutPaths) { Remove-Item -LiteralPath $shortcut -Force -ErrorAction SilentlyContinue }
        foreach ($snapshot in $shortcutSnapshots) {
            try { New-Item -ItemType Directory -Path (Split-Path -Parent $snapshot.Original) -Force | Out-Null; Copy-Item -LiteralPath $snapshot.Backup -Destination $snapshot.Original -Force } catch { $rescueWarnings += "restore shortcut: $($_.Exception.Message)" }
        }

        try {
            $restored = Get-TreeFingerprint $installRoot
            if (-not (Same-Fingerprint $treeBefore $restored)) { throw 'rescue install tree fingerprint mismatch' }
        }
        catch { $rescueWarnings += $_.Exception.Message }

        if ($rescueWarnings.Count -eq 0) {
            try { Restore-RuntimeShape $runtimeBefore } catch { $rescueWarnings += "restore runtime shape: $($_.Exception.Message)" }
        }
    }
}

if (Test-Path -LiteralPath $EvidencePath -PathType Leaf) {
    try {
        $evidence = Get-Content -LiteralPath $EvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $evidence | Add-Member -NotePropertyName owner_host_rescue_armed -NotePropertyValue $true -Force
        $evidence | Add-Member -NotePropertyName owner_host_rescue_used -NotePropertyValue $rescueUsed -Force
        $evidence | Add-Member -NotePropertyName owner_host_rescue_install_tree_sha256 -NotePropertyValue $treeBefore.Sha256 -Force
        $evidence | Add-Member -NotePropertyName owner_host_rescue_restored -NotePropertyValue ($rescueWarnings.Count -eq 0) -Force
        if ($rescueWarnings.Count -gt 0) { $evidence.result = 'BLOCK'; $evidence | Add-Member -NotePropertyName owner_host_rescue_warnings -NotePropertyValue @($rescueWarnings) -Force }
        $evidence | ConvertTo-Json -Depth 18 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
    }
    catch { $rescueWarnings += "rescue evidence update: $($_.Exception.Message)" }
}

Remove-Item -LiteralPath $rescueRoot -Recurse -Force -ErrorAction SilentlyContinue

if ($rescueWarnings.Count -gt 0) { throw "APL-REL-014 rescue restoration BLOCK: $($rescueWarnings -join '; ')" }
if (-not $innerPassed) { throw "APL-REL-014 inner acceptance BLOCK; owner host restored from independent rescue: $innerError" }

Write-Host ''
Write-Host 'APL-REL-014 independent owner-host rescue guard: PASS'
Write-Host 'Owner-host rescue snapshot: ARMED'
Write-Host 'Inner generalized compatibility acceptance: PASS'
Write-Host 'Pre-run install tree fingerprint preserved: PASS'
Write-Host 'Independent rescue used: False'
Write-Host "Evidence: $EvidencePath"
