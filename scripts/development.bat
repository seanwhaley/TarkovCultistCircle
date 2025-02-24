@echo off
setlocal enabledelayedexpansion

REM Get absolute path to project root
set "PROJECT_ROOT=%~dp0.."
cd "%PROJECT_ROOT%"

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found! Please run setup_windows.bat first.
    exit /b 1
)

REM Activate virtual environment if not already activated
if "%VIRTUAL_ENV%"=="" (
    call .venv\Scripts\activate.bat
)

REM Set up Python path to include src directory
set "PYTHONPATH=%PROJECT_ROOT%\src;%PYTHONPATH%"

REM Run the application
python wsgi.py
