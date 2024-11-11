import sqlite3


# Conexión a la Base de Datos 
def conexion_db():
    conn = sqlite3.connect('usuarios.db')
    conn.row_factory = sqlite3.Row
    return conn 

# Crear la tabla de usuarios si no existe
def crear_tablas_usuario():
    conn = conexion_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT NOT NULL,
            correo_usuario TEXT NOT NULL UNIQUE,
            telefono_usuario NUMERIC NOT NULL,
            direccion_usuario TEXT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

    return "Tabla creada exitosamente"

# Llama a la función para crear la tabla al importar este archivo
crear_tablas_usuario()
