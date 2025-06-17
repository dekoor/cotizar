# app.py
# Importamos las librerías necesarias
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Inicializamos la aplicación de Flask
app = Flask(__name__)

# --- CORRECCIÓN DE CORS ---
# Configuramos CORS para ser más explícito.
# Esto le dice a Flask que permita peticiones desde CUALQUIER origen (*)
# específicamente para las rutas que empiecen con /api/.
CORS(app, resources={r"/api/*": {"origins": "*"}})


# Definimos la URL del endpoint de cotización de Envia.com
ENVIA_API_URL = "https://api.envia.com/ship/rates"

# Leemos la API Key desde una variable de entorno para mayor seguridad.
API_KEY = os.environ.get('ENVIA_API_KEY')

# Creamos una ruta o endpoint "/api/cotizar" que aceptará peticiones POST
@app.route('/api/cotizar', methods=['POST', 'OPTIONS'])
def cotizar_envio():
    """
    Este endpoint recibe los datos del envío desde el frontend,
    contacta la API de Envia.com y devuelve las cotizaciones.
    También maneja las peticiones OPTIONS para el preflight de CORS.
    """
    # El navegador envía una petición OPTIONS antes del POST (preflight)
    # Debemos responder a ella con éxito. Flask-Cors usualmente lo hace
    # automáticamente, pero este bloque lo asegura.
    if request.method == 'OPTIONS':
        return '', 200

    # Verificamos si la API Key fue cargada correctamente desde las variables de entorno
    if not API_KEY:
        return jsonify({"error": "La API Key no está configurada en el servidor."}), 500

    # Obtenemos los datos JSON que envió el frontend
    datos_envio = request.get_json()
    if not datos_envio:
        return jsonify({"error": "No se recibieron datos en la petición."}), 400

    # Creamos la cabecera (header) de autorización con nuestro Bearer Token
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
