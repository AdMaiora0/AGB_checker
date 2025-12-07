@echo off
setlocal EnableDelayedExpansion

REM Bepaal de map waar dit script staat
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
set "PY_SCRIPT=%SCRIPT_DIR%agb_checker.py"

REM Check of de virtual environment python bestaat, anders fallback naar systeem python
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

REM Check of er een argument is meegegeven
set "AGB_CODE=%~1"

REM Als er geen argument is, probeer het klembord te lezen via PowerShell
if "%AGB_CODE%"=="" (
    for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "Get-Clipboard | Select-Object -First 1"`) do (
        set "AGB_CODE=%%I"
    )
    if not "!AGB_CODE!"=="" (
        echo Gebruik klembord input: !AGB_CODE!
    )
)

REM Als er nog steeds geen code is, toon foutmelding
if "%AGB_CODE%"=="" (
    echo Gebruik: agb.bat [AGB-code]
    echo Of zorg dat er een code op het klembord staat.
    exit /b 1
)

REM Roep het Python script aan
"%PYTHON_EXE%" "%PY_SCRIPT%" "%AGB_CODE%"

endlocal
