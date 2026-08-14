$ErrorActionPreference = 'Stop'

$root = Split-Path $PSScriptRoot -Parent
$package = Join-Path $root 'release\Arvectum-Proxy-Launcher-Windows-0.2.2-P0.4-client'
$app = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'ArvectumProxyLauncher'
$exe = Join-Path $app 'Arvectum Proxy Launcher.exe'
$state = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$report = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Arvectum_p04_active_legacy_recovery.json'
$fixtureRoot = Join-Path $env:TEMP ('P04_Arvectum-Proxy-Launcher-Windows-RC2-client.zip.fixture-' + [guid]::NewGuid().ToString('N'))
$legacyDir = Join-Path $fixtureRoot 'recovery'
$legacyExe = Join-Path $legacyDir 'Arvectum Proxy Launcher.exe'
$legacyUserDir = Join-Path $fixtureRoot 'autostart'
$legacyUserExe = Join-Path $legacyUserDir 'Arvectum Proxy Launcher.exe'
$expectedHash = (Get-FileHash (Join-Path $package 'Arvectum Proxy Launcher.exe') -Algorithm SHA256).Hash
$proxyResumed = $false

function Read-Run([string]$name) {
    $item = Get-ItemProperty -Path $runPath -Name $name -ErrorAction SilentlyContinue
    $property = if ($item) { $item.PSObject.Properties[$name] } else { $null }
    [pscustomobject]@{ exists = [bool]$property; value = if ($property) { [string]$property.Value } else { $null } }
}

function Restore-Run([string]$name, $saved) {
    if ($saved.exists) {
        New-ItemProperty -Path $runPath -Name $name -Value $saved.value -PropertyType String -Force | Out-Null
    } else {
        Remove-ItemProperty -Path $runPath -Name $name -ErrorAction SilentlyContinue
    }
}

function Read-Reg($path, $name) {
    $item = Get-ItemProperty -LiteralPath $path -ErrorAction SilentlyContinue
    $property = if ($item) { $item.PSObject.Properties[$name] } else { $null }
    [pscustomobject]@{ exists = [bool]$property; value = if ($property) { [string]$property.Value } else { $null } }
}

function Same($actual, $expected) {
    if ([bool]$actual.exists -ne [bool]$expected.exists) { return $false }
    if (-not [bool]$expected.exists) { return $true }
    return [string]$actual.value -eq [string]$expected.value
}

function Stop-ExactStartProcesses([string]$path) {
    $processes = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue | Where-Object {
        $_.ExecutablePath -and
        [IO.Path]::GetFullPath($_.ExecutablePath) -ieq [IO.Path]::GetFullPath($path) -and
        $_.CommandLine -match '(?i)(?:^|\s)--start(?:\s|$)'
    })
    foreach ($process in $processes) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
    }
    return $processes.Count
}

function Stop-CanonicalProxyForFixture {
    & $exe --stop
    Start-Sleep -Seconds 4
    $ports = @(8080,1080,8082 | ForEach-Object { Get-NetTCPConnection -State Listen -LocalPort $_ -ErrorAction SilentlyContinue })
    if ($ports.Count -eq 0) { return }
    if ((Test-Path (Join-Path $state 'proxy_internet_backup.json')) -or (Test-Path (Join-Path $state 'proxy_env_backup.json'))) {
        throw 'Canonical proxy did not stop and recovery backups remain; fixture is unsafe to run.'
    }
    Stop-ExactStartProcesses $exe | Out-Null
    Start-Sleep -Seconds 2
    $ports = @(8080,1080,8082 | ForEach-Object { Get-NetTCPConnection -State Listen -LocalPort $_ -ErrorAction SilentlyContinue })
    if ($ports.Count -ne 0) { throw 'Canonical proxy listeners remain after exact owned process cleanup.' }
}

if (-not (Test-Path $package)) { throw "P0.4 package folder is missing: $package" }
if (-not (Test-Path $exe)) { throw "Active Launcher is missing: $exe" }

$savedRecovery = Read-Run 'ArvectumProxyLauncherRecovery'
$savedAutostart = Read-Run 'ArvectumProxyLauncher'

try {
    Stop-CanonicalProxyForFixture
    if ((Test-Path (Join-Path $state 'proxy_internet_backup.json')) -or (Test-Path (Join-Path $state 'proxy_env_backup.json'))) {
        throw 'Canonical recovery backups remain after stop; fixture is unsafe to run.'
    }

    New-Item -ItemType Directory -Path $legacyDir,$legacyUserDir -Force | Out-Null
    $eventName = 'ArvectumP04LegacyStop_' + [guid]::NewGuid().ToString('N')
    $source = @"
using System;
using System.Threading;
class Program {
  static int Main(string[] args) {
    using (var signal = new EventWaitHandle(false, EventResetMode.AutoReset, "$eventName")) {
      if (args.Length == 1 && args[0] == "--stop") { signal.Set(); return 0; }
      if (args.Length == 1 && args[0] == "--start") { signal.WaitOne(60000); return 0; }
      return 2;
    }
  }
}
"@
    $cs = Join-Path $fixtureRoot 'legacy_fixture.cs'
    Set-Content -LiteralPath $cs -Value $source -Encoding UTF8
    & 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe' /nologo /target:exe /out:$legacyExe $cs
    if ($LASTEXITCODE -ne 0) { throw 'Unable to compile isolated legacy fixture.' }
    Copy-Item $legacyExe $legacyUserExe -Force

    $legacyRecovery = '"' + $legacyExe + '" --start'
    $legacyUserAutostart = '"' + $legacyUserExe + '" --start'
    New-ItemProperty -Path $runPath -Name ArvectumProxyLauncherRecovery -Value $legacyRecovery -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $runPath -Name ArvectumProxyLauncher -Value $legacyUserAutostart -PropertyType String -Force | Out-Null

    $legacyProcess = Start-Process -FilePath $legacyExe -ArgumentList '--start' -PassThru
    Start-Sleep -Seconds 2
    $legacyActiveBeforeInstall = -not $legacyProcess.HasExited
    if (-not $legacyActiveBeforeInstall) { throw 'Legacy fixture did not remain active.' }

    $env:ARVECTUM_APP_DIR = $app
    $env:ARVECTUM_NONINTERACTIVE = '1'
    $installerOutput = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $package 'install.ps1') -AppDir $app -SourceDir $package
    $installExit = [int]$LASTEXITCODE
    Remove-Item Env:\ARVECTUM_APP_DIR,Env:\ARVECTUM_NONINTERACTIVE -ErrorAction SilentlyContinue

    Start-Sleep -Seconds 3
    $recoveryAfter = Read-Run 'ArvectumProxyLauncherRecovery'
    $autostartAfter = Read-Run 'ArvectumProxyLauncher'
    $legacyStillActive = -not $legacyProcess.HasExited
    $log = if (Test-Path (Join-Path $state 'install.log')) { Get-Content (Join-Path $state 'install.log') -Raw } else { '' }

    Start-Process $exe -ArgumentList '--start'
    Start-Sleep -Seconds 16
    $ports = @(8080,1080,8082 | ForEach-Object { Get-NetTCPConnection -State Listen -LocalPort $_ -ErrorAction SilentlyContinue })
    if ($ports.Count -ne 3) { throw 'Canonical proxy did not start all three listeners after P0.4 installation.' }
    if (-not (Test-Path (Join-Path $state 'proxy_internet_backup.json')) -or -not (Test-Path (Join-Path $state 'proxy_env_backup.json'))) {
        throw 'Canonical proxy started without expected recovery backups.'
    }
    $backup = Get-Content (Join-Path $state 'proxy_internet_backup.json') -Raw | ConvertFrom-Json
    $envBackup = Get-Content (Join-Path $state 'proxy_env_backup.json') -Raw | ConvertFrom-Json
    & $exe --stop
    Start-Sleep -Seconds 4
    $internet = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
    $environment = 'HKCU:\Environment'
    $rollback = @{}
    foreach ($name in 'AutoConfigURL','ProxyEnable','ProxyServer','ProxyOverride','AutoDetect') { $rollback[$name] = Same (Read-Reg $internet $name) $backup.$name }
    $envRollback = @{}
    foreach ($name in 'HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY') { $envRollback[$name] = Same (Read-Reg $environment $name) $envBackup.$name }

    [pscustomobject]@{
        install_exit_code = $installExit
        legacy_recovery_active_before_install = $legacyActiveBeforeInstall
        legacy_process_exited = -not $legacyStillActive
        recovery_run_removed = -not $recoveryAfter.exists
        user_autostart_migrated = $autostartAfter.value -eq ('"' + $exe + '" --start')
        installed_hash_verified = (Get-FileHash $exe -Algorithm SHA256).Hash -eq $expectedHash
        install_log_classification = $log -match 'legacy recovery Run classification: LEGACY_ARVECTUM'
        install_log_graceful_stop = $log -match 'legacy recovery --stop result'
        install_log_process_exit = $log -match 'legacy recovery process exited'
        listener_count_after_16_seconds = $ports.Count
        exact_wininet_rollback = $rollback
        exact_environment_rollback = $envRollback
    } | ConvertTo-Json -Depth 5 | Set-Content $report -Encoding UTF8
}
finally {
    Remove-Item Env:\ARVECTUM_APP_DIR,Env:\ARVECTUM_NONINTERACTIVE -ErrorAction SilentlyContinue
    Restore-Run 'ArvectumProxyLauncherRecovery' $savedRecovery
    Restore-Run 'ArvectumProxyLauncher' $savedAutostart
    if (Test-Path $fixtureRoot) { Remove-Item $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue }
    Stop-CanonicalProxyForFixture
    Start-Process $exe -ArgumentList '--start' -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 8
    $ports = @(8080,1080,8082 | ForEach-Object { Get-NetTCPConnection -State Listen -LocalPort $_ -ErrorAction SilentlyContinue })
    $proxyResumed = $ports.Count -eq 3
    if (Test-Path $report) {
        $result = Get-Content $report -Raw | ConvertFrom-Json
        $result | Add-Member proxy_resumed $proxyResumed -Force
        $result | Add-Member listeners_after_final_restart $ports.Count -Force
        $result | ConvertTo-Json -Depth 5 | Set-Content $report -Encoding UTF8
    }
}

Get-Content $report
