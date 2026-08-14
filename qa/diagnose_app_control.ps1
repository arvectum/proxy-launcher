param(
    [string]$ExePath = (Join-Path $env:USERPROFILE 'Documents\ArvectumProxyLauncher\Arvectum Proxy Launcher.exe'),
    [string]$OutputPath = (Join-Path $env:USERPROFILE 'Documents\Arvectum-AppControl-Diagnostic.txt')
)

$ErrorActionPreference = 'Continue'
$lines = New-Object System.Collections.Generic.List[string]

function Add-Line([string]$Text = '') {
    $lines.Add($Text) | Out-Null
}

Add-Line 'Arvectum Proxy Launcher - Windows Application Control diagnostic'
Add-Line ('Generated: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'))
Add-Line ('Computer: ' + $env:COMPUTERNAME)
Add-Line ('Windows: ' + [Environment]::OSVersion.VersionString)
Add-Line ('Target EXE: ' + $ExePath)
Add-Line ''

Add-Line '=== FILE ==='
if (Test-Path -LiteralPath $ExePath -PathType Leaf) {
    $item = Get-Item -LiteralPath $ExePath
    Add-Line 'Exists: YES'
    Add-Line ('Length: ' + $item.Length)
    Add-Line ('SHA256: ' + (Get-FileHash -LiteralPath $ExePath -Algorithm SHA256).Hash)
    Add-Line ('FileVersion: ' + $item.VersionInfo.FileVersion)
    Add-Line ('ProductVersion: ' + $item.VersionInfo.ProductVersion)

    $sig = Get-AuthenticodeSignature -LiteralPath $ExePath
    Add-Line ('SignatureStatus: ' + $sig.Status)
    if ($sig.SignerCertificate) {
        Add-Line ('SignerSubject: ' + $sig.SignerCertificate.Subject)
        Add-Line ('SignerThumbprint: ' + $sig.SignerCertificate.Thumbprint)
    }

    try {
        $zone = Get-Content -LiteralPath ($ExePath + ':Zone.Identifier') -ErrorAction Stop
        Add-Line 'Zone.Identifier: PRESENT'
        foreach ($z in $zone) { Add-Line ('  ' + $z) }
    } catch {
        Add-Line 'Zone.Identifier: ABSENT/UNREADABLE'
    }
} else {
    Add-Line 'Exists: NO'
}
Add-Line ''

Add-Line '=== ACTIVE APP CONTROL POLICIES (CiTool) ==='
$ciTool = Join-Path $env:SystemRoot 'System32\CiTool.exe'
if (Test-Path -LiteralPath $ciTool) {
    try {
        $policyOutput = & $ciTool -lp 2>&1 | Out-String
        foreach ($line in ($policyOutput -split "`r?`n")) {
            if ($line.Trim()) { Add-Line $line }
        }
    } catch {
        Add-Line ('CiTool error: ' + $_.Exception.Message)
    }
} else {
    Add-Line 'CiTool.exe not found on this Windows build.'
}
Add-Line ''

Add-Line '=== SMART APP CONTROL REGISTRY SIGNAL ==='
try {
    $ci = Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy' -ErrorAction Stop
    if ($null -ne $ci.VerifiedAndReputablePolicyState) {
        Add-Line ('VerifiedAndReputablePolicyState: ' + $ci.VerifiedAndReputablePolicyState)
    } else {
        Add-Line 'VerifiedAndReputablePolicyState: not present'
    }
} catch {
    Add-Line ('CI Policy registry read: ' + $_.Exception.Message)
}
Add-Line ''

$since = (Get-Date).AddHours(-6)

Add-Line '=== RECENT CODE INTEGRITY EVENTS ==='
try {
    $events = Get-WinEvent -FilterHashtable @{
        LogName='Microsoft-Windows-CodeIntegrity/Operational'
        StartTime=$since
    } -ErrorAction Stop |
        Where-Object {
            ($_.Message -like '*Arvectum Proxy Launcher*') -or
            ($_.Id -in 3076,3077,3089,3099)
        } |
        Select-Object -First 80

    if (-not $events) {
        Add-Line 'No matching/relevant recent Code Integrity events found.'
    }

    foreach ($e in $events) {
        Add-Line ('[' + $e.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss') +
                  '] EventId=' + $e.Id + ' Level=' + $e.LevelDisplayName)
        $msg = (($e.Message -replace "`r", ' ') -replace "`n", ' ')
        if ($msg.Length -gt 1400) {
            $msg = $msg.Substring(0, 1400) + '...'
        }
        Add-Line $msg
        Add-Line ''
    }
} catch {
    Add-Line ('Code Integrity log read error: ' + $_.Exception.Message)
}

Add-Line '=== RECENT APPLOCKER EXE/DLL EVENTS ==='
try {
    $events = Get-WinEvent -FilterHashtable @{
        LogName='Microsoft-Windows-AppLocker/EXE and DLL'
        StartTime=$since
    } -ErrorAction Stop |
        Where-Object { $_.Message -like '*Arvectum Proxy Launcher*' } |
        Select-Object -First 40

    if (-not $events) {
        Add-Line 'No matching recent AppLocker EXE/DLL events found.'
    }

    foreach ($e in $events) {
        Add-Line ('[' + $e.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss') +
                  '] EventId=' + $e.Id + ' Level=' + $e.LevelDisplayName)
        Add-Line ((($e.Message -replace "`r", ' ') -replace "`n", ' '))
        Add-Line ''
    }
} catch {
    Add-Line ('AppLocker log read error: ' + $_.Exception.Message)
}

$lines | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host "Diagnostic saved: $OutputPath"
Write-Host 'No proxy credentials are collected by this script.'
