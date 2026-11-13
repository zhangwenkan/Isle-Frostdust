param([string]$Phase='review')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$godotExe='C:\Users\51440\Desktop\Godot_v4.6.1-stable_win64.exe'
$reviewRoot=Join-Path $projectRoot 'artifacts/procedural-sky-review'
$arguments=@('--path',('"'+$projectRoot+'"'),'--resolution','1280x720','--script','res://tools/capture_procedural_sky.gd','--',('--phase='+$Phase))
$process=Start-Process -FilePath $godotExe -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reviewRoot ($Phase+'.log')) -RedirectStandardError (Join-Path $reviewRoot ($Phase+'-errors.log'))
$captureHandle=$process.Handle
$process.WaitForExit()
if($process.ExitCode -ne 0){throw 'Godot sky capture failed'}
Get-Content -LiteralPath (Join-Path $reviewRoot ($Phase+'-errors.log'))
Get-Content -LiteralPath (Join-Path $reviewRoot ($Phase+'.log')) -Tail 8
