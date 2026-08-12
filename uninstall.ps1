param(
    [string]$AppDir = $PSScriptRoot,
    [switch]$NonInteractive
)

$ErrorActionPreference = 'Stop'
$taskName = 'ArvectumProxyLauncher'
$shortcut = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Arvectum Proxy Launcher.lnk'
$exe = Join-Path $AppDir 'Arvectum Proxy Launcher.exe'
$internetBackup = Join-Path $AppDir 'proxy_internet_backup.json'
$envBackup = Join-Path $AppDir 'proxy_env_backup.json'

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
Write-Host '       Done.'

Write-Host '[3/3] Removing files and shortcut...'
Remove-Item -LiteralPath $shortcut -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $AppDir -Recurse -Force
if (Test-Path -LiteralPath $AppDir) { throw "Could not remove application folder: $AppDir" }
Write-Host '       Done.'
Write-Host ''
Write-Host 'Application removed. Network settings restored.'

if (-not $NonInteractive) {
    Read-Host 'Press Enter to close'
}
