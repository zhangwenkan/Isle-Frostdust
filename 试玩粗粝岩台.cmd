@echo off
chcp 65001 >nul
set "ROCK_PREVIEW_GODOT=%~dp0tools\godot\Godot_v4.7.2-stable_win64_console.exe"
if not exist "%ROCK_PREVIEW_GODOT%" set "ROCK_PREVIEW_GODOT=D:\孤屿霜尘\tools\godot\Godot_v4.7.2-stable_win64_console.exe"
if not exist "%ROCK_PREVIEW_GODOT%" (
  echo 未找到 Godot 4.7.2，请打开 scenes/layered_island.tscn。
  pause
  exit /b 1
)
"%ROCK_PREVIEW_GODOT%" --path "%~dp0." --windowed --resolution 1600x900 res://scenes/layered_island.tscn -- --tripo-rock-preview
