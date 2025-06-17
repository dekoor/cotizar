# app.py
# Importamos las librerías necesarias
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Inicializamos la aplicación de Flask
app = Flask(__name__)

# Configuramos CORS para permitir peticiones desde cualquier origen.
# En un entorno de producción real, podrías restringirlo a tu dominio del frontend.
CORS(app)

# Definimos la URL del endpoint de cotización de Envia.com
ENVIA_API_URL = "https://api.envia.com/ship/rates"

# Leemos la API Key desde una variable de entorno para mayor seguridad.
# Nunca escribas tu API Key directamente en el código.
API_KEY = os.environ.get('ENVIA_API_KEY')

# Creamos una ruta o endpoint "/api/cotizar" que aceptará peticiones POST
@app.route('/api/cotizar', methods=['POST'])
def cotizar_envio():
    """
    Este endpoint recibe los datos del envío desde el frontend,
    contacta la API de Envia.com y devuelve las cotizaciones.
    """
    # Verificamos si la API Key fue cargada correctamente desde las variables de entorno
    if not API_KEY:
        # Si no se encuentra la API Key, devolvemos un error.
        return jsonify({"error": "La API Key no está configurada en el servidor."}), 500

    # Obtenemos los datos JSON que envió el frontend
    datos_envio = request.get_json()

    # Validamos que se hayan recibido datos
    if not datos_envio:
        return jsonify({"error": "No se recibieron datos en la petición."}), 400

    # Creamos la cabecera (header) de autorización con nuestro Bearer Token
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Hacemos la petición POST a la API de Envia.com
        # Pasamos la cabecera de autorización y los datos del envío en formato JSON
        response = requests.post(ENVIA_API_URL, headers=headers, json=datos_envio)

        # Forzamos que la respuesta sea interpretada como UTF-8 para evitar problemas con caracteres especiales
        response.encoding = 'utf-8'

        # Verificamos si la respuesta de Envia.com fue exitosa (código 200-299)
        response.raise_for_status() 

        # Obtenemos la respuesta JSON de Envia.com
        data = response.json()
        
        # Devolvemos los datos recibidos de Envia.com al frontend
        return jsonify(data)

    except requests.exceptions.HTTPError as err:
        # Si Envia.com devuelve un error (ej. 4xx o 5xx), lo capturamos
        # e intentamos devolver el mensaje de error que ellos proporcionan.
        error_details = {"error": f"Error en la API de Envia.com: {err.response.status_code}", "details": err.response.text}
        return jsonify(error_details), err.response.status_code
        
    except requests.exceptions.RequestException as e:
        # Si ocurre un error de red o de conexión, lo capturamos
        return jsonify({"error": f"Error de conexión: {e}"}), 503

# Esto permite ejecutar la aplicación directamente con "python app.py" para pruebas locales
if __name__ == '__main__':
    # El puerto se obtiene de una variable de entorno, útil para Render.
    # Si no existe, se usa el 5001 por defecto para desarrollo local.
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
