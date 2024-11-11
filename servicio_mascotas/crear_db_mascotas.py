import sqlite3

def get_db_connection():
    conn = sqlite3.connect("mascotas.db")
    conn.row_factory = sqlite3.Row 
    return conn

def crear_tabla_mascota():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Crear tabla mascota
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mascota (
        id_mascota INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_mascota TEXT NOT NULL,
        especie TEXT NOT NULL,
        edad_mascota TEXT NOT NULL,
        estado_mascota TEXT CHECK(estado_mascota IN ('disponible', 'adoptada')) DEFAULT 'disponible',
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    conn.commit()
    conn.close()

    return "Tabla creada exitosamente"

crear_tabla_mascota()
