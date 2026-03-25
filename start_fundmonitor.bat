@echo off
REM Wait 15 seconds for system to initialize
timeout /t 15 /nobreak

cd /d C:\Users\dtial\Documents\GitHub\DTI-FUNDMONITORING-SYSTEM\DTI-Project\fundmonitor

:loop
"C:\Users\dtial\Documents\GitHub\DTI-FUNDMONITORING-SYSTEM\venv\Scripts\python.exe" -m waitress --host=0.0.0.0 --port=8000 fundmonitor.wsgi:application

echo Server stopped! Restarting in 5 seconds...
timeout /t 5
goto loop