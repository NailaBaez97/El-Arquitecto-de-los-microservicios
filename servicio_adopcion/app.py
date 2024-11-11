from flask import Flask, request, jsonify, json
import sqlite3
import requests
from circuitbreaker import circuit
import requests
import jwt
from functools import wraps
import pika

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_usuario' 

# Conexion a la base de datos
def conexion_db():
    conn = sqlite3.connect('adopciones.db')
    conn.row_factory = sqlite3.Row
    return conn

# Configuración del Circuit Breaker para llamadas al microservicio de Mascotas
@circuit(failure_threshold=3, recovery_timeout=30, expected_exception=Exception)
def verificar_mascota_con_circuit_breaker(id_mascota):
    response = requests.get(f'http://localhost:5001/mascotas/{id_mascota}')
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Servicio Mascotas no disponible")

# @app.route('/verificar_mascota/<int:mascota_id>', methods=['GET'])
# def verificar_mascota(mascota_id):
#     try:
#         mascota = verificar_mascota_con_circuit_breaker(mascota_id)
#         if mascota['estado_mascota'] == 'disponible':
#             return jsonify({'message': 'Mascota disponible para adopcion'}), 200
#         else:
#             return jsonify({'error': 'Mascota no disponible'}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 503



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


# Crear adopcion
@app.route('/adopciones', methods=['POST'])
def crear_adopcion():
    try:
        id_usuario = request.json['id_usuario']
        id_mascota = request.json['id_mascota']
    except KeyError as e:
        return jsonify({'error': f'Missing parameter: {str(e)}'}), 400

    conn = conexion_db()
    cursor = conn.cursor()

    
    cursor.execute('''
        INSERT INTO adopcion (id_usuario, id_mascota, fecha_adopcion)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (id_usuario, id_mascota))

    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Adopcion registrada exitosamente'}), 201
    

# Conectar a RabbitMQ
def conexion_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    return channel

# Función para escuchar mensajes de RabbitMQ
def escuchar_mensajes_rabbitmq(queue):
    channel = conexion_rabbitmq()
    channel.queue_declare(queue=queue, durable=True)
    
    def callback(ch, method, properties, body):
        mensaje = json.loads(body)
        print(f"Recibido mensaje: {mensaje}")
        if mensaje['accion'] == 'crear':
            print(f"Usuario creado con ID {mensaje['id_usuario']}, nombre: {mensaje['usuario']}")

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
    print(f'Esperando mensajes en la cola {queue}. Para salir presiona CTRL+C')
    channel.start_consuming()




if __name__ == '__main__':
    app.run(port= 5002,debug=True)
    escuchar_mensajes_rabbitmq('usuario_creado')# Iniciar el servicio para escuchar mensajes de RabbitMQ
    


