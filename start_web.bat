@echo off
cd /d "%~dp0web"
dotnet run --urls "http://localhost:5000"
pause
