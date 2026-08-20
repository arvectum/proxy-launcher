[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') { throw 'ConfigCI smoke must run on Windows.' }

Import-Module ConfigCI -ErrorAction Stop

$root = Join-Path $env:TEMP ('Arvectum-AppControl-Smoke-' + [guid]::NewGuid().ToString('N'))
$scanRoot = Join-Path $root 'scan'
New-Item -ItemType Directory -Path $scanRoot -Force | Out-Null

try {
    $sample = Join-Path $env:WINDIR 'System32\notepad.exe'
    if (-not (Test-Path -LiteralPath $sample -PathType Leaf)) { throw 'notepad.exe is missing.' }
    Copy-Item -LiteralPath $sample -Destination (Join-Path $scanRoot 'notepad.exe') -Force

    $xml = Join-Path $root 'supplemental.xml'
    $basePolicyId = [guid]'11111111-2222-3333-4444-555555555555'

    New-CIPolicy -MultiplePolicyFormat -ScanPath $scanRoot -UserPEs -FilePath $xml -Level Hash | Out-Null
    if (-not (Test-Path -LiteralPath $xml -PathType Leaf)) { throw 'New-CIPolicy did not create XML.' }

    Set-CIPolicyIdInfo -FilePath $xml -ResetPolicyID -PolicyName 'Arvectum APL-WIN-014 CI Smoke' -SupplementsBasePolicyID $basePolicyId | Out-Null
    Set-CIPolicyVersion -FilePath $xml -Version '0.0.0.1'

    $text = Get-Content -LiteralPath $xml -Raw -Encoding UTF8
    $match = [regex]::Match($text, '<PolicyID>\s*([^<]+)\s*</PolicyID>', 'IgnoreCase')
    if (-not $match.Success) { throw 'Generated policy has no PolicyID.' }

    $policyId = $match.Groups[1].Value.Trim().Trim('{}')
    $cip = Join-Path $root ("{$policyId}.cip")
    ConvertFrom-CIPolicy -XmlFilePath $xml -BinaryFilePath $cip

    if (-not (Test-Path -LiteralPath $cip -PathType Leaf)) { throw 'Binary supplemental policy was not created.' }
    if ((Get-Item -LiteralPath $cip).Length -le 0) { throw 'Binary supplemental policy is empty.' }

    if ($text -notmatch [regex]::Escape($basePolicyId.ToString('B'))) {
        throw 'Generated policy does not reference the requested base policy ID.'
    }

    if ($text -notmatch '(?i)Hash') {
        throw 'Generated policy does not contain hash-rule evidence.'
    }

    Write-Host 'APL-WIN-014 ConfigCI supplemental-policy smoke: PASS'
}
finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
