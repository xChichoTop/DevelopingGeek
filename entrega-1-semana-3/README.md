# Gestor de tareas con dos contenedores Docker

**Estudiante:** Johan Alvarez Parra  
**Docente:** Edwar Reyes  
**Institución:** Politécnico Grancolombiano  
**Módulo:** Énfasis Profesional I (Integración Continua)  
**Entrega:** 1, semana 3. Trabajo individual.

La aplicación permite agregar, consultar y eliminar tareas. Tiene dos servicios:

| Servicio | Tecnología | Función |
|---|---|---|
| web | Python 3.12, Flask y Gunicorn | Procesar solicitudes HTTP |
| datos | Redis 7.4 Alpine | Guardar las tareas |

Los servicios comparten la red `proyecto`. Web se conecta a `datos:6379`.
El navegador accede a `http://localhost:5000`. Redis no publica puertos al equipo.
El volumen `tareas` conserva los archivos AOF del almacenamiento.

## Ejecución en Windows

El proyecto requiere Docker Desktop con el motor iniciado.
`INICIAR.bat` construye e inicia la aplicación. `VERIFICAR.bat` realiza la prueba
básica. `DETENER.bat` apaga los servicios sin eliminar los datos.

`PREPARAR_ENTREGA.bat` ejecuta la comprobación completa. Verifica dos servicios
saludables, red compartida, nueve pruebas, lectura directa de Redis, recreación
de contenedores y conservación de un registro. Si todos los controles pasan,
genera un ZIP con el informe, el código y las evidencias de ejecución. Si un paso
falla, guarda un registro ERROR.txt y detiene el proceso.

## Ejecución manual

En una terminal abierta en la carpeta del proyecto:

```powershell
docker compose up --build -d --wait
docker compose ps
docker compose exec -T web python comprobar.py
docker compose exec -T datos redis-cli HGETALL tareas
```

Para comprobar persistencia, registrar una tarea, ejecutar los siguientes comandos
y volver a consultar la página:

```powershell
docker compose down
docker compose up -d --wait
```

No usar `down -v` si se desea conservar los datos: elimina el volumen.

## Código publicado

[Carpeta de la entrega en GitHub](https://github.com/xChichoTop/DevelopingGeek/tree/entrega-1-semana-3/entrega-1-semana-3).
La entrega está en una rama independiente; master conserva el proyecto anterior.
Al clonar el repositorio, seleccionar la rama `entrega-1-semana-3` y entrar a la
carpeta `entrega-1-semana-3` antes de ejecutar Docker Compose.

No es necesario crear otro repositorio ni volver a subir el código a GitHub.

## Estado de las pruebas

`VALIDACION.md` distingue las pruebas locales de las de Docker. Se incluyen nueve
comprobaciones aprobadas con Redis real como proceso local y un ensayo de reinicio.
Las capturas locales no se presentan como evidencia de contenedores.

El flujo de GitHub Actions está preparado, pero su primer intento no inició el
runner. No se dispone de una validación Docker aprobada en el entorno de preparación.
`PREPARAR_ENTREGA.bat` obtiene esa evidencia en el computador donde se ejecute Docker.
La automatización fue revisada por separado; eso tampoco equivale a ejecutar Docker.

## Solución de problemas

- Si Docker no responde, abrir Docker Desktop y esperar a que el motor esté activo.
- Si el puerto 5000 está ocupado, cambiar en `compose.yaml` la publicación a
  `127.0.0.1:5001:5000`. La aplicación se abrirá manualmente en localhost:5001.
  La comprobación interna continúa usando el puerto 5000 del contenedor.
- Si falla la descarga de imágenes, revisar Internet y repetir el inicio.
- Consultar `docker compose logs web datos` para diagnosticar errores.
- Después de modificar Python, reconstruir con `docker compose up --build -d --wait`.

## Fuentes

- Politécnico Grancolombiano. Guía del proyecto, entrega 1, semana 3.
- Oliveros Acosta, E. E. Lectura fundamental del escenario 3, *Máquinas virtuales y Dockers para construcción de ambientes*.
- Docker. [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/).
- Docker. [Control startup and shutdown order in Compose](https://docs.docker.com/compose/how-tos/startup-order/).
