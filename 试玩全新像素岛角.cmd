@echo off
chcp 65001 >nul
set "FRESH_CAPE_GODOT=D:\孤屿霜尘\tools\godot\Godot_v4.7.2-stable_win64_console.exe"
"%FRESH_CAPE_GODOT%" --path "%~dp0." --resolution 1280x720 res://scenes/fresh_pixel_cape_preview.tscn
