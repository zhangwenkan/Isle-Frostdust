param([string]$Phase='pass1',[switch]$ImportOnly)
$ErrorActionPreference='Stop'
$projectRoot='D:\自己做着玩的\孤屿霜尘'
$engine='D:\孤屿霜尘\tools\godot\Godot_v4.7.2-stable_win64_console.exe'
$reviewDir=Join-Path $projectRoot 'artifacts\shallow-cape-review'
if($ImportOnly){
 & $engine --headless --path $projectRoot --editor --import --quit *> (Join-Path $reviewDir 'import.log')
 exit $LASTEXITCODE
}
$arguments='--path "'+$projectRoot+'" --script res://tools/capture_shallow_cape.gd --resolution 1280x720 -- --phase='+$Phase+' --skip-opening'
Start-Process -FilePath $engine -ArgumentList $arguments -WindowStyle Hidden -RedirectStandardOutput (Join-Path $reviewDir ($Phase+'-runtime.log')) -RedirectStandardError (Join-Path $reviewDir ($Phase+'-errors.log')) -PassThru | Select-Object Id
