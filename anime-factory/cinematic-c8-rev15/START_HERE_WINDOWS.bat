@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (py -3 -m studio.director examples\REV15_DUEL_LYRA_KAEL_NONCANON.json --iterations 100 & goto finish)
where python >nul 2>&1
if %errorlevel%==0 (python -m studio.director examples\REV15_DUEL_LYRA_KAEL_NONCANON.json --iterations 100 & goto finish)
echo Python 3.10+ is required for Rev15 Director. Install from https://www.python.org/downloads/windows/
:finish
if errorlevel 1 echo ERROR: see console output and README_RU.md
pause
