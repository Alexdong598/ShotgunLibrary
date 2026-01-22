@echo off
setlocal

:: ============================================================================
:: 1. CONFIGURATION (Edit these lines)
:: ============================================================================

:: -- Set the Project Name (Critical for your tool to work) --
set "HAL_PROJECT=Demo_Project"
:: (Optional) Set User info if your tool uses them
set "HAL_USER_LOGIN=%USERNAME%"
set "HAL_TASK=generic"

:: -- Choose your Python Interpreter --
:: Option A: Use standard system Python (if added to PATH)
set "PYTHON_EXE=python"

:: Option B: Use Maya's Python (mayapy) - Recommended if you need Maya libraries
:: set "PYTHON_EXE=C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"

:: Option C: Use Houdini's Python (hython) - Recommended if you need Houdini libraries
:: set "PYTHON_EXE=C:\Program Files\Side Effects Software\Houdini 19.5.303\bin\hython.exe"

:: -- Set the path to your script folder --
:: "%~dp0" automatically resolves to the folder where this .bat file is located.
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_NAME=ui.py"


:: ============================================================================
:: 2. ENVIRONMENT SETUP
:: ============================================================================

echo ---------------------------------------------------
echo Launching Shotgun Library...
echo Host Mode: Standalone
echo Project:   %HAL_PROJECT%
echo Script:    %SCRIPT_DIR%%SCRIPT_NAME%
echo ---------------------------------------------------

:: Add the script directory to PYTHONPATH so it can find 'shotgun_data_manager.py'
set "PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%"


:: ============================================================================
:: 3. EXECUTION
:: ============================================================================

:: Run the script
"%PYTHON_EXE%" "%SCRIPT_DIR%%SCRIPT_NAME%"

:: If the script crashes or closes, pause so you can see the error message
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    echo CRASH DETECTED or Script finished with errors.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    pause
)

endlocal