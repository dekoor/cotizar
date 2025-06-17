# app.py
# Importamos las librerías necesarias
import os
from flask import Flask, request, jsonify
from flask_cors import CORS # Importamos la librería
import requests

# Inicializamos la aplicación de Flask
app = Flask(__name__)

# --- CORRECCIÓN DE CORS ---
# Simplificamos la configuración de CORS para que aplique a toda la aplicación.
# La librería Flask-CORS se encargará de manejar correctamente todas las
# peticiones, incluyendo las de tipo OPTIONS (preflight), de forma automática.
CORS(app)

# Definimos la URL del endpoint de cotización de Envia.com
ENVIA_API_URL = "https://api.envia.com/ship/rates"

# Leemos la API Key desde una variable de entorno para mayor seguridad.
API_KEY = os.environ.get('ENVIA_API_KEY')

# --- IMPORTANTE ---
# El decorador @app.after_request ha sido ELIMINADO.
# Ya no es necesario y podría causar conflictos.

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
        # Intentamos obtener más detalles del error de la respuesta de Envia.com
        try:
            details = err.response.json()
        except ValueError:
            details = err.response.text
        error_details = {"error": f"Error en la API de Envia.com: {err.response.status_code}", "details": details}
        return jsonify(error_details), err.response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error de conexión: {e}"}), 503

# Esto permite ejecutar la aplicación directamente con "python app.py" para pruebas locales
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
