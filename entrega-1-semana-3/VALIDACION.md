# Verificación del proyecto

## Declaración del autor

Analicé y comprobé el proyecto que presento como entrega individual de la semana 3.
Revisé el código fuente y la configuración de los servicios web y datos.

Johan Alvarez Parra  
10 de noviembre de 2026

## Pruebas automáticas documentadas

Se incluyen nueve comprobaciones aprobadas sobre HTTP con Gunicorn y un servidor
Redis 6.2.14 ejecutado como proceso local. El ensayo de reinicio conservó los dos
registros mediante persistencia AOF.

Los archivos `pruebas_http_redis_real.json`, `datos_redis_real.json` y
`persistencia_redis_real.json` corresponden a ese ensayo local. Las capturas con
`ejecucion_local` en su nombre pertenecen al mismo entorno. Estos registros no se
presentan como resultados de una ejecución Docker.

## Configuración de los contenedores

`compose.yaml` define los servicios web y datos, su red compartida y el volumen
persistente de Redis. La aplicación utiliza REDIS_HOST=datos y el puerto 6379.
La imagen del almacenamiento configurada es Redis 7.4 Alpine.

## Reproducción de las comprobaciones

`comprobar.py` verifica las operaciones HTTP y el acceso al almacenamiento.
`PREPARAR_ENTREGA.bat` automatiza además la construcción, el estado de los dos
servicios, la red, la recreación de contenedores y la persistencia.
Los registros que genera ese programa corresponden a la ejecución en la que
realmente se utilice. La declaración del autor se distingue de esos registros.
