@echo off
cd /d "%~dp0"
docker compose -f ci/jenkins/compose.yaml down
pause
