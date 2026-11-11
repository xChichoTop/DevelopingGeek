# Gestor de tareas con Docker

**Estudiante:** Johan Alvarez Parra  
**Docente:** Edwar Reyes  
**Institución:** Politécnico Grancolombiano  
**Módulo:** Énfasis Profesional I (Integración Continua)  
**Actividad:** Entrega 1, semana 3. Modalidad individual.

## Descripción

Aplicación web para registrar, consultar y eliminar tareas. La solución separa el
procesamiento HTTP y el almacenamiento mediante dos servicios Docker Compose.

| Servicio | Tecnología | Función |
|---|---|---|
| web | Python 3.12, Flask y Gunicorn | Interfaz web y procesamiento de solicitudes |
| datos | Redis 7.4 Alpine | Almacenamiento de las tareas |

La comunicación utiliza `datos:6379` en la red `proyecto`. El servicio web publica
el puerto `127.0.0.1:5000`; Redis se mantiene en la red interna de los servicios.
El volumen `tareas` conserva los archivos de persistencia AOF de Redis.

## Requisitos

- Docker Engine o Docker Desktop con contenedores Linux.
- Docker Compose con soporte para `--wait`.
- Conexión a Internet para la descarga inicial de imágenes y dependencias.

## Ejecución

Desde la carpeta que contiene `compose.yaml`:

```powershell
docker compose up --build -d --wait
docker compose ps
```

Interfaz: `http://localhost:5000`. Estado de conexión: `http://localhost:5000/salud`.

## Pruebas

```powershell
docker compose exec -T web python comprobar.py
docker compose exec -T datos redis-cli HGETALL tareas
```

`comprobar.py` realiza nueve comprobaciones sobre HTTP y Redis: disponibilidad,
conexión, validación de entradas, creación, lectura directa, presentación,
escape de HTML y eliminación. Los registros temporales de prueba se eliminan
al finalizar.

La persistencia se verifica conservando una tarea después de recrear los servicios:

```powershell
docker compose down
docker compose up -d --wait
```

`docker compose down -v` elimina el volumen y sus datos.

## Automatización en Windows

`PREPARAR_ENTREGA.bat` ejecuta la comprobación completa del proyecto: construcción,
estado saludable de ambos contenedores, red compartida, pruebas HTTP y Redis,
recreación de los servicios y persistencia. Una ejecución satisfactoria genera un
paquete con el informe, el código y los registros de esa ejecución.

`INICIAR.bat`, `VERIFICAR.bat` y `DETENER.bat` permiten ejecutar las operaciones
básicas por separado. Los resultados y su alcance se documentan en `VALIDACION.md`.

## Estructura

- `app.py`: rutas HTTP y acceso a Redis.
- `templates/index.html`: interfaz web.
- `Dockerfile`: imagen de la aplicación.
- `compose.yaml`: servicios, red, volumen y comprobaciones de salud.
- `comprobar.py`: pruebas de funcionamiento y comunicación.
- `evidencias/`: registros y capturas identificados por su entorno de ejecución.
- `informe/`: informe académico en Word y PDF.

## Referencias

- Politécnico Grancolombiano. Guía del proyecto, entrega 1, semana 3.
- Oliveros Acosta, E. E. *Máquinas virtuales y Dockers para construcción de ambientes*. Lectura fundamental del escenario 3.
- Docker. [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/).
- Docker. [Control startup and shutdown order in Compose](https://docs.docker.com/compose/how-tos/startup-order/).
