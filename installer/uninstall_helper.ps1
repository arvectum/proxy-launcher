[CmdletBinding()]
param([Parameter(Mandatory)] [string]$InstallRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Test-ExactPath([string]$Candidate, [string]$Expected) { $Candidate -and ([IO.Path]::GetFullPath($Candidate) -ieq [IO.Path]::GetFullPath($Expected)) }
try {
  $exe = Join-Path $InstallRoot 'Arvectum Proxy Launcher.exe'
  if (Test-Path -LiteralPath $exe) {
    # Network rollback must complete before any destructive uninstall work.
    $global:LASTEXITCODE = 0
    & $exe --rollback
    if ($LASTEXITCODE -ne 0) { throw 'Network rollback was not confirmed; uninstall stopped safely.' }
    Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" | Where-Object { Test-ExactPath $_.ExecutablePath $exe } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop }
  }
  exit 0
} catch { Write-Error $_.Exception.Message; exit 1 }
