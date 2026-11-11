# Procedencia de las evidencias

Los archivos que contienen "local" o "redis_real" muestran una ejecución real de la aplicación y Redis como procesos locales. No son capturas ni registros de contenedores Docker.

- pruebas_http_redis_real.json: nueve comprobaciones aprobadas sobre HTTP y Redis reales.
- datos_redis_real.json: identificadores y textos de las dos tareas de demostración.
- persistencia_redis_real.json: comparación tras reiniciar Redis local con AOF.
- interfaz_ejecucion_local.png: captura real de la aplicación local.
- salud_ejecucion_local.png: captura real de /salud.

Las evidencias de Docker se generan por separado: ejecutando VERIFICAR.bat o descargando el artefacto evidencias-dos-contenedores de GitHub Actions. No sustituirlas por las pruebas locales.
