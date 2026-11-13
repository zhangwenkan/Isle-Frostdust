$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$reviewRoot=Join-Path $projectRoot 'artifacts/coast-integration-review'
$godotExe='C:\Users\51440\Desktop\Godot_v4.6.1-stable_win64.exe'
$arguments=@('--path',('"'+$projectRoot+'"'),'--resolution','1280x720','--script','res://tools/capture_integrated_coast_motion.gd','--','--skip-opening')
$process=Start-Process -FilePath $godotExe -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reviewRoot 'motion.log') -RedirectStandardError (Join-Path $reviewRoot 'motion-errors.log')
$captureHandle=$process.Handle
$process.WaitForExit()
if($process.ExitCode -ne 0){throw 'Coast motion capture failed'}
Get-Content -LiteralPath (Join-Path $reviewRoot 'motion-errors.log') -Tail 8
Get-Content -LiteralPath (Join-Path $reviewRoot 'motion.log') -Tail 8
