$ErrorActionPreference = 'Stop'

$root = Split-Path $PSScriptRoot -Parent
$package = Join-Path $root 'release\Arvectum-Proxy-Launcher-Windows-0.2.2-P0.4-client'
$app = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'ArvectumProxyLauncher'
$exe = Join-Path $app 'Arvectum Proxy Launcher.exe'
$state = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$runPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$report = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Arvectum_p04_remaining_safety.json'
$expectedHash = (Get-FileHash (Join-Path $package 'Arvectum Proxy Launcher.exe') -Algorithm SHA256).Hash
$fixtureRoot = Join-Path $env:TEMP ('P04_Arvectum-Proxy-Launcher-Windows-RC2.1-client.zip.stale-' + [guid]::NewGuid().ToString('N'))

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

function Stop-Canonical {
    & $exe --stop
    Start-Sleep -Seconds 4
    $ports = @(8080,1080,8082 | ForEach-Object { Get-NetTCPConnection -State Listen -LocalPort $_ -ErrorAction SilentlyContinue })
    if ($ports.Count -eq 0) { return }
    if ((Test-Path (Join-Path $state 'proxy_internet_backup.json')) -or (Test-Path (Join-Path $state 'proxy_env_backup.json'))) {
        throw 'Canonical proxy did not stop and recovery backups remain.'
    }
    Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.ExecutablePath -and
            [IO.Path]::GetFullPath($_.ExecutablePath) -ieq [IO.Path]::GetFullPath($exe) -and
            $_.CommandLine -match '(?i)(?:^|\s)--start(?:\s|$)'
        } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop }
    Start-Sleep -Seconds 2
    $ports = @(8080,1080,8082 | ForEach-Object { Get-NetTCPConnection -State Listen -LocalPort $_ -ErrorAction SilentlyContinue })
    if ($ports.Count -ne 0) { throw 'Canonical listeners remain after exact owned process cleanup.' }
}

function Run-Installer {
    $env:ARVECTUM_APP_DIR = $app
    $env:ARVECTUM_NONINTERACTIVE = '1'
    try {
        $installerOutput = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $package 'install.ps1') -AppDir $app -SourceDir $package
        return [int]$LASTEXITCODE
    }
    finally {
        Remove-Item Env:\ARVECTUM_APP_DIR,Env:\ARVECTUM_NONINTERACTIVE -ErrorAction SilentlyContinue
    }
}

if (-not (Test-Path $package)) { throw "P0.4 package folder is missing: $package" }
if (-not (Test-Path $exe)) { throw "Active Launcher is missing: $exe" }

$savedRecovery = Read-Run 'ArvectumProxyLauncherRecovery'
$savedAutostart = Read-Run 'ArvectumProxyLauncher'
$proxyResumed = $false

try {
    # Gate 14: exact known Temp ZIP path, but target missing and no process.
    Stop-Canonical
    $missingExe = Join-Path (Join-Path $fixtureRoot 'recovery') 'Arvectum Proxy Launcher.exe'
    $staleRecovery = '"' + $missingExe + '" --start'
    New-ItemProperty -Path $runPath -Name ArvectumProxyLauncherRecovery -Value $staleRecovery -PropertyType String -Force | Out-Null
    $staleExit = Run-Installer
    Start-Sleep -Seconds 2
    $staleAfter = Read-Run 'ArvectumProxyLauncherRecovery'
    $staleHash = (Get-FileHash $exe -Algorithm SHA256).Hash

    # Gate 15: an active unrelated process and same-named Run value must stay untouched.
    Stop-Canonical
    $foreignCommand = 'C:\Windows\System32\cmd.exe /c ping -n 60 127.0.0.1 >nul'
    $foreignProcess = Start-Process -FilePath 'C:\Windows\System32\cmd.exe' -ArgumentList '/c','ping -n 60 127.0.0.1 >nul' -PassThru
    New-ItemProperty -Path $runPath -Name ArvectumProxyLauncherRecovery -Value $foreignCommand -PropertyType String -Force | Out-Null
    $foreignExit = Run-Installer
    $foreignAfter = Read-Run 'ArvectumProxyLauncherRecovery'
    $foreignHash = (Get-FileHash $exe -Algorithm SHA256).Hash

    # Gate 17: current canonical GUI is open; installer may close only its exact path.
    Restore-Run 'ArvectumProxyLauncherRecovery' $savedRecovery
    Stop-Canonical
    $gui = Start-Process -FilePath $exe -PassThru
    Start-Sleep -Seconds 2
    $guiOpen = -not $gui.HasExited
    $guiExit = Run-Installer
    Start-Sleep -Seconds 2
    $guiClosed = $gui.HasExited
    $guiHash = (Get-FileHash $exe -Algorithm SHA256).Hash

    [pscustomobject]@{
        stale_legacy_install_exit_code = $staleExit
        stale_legacy_recovery_removed = -not $staleAfter.exists
        stale_legacy_installed_hash_verified = $staleHash -eq $expectedHash
        foreign_process_active_before_install = -not $foreignProcess.HasExited
        foreign_install_exit_nonzero = $foreignExit -ne 0
        foreign_run_preserved = $foreignAfter.exists -and $foreignAfter.value -eq $foreignCommand
        foreign_process_preserved = -not $foreignProcess.HasExited
        foreign_old_exe_unchanged = $foreignHash -eq $expectedHash
        canonical_gui_open_before_install = $guiOpen
        canonical_gui_install_exit_code = $guiExit
        canonical_gui_closed_by_exact_path = $guiClosed
        canonical_gui_installed_hash_verified = $guiHash -eq $expectedHash
    } | ConvertTo-Json | Set-Content $report -Encoding UTF8
}
finally {
    Remove-Item Env:\ARVECTUM_APP_DIR,Env:\ARVECTUM_NONINTERACTIVE -ErrorAction SilentlyContinue
    Restore-Run 'ArvectumProxyLauncherRecovery' $savedRecovery
    Restore-Run 'ArvectumProxyLauncher' $savedAutostart
    if ((Get-Variable foreignProcess -ErrorAction SilentlyContinue) -and $foreignProcess -and $foreignProcess.ProcessId) { Stop-Process -Id $foreignProcess.ProcessId -Force -ErrorAction SilentlyContinue }
    if (Test-Path $fixtureRoot) { Remove-Item $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue }
    Stop-Canonical
    Start-Process $exe -ArgumentList '--start' -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 8
    $ports = @(8080,1080,8082 | ForEach-Object { Get-NetTCPConnection -State Listen -LocalPort $_ -ErrorAction SilentlyContinue })
    $proxyResumed = $ports.Count -eq 3
    if (Test-Path $report) {
        $result = Get-Content $report -Raw | ConvertFrom-Json
        $result | Add-Member proxy_resumed $proxyResumed -Force
        $result | Add-Member listeners_after_final_restart $ports.Count -Force
        $result | ConvertTo-Json | Set-Content $report -Encoding UTF8
    }
}

Get-Content $report
