[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') { throw 'ConfigCI smoke must run on Windows.' }

Import-Module ConfigCI -ErrorAction Stop

$root = Join-Path $env:TEMP ('Arvectum-AppControl-Smoke-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $root -Force | Out-Null

try {
    $xml = Join-Path $root 'supplemental.xml'
    $basePolicyId = [guid]'11111111-2222-3333-4444-555555555555'
    $sampleRulePath = Join-Path $root 'sample.exe'

    $rules = @(New-CIPolicyRule -FilePathRule $sampleRulePath)
    if ($rules.Count -lt 1) { throw 'ConfigCI did not create a smoke rule.' }

    New-CIPolicy -MultiplePolicyFormat -FilePath $xml -Rules $rules -UserPEs | Out-Null
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

    Write-Host 'APL-WIN-014 ConfigCI supplemental-policy conversion smoke: PASS'
}
finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
