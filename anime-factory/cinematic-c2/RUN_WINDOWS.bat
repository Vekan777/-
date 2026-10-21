@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if exist "CINEMATIC_C2_STANDALONE.html" (start "" "%~dp0CINEMATIC_C2_STANDALONE.html") else (start "" "%~dp0index.html")
