param(
    [string]$AppDir,
    [string]$SourceDir
)

$ErrorActionPreference = 'Stop'
$stateDir = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$installLog = Join-Path $stateDir 'install.log'

try {
    & (Join-Path $SourceDir 'uninstall.ps1') -Install -AppDir $AppDir -SourceDir $SourceDir -NonInteractive
    exit 0
}
catch {
    Write-Host ''
    Write-Host 'Installation did not complete.' -ForegroundColor Red
    Write-Host 'Reason:'
    Write-Host $_.Exception.Message
    Write-Host 'Network settings were not removed. The previous Launcher version was preserved.'
    Write-Host 'Please provide this file:'
    Write-Host $installLog
    exit 1
}
