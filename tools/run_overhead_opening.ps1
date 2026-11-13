param([string]$Script='capture_overhead_opening',[string]$Label='preview',[switch]$Import,[switch]$SkipOpening)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$godotExe='C:\Users\51440\Desktop\Godot_v4.6.1-stable_win64.exe'
$reviewRoot=Join-Path $projectRoot 'artifacts/overhead-opening-review'
if($Import){
    $process=Start-Process -FilePath $godotExe -ArgumentList @('--headless','--path',('"'+$projectRoot+'"'),'--editor','--import') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reviewRoot 'import.log') -RedirectStandardError (Join-Path $reviewRoot 'import-errors.log')
    $captureHandle=$process.Handle
    $process.WaitForExit()
    if($process.ExitCode -ne 0){throw 'Godot import failed'}
}
$arguments=@('--path',('"'+$projectRoot+'"'),'--resolution','1280x720','--fixed-fps','24','--script',('res://tools/'+$Script+'.gd'))
if($SkipOpening){$arguments+=@('--','--skip-opening')}
$process=Start-Process -FilePath $godotExe -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reviewRoot ($Label+'.log')) -RedirectStandardError (Join-Path $reviewRoot ($Label+'-errors.log'))
$captureHandle=$process.Handle
$process.WaitForExit()
if($process.ExitCode -ne 0){throw 'Godot opening check failed'}
Get-Content -LiteralPath (Join-Path $reviewRoot ($Label+'-errors.log')) -Tail 20
Get-Content -LiteralPath (Join-Path $reviewRoot ($Label+'.log')) -Tail 20
