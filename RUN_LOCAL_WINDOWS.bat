@echo off
setlocal
cd /d "%~dp0"
echo Installing required oTree version...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error
echo.
echo Starting oTree at http://localhost:8000/
otree devserver
if errorlevel 1 python -m otree devserver
goto :eof
:error
echo.
echo Installation failed. See README.md for the virtual-environment setup option.
pause
