param([string]$Script='verify_coast_opening',[string]$Label='opening-check',[switch]$SkipOpening)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$reviewRoot=Join-Path $projectRoot 'artifacts/coast-unification-review'
$arguments=@('--path',('"'+$projectRoot+'"'),'--resolution','1280x720','--fixed-fps','24','--script',('res://tools/'+$Script+'.gd'))
if($SkipOpening){$arguments+=@('--','--skip-opening')}
$process=Start-Process -FilePath 'C:/Users/51440/Desktop/Godot_v4.6.1-stable_win64.exe' -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reviewRoot ($Label+'.log')) -RedirectStandardError (Join-Path $reviewRoot ($Label+'-errors.log'))
$handle=$process.Handle
$process.WaitForExit()
if($process.ExitCode -ne 0){throw 'Godot coast verification failed'}
Get-Content (Join-Path $reviewRoot ($Label+'-errors.log')) -Tail 12
Get-Content (Join-Path $reviewRoot ($Label+'.log')) -Tail 12
