@echo off
REM Launch script for the MCP (Model Context Protocol) server
REM This script provides a convenient way to start the dev-tool-mcp-server

setlocal enabledelayedexpansion

echo Checking virtual environment...

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"

REM Check if virtual environment exists, create if it doesn't
if not exist "%VENV_DIR%" (
    echo Virtual environment not found. Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo Failed to create virtual environment.
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Ensure pip is available and upgrade it
python -m ensurepip --upgrade
if !errorlevel! neq 0 (
    echo Failed to ensure pip is available.
    exit /b 1
)
pip install --upgrade pip
if !errorlevel! neq 0 (
    echo Failed to upgrade pip.
    exit /b 1
)

echo Installing dependencies from pyproject.toml...
REM Install the package in editable mode from the current directory
cd /d "%SCRIPT_DIR%"
pip install -e .
if !errorlevel! neq 0 (
    echo Failed to install dependencies.
    exit /b 1
)

echo Starting dev-tool-mcp-server...
echo This server provides web crawling, content extraction, and browser interaction features.
echo Press Ctrl+C to stop the server.
echo.

REM Run the Python server
python "%SCRIPT_DIR%mcp_server\server.py"

REM Check the exit status
if !errorlevel! equ 0 (
    echo Server stopped.
) else (
    echo Server stopped with error.
    exit /b 1
)

pause