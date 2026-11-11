@echo off
cd /d "%~dp0"
docker info >nul 2>&1
if errorlevel 1 (
 echo Abre Docker Desktop y espera a que el motor este activo.
 pause
 exit /b 1
)
docker compose up --build -d --wait
if errorlevel 1 (
 echo No se pudo iniciar. Revisa los mensajes anteriores.
 pause
 exit /b 1
)
start http://localhost:5000
echo Aplicacion iniciada. Puedes cerrar esta ventana.
pause
