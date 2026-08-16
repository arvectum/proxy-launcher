[CmdletBinding()]
param([Parameter(Mandatory)] [string]$InstallRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$StateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$LogPath = Join-Path $StateRoot 'install.log'
$RunPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$TaskName = 'ArvectumProxyLauncher'
$MainRunName = 'ArvectumProxyLauncher'
$RecoveryRunName = 'ArvectumProxyLauncherRecovery'

function Write-MaintenanceLog([string]$Message) {
  try {
    New-Item -ItemType Directory -Force -Path $StateRoot | Out-Null
    Add-Content -LiteralPath $LogPath -Value "$(Get-Date -Format o) $Message" -Encoding utf8
  } catch {}
}

function Test-ExactPath([string]$Candidate, [string]$Expected) {
  if (-not $Candidate -or -not $Expected) { return $false }
  try { return [IO.Path]::GetFullPath($Candidate) -ieq [IO.Path]::GetFullPath($Expected) } catch { return $false }
}

function Get-RecoveryBackups {
  @('proxy_internet_backup.json','proxy_env_backup.json') |
    ForEach-Object { Join-Path $StateRoot $_ } |
    Where-Object { Test-Path -LiteralPath $_ -PathType Leaf }
}

function Test-OwnedStartCommand([string]$Command, [string]$ExpectedExe) {
  if (-not $Command) { return $false }
  if ($Command -notmatch '^\s*"([^"]+)"\s+--start\s*$') { return $false }
  return Test-ExactPath $matches[1] $ExpectedExe
}

function Get-RunValue([string]$Name) {
  try {
    $item = Get-ItemProperty -Path $RunPath -Name $Name -ErrorAction Stop
    return [string]$item.$Name
  } catch [System.Management.Automation.ItemNotFoundException] {
    return $null
  } catch {
    if ($_.FullyQualifiedErrorId -match 'PropertyNotFound') { return $null }
    throw
  }
}

function Remove-OwnedRunValue([string]$Name, [string]$ExpectedExe) {
  $value = Get-RunValue $Name
  if (-not $value) { return }
  if (Test-OwnedStartCommand $value $ExpectedExe) {
    Remove-ItemProperty -Path $RunPath -Name $Name -ErrorAction Stop
    Write-MaintenanceLog "owned Run value removed: $Name"
  } else {
    Write-MaintenanceLog "foreign or unknown Run value preserved: $Name"
  }
}

function Remove-OwnedLegacyTask([string]$ExpectedExe) {
  $schtasks = Join-Path $env:SystemRoot 'System32\schtasks.exe'
  $xmlText = (& $schtasks /Query /TN $TaskName /XML 2>$null | Out-String)
  if ($LASTEXITCODE -ne 0 -or -not $xmlText.Trim()) { return }

  try { [xml]$taskXml = $xmlText } catch {
    Write-MaintenanceLog 'legacy scheduled task XML could not be parsed; task preserved'
    return
  }

  $ns = New-Object System.Xml.XmlNamespaceManager($taskXml.NameTable)
  if ($taskXml.DocumentElement.NamespaceURI) { $ns.AddNamespace('t', $taskXml.DocumentElement.NamespaceURI) }
  $nodes = if ($taskXml.DocumentElement.NamespaceURI) {
    @($taskXml.SelectNodes('//t:Actions/t:Exec', $ns))
  } else {
    @($taskXml.SelectNodes('//Actions/Exec'))
  }

  $owned = $false
  foreach ($node in $nodes) {
    $command = [Environment]::ExpandEnvironmentVariables([string]$node.Command)
    $arguments = ([string]$node.Arguments).Trim()
    if ((Test-ExactPath $command $ExpectedExe) -and $arguments -ieq '--start') {
      $owned = $true
      break
    }
  }
  if (-not $owned) {
    Write-MaintenanceLog 'foreign or unknown legacy scheduled task preserved'
    return
  }

  & $schtasks /Delete /F /TN $TaskName *> $null
  if ($LASTEXITCODE -ne 0) { throw 'owned legacy scheduled task could not be removed' }
  & $schtasks /Query /TN $TaskName *> $null 2>&1
  if ($LASTEXITCODE -eq 0) { throw 'owned legacy scheduled task still exists after deletion' }
  Write-MaintenanceLog 'owned legacy scheduled task removed'
}

function Stop-OwnedProcesses([string]$ExpectedExe) {
  $owned = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.ExecutablePath -and (Test-ExactPath $_.ExecutablePath $ExpectedExe) })
  foreach ($process in $owned) {
    Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
  }
}

function Remove-StalePid {
  $pidPath = Join-Path $StateRoot 'proxy_core.pid'
  if (Test-Path -LiteralPath $pidPath -PathType Leaf) {
    Remove-Item -LiteralPath $pidPath -Force -ErrorAction Stop
    Write-MaintenanceLog 'stale runtime PID removed during uninstall'
  }
}

try {
  Write-MaintenanceLog '=== UNINSTALL SESSION START'
  $exe = Join-Path $InstallRoot 'Arvectum Proxy Launcher.exe'
  $backups = @(Get-RecoveryBackups)

  if ($backups.Count -gt 0) {
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
      throw 'Network rollback cannot be proven because recovery backups exist but the installed Launcher executable is missing.'
    }
    $rollback = Start-Process `
      -FilePath $exe `
      -ArgumentList '--rollback' `
      -PassThru `
      -Wait
    if ($rollback.ExitCode -ne 0) {
      throw "Network rollback was not confirmed; uninstall stopped safely. Exit code: $($rollback.ExitCode)"
    }
    if (@(Get-RecoveryBackups).Count -gt 0) {
      throw 'Network rollback was not confirmed; recovery backups remain and uninstall stopped safely.'
    }
  }

  Stop-OwnedProcesses $exe
  Remove-OwnedRunValue $MainRunName $exe
  Remove-OwnedRunValue $RecoveryRunName $exe
  Remove-OwnedLegacyTask $exe
  Remove-StalePid

  Write-MaintenanceLog '=== UNINSTALL SESSION END: PASS'
  exit 0
} catch {
  Write-MaintenanceLog "UNINSTALL ERROR: $($_.Exception.Message)"
  Write-Error $_.Exception.Message
  exit 1
}
