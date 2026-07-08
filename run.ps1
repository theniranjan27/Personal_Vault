# Run script for Private Personal Vault
# Automatically uses the virtual environment python with flask run to avoid duplicate import issues

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (Test-Path ".\venv\Scripts\python.exe") {
    Write-Host "Starting Private Personal Vault using virtual environment (flask run)..." -ForegroundColor Green
    .\venv\Scripts\python.exe -m flask run --host=0.0.0.0 --port=5000 --cert=adhoc
} else {
    Write-Host "Error: Virtual environment not found at .\venv" -ForegroundColor Red
    Write-Host "Please create it using: python -m venv venv" -ForegroundColor Yellow
}
