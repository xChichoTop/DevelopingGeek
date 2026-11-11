# Gestor de tareas - Entrega 1, semana 3

Proyecto académico para Énfasis Profesional I (Integración Continua).
Permite agregar, consultar y eliminar tareas. Usa exactamente dos servicios:
- `web`: aplicación Python/Flask, imagen construida con Dockerfile.
- `datos`: Redis, base de datos clave-valor, imagen oficial.

La comunicación ocurre entre `web` y `datos:6379` en la red `proyecto`.
Dentro de web, localhost sería el propio contenedor: por eso REDIS_HOST es datos.
Redis no publica puertos al equipo. El navegador accede a web en localhost:5000.
El volumen `tareas` conserva los datos al recrear contenedores.

## 1. Preparar el computador (Windows)
Instala Docker Desktop desde https://www.docker.com/products/docker-desktop/ .
Sigue sus indicaciones de WSL 2/virtualización si las solicita y reinicia cuando corresponda.
Abre Docker Desktop y espera a que el motor esté activo.
Extrae este ZIP. Abre la carpeta que contiene compose.yaml en el Explorador,
escribe `powershell` en la barra de direcciones y presiona Enter.
Comprueba:

```powershell
docker --version
docker compose version
```

## Atajo para Windows
Con Docker Desktop abierto, haz doble clic en INICIAR.bat.
Luego puedes hacer doble clic en VERIFICAR.bat para guardar registros reales en evidencias.
DETENER.bat apaga los contenedores sin borrar las tareas.
Si usas otro puerto, abre manualmente la dirección que hayas configurado.

## 2. Construir e iniciar
En esa misma carpeta:

```powershell
docker compose up --build -d
docker compose ps
```

La primera ejecución necesita Internet para descargar imágenes y dependencias.
Abre http://localhost:5000 . Agrega dos tareas de prueba.

## 3. Comprobar la comunicación

```powershell
docker compose exec web python -c "from app import db; print(db.ping()); print(db.hgetall('tareas'))"
docker compose exec datos redis-cli HGETALL tareas
```

El primer comando debe mostrar True y las tareas. El segundo debe mostrar
los mismos identificadores y títulos. Son resultados esperados: obtén tus propias evidencias.
Abre también http://localhost:5000/salud : debe indicar estado ok.

## 4. Comprobar persistencia

```powershell
docker compose down
docker compose up -d
```

Vuelve al navegador: las tareas deben permanecer. No uses `down -v`, porque elimina el volumen.
Para detener el proyecto después de la demostración: `docker compose down`.

## 5. Subir a GitHub sin usar Git
1. Ingresa a tu cuenta de https://github.com . Si no tienes cuenta, créala.
2. Crea un repositorio llamado `gestor-tareas-integracion-continua`.
3. Elige la visibilidad de acuerdo con la indicación del docente.
4. Usa “uploading an existing file” o “Add file > Upload files”.
5. Sube los archivos y la carpeta templates, no el ZIP. Dockerfile y compose.yaml
   deben quedar en la raíz. Incluye .gitignore y .dockerignore (pueden estar ocultos).
6. Guarda los cambios con el mensaje “Entrega 1: aplicación y dos contenedores comunicados”.
7. Copia la dirección real del repositorio al informe.

## 6. Evidencias que debes capturar
- Repositorio de GitHub mostrando los archivos y el commit.
- `docker compose up --build -d`: construcción e inicio sin errores.
- `docker compose ps`: los dos servicios activos y saludables.
- Navegador con dos tareas creadas.
- Los dos comandos de comunicación con los mismos datos.
- Persistencia después de detener y volver a iniciar.

## Dificultades frecuentes
- No conecta con Docker: abre Docker Desktop y espera el inicio del motor.
- Puerto 5000 ocupado: cambia en compose.yaml solo el primer 5000 por 5001
  (`127.0.0.1:5001:5000`), ejecuta `docker compose up -d` y abre localhost:5001.
- Error de descarga: verifica conexión a Internet y vuelve a ejecutar el inicio.
- Para diagnosticar: `docker compose logs web datos`.
- Si modificas app.py, reconstruye con `docker compose up --build -d`.

## Prueba automática
Con los contenedores iniciados, ejecuta `docker compose exec -T web python comprobar.py`.
La prueba crea registros temporales, valida HTTP y la lectura directa de Redis y elimina sus registros al terminar.

## Estado de validación
El archivo VALIDACION.md registra qué se verificó al preparar el proyecto.
No se incluyen capturas ficticias ni se afirma que GitHub ya esté publicado.
Este ejemplo es local y académico; no incluye autenticación para publicarlo en Internet.

## Fuentes
- Politécnico Grancolombiano. Guía “Proyecto de software basado en herramientas de integración continua”, entrega 1, semana 3.
- Oliveros Acosta, Eduardo Enrique. “Máquinas virtuales y Dockers para construcción de ambientes”, lectura fundamental, escenario 3, Politécnico Grancolombiano.
- Docker. Networking in Compose. https://docs.docker.com/compose/how-tos/networking/
- Docker. Control startup and shutdown order in Compose. https://docs.docker.com/compose/how-tos/startup-order/
- Docker. Docker Compose Quickstart. https://docs.docker.com/compose/gettingstarted/

## Comprobar Docker desde GitHub Actions
El repositorio incluye `.github/workflows/verificar-docker.yml`.
Al subirlo a main o master, GitHub puede ejecutar la construcción y comprobación en un runner Linux.
Abre Actions, selecciona “Comprobar dos contenedores Docker” y revisa el resultado real.
También puedes iniciarlo con Run workflow, gracias a workflow_dispatch.
El flujo genera el artefacto `evidencias-dos-contenedores` con construcción, estado, pruebas y persistencia.
Si no aparece el flujo, comprueba que subiste la carpeta .github completa y que Actions esté habilitado.
Un archivo de flujo preparado no equivale a una ejecución aprobada.
