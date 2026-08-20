<#
.SYNOPSIS
    Supported owner/developer source-mode profile for APL-WIN-014.
.DESCRIPTION
    Keeps the owner workstation operational without disabling Smart App Control.
    This is NOT a customer production distribution format. It runs the repository
    source under an already trusted controlled Python runtime, creates a recoverable
    desktop shortcut, and optionally restores the existing source-mode autostart intent.

    No Windows application-control policy or Smart App Control registry value is changed.
#>
[CmdletBinding()]
param(
    [ValidateSet('Enable','Status')]
    [string]$Action = 'Status',

    [string]$RepoPath = 'C:\Opencode projects\proxy-launcher',
    [string]$PythonPath = 'C:\P0_2_RECOVERY\Python312\python.exe',
    [switch]$EnableAutostart,
    [string]$EvidencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') { throw 'Owner source mode is Windows-only.' }

$RepoPath = (Resolve-Path -LiteralPath $RepoPath).Path
$PythonPath = (Resolve-Path -LiteralPath $PythonPath).Path
$pythonw = Join-Path (Split-Path -Parent $PythonPath) 'pythonw.exe'
if (-not (Test-Path -LiteralPath $pythonw -PathType Leaf)) { $pythonw = $PythonPath }

$coreScript = Join-Path $RepoPath 'proxy_core.py'
$guiScript = Join-Path $RepoPath 'proxy_gui.py'
foreach ($required in @($coreScript, $guiScript)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Required source file is missing: $required" }
}

$versionRaw = & $PythonPath -c 'import proxy_core; print(proxy_core.APP_VERSION)' 2>&1
if ($LASTEXITCODE -ne 0) { throw "Controlled Python cannot import Arvectum source: $($versionRaw -join ' | ')" }
$version = [string]$versionRaw[-1]
if ($version.Trim() -ne '0.2.3') { throw "Unexpected source runtime version: $version" }

$pythonHash = (Get-FileHash -LiteralPath $PythonPath -Algorithm SHA256).Hash.ToLowerInvariant()
$repoHead = $null
$repoClean = $null
if (Get-Command git.exe -ErrorAction SilentlyContinue) {
    $oldLocation = Get-Location
    try {
        Set-Location -LiteralPath $RepoPath
        $repoHead = (& git rev-parse HEAD 2>$null | Select-Object -Last 1)
        if ($LASTEXITCODE -eq 0) {
            $dirty = (& git status --porcelain 2>$null) -join "`n"
            $repoClean = -not [bool]$dirty.Trim()
        }
    }
    finally { Set-Location $oldLocation }
}

$stateRoot = Join-Path $env:LOCALAPPDATA 'Arvectum\ProxyLauncher'
$settingsPath = Join-Path $stateRoot 'proxy_settings.json'
if (-not (Test-Path -LiteralPath $settingsPath -PathType Leaf)) {
    throw "Persistent proxy settings are missing: $settingsPath"
}
$settings = Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
$pacPort = [int]$settings.local_pac_port

function Get-SourceCore {
    return @(
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -and
            $_.CommandLine -match 'proxy_core\.py' -and
            $_.CommandLine -match '(?i)(^|\s)--start(\s|$)'
        }
    )
}

function Get-SourceGui {
    return @(
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -and $_.CommandLine -match 'proxy_gui\.py'
        }
    )
}

function Get-PacListener {
    return @(
        Get-NetTCPConnection -State Listen -LocalPort $pacPort -ErrorAction SilentlyContinue
    )
}

function Get-RunValue([string]$Name) {
    $key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    $item = Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
    if (-not $item) { return $null }
    $property = $item.PSObject.Properties[$Name]
    if (-not $property) { return $null }
    return [string]$property.Value
}

$coreBefore = @(Get-SourceCore)
$guiBefore = @(Get-SourceGui)
$listenerBefore = @(Get-PacListener)

if ($Action -eq 'Enable') {
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $recoveryRoot = Join-Path 'C:\Arvectum\Recovery' "OWNER-SOURCE-MODE-$timestamp"
    New-Item -ItemType Directory -Path $recoveryRoot -Force | Out-Null

    $desktop = [Environment]::GetFolderPath('Desktop')
    $shortcutPath = Join-Path $desktop 'Arvectum Proxy Launcher.lnk'
    if (Test-Path -LiteralPath $shortcutPath -PathType Leaf) {
        Copy-Item -LiteralPath $shortcutPath -Destination (Join-Path $recoveryRoot 'desktop-shortcut-before.lnk') -Force
    }

    $runBefore = [ordered]@{
        main = Get-RunValue 'ArvectumProxyLauncher'
        recovery = Get-RunValue 'ArvectumProxyLauncherRecovery'
    }
    $runBefore | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $recoveryRoot 'run-before.json') -Encoding UTF8

    if ($coreBefore.Count -eq 0) {
        $internetKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
        $internet = Get-ItemProperty -LiteralPath $internetKey -ErrorAction SilentlyContinue
        $autoConfig = [string]$internet.AutoConfigURL
        if ($autoConfig -match '^https?://(127\.0\.0\.1|localhost):\d+/' -and $listenerBefore.Count -eq 0) {
            $oldEap = $ErrorActionPreference
            try {
                $ErrorActionPreference = 'Continue'
                & $PythonPath $coreScript '--rollback' 2>&1 | Out-Host
                $rollbackExit = $LASTEXITCODE
            }
            finally { $ErrorActionPreference = $oldEap }
            if ($rollbackExit -ne 0) { throw 'Dead-localhost recovery rollback did not complete.' }
        }

        Start-Process -FilePath $pythonw -ArgumentList ('"' + $coreScript + '" --start') -WorkingDirectory $RepoPath | Out-Null
        Start-Sleep -Seconds 5
    }

    $coreAfterStart = @(Get-SourceCore)
    $listenerAfterStart = @(Get-PacListener)
    if ($coreAfterStart.Count -lt 1 -or $listenerAfterStart.Count -lt 1) {
        throw 'Source-mode core did not become healthy; shortcut/autostart were not changed.'
    }

    if ($guiBefore.Count -eq 0) {
        Start-Process -FilePath $pythonw -ArgumentList ('"' + $guiScript + '"') -WorkingDirectory $RepoPath | Out-Null
        Start-Sleep -Seconds 2
    }

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $pythonw
    $shortcut.Arguments = '"' + $guiScript + '"'
    $shortcut.WorkingDirectory = $RepoPath
    $shortcut.Description = 'Arvectum Proxy Launcher - supported owner source mode'
    $shortcut.Save()

    $runKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    New-Item -Path $runKey -Force | Out-Null
    $recoveryCommand = '"' + $pythonw + '" "' + $coreScript + '" --rollback'
    New-ItemProperty -LiteralPath $runKey -Name 'ArvectumProxyLauncherRecovery' -Value $recoveryCommand -PropertyType String -Force | Out-Null

    if ($EnableAutostart) {
        $mainCommand = '"' + $pythonw + '" "' + $coreScript + '" --start'
        New-ItemProperty -LiteralPath $runKey -Name 'ArvectumProxyLauncher' -Value $mainCommand -PropertyType String -Force | Out-Null
    }

    $marker = [ordered]@{
        schema = 'arvectum.proxy.owner-source-mode.v1'
        enabled_utc = [DateTime]::UtcNow.ToString('o')
        version = '0.2.3'
        repo_path = $RepoPath
        repo_head = $repoHead
        repo_clean = $repoClean
        python_path = $PythonPath
        python_sha256 = $pythonHash
        desktop_shortcut = $shortcutPath
        main_autostart_enabled = [bool]$EnableAutostart
        recovery_autostart_enabled = $true
        recovery_snapshot = $recoveryRoot
        security_boundary = 'no Smart App Control or App Control policy changes'
    }
    New-Item -ItemType Directory -Path $stateRoot -Force | Out-Null
    $marker | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $stateRoot 'owner-source-mode.json') -Encoding UTF8
}

$coreNow = @(Get-SourceCore)
$guiNow = @(Get-SourceGui)
$listenerNow = @(Get-PacListener)
$statusRaw = & $PythonPath $coreScript '--status' 2>&1
$statusExit = $LASTEXITCODE

$evidence = [ordered]@{
    schema = 'arvectum.proxy.owner-source-mode-status.v1'
    task = 'APL-WIN-014'
    action = $Action
    created_utc = [DateTime]::UtcNow.ToString('o')
    version = '0.2.3'
    repo_path = $RepoPath
    repo_head = $repoHead
    repo_clean = $repoClean
    python_path = $PythonPath
    python_sha256 = $pythonHash
    source_core_processes = $coreNow.Count
    source_gui_processes = $guiNow.Count
    pac_port = $pacPort
    pac_listener_count = $listenerNow.Count
    status_exit_code = $statusExit
    status_output = @($statusRaw | ForEach-Object { $_.ToString() })
    main_autostart = Get-RunValue 'ArvectumProxyLauncher'
    recovery_autostart = Get-RunValue 'ArvectumProxyLauncherRecovery'
    result = $(if ($coreNow.Count -gt 0 -and $listenerNow.Count -gt 0 -and $statusExit -eq 0) { 'PASS' } else { 'BLOCK' })
    production_distribution = $false
    security_invariants = @(
        'Smart App Control is not disabled',
        'App Control policy is not changed',
        'blocked unsigned legacy EXE is not required for operation',
        'source mode is owner/developer profile only'
    )
}

if ($EvidencePath) {
    $parent = Split-Path -Parent $EvidencePath
    if ($parent) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    $evidence | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
}

$evidence | ConvertTo-Json -Depth 10
if ($evidence.result -ne 'PASS') { exit 1 }
