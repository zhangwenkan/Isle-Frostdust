param([Parameter(Mandatory=$true)][string]$ListPath)
$ErrorActionPreference = 'Stop'
$studyRoot = Join-Path $PSScriptRoot '../artifacts/wandering-sword-local-study'
$studyRoot = [System.IO.Path]::GetFullPath($studyRoot)
$null = [System.Reflection.Assembly]::LoadFrom((Join-Path $studyRoot 'tools/uassetapi/UAssetAPI.dll'))
$studyInputs = Get-Content -LiteralPath $ListPath -Encoding utf8 | ConvertFrom-Json
$studyResults = @()
foreach ($relative in $studyInputs) {
    $source = Join-Path $studyRoot ('extracted/' + $relative)
    $output = Join-Path $studyRoot ('json/' + $relative + '.json')
    try {
        if (-not (Test-Path -LiteralPath $output)) {
            $asset = [UAssetAPI.UAsset]::new($source,[UAssetAPI.UnrealTypes.EngineVersion]::VER_UE4_27)
            $null = New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($output))
            [System.IO.File]::WriteAllText($output,$asset.SerializeJson([Newtonsoft.Json.Formatting]::Indented),[System.Text.UTF8Encoding]::new($false))
        }
        $studyResults += @{path=$relative; success=$true}
    } catch {
        $studyResults += @{path=$relative; success=$false; error=$_.Exception.Message}
        Write-Output ('FAILED ' + $relative + ': ' + $_.Exception.Message)
    }
}
$logName = [System.IO.Path]::GetFileNameWithoutExtension($ListPath) + '-results.json'
$studyResults | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $studyRoot $logName) -Encoding utf8
Write-Output ('Parsed ' + @($studyResults | Where-Object {$_.success}).Count + '/' + $studyResults.Count)
