# Alcance de las evidencias

- `jenkins/validacion-Jenkinsfile.txt`: respuesta del linter declarativo de Jenkins para el Jenkinsfile principal. Valida sintaxis y referencias a pasos disponibles; no ejecuta Docker.
- `jenkins/ejecucion-jenkins.json`: resumen de la ejecución real del job de verificación local, con versión, resultado y conteos JUnit.
- `jenkins/consola-validacion-local.txt`: consola de ese job.
- `jenkins/junit-publicado.json`: resultados consultados en la API de Jenkins después de publicar JUnit.
- `validacion-jenkins/`: informes XML y JSON y registros de Gunicorn y Redis producidos por el job local.
- `configuracion-compose.json`: resultado de validar los tres archivos Compose con el cliente real.

La verificación local usa Redis 6.2.14 como proceso independiente; los archivos Docker declaran Redis 7.4 Alpine. El núcleo de Jenkins ejecutado fue 2.580.2 con Java 21. La persistencia se comprobó mediante el reinicio del proceso local sobre los mismos archivos AOF. El pipeline principal está configurado para comprobarla al recrear el contenedor Redis y conservar su volumen.

No se aporta una ejecución completa de Docker ni una consulta automática real a GitHub desde el job de verificación local. Estos puntos se comprueban al ejecutar el pipeline principal en el laboratorio descrito en el informe.
