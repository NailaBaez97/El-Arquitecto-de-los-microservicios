from flask import Flask, request, jsonify
import sqlite3
import jwt  
from functools import wraps


app = Flask (__name__)


app.config['SECRET_KEY'] = 'clave_secreta_usuario'  

#Conexion con Db
def conexion_db():
    conn = sqlite3.connect('mascotas.db')
    conn.row_factory = sqlite3.Row
    return conn
#TOKEN
def token_requerido(f):
    @wraps(f) 
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token es requerido'}), 403
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token ha expirado'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalido'}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/ruta_protegida', methods=['GET'])
@token_requerido
def ruta_protegida():
    return jsonify({'mensaje': 'Tienes acceso a esta ruta protegida'})


#Agregar mascota
@app.route('/mascota', methods=['POST'])
def agregar_mascota():
    try:
        nombre_mascota = request.json['nombre_mascota']
        especie = request.json['especie']
        edad_mascota = request.json['edad_mascota']
        estado_mascota = request.json['estado_mascota']
    except KeyError as e:
        return jsonify({'error' : f'Missing Parameter: {str(e)}'}) , 400
    
    conn = conexion_db()
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO mascota (nombre_mascota, especie, edad_mascota, estado_mascota) VALUES (?,?,?,?)''', (nombre_mascota, especie, edad_mascota,estado_mascota))
    
    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Mascota agregada correctamente'}), 201

#Actualizar datos de la mascota
@app.route('/actualizar_mascota/<int:id_mascota>', methods=['PUT'])
def actualizar_mascota(id_mascota):
    try:
        edad_mascota = request.json['edad_mascota']
        estado_mascota = request.json['estado_mascota']
    except KeyError as e:
        return jsonify({'error' : f'Missing Parameter: {str(e)}'}), 400
    
    conn = conexion_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE mascota 
            SET  edad_mascota = ?, estado_mascota =?
            WHERE id_mascota = ?
        ''', (edad_mascota, estado_mascota, id_mascota))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'No se encontró la mascota'}), 404
        
        conn.commit()
        return jsonify({'mensaje':'Datos de la mascota actualizados exitosamente'}) , 200
    except sqlite3.Error as e:
        return jsonify({'error': f'Error al actualizar la mascota: {str(e)}'})
    finally:
        conn.close()

#VER MASCOTAS DISPONIBLES Y MASCOTAS ADOPTADAS
@app.route('/mascotas', methods=['GET'])
def obtener_mascotas():
    estado = request.args.get('estado') 
    conn = conexion_db()
    cursor = conn.cursor()

    if estado:
        cursor.execute('SELECT * FROM mascota WHERE estado_mascota = ?', (estado,))
    else:
        cursor.execute('SELECT * FROM mascota')

    mascotas = cursor.fetchall()
    conn.close()

    mascotas_list = [dict(mascota) for mascota in mascotas]
    return jsonify(mascotas_list), 200

# Ruta para obtener una mascota por su ID
@app.route('/mascotas/<int:id_mascota>', methods=['GET'])
def obtener_mascota_por_id(id_mascota):
    conn = conexion_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM mascota WHERE id_mascota = ?', (id_mascota,))
    mascota = cursor.fetchone()
    conn.close()

    if mascota is None:
        return jsonify({'error': 'No se encontró la mascota'}), 404

    mascota_dict = dict(mascota)  
    return jsonify(mascota_dict), 200




if __name__ == '__main__':
    app.run(port=5001,debug=True)