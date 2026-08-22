<#
.SYNOPSIS
    APL-IP-004 fail-closed license-bundle gate for Windows promoted artifacts.
.DESCRIPTION
    Builds the exact Python/Tcl/Tk/PyInstaller third-party license bundle from
    the canonical clean-build virtual environment, embeds it together with the
    product LICENSE and THIRD_PARTY_NOTICES into the portable ZIP, then verifies
    the resulting archive. The ZIP checksum/build-result are rebound to the
    post-compliance bytes so downstream release evidence cannot retain the
    pre-bundle hash.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PortableZip
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $root
$zip = (Resolve-Path -LiteralPath $PortableZip).Path
$python = Join-Path $root '.build-venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'APL-IP-004: canonical .build-venv Python is missing.' }
foreach ($required in @('LICENSE', 'THIRD_PARTY_NOTICES.txt', 'tools\third_party_license_bundle.py')) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $required))) { throw "APL-IP-004: missing $required" }
}

$work = Join-Path $env:TEMP ("apl-ip-004-" + [guid]::NewGuid().ToString('N'))
$stage = Join-Path $work 'stage'
$bundle = Join-Path $stage 'THIRD_PARTY_LICENSES'
New-Item -ItemType Directory -Path $stage -Force | Out-Null
try {
    Expand-Archive -LiteralPath $zip -DestinationPath $stage -Force
    Copy-Item -LiteralPath (Join-Path $root 'LICENSE') -Destination (Join-Path $stage 'LICENSE.txt') -Force
    Copy-Item -LiteralPath (Join-Path $root 'THIRD_PARTY_NOTICES.txt') -Destination (Join-Path $stage 'THIRD_PARTY_NOTICES.txt') -Force
    & $python (Join-Path $root 'tools\third_party_license_bundle.py') --build --output $bundle
    if ($LASTEXITCODE -ne 0) { throw 'APL-IP-004: third-party license bundle generation failed.' }
    & $python (Join-Path $root 'tools\third_party_license_bundle.py') --verify --output $bundle
    if ($LASTEXITCODE -ne 0) { throw 'APL-IP-004: third-party license bundle verification failed.' }

    foreach ($required in @('LICENSE.txt','THIRD_PARTY_NOTICES.txt','THIRD_PARTY_LICENSES\manifest.json')) {
        $path = Join-Path $stage $required
        if (-not (Test-Path -LiteralPath $path) -or (Get-Item -LiteralPath $path).Length -eq 0) {
            throw "APL-IP-004: portable compliance payload missing/empty: $required"
        }
    }

    Remove-Item -LiteralPath $zip -Force
    Compress-Archive -Path "$stage\*" -DestinationPath $zip -Force

    $verify = Join-Path $work 'verify'
    Expand-Archive -LiteralPath $zip -DestinationPath $verify -Force
    & $python (Join-Path $root 'tools\third_party_license_bundle.py') --verify --output (Join-Path $verify 'THIRD_PARTY_LICENSES')
    if ($LASTEXITCODE -ne 0) { throw 'APL-IP-004: final portable archive license verification failed.' }

    $zipHash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
    $outDir = Split-Path -Parent $zip
    Set-Content -LiteralPath (Join-Path $outDir 'SHA256SUMS.txt') -Value "$zipHash  $(Split-Path $zip -Leaf)" -Encoding ascii
    $buildResult = Join-Path $outDir 'build-result.json'
    if (Test-Path -LiteralPath $buildResult) {
        $manifest = Get-Content -LiteralPath $buildResult -Raw -Encoding UTF8 | ConvertFrom-Json
        $manifest.zip_sha256 = $zipHash
        $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $buildResult -Encoding utf8
    }
    Write-Host "APL-IP-004 Windows portable PASS: $zip SHA256=$zipHash"
} finally {
    Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
