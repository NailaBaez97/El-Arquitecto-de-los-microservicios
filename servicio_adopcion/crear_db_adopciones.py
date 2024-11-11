import sqlite3

def get_db_connection():
    conn = sqlite3.connect("adopciones.db")
    conn.row_factory = sqlite3.Row
    return conn

def crear_tabla_adopcion():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Crear tabla adopcion
    cursor.execute('''
    CREATE TABLE adopcion(
        id_adopcion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        id_mascota INTEGER NOT NULL,
        fecha_adopcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario),
        FOREIGN KEY (id_mascota) REFERENCES mascotas (id_mascota)
    );
    ''')
    conn.commit()
    conn.close()

    return "Tabla creada exitosamente"

crear_tabla_adopcion()
