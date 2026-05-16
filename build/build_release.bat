@echo off
setlocal

cd /d "%~dp0\.."

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

"%PYTHON_EXE%" -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name TPR_Concession_Method ^
  --distpath dist ^
  --workpath build\pyinstaller ^
  --specpath build ^
  main.py

if errorlevel 1 exit /b 1

echo Release build created: dist\TPR_Concession_Method.exe
endlocal
