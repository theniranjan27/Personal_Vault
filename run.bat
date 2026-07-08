@echo off
REM Run script for Private Personal Vault
REM Automatically uses the virtual environment python with flask run to avoid duplicate import issues

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    echo Starting Private Personal Vault using virtual environment (flask run)...
    venv\Scripts\python.exe -m flask run --host=0.0.0.0 --port=5000 --cert=adhoc
) else (
    echo Error: Virtual environment not found at venv
    echo Please create it using: python -m venv venv
    pause
)
