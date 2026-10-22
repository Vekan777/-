@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (py -3 -m unittest discover -s tests -v & goto finish)
where python >nul 2>&1
if %errorlevel%==0 (python -m unittest discover -s tests -v & goto finish)
echo Python not found
:finish
pause
