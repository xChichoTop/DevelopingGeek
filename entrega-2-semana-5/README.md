# Integración continua del gestor de tareas con Jenkins

**Entrega 2 · Semana 5**  
**Estudiante:** Johan Alvarez Parra  
**Docente:** Edwar Reyes  
**Módulo:** Énfasis Profesional I (Integración Continua)  
**Institución:** Politécnico Grancolombiano

El proyecto continúa la aplicación Flask y Redis de la semana 3. Jenkins coordina la obtención del código, la validación de Compose, la construcción de la imagen, el inicio de los servicios, las pruebas y la publicación de resultados. El documento principal está en `informe/`.

## Requisitos del laboratorio

- Docker Desktop iniciado en modo de contenedores Linux, o Docker Engine en Linux.
- Plugin Docker Compose con soporte de `up --wait` y `cp`.
- Conexión a GitHub, Docker Hub, al repositorio de Docker y al centro de actualizaciones de Jenkins.
- Recursos recomendados para el equipo completo: 8 GB de RAM y 50 GB de espacio libre. Es una estimación para este laboratorio, no un mínimo universal de Jenkins.
- Puerto local 8080 disponible para Jenkins y, si se ejecuta la aplicación manualmente, 5000 disponible.

La imagen de Jenkins incluye Java 21. No es necesario instalar Java ni Python en Windows para la ejecución con Docker.

## Iniciar Jenkins

Desde la carpeta que contiene este README:

```powershell
docker compose -f ci/jenkins/compose.yaml up -d --build --wait --wait-timeout 300
docker compose -f ci/jenkins/compose.yaml exec -T jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

En Windows también se puede ejecutar `INICIAR_JENKINS.bat`. El primer arranque descarga las imágenes y los plugins y puede tardar varios minutos. Si vence el tiempo de espera, consultar `docker compose -f ci/jenkins/compose.yaml logs jenkins motor` y repetir `up` una vez resuelto el motivo.

1. Abrir <http://localhost:8080> e ingresar la contraseña inicial mostrada en la terminal.
2. Completar el asistente y crear la cuenta administradora. Los plugins requeridos ya se incluyen en la imagen; si el asistente ofrece instalar los recomendados, también se puede usar esa opción.
3. En **Manage Jenkins → Nodes → Built-In Node → Configure**, establecer **1 executor** para este laboratorio individual y guardar.
4. En **Manage Jenkins → Plugins → Installed**, comprobar Pipeline, Git, JUnit y Timestamper.
5. En **New Item**, crear `gestor-tareas-semana-5` de tipo **Pipeline**.
6. En **Pipeline → Definition**, seleccionar **Pipeline script from SCM** y SCM **Git**.
7. Repository URL: `https://github.com/xChichoTop/DevelopingGeek.git`.
8. Credentials: ninguna, mientras el repositorio sea público. Si se cambia a privado, registrar una credencial de lectura en Jenkins.
9. Branch Specifier: `*/entrega-2-semana-5`.
10. Script Path: `entrega-2-semana-5/Jenkinsfile`.
11. Guardar y ejecutar **Build Now**. Después de esa primera ejecución queda registrado el sondeo de cambios cada cinco minutos.

El sondeo requiere que Jenkins esté encendido y con conexión a GitHub. La configuración local no necesita una URL pública ni un webhook.

## Resultado del pipeline con Docker

El pipeline usa `compose.ci.yaml` con un nombre de proyecto derivado de cada ejecución. Construye la aplicación, inicia dos servicios sin publicar puertos al equipo anfitrión y ejecuta 12 pruebas HTTP y Redis. Después recrea únicamente Redis, conserva el volumen y verifica un registro adicional. Publica los informes JUnit, las versiones, el commit y los registros en los artefactos de la ejecución.

Un error de construcción, arranque o prueba interrumpe las etapas siguientes. El bloque final recoge los registros disponibles y elimina los contenedores, la red y el volumen **del proyecto de pruebas de esa ejecución**. Si faltan los dos informes JUnit obligatorios o alguno de ellos al terminar las etapas correctamente, la ejecución también falla. La aplicación manual utiliza otro proyecto y otro volumen.

## Ejecutar la aplicación manualmente

```powershell
docker compose -f compose.yaml up -d --build --wait --wait-timeout 120
```

Abrir <http://localhost:5000>. Para detener sin eliminar las tareas:

```powershell
docker compose -f compose.yaml down
```

Para detener Jenkins y su motor conservando los datos:

```powershell
docker compose -f ci/jenkins/compose.yaml down
```

Los volúmenes conservan la configuración de Jenkins y las tareas. `down --volumes` elimina volúmenes; se reserva para el entorno efímero de pruebas que administra el Jenkinsfile.

## Verificación registrada

En `evidencias/` se incluyen la validación real del Jenkinsfile con el linter de Jenkins 2.580.2 y una ejecución satisfactoria de un pipeline de comprobación local. Esta ejecución publicó 13 pruebas mediante JUnit y utilizó procesos reales de Gunicorn y Redis, sin contenedores y sin checkout SCM. El archivo `ci/Jenkinsfile.local` contiene ese pipeline de comprobación previa.

Se realizó una segunda ejecución en Jenkins, `Verificacion-GitHub-semana-5`, que obtuvo `ci/Jenkinsfile.local` y el código desde la rama `entrega-2-semana-5` en GitHub (commit `36bfe0b7d906e3722bd9a0bb45d5b9ba3c3f0673`). Finalizó con `SUCCESS` y publicó 13 pruebas aprobadas, sin fallas ni omisiones. Las evidencias están en `evidencias/jenkins-github/`. La ejecución utilizó procesos locales; las actualizaciones posteriores corresponden a documentación y evidencias.

La ejecución completa del Jenkinsfile principal con Docker debe comprobarse en el equipo del laboratorio. La validación de sintaxis y los resultados locales no sustituyen esa ejecución. Los archivos de evidencia identifican el alcance y las versiones utilizadas.

Para repetir la comprobación previa en un nodo Linux con Python 3.12, dependencias de `requirements.txt` y `redis-server` en PATH:

```bash
python ci/validar_local.py --salida reportes/local
```

## Decisiones de configuración

Jenkins usa la imagen oficial `jenkins/jenkins:2.580.2-jdk21`, ampliada con Docker CLI, Compose y cuatro plugins. Un servicio `docker:dind` proporciona el motor por TLS en el puerto interno 2376. Solo la interfaz de Jenkins se publica, en la dirección local del equipo. Redis no expone su puerto.

El motor Docker requiere modo privilegiado. Esta configuración corresponde a un laboratorio individual con código de confianza. Para una instalación compartida se deben separar los agentes del controlador, restringir los permisos y revisar el aislamiento del motor. No se incluyen contraseñas, tokens ni claves de acceso en el repositorio.

El núcleo de Jenkins y las dependencias principales de Python tienen versiones explícitas. Los plugins, el motor y algunas imágenes base se resuelven al construir o descargar. Para repetir exactamente una instalación se deben conservar sus versiones y digests; el pipeline archiva las versiones del motor y de Compose y el commit construido.
