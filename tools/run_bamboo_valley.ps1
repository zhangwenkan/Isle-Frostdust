param([string]$Phase='review',[switch]$Import)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$godotExe='C:\Users\51440\Desktop\Godot_v4.6.1-stable_win64.exe'
$reviewRoot=Join-Path $projectRoot 'artifacts/bamboo-valley-review'
if($Import){
    $process=Start-Process -FilePath $godotExe -ArgumentList @('--headless','--path',('"'+$projectRoot+'"'),'--editor','--import') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reviewRoot 'import.log') -RedirectStandardError (Join-Path $reviewRoot 'import-errors.log')
    $captureHandle=$process.Handle
    $process.WaitForExit()
    if($process.ExitCode -ne 0){throw 'Godot import failed'}
}
$arguments=@('--path',('"'+$projectRoot+'"'),'--resolution','1280x720','--script','res://tools/capture_bamboo_valley.gd','--','--skip-opening',('--phase='+$Phase))
$process=Start-Process -FilePath $godotExe -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reviewRoot ($Phase+'.log')) -RedirectStandardError (Join-Path $reviewRoot ($Phase+'-errors.log'))
$captureHandle=$process.Handle
$process.WaitForExit()
if($process.ExitCode -ne 0){throw 'Godot valley capture failed'}
Get-Content -LiteralPath (Join-Path $reviewRoot ($Phase+'-errors.log'))
Get-Content -LiteralPath (Join-Path $reviewRoot ($Phase+'.log')) -Tail 14
