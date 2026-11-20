@echo off
chcp 65001 >nul
set "PIXEL_CAVERN_GODOT=D:\孤屿霜尘\tools\godot\Godot_v4.7.2-stable_win64_console.exe"
"%PIXEL_CAVERN_GODOT%" --path "%~dp0." --resolution 1280x720 res://scenes/pixel_cavern_coast_preview.tscn
