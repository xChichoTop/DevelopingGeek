@echo off
cd /d "%~dp0"
if not exist evidencias mkdir evidencias
docker compose ps > evidencias\estado_contenedores.txt 2>&1
docker compose exec -T web python comprobar.py > evidencias\pruebas_docker.json 2> evidencias\errores_pruebas.txt
if errorlevel 1 (
 echo La comprobacion fallo. Revisa evidencias\errores_pruebas.txt
 type evidencias\errores_pruebas.txt
 pause
 exit /b 1
)
docker compose exec -T datos redis-cli HGETALL tareas > evidencias\datos_redis.txt 2>&1
docker compose logs --no-color > evidencias\registros_docker.txt 2>&1
type evidencias\estado_contenedores.txt
type evidencias\pruebas_docker.json
echo Evidencias reales guardadas en la carpeta evidencias.
pause
