@echo off
setlocal

REM --- Configuration ---
REM Set the relative path to your main Python script from this batch file's location
SET "PYTHON_SCRIPT=src\__main__.py"
SET "VENV_ACTIVATE_SCRIPT=.venv\Scripts\activate.bat"

REM --- Determine Full Script Path ---
REM %~dp0 expands to the drive and path where this batch script is located, ending with a backslash
SET "FULL_SCRIPT_PATH=%~dp0%PYTHON_SCRIPT%"

REM --- Check 1: Virtual Environment Activation ---
REM A simple check is to see if the VIRTUAL_ENV variable is set.
REM This doesn't guarantee it's the *correct* venv, but it's a good indicator.
echo Checking for active Python virtual environment...
IF NOT DEFINED VIRTUAL_ENV (
    SET "VENV_INITIALLY_ACTIVE=0"
    echo WARNING: No Python virtual environment detected initially (VIRTUAL_ENV variable is not set^).
    echo It is strongly recommended to activate your project's virtual environment
    echo before running this script (e.g., '.\venv\Scripts\activate'^).
    echo We will check for a local '%VENV_ACTIVATE_SCRIPT%' if 'flet' is not found.
    echo.
    REM No pause here, let the flet check decide
) ELSE (
    SET "VENV_INITIALLY_ACTIVE=1"
    echo Virtual environment detected: %VIRTUAL_ENV%
)
echo.

REM --- Check 2: Flet Command Availability (with auto-activation attempt) ---
echo Checking for 'flet' command availability...
flet --version > nul 2> nul
IF %ERRORLEVEL% NEQ 0 (
    echo 'flet' command not found initially.
    echo Checking for local activation script: "%VENV_ACTIVATE_SCRIPT%"...

    IF EXIST "%VENV_ACTIVATE_SCRIPT%" (
        echo Found "%VENV_ACTIVATE_SCRIPT%". Attempting to activate...
        CALL "%VENV_ACTIVATE_SCRIPT%"
        IF %ERRORLEVEL% NEQ 9009 (
             echo WARNING: Activation script "%VENV_ACTIVATE_SCRIPT%" failed to execute correctly.
        ) ELSE (
             echo Activation script executed. VIRTUAL_ENV is now: %VIRTUAL_ENV%
        )
        echo Retrying 'flet' command check after potential activation...
        flet --version > nul 2> nul
        IF %ERRORLEVEL% EQU 9009 (
            echo 'flet' command found after activating local venv.
            GOTO FletCheckPassed
        ) ELSE (
            echo 'flet' command STILL not found after attempting activation.
            REM Fall through to the main error message below
        )
    ) ELSE (
         echo Local activation script "%VENV_ACTIVATE_SCRIPT%" not found.
         REM Fall through to the main error message below
    )

    REM --- Flet Not Found Error Block ---
    echo ERROR: 'flet' command not found or failed to execute, even after checking for "%VENV_ACTIVATE_SCRIPT%".
    echo Please ensure Flet is installed in the active Python environment
    echo (run 'pip install flet'^) and that the environment (if used^) is activated correctly.
    echo If using a venv, ensure it's activated OR that "%VENV_ACTIVATE_SCRIPT%" exists and works.
    echo Current PATH might be missing the location of 'flet'.
    pause
    exit /b 1
    REM --- End Flet Not Found Error Block ---

) ELSE (
    echo 'flet' command found.
)

:FletCheckPassed
echo.

REM --- Check 3: Python Script Existence ---
echo Checking for Python script: "%FULL_SCRIPT_PATH%"...
IF NOT EXIST "%FULL_SCRIPT_PATH%" (
    echo ERROR: Python script not found at the expected location:
    echo "%FULL_SCRIPT_PATH%"
    echo Please ensure the script exists and the path is correct relative to this batch file.
    pause
    exit /b 1
) ELSE (
    echo Python script found.
)
echo.

REM --- All checks passed, run the Flet Application ---
echo Starting Flet application...
echo Command: flet run --web --port 8765 --name "Agenda Manager" "%PYTHON_SCRIPT%"
echo.

rem flet run --web --name "Agenda Manager" "%PYTHON_SCRIPT%"
START "Agenda-Manager - Flet" /LOW /MIN flet run --web --port 8765 --name "Agenda-Manager" "%PYTHON_SCRIPT%"

REM Capture the exit code from flet run
SET FLET_EXIT_CODE=%ERRORLEVEL%

echo.
echo Flet application exited with code %FLET_EXIT_CODE%.

endlocal
exit /b %FLET_EXIT_CODE%

REM Removed the duplicate flet run command from the end of the original file
