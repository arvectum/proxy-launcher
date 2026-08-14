[CmdletBinding()]
param([Parameter(Mandatory)] [string]$PayloadRoot, [Parameter(Mandatory)] [string]$InstallRoot, [switch]$PreflightOnly)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$StateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$LogPath = Join-Path $StateRoot 'install.log'
New-Item -ItemType Directory -Force -Path $StateRoot | Out-Null
function Write-InstallLog([string]$Message) { Add-Content -LiteralPath $LogPath -Value "$(Get-Date -Format o) $Message" -Encoding utf8 }
function Get-Sha256([string]$Path) {
  # Use the .NET cryptography API so payload verification is available on every
  # Windows PowerShell host used by Setup.
  $sha256 = [System.Security.Cryptography.SHA256]::Create()
  try {
    $bytes = [IO.File]::ReadAllBytes($Path)
    ([BitConverter]::ToString($sha256.ComputeHash($bytes)) -replace '-', '').ToLowerInvariant()
  } finally {
    $sha256.Dispose()
  }
}
function Test-ExactPath([string]$Candidate, [string]$Expected) { $Candidate -and ([IO.Path]::GetFullPath($Candidate) -ieq [IO.Path]::GetFullPath($Expected)) }
function Stop-OwnedProcess([string]$Exe) {
  Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" | Where-Object { Test-ExactPath $_.ExecutablePath $Exe } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop }
}
function Assert-RecoverySafe {
  $backups = @('proxy_internet_backup.json','proxy_env_backup.json') | ForEach-Object { Join-Path $StateRoot $_ } | Where-Object { Test-Path -LiteralPath $_ }
  if ($backups) { throw 'recovery backups remain after stopping the previous version' }
  # Never remove foreign Run values. A conflicting recovery autostart is not owned.
  $run = Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue
  if ($run -and $run.PSObject.Properties.Name -contains 'ArvectumProxyLauncherRecovery' -and $run.ArvectumProxyLauncherRecovery -notmatch [regex]::Escape($InstallRoot)) { throw 'conflicting recovery autostart is not owned' }
}
function Invoke-PreviousRollback([string]$ExistingExe) {
  if (Test-Path -LiteralPath $ExistingExe) {
    & $ExistingExe --stop
    if ($LASTEXITCODE -ne 0) { throw 'previous version did not complete network rollback' }
    Stop-OwnedProcess $ExistingExe
  }
}
try {
  Write-InstallLog '=== INSTALL SESSION START'
  Write-InstallLog "PayloadRoot: $PayloadRoot"
  Write-InstallLog "InstallRoot: $InstallRoot"
  $manifest = Get-Content -LiteralPath (Join-Path $PayloadRoot 'build_manifest.json') -Raw | ConvertFrom-Json
  $payloadExe = Join-Path $PayloadRoot 'Arvectum Proxy Launcher.exe'
  Write-InstallLog "payload EXE: $payloadExe"
  $embeddedHash = Get-Sha256 $payloadExe
  Write-InstallLog "embedded application expected SHA256: $($manifest.application_sha256)"
  if ($embeddedHash -ne $manifest.application_sha256) { throw 'embedded application SHA256 verification failed' }
  $selfHash = Get-Sha256 (Join-Path $PayloadRoot 'upgrade_helper.ps1')
  if ($selfHash -ne $manifest.upgrade_helper_sha256) { throw 'upgrade helper SHA256 verification failed' }
  $existingExe = Join-Path $InstallRoot 'Arvectum Proxy Launcher.exe'
  Write-InstallLog "final EXE: $existingExe"
  Invoke-PreviousRollback $existingExe
  Assert-RecoverySafe
  if ($PreflightOnly) { Write-InstallLog '=== INSTALL SESSION END: PASS (preflight)'; exit 0 }
  New-Item -ItemType Directory -Force -Path $InstallRoot | Out-Null
  $staged = "$existingExe.new"; $old = "$existingExe.old"
  Copy-Item -LiteralPath $payloadExe -Destination $staged -Force
  if ((Get-Sha256 $staged) -ne $manifest.application_sha256) { throw 'staged application SHA256 verification failed' }
  try {
    if (Test-Path -LiteralPath $existingExe) { Move-Item -LiteralPath $existingExe -Destination $old -Force }
    Move-Item -LiteralPath $staged -Destination $existingExe -Force
    if ((Get-Sha256 $existingExe) -ne $manifest.application_sha256) { throw 'final application SHA256 verification failed' }
    Remove-Item -LiteralPath $old -Force -ErrorAction SilentlyContinue
    Write-InstallLog 'transactional replacement committed'
  } catch {
    if (Test-Path -LiteralPath $old) { Move-Item -LiteralPath $old -Destination $existingExe -Force }
    Write-InstallLog 'transactional replacement rolled back'
    throw
  }
  # Known legacy releaseFolder pattern: arvectum-proxy-launcher-windows. Migration is ownership-gated above.
  $releaseFolder = 'arvectum-proxy-launcher-windows'
  Write-InstallLog '=== INSTALL SESSION END: PASS'
} catch {
  Write-InstallLog "ERROR TYPE: $($_.Exception.GetType().Name)"
  Write-InstallLog "ERROR MESSAGE: $($_.Exception.Message)"
  exit 1
}
