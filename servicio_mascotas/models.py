# import sqlite3

# def get_db_connection():
#     conn = sqlite3.connect("mascotas.db")
#     conn.row = sqlite3.Row
#     return conn

# def crear_tabla_mascota():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     #crear tabla mascotas 
#     cursor.execute('''
#     CREATE TABLE mascota(
#         id_mascota INTEGER PRIMARY KEY AUTOINCREMENT,
#         nombre_mascota TEXT NOT NULL,
#         especie TEXT NOT NULL,
#         edad_mascota INTEGER,
#         estado_mascota TEXT CHECK(estado in ('disponible',('adoptada')) DEFAULT 'disponible',
#         fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#     ''')