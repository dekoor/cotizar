# app.py
# Importamos las librerías necesarias
import os
from flask import Flask, request, jsonify
from flask_cors import CORS # Aún la necesitamos para manejar OPTIONS
import requests

# Inicializamos la aplicación de Flask
app = Flask(__name__)

# Le decimos a Flask-CORS que maneje las peticiones OPTIONS (preflight)
# que los navegadores envían antes de la petición POST real.
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


# Definimos la URL del endpoint de cotización de Envia.com
ENVIA_API_URL = "https://api.envia.com/ship/rates"

# Leemos la API Key desde una variable de entorno para mayor seguridad.
API_KEY = os.environ.get('ENVIA_API_KEY')

# --- CORRECCIÓN DEFINITIVA DE CORS ---
# Esta función se ejecuta después de CADA petición.
# Agrega manualmente las cabeceras necesarias para evitar problemas de CORS.
@app.after_request
def after_request(response):
    header = response.headers
    # Permitimos el acceso desde cualquier dominio. Para más seguridad,
    # podrías cambiar '*' por 'https://dekoormx.com'.
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
    return response

# Creamos una ruta o endpoint "/api/cotizar" que aceptará peticiones POST
@app.route('/api/cotizar', methods=['POST'])
def cotizar_envio():
    """
    Este endpoint recibe los datos del envío desde el frontend,
    contacta la API de Envia.com y devuelve las cotizaciones.
    """
    # Verificamos si la API Key fue cargada correctamente
    if not API_KEY:
        return jsonify({"error": "La API Key no está configurada en el servidor."}), 500

    # Obtenemos los datos JSON que envió el frontend
    datos_envio = request.get_json()
    if not datos_envio:
        return jsonify({"error": "No se recibieron datos en la petición."}), 400

    # Creamos la cabecera de autorización
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Hacemos la petición POST a la API de Envia.com
        response = requests.post(ENVIA_API_URL, headers=headers, json=datos_envio)
        response.raise_for_status() 
        data = response.json()
        return jsonify(data)

    except requests.exceptions.HTTPError as err:
        error_details = {"error": f"Error en la API de Envia.com: {err.response.status_code}", "details": err.response.text}
        return jsonify(error_details), err.response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error de conexión: {e}"}), 503

# Esto permite ejecutar la aplicación directamente con "python app.py" para pruebas locales
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
