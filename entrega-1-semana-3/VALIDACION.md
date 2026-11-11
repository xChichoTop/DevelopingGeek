# Validación del proyecto

## Pruebas locales

La aplicación se comprobó mediante solicitudes HTTP a Gunicorn y un servidor
Redis 6.2.14 ejecutado como proceso local. Se aprobaron nueve pruebas de
funcionamiento y se verificó la conservación de dos registros tras reiniciar
Redis con persistencia AOF.

Los archivos `pruebas_http_redis_real.json`, `datos_redis_real.json` y
`persistencia_redis_real.json` registran esos resultados. Las imágenes cuyos
nombres contienen `ejecucion_local` corresponden a ese mismo entorno.

## Alcance

Las pruebas locales no acreditan la construcción de imágenes, la red ni el
volumen de Docker. `compose.yaml` configura Redis 7.4 Alpine; esa imagen requiere
su propia ejecución y comprobación. No se dispone de un resultado Docker
aprobado en las evidencias publicadas actualmente.

## Comprobación en contenedores

`PREPARAR_ENTREGA.bat` comprueba la configuración, construye la imagen web e inicia
los dos servicios. Verifica sus estados, la red compartida, las nueve pruebas,
la lectura directa de Redis y la persistencia después de recrear los contenedores.

Una ejecución satisfactoria genera `resultado_docker.json`, con fecha,
identificadores de contenedor, red, volumen y resultados. Los registros se
incluyen en la carpeta `evidencias_docker` del paquete generado.

## GitHub Actions

El flujo `.github/workflows/verificar-docker.yml` define la construcción y las
comprobaciones en un runner Linux. La ejecución inicial 42946871111 no inició
el runner ni ejecutó los pasos; no constituye evidencia de pruebas aprobadas.
