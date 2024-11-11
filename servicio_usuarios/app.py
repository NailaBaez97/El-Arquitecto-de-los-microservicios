from flask import Flask, request, jsonify
import sqlite3
import jwt  
import datetime
import pika
import json
app = Flask(__name__)

app.config['SECRET_KEY'] = 'clave_secreta' 

#Conexion a la Base de Datos 
def conexion_db():
    conn = sqlite3.connect('usuarios.db')
    conn.row_factory = sqlite3.Row
    return conn 


# Función para generar el token
def generar_token(usuario_id):
    payload = {
        'usuario_id': usuario_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Ruta de autenticación para generar el token
@app.route('/login', methods=['POST'])
def login():
    correo_usuario = request.json.get('correo_usuario')
    
    if correo_usuario == "usuario@ejemplo.com":  
        token = generar_token(1)  
        return jsonify({'token': token}), 200
    return jsonify({'error': 'Credenciales inválidas'}), 401

#Agregar usuario nuevo
# Conectar a RabbitMQ
def conexion_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    return channel

# Función para enviar un mensaje a la cola
def enviar_mensaje_a_rabbitmq(queue, message):
    channel = conexion_rabbitmq()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  
        )
    )
    print(f'Mensaje enviado a la cola: {message}')
    channel.close()

@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    try:
        nombre_usuario = request.json['nombre_usuario']
        correo_usuario = request.json['correo_usuario']
        telefono_usuario = request.json['telefono_usuario']
        direccion_usuario = request.json['direccion_usuario']
    except KeyError as e:
        return jsonify({'error': f'Missing Parameter: {str(e)}'}), 400
    
    conn = conexion_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO usuario (nombre_usuario, correo_usuario, telefono_usuario, direccion_usuario) VALUES (?,?,?,?)''', 
                (nombre_usuario, correo_usuario, telefono_usuario, direccion_usuario))
        conn.commit()
        
        # Enviar mensaje a RabbitMQ sobre la creación del nuevo usuario
        mensaje = {'usuario_id': cursor.lastrowid, 'accion': 'crear', 'usuario': nombre_usuario}
        enviar_mensaje_a_rabbitmq('usuario_creado', mensaje)

        return jsonify({'mensaje': 'Usuario agregado exitosamente'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'El correo del usuario ya existe'}), 400
    finally:
        conn.close()

#Actualizar datos del usuario 
@app.route('/actualizar_usuario/<int:id_usuario>', methods=['PUT'])
def actualizar_usuario(id_usuario):
    try:
        correo_usuario = request.json['correo_usuario']
        telefono_usuario = request.json['telefono_usuario']
        direccion_usuario = request.json['direccion_usuario']
        
    except KeyError as e:
        return jsonify({'error': f'Missing parameter: {str(e)}'}), 400

    conn = conexion_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE usuario
            SET  correo_usuario = ?, telefono_usuario = ?, direccion_usuario = ?
            WHERE id_usuario = ?
        ''', (correo_usuario, telefono_usuario, direccion_usuario, id_usuario))

        if cursor.rowcount == 0:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        conn.commit()
        return jsonify({'message': 'Datos del Usuario actualizado exitosamente'}), 200
    except sqlite3.IntegrityError:
        return jsonify({'error': 'El correo del usuario ya existe'}), 400
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

