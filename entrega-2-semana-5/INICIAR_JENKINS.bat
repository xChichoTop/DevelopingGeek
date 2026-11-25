@echo off
cd /d "%~dp0"
docker compose -f ci/jenkins/compose.yaml up -d --build --wait --wait-timeout 300
if errorlevel 1 (
  docker compose -f ci/jenkins/compose.yaml logs --tail 60 jenkins motor
  pause
  exit /b 1
)
echo Contrasena inicial de Jenkins para el primer inicio:
docker compose -f ci/jenkins/compose.yaml exec -T jenkins cat /var/jenkins_home/secrets/initialAdminPassword
start "" http://localhost:8080
pause
