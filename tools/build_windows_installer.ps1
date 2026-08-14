<# Canonical APL-REL-006 installer build. Requires Inno Setup 6.7.1. #>
[CmdletBinding()]
param([string]$PythonExecutable = 'python', [string]$IsccPath)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Windows installer build must run on Windows.' }
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root
$version = (Get-Content VERSION -Raw).Trim()
$exe = Join-Path $root 'dist\Arvectum Proxy Launcher.exe'
if (-not (Test-Path -LiteralPath $exe)) { & (Join-Path $root 'tools\clean_build_windows.ps1') -PythonExecutable $PythonExecutable; if ($LASTEXITCODE) { throw 'portable build failed' } }
if (-not (Test-Path -LiteralPath $exe)) { throw 'dist\\Arvectum Proxy Launcher.exe is required' }
$payload = Join-Path $root 'out\installer-payload'
Remove-Item -LiteralPath $payload -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $payload -Force | Out-Null
Copy-Item -LiteralPath $exe -Destination (Join-Path $payload 'Arvectum Proxy Launcher.exe')
Copy-Item -LiteralPath (Join-Path $root 'installer\upgrade_helper.ps1') -Destination $payload
Copy-Item -LiteralPath (Join-Path $root 'installer\uninstall_helper.ps1') -Destination $payload
function Hash([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
$manifest = [ordered]@{ product='Arvectum Proxy Launcher'; version=$version; platform='windows-x64'; format='setup'; source_commit=(git rev-parse HEAD).Trim(); application_sha256=(Hash (Join-Path $payload 'Arvectum Proxy Launcher.exe')); upgrade_helper_sha256=(Hash (Join-Path $payload 'upgrade_helper.ps1')); uninstall_helper_sha256=(Hash (Join-Path $payload 'uninstall_helper.ps1')) }
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $payload 'build_manifest.json') -Encoding utf8
if (-not $IsccPath) { $IsccPath = @("$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1 }
if (-not $IsccPath) { throw 'Inno Setup 6.7.1 ISCC.exe was not found.' }
& $IsccPath "/DAppVersion=$version" "/DPayloadDir=$payload" 'installer\ArvectumProxyLauncher.iss'
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup compilation failed' }
$setup = Join-Path $root "out\installer\Arvectum-Proxy-Launcher-$version-windows-x64-setup.exe"
if (-not (Test-Path -LiteralPath $setup)) { throw "Expected setup EXE was not produced: $setup" }
$setupHash = Hash $setup
if ($env:GITHUB_OUTPUT) { "setup_path=$setup" >> $env:GITHUB_OUTPUT; "setup_name=$(Split-Path $setup -Leaf)" >> $env:GITHUB_OUTPUT; "setup_sha256=$setupHash" >> $env:GITHUB_OUTPUT }
Write-Host "Installer build PASS: $setup SHA256=$setupHash"
