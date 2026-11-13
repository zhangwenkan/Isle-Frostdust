param([string]$Phase='pass1',[switch]$Import,[string]$Script='capture_junction_refine')
$ErrorActionPreference='Stop'
$coastRoot=Split-Path -Parent $PSScriptRoot
$coastReview=Join-Path $coastRoot 'artifacts/coast-junction-refine-review'
$coastEngine='C:/Users/51440/Desktop/Godot_v4.6.1-stable_win64.exe'
if($Import){
    $coastProcess=Start-Process -FilePath $coastEngine -ArgumentList @('--headless','--path',('"'+$coastRoot+'"'),'--editor','--import') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $coastReview 'import.log') -RedirectStandardError (Join-Path $coastReview 'import-errors.log')
    $coastHandle=$coastProcess.Handle
    $coastProcess.WaitForExit()
    if($coastProcess.ExitCode -ne 0){throw 'Junction import failed'}
}
$coastProcess=Start-Process -FilePath $coastEngine -ArgumentList @('--path',('"'+$coastRoot+'"'),'--resolution','1280x720','--script',('res://tools/'+$Script+'.gd'),'--','--skip-opening',('--phase='+$Phase)) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $coastReview ($Phase+'.log')) -RedirectStandardError (Join-Path $coastReview ($Phase+'-errors.log'))
$coastHandle=$coastProcess.Handle
$coastProcess.WaitForExit()
if($coastProcess.ExitCode -ne 0){throw 'Junction runtime failed'}
Get-Content (Join-Path $coastReview ($Phase+'-errors.log')) -Tail 10
Get-Content (Join-Path $coastReview ($Phase+'.log')) -Tail 4
