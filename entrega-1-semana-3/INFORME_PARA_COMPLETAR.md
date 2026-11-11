# Entrega 1 - Semana 3
## Proyecto de software basado en herramientas de integración continua

Institución: Politécnico Grancolombiano  
Módulo: Énfasis Profesional I (Integración Continua)  
Integrantes: [Completar nombres]  
Docente: [Completar]  
Fecha: [Completar]  
Repositorio GitHub: [Pegar URL real]

## Introducción
Este proyecto propone un gestor de tareas para demostrar la separación de una aplicación en dos contenedores comunicados. La interfaz web permite registrar, consultar y eliminar pendientes; Redis almacena los datos en un servicio independiente. Esta estructura constituye una base para incorporar herramientas de integración continua en las siguientes entregas.

## Objetivo general
Implementar una aplicación mediante dos contenedores Docker conectados en una red común.

## Objetivos específicos
- Organizar el código fuente en un repositorio GitHub.
- Construir una imagen de la aplicación mediante Dockerfile.
- Ejecutar la aplicación y el almacenamiento con Docker Compose.
- Verificar la comunicación y la persistencia de las tareas.

## Descripción y alcance
El sistema permite crear tareas de hasta 120 caracteres, listarlas y eliminarlas. No incluye usuarios ni autenticación. Su alcance es una demostración local académica. Jenkins y las demás plataformas de integración se abordarán en entregas posteriores.

## Fundamentos
Una imagen define el software y las instrucciones con las que se crea un contenedor. Un contenedor es una instancia en ejecución que aísla procesos y dependencias. A diferencia de una máquina virtual, no requiere un sistema operativo invitado completo por cada instancia. Dockerfile describe la construcción de la imagen; Compose declara servicios, redes y volúmenes. Estos conceptos se relacionan con la lectura fundamental del escenario 3.

## Arquitectura
El navegador se conecta al puerto 5000 del equipo, que se redirige al servicio web. La aplicación se comunica con Redis usando el nombre de servicio datos y el puerto 6379. Ambos servicios pertenecen a la red proyecto. El volumen tareas conserva los datos al recrear los contenedores.

| Componente | Tecnología | Función |
|---|---|---|
| web | Python 3.12, Flask y Gunicorn | Interfaz y procesamiento de solicitudes |
| datos | Redis 7.4 | Almacenamiento de tareas |
| proyecto | Red bridge de Docker | Comunicación entre servicios |
| tareas | Volumen de Docker | Persistencia de Redis |

## Configuración
El Dockerfile instala las dependencias, copia el código y arranca Gunicorn en el puerto 5000 con un usuario sin privilegios administrativos. compose.yaml define los dos servicios. web espera a que la comprobación de salud de Redis responda correctamente. La variable REDIS_HOST usa datos, nombre que Docker resuelve dentro de la red. Redis utiliza persistencia AOF y un volumen.

## Procedimiento y evidencias
Completar esta sección después de ejecutar los pasos del README. No presentar resultados esperados como si ya se hubieran observado.

1. Preparación: [Versiones reales de Docker y Compose y sistema operativo].
2. Construcción: ejecutar docker compose up --build -d. [Insertar captura y describir resultado real].
3. Estado: ejecutar docker compose ps. [Insertar captura de los dos servicios].
4. Uso: crear dos tareas en localhost:5000. [Insertar captura].
5. Comunicación: ejecutar los comandos del apartado 3 del README. [Insertar capturas con los mismos registros en web y datos].
6. Persistencia: ejecutar docker compose down y docker compose up -d. [Insertar captura y describir si se conservaron las tareas].
7. GitHub: [Insertar URL y captura de los archivos publicados].

## Resultados
[Completar únicamente con lo observado. Indicar problemas encontrados y su solución. Si algo no funcionó, explicarlo y no afirmar que fue validado].

## Conclusiones para completar
- La separación de interfaz y almacenamiento permite [explicar a partir de la práctica].
- La comunicación entre contenedores se comprobó mediante [evidencia real].
- La persistencia se verificó al [resultado real].

## Referencias
Politécnico Grancolombiano. (s. f.). Proyecto de software basado en herramientas de integración continua. Guía del proyecto.

Oliveros Acosta, E. E. (s. f.). Máquinas virtuales y Dockers para construcción de ambientes. Politécnico Grancolombiano.

Docker. (s. f.). Networking in Compose. https://docs.docker.com/compose/how-tos/networking/

Docker. (s. f.). Control startup and shutdown order in Compose. https://docs.docker.com/compose/how-tos/startup-order/
