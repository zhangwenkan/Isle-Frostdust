param([switch]$Import)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$godotExe='C:\Users\51440\Desktop\Godot_v4.6.1-stable_win64.exe'
$reviewRoot=Join-Path $projectRoot 'artifacts/cape-road-alignment-review/opening'
if($Import){
    $process=Start-Process -FilePath $godotExe -ArgumentList @('--headless','--path',('"'+$projectRoot+'"'),'--editor','--import') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reviewRoot 'import.log') -RedirectStandardError (Join-Path $reviewRoot 'import-errors.log')
    $captureHandle=$process.Handle
    $process.WaitForExit()
    if($process.ExitCode -ne 0){throw 'Godot import failed'}
}
$arguments=@('--path',('"'+$projectRoot+'"'),'--resolution','1280x720','--fixed-fps','24','--disable-vsync','--script','res://tools/capture_cape_road_opening.gd')
$process=Start-Process -FilePath $godotExe -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reviewRoot 'capture.log') -RedirectStandardError (Join-Path $reviewRoot 'capture-errors.log')
$captureHandle=$process.Handle
$process.WaitForExit()
if($process.ExitCode -ne 0){throw 'Godot opening capture failed'}
Get-Content -LiteralPath (Join-Path $reviewRoot 'capture-errors.log')
Get-Content -LiteralPath (Join-Path $reviewRoot 'capture.log') -Tail 3
