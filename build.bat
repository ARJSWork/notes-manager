@echo off
setlocal enabledelayedexpansion

REM Set batch file path and change to project folder
cd /d "%~dp0"

REM Configuration (adjust as needed)
set "APP_NAME=NotesManager"
set "MAIN_SCRIPT=src\main.py"
set "ICON_FILE=src\assets\icon.ico"
set "DIST_DIR=dist"
set "LOG_FILE=%~dp0build.log"
set "CLEAN_BUILD=1"

REM Pre-checks
echo Checking prerequisites...
python -V >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python not found in PATH. Please install Python and add it to your PATH.
    goto :eof
)

IF NOT EXIST "%MAIN_SCRIPT%" (
    echo ERROR: Entry script not found: %MAIN_SCRIPT%
    goto :eof
)

python -m PyInstaller --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: PyInstaller is not installed in this Python environment.
    echo Install it using: python -m pip install pyinstaller
    goto :eof
)

REM Optional: clean build environment
IF "%CLEAN_BUILD%"=="1" (
    echo [INFO] Cleaning up previous PyInstaller artifacts...
    python -m PyInstaller --clean >nul 2>&1
)

REM Ensure Dist directory exists
IF NOT EXIST "%DIST_DIR%" mkdir "%DIST_DIR%"

REM Build command
set "BUILD_CMD=python -m PyInstaller --onefile --windowed --name "%APP_NAME%" "%MAIN_SCRIPT%""
REM Ensure PyInstaller can find local modules placed in the src/ folder
set "BUILD_CMD=%BUILD_CMD% --paths "%~dp0src""
IF NOT "%ICON_FILE%"=="" (
    set "BUILD_CMD=%BUILD_CMD% --icon "%ICON_FILE%""
)

echo [INFO] Building application with:
echo %BUILD_CMD%

REM Execute build and capture output to log
call %BUILD_CMD% > "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Build failed. See log file: "%LOG_FILE%"
    goto :eof
)

REM Check for generated executable
IF EXIST "%DIST_DIR%\%APP_NAME%.exe" (
    echo [OK] Build successful. Executable found at: "%DIST_DIR%\%APP_NAME%.exe"
) ELSE (
    echo [WARN] Build finished, but EXE not found. See log file: "%LOG_FILE%"
)

echo.
echo Note: For GUI applications, no console window is shown (--windowed).
echo For debugging or for a console application, remove "--windowed" from the BUILD_CMD.