param(
    [string]$AppDir = $PSScriptRoot,
    [switch]$NonInteractive,
    [switch]$Install,
    [string]$SourceDir = $PSScriptRoot
)

$ErrorActionPreference = 'Stop'
$taskName = 'ArvectumProxyLauncher'
$shortcut = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Arvectum Proxy Launcher.lnk'
$startMenuShortcut = Join-Path ([Environment]::GetFolderPath('Programs')) 'Arvectum Proxy Launcher.lnk'
$arpKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\ArvectumProxyLauncher'
$exe = Join-Path $AppDir 'Arvectum Proxy Launcher.exe'
$stateDir = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$internetBackup = Join-Path $stateDir 'proxy_internet_backup.json'
$envBackup = Join-Path $stateDir 'proxy_env_backup.json'
$ownerMarker = Join-Path $AppDir '.arvectum-install-owner'
$ownerMarkerValue = 'ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER'
$legacyOwnerMarkerValue = 'ARVECTUM_PROXY_LAUNCHER_WINDOWS_RC2_1'

if ($Install) {
    $sourceDirFull = [System.IO.Path]::GetFullPath($SourceDir)
    $sourceExe = Join-Path $sourceDirFull 'Arvectum Proxy Launcher.exe'
    $exeForInstall = Join-Path $AppDir 'Arvectum Proxy Launcher.exe'
    if (-not (Test-Path -LiteralPath $sourceExe -PathType Leaf)) {
        throw "Installer failed: release executable is missing: '$sourceExe'."
    }
    if (Test-Path -LiteralPath $exeForInstall -PathType Leaf) {
        & $exeForInstall --stop
        if ($LASTEXITCODE -ne 0) {
            throw 'Installer failed: previous version could not safely stop and roll back network settings.'
        }
    }
    if ((Test-Path -LiteralPath $internetBackup) -or (Test-Path -LiteralPath $envBackup)) {
        throw 'Installer failed: recovery backups remain after stopping the previous version.'
    }
    New-Item -ItemType Directory -Path $AppDir -Force | Out-Null
    foreach ($name in @('Arvectum Proxy Launcher.exe', 'install.bat', 'uninstall.bat', 'uninstall.ps1', 'restore_network.bat', 'INSTALL.txt', 'THIRD_PARTY_NOTICES.txt', 'RELEASE_NOTES_0.2.1.md')) {
        $sourceFile = Join-Path $sourceDirFull $name
        if (-not (Test-Path -LiteralPath $sourceFile -PathType Leaf)) {
            throw "Installer failed: required release file is missing: '$name'."
        }
        Copy-Item -LiteralPath $sourceFile -Destination (Join-Path $AppDir $name) -Force
    }
    $shortcut = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Arvectum Proxy Launcher.lnk'
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut($shortcut)
    $lnk.TargetPath = $exeForInstall
    $lnk.WorkingDirectory = $AppDir
    $lnk.IconLocation = "$exeForInstall,0"
    $lnk.Save()
    if (-not (Test-Path -LiteralPath $shortcut -PathType Leaf)) {
        throw "Installer finalization failed: desktop shortcut was not created: '$shortcut'."
    }
    Set-Content -LiteralPath $ownerMarker -Value $ownerMarkerValue -Encoding Ascii -NoNewline
    if (-not (Test-Path -LiteralPath $ownerMarker -PathType Leaf)) {
        throw 'Installer finalization failed: ownership marker was not created.'
    }
    Start-Process -FilePath $exeForInstall
    exit 0
}

# Destructive removal is allowed only for a directory that is clearly owned by
# Arvectum Proxy Launcher.  AppDir can be overridden for QA, so never trust the
# argument/environment variable by itself before Remove-Item -Recurse.
$fullAppDir = [System.IO.Path]::GetFullPath($AppDir).TrimEnd('\')
$protectedPaths = @(
    [System.IO.Path]::GetFullPath($env:USERPROFILE).TrimEnd('\'),
    [System.IO.Path]::GetFullPath([Environment]::GetFolderPath('MyDocuments')).TrimEnd('\')
)
if ([System.IO.Path]::GetFileName($fullAppDir) -ne 'ArvectumProxyLauncher') {
    throw "Refusing uninstall: unexpected application directory '$fullAppDir'."
}
if ($protectedPaths -contains $fullAppDir) {
    throw "Refusing uninstall: protected directory '$fullAppDir'."
}
if (-not (Test-Path -LiteralPath $fullAppDir -PathType Container)) {
    throw "Application directory does not exist: '$fullAppDir'."
}
$appDirItem = Get-Item -LiteralPath $fullAppDir -Force
if (($appDirItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'Refusing uninstall from a reparse-point application directory.'
}
if (-not (Test-Path -LiteralPath $ownerMarker -PathType Leaf)) {
    throw 'Refusing uninstall: Arvectum ownership marker is missing.'
}
$markerValue = (Get-Content -LiteralPath $ownerMarker -Raw).Trim()
if ($markerValue -notin @($ownerMarkerValue, $legacyOwnerMarkerValue)) {
    throw 'Refusing uninstall: Arvectum ownership marker is invalid.'
}

Write-Host '============================================'
Write-Host '  Arvectum Proxy Launcher - uninstall'
Write-Host '============================================'
Write-Host ''

Write-Host '[1/3] Restoring network settings...'
# A clean installation that was never started owns no network backup.  Its
# uninstaller must be a no-op for network settings; invoking --rollback from
# this unrelated copy could otherwise interfere with another Launcher folder.
if ((Test-Path -LiteralPath $internetBackup) -or (Test-Path -LiteralPath $envBackup)) {
    if (-not (Test-Path -LiteralPath $exe)) {
        throw 'Recovery files exist but the application executable is missing.'
    }
    & $exe --rollback
    if ($LASTEXITCODE -ne 0) { throw 'Network restore is incomplete.' }
}

if ((Test-Path -LiteralPath $internetBackup) -or (Test-Path -LiteralPath $envBackup)) {
    throw 'Network restore is incomplete: recovery files were kept for retry.'
}
Write-Host '       Done.'

Write-Host '[2/3] Removing autostart...'
$taskXml = cmd /c "schtasks /Query /TN $taskName /XML 2>nul"
if ($LASTEXITCODE -eq 0 -and $taskXml -match [regex]::Escape($exe)) {
    schtasks /Delete /F /TN $taskName *> $null
}
$runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$runValue = (Get-ItemProperty -Path $runPath -Name 'ArvectumProxyLauncherRecovery' -ErrorAction SilentlyContinue).ArvectumProxyLauncherRecovery
if ($runValue -and $runValue -match [regex]::Escape($exe)) {
    Remove-ItemProperty -Path $runPath -Name 'ArvectumProxyLauncherRecovery' -ErrorAction SilentlyContinue
}
$userAutostart = (Get-ItemProperty -Path $runPath -Name 'ArvectumProxyLauncher' -ErrorAction SilentlyContinue).ArvectumProxyLauncher
if ($userAutostart -and $userAutostart -match [regex]::Escape($exe)) {
    Remove-ItemProperty -Path $runPath -Name 'ArvectumProxyLauncher' -ErrorAction SilentlyContinue
}
Write-Host '       Done.'

Write-Host '[3/3] Removing files and shortcut...'
# The GUI and headless engine share the same one-file executable.  After a
# successful rollback, close only processes whose resolved executable path is
# exactly this owned installation; never kill a same-named foreign copy.
$ownedProcesses = Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue |
    Where-Object {
        $_.ExecutablePath -and
        [System.IO.Path]::GetFullPath($_.ExecutablePath) -ieq $exe
    }
foreach ($process in $ownedProcesses) {
    Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
}
if ($ownedProcesses) {
    Start-Sleep -Milliseconds 500
}
Remove-Item -LiteralPath $shortcut -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $startMenuShortcut -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $arpKey -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $fullAppDir -Recurse -Force
if (Test-Path -LiteralPath $fullAppDir) { throw "Could not remove application folder: $fullAppDir" }
Write-Host '       Done.'
Write-Host ''
Write-Host 'Application removed. Network settings restored.'

if (-not $NonInteractive) {
    Read-Host 'Press Enter to close'
}
