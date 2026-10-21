@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if exist "CINEMATIC_C4_STANDALONE.html" (
 start "" "%~dp0CINEMATIC_C4_STANDALONE.html"
) else (
 echo File not found: CINEMATIC_C4_STANDALONE.html
 pause
)
