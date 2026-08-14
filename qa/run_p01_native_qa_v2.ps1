param(
    [Parameter(Mandatory=$true)]
    [string]$SourceExe,

    [string]$CanonicalExe = (Join-Path $env:USERPROFILE 'Documents\ArvectumProxyLauncher\Arvectum Proxy Launcher.exe'),

    [string]$OutputPath = (Join-Path $env:USERPROFILE 'Documents\Arvectum-P0.2-Native-QA.json')
)

$ErrorActionPreference = 'Stop'

function Get-LaunchResult([string]$Path) {
    $result = [ordered]@{
        path = $Path
        exists = $false
        sha256 = $null
        launched = $false
        exit_code = $null
        error = $null
        native_error_code = $null
        hresult = $null
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        $result.error = 'FILE_NOT_FOUND'
        return [pscustomobject]$result
    }

    $result.exists = $true
    $result.sha256 = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash

    try {
        # --status is read-only with respect to WinINET/proxy state.
        $p = Start-Process -FilePath $Path -ArgumentList '--status' -PassThru -Wait -ErrorAction Stop
        $result.launched = $true
        $result.exit_code = $p.ExitCode
    } catch {
        $result.error = $_.Exception.Message
        $result.hresult = ('0x{0:X8}' -f ($_.Exception.HResult -band 0xffffffff))

        $ex = $_.Exception
        while ($ex) {
            if ($null -ne $ex.NativeErrorCode) {
                $result.native_error_code = [int]$ex.NativeErrorCode
                break
            }
            $ex = $ex.InnerException
        }
    }

    return [pscustomobject]$result
}

if (-not (Test-Path -LiteralPath $SourceExe -PathType Leaf)) {
    throw "Source EXE not found: $SourceExe"
}

$SourceExe = [IO.Path]::GetFullPath($SourceExe)
$CanonicalExe = [IO.Path]::GetFullPath($CanonicalExe)
$canonicalDir = [IO.Path]::GetDirectoryName($CanonicalExe)
New-Item -ItemType Directory -Path $canonicalDir -Force | Out-Null

# Do not replace a canonical executable while it is running.
try {
    $active = @(Get-CimInstance Win32_Process -Filter "Name='Arvectum Proxy Launcher.exe'" -ErrorAction Stop |
        Where-Object {
            $_.ExecutablePath -and
            ([IO.Path]::GetFullPath($_.ExecutablePath) -ieq $CanonicalExe)
        })
} catch {
    $active = @()
}

if ($active.Count -gt 0) {
    throw "QA STOP: canonical Launcher is currently running (PID(s): $($active.ProcessId -join ', ')). Close the Launcher/proxy process first; this QA will not kill it."
}

$sourceHash = (Get-FileHash -LiteralPath $SourceExe -Algorithm SHA256).Hash
$backupExe = $null
$hadCanonical = Test-Path -LiteralPath $CanonicalExe -PathType Leaf
$backupOwner = $null
$ownerMarker = Join-Path $canonicalDir '.arvectum-install-owner'

if ($hadCanonical) {
    $backupExe = $CanonicalExe + '.chatgpt-qa-backup'
    Copy-Item -LiteralPath $CanonicalExe -Destination $backupExe -Force
}
if (Test-Path -LiteralPath $ownerMarker -PathType Leaf) {
    $backupOwner = Get-Content -LiteralPath $ownerMarker -Raw
}

$canonical = $null
$source = $null
$stagingHash = $null

try {
    Copy-Item -LiteralPath $SourceExe -Destination $CanonicalExe -Force
    $stagingHash = (Get-FileHash -LiteralPath $CanonicalExe -Algorithm SHA256).Hash
    if ($stagingHash -ne $sourceHash) {
        throw 'QA staging hash mismatch'
    }

    # Test the exact permanent Documents binary first.
    $canonical = Get-LaunchResult $CanonicalExe

    # Then test the original source path with the identical canonical hash in
    # place. If canonical handoff is blocked but source execution is allowed,
    # proxy_gui.py must fall back to current portable code and --status exits 0.
    $source = Get-LaunchResult $SourceExe

    $verdict = 'INCONCLUSIVE'
    $reason = ''

    if ($canonical.launched -and $canonical.exit_code -eq 0) {
        $verdict = 'CANONICAL_GO'
        $reason = 'The P0.2 Documents executable runs successfully.'
    }
    elseif ($source.launched -and $source.exit_code -eq 0) {
        $verdict = 'MANUAL_PORTABLE_GO_AUTOSTART_BLOCKED'
        $reason = 'Documents execution failed, but the same P0.2 binary runs from the original portable path and completes --status. Manual portable fallback is viable; autostart must remain disabled.'
    }
    elseif (($canonical.native_error_code -eq 4551) -or ($source.native_error_code -eq 4551)) {
        $verdict = 'APP_CONTROL_BLOCKED'
        $reason = 'Application Control blocked executable launch (Win32 4551 / HRESULT low word 0x11C7). Collect policy diagnostics before deciding the signing path.'
    }
    else {
        $verdict = 'FAIL'
        $reason = 'Neither canonical nor portable execution produced a successful read-only --status result.'
    }

    $report = [ordered]@{
        generated = (Get-Date -Format 'o')
        verdict = $verdict
        reason = $reason
        source_sha256 = $sourceHash
        staged_canonical_sha256 = $stagingHash
        source = $source
        canonical = $canonical
        restored_previous_canonical_after_test = $hadCanonical
        notes = @(
            'QA temporarily stages the supplied EXE at the canonical Documents path and restores the previous file in finally.',
            'QA does not stop processes, change WinINET, change proxy environment variables, or read proxy credentials.',
            'A canonical block alone is not sufficient to reject manual portable fallback.',
            'Win32 error 4551 proves Application Control blocked the file but does not by itself identify Smart App Control vs App Control for Business/WDAC vs AppLocker.'
        )
    }

    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    $report | ConvertTo-Json -Depth 8
}
finally {
    # Restore the exact pre-QA canonical file state.
    try {
        if ($hadCanonical -and $backupExe -and (Test-Path -LiteralPath $backupExe -PathType Leaf)) {
            Copy-Item -LiteralPath $backupExe -Destination $CanonicalExe -Force
            Remove-Item -LiteralPath $backupExe -Force
        }
        elseif (-not $hadCanonical -and (Test-Path -LiteralPath $CanonicalExe -PathType Leaf)) {
            Remove-Item -LiteralPath $CanonicalExe -Force
        }

        if ($null -ne $backupOwner) {
            Set-Content -LiteralPath $ownerMarker -Value $backupOwner -Encoding Ascii -NoNewline
        }
    } catch {
        Write-Warning ("QA cleanup failed: " + $_.Exception.Message)
        Write-Warning "Inspect the canonical Documents folder before using autostart."
    }
}

Write-Host ''
Write-Host "QA report saved: $OutputPath"
