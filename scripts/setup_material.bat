@echo off
echo Installing Material Design dependencies...

:: Navigate to static directory
cd ..\src\static

:: Install dependencies
call npm install

:: Build CSS
call npm run build

echo Material Design dependencies installed and built successfully
pause