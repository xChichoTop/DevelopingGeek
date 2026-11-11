# Estado real de validación

## Realizado
- Revisada la configuración YAML: dos servicios, red común, host datos y volumen tareas.
- Ejecutadas nueve comprobaciones sobre HTTP con Gunicorn y un servidor Redis real local: interfaz, conexión, entradas vacías, longitud, creación, lectura directa en Redis, consulta visible, escape HTML y eliminación.
- Reiniciado el servidor Redis real y confirmada la conservación de los dos registros mediante AOF.
- Obtenidas capturas reales de la interfaz y del endpoint de salud en esa ejecución local.

## Alcance de estas pruebas
Las evidencias de esta carpeta proceden de procesos locales, sin Docker. El servidor Redis de la prueba local es 6.2.14; compose.yaml solicita Redis 7.4 Alpine. La prueba local no demuestra la construcción de la imagen 7.4, la red de Docker ni el volumen de Docker.

## GitHub
El código está publicado en https://github.com/xChichoTop/DevelopingGeek/tree/entrega-1-semana-3/entrega-1-semana-3 .
La ejecución Actions 42946871111 terminó sin iniciar el runner ni ejecutar pasos. No hay resultados Docker aprobados.

## Pendiente
- Construir e iniciar la composición en un motor Docker y comprobar ambos servicios.
- Verificar comunicación entre contenedores y persistencia del volumen en Docker.


## Automatización preparada
.github/workflows/verificar-docker.yml permite ejecutar esas comprobaciones de Docker en GitHub Actions después de subir el repositorio. El primer intento del flujo no inició los pasos de construcción. Genera un artefacto llamado evidencias-dos-contenedores con registros reales. También puede validarse en Windows mediante INICIAR.bat y VERIFICAR.bat.
