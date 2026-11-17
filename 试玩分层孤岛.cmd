@echo off
chcp 65001 >nul
set "LAYERED_GODOT=%~dp0tools\godot\Godot_v4.7.2-stable_win64_console.exe"
if not exist "%LAYERED_GODOT%" set "LAYERED_GODOT=D:\孤屿霜尘\tools\godot\Godot_v4.7.2-stable_win64_console.exe"
if not exist "%LAYERED_GODOT%" (
  echo 未找到 Godot 4.7.2，请在编辑器中打开 scenes/layered_island.tscn 并按 F6。
  pause
  exit /b 1
)
"%LAYERED_GODOT%" --path "%~dp0." res://scenes/layered_island.tscn
