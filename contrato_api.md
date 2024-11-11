Contrato API de Microservicios de Adopciones
Este contrato API describe las interfaces de los tres microservicios utilizados en el sistema de adopciones. Cada servicio tiene su propósito específico y opera en conjunto para gestionar los usuarios, las mascotas y las adopciones.

Microservicio de Usuarios
Base URL: http://localhost:5000

Rutas
POST /login
Descripción: Autentica al usuario y genera un token JWT.
Parámetros:
correo_usuario (string, body, requerido)
Respuesta:
200 OK: { "token": "<jwt_token>" }
401 Unauthorized: { "error": "Credenciales inválidas" }
POST /agregar_usuario

Descripción: Crea un nuevo usuario y envía un mensaje a RabbitMQ con el evento de creación.
Parámetros:
nombre_usuario (string, body, requerido)
correo_usuario (string, body, requerido)
telefono_usuario (string, body, requerido)
direccion_usuario (string, body, requerido)

Respuesta:
201 Created: { "mensaje": "Usuario agregado exitosamente" }
400 Bad Request: { "error": "El correo del usuario ya existe" }
PUT /actualizar_usuario/<int:id_usuario>

Descripción: Actualiza la información del usuario por su ID.
Parámetros:
correo_usuario (string, body, requerido)
telefono_usuario (string, body, requerido)
direccion_usuario (string, body, requerido)

Respuesta:
200 OK: { "mensaje": "Datos del Usuario actualizado exitosamente" }
404 Not Found: { "error": "Usuario no encontrado" }
Microservicio de Mascotas
Base URL: http://localhost:5001

Rutas
POST /mascota
Descripción: Agrega una nueva mascota al sistema.
Parámetros:
nombre_mascota (string, body, requerido)
especie (string, body, requerido)
edad_mascota (int, body, requerido)
estado_mascota (string, body, requerido)
Respuesta:
201 Created: { "mensaje": "Mascota agregada correctamente" }
PUT /actualizar_mascota/<int:id_mascota>
Descripción: Actualiza la información de una mascota por su ID.
Parámetros:
edad_mascota (int, body, requerido)
estado_mascota (string, body, requerido)
Respuesta:
200 OK: { "mensaje": "Datos de la mascota actualizados exitosamente" }
404 Not Found: { "error": "No se encontró la mascota" }
GET /mascotas
Descripción: Obtiene la lista de mascotas, filtrando por estado si se proporciona.
Parámetros:
estado (string, query, opcional)
Respuesta:
200 OK: [ { "id_mascota": int, "nombre_mascota": string, "especie": string, "edad_mascota": int, "estado_mascota": string }, ... ]
GET /mascotas/<int:id_mascota>
Descripción: Obtiene la información de una mascota por su ID.
Respuesta:
200 OK: { "id_mascota": int, "nombre_mascota": string, "especie": string, "edad_mascota": int, "estado_mascota": string }
404 Not Found: { "error": "No se encontró la mascota" }
Microservicio de Adopciones
Base URL: http://localhost:5002

Rutas
GET /verificar_mascota/<int:mascota_id>
Descripción: Verifica si una mascota está disponible para adopción usando un Circuit Breaker para el servicio de mascotas.
Parámetros:
mascota_id (int, URL, requerido)
Respuesta:
200 OK: { "mensaje": "Mascota disponible para adopción" }
400 Bad Request: { "error": "Mascota no disponible" }
503 Service Unavailable: { "error": "Servicio Mascotas no disponible" }
POST /adopciones
Descripción: Crea un registro de adopción entre un usuario y una mascota.
Parámetros:
usuario_id (int, body, requerido)
mascota_id (int, body, requerido)
Respuesta:
201 Created: { "mensaje": "Adopción registrada exitosamente" }
400 Bad Request: { "error": "Missing parameter: <parameter>" }
Notas Generales
Cada servicio está configurado para comunicarse a través de RabbitMQ y puede lanzar mensajes a diferentes colas (usuario_creado, etc.) en caso de eventos importantes.
Los servicios utilizan tokens JWT para proteger ciertas rutas. Los tokens expiran después de una hora.
Los microservicios están conectados a bases de datos SQLite individuales y tienen una configuración de Circuit Breaker para manejar la resiliencia de las llamadas al servicio de mascotas.