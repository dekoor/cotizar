# app.py
# Importamos las librerías necesarias
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Inicializamos la aplicación de Flask
app = Flask(__name__)

# Configuración de CORS para permitir peticiones desde cualquier origen
CORS(app)

# --- RUTA DE DIAGNÓSTICO ---
@app.route('/')
def health_check():
    """Ruta de diagnóstico para verificar que el servidor está en línea."""
    return jsonify({
        "status": "ok", 
        "message": "El backend del cotizador está funcionando correctamente. Versión para Enviosperros.com."
    })

# --- CONFIGURACIÓN DE LA API DE ENVÍOS ---
# URL del endpoint de cotización de Enviosperros.com
SHIPPING_API_URL = "https://app.enviosperros.com/api/v2/shipping/rates"

# Leemos la API Key desde las variables de entorno de Render.
# IMPORTANTE: Debes reemplazar el valor en Render por tu nueva clave de Enviosperros.com
API_KEY = os.environ.get('ENVIA_API_KEY') 

# Endpoint para cotizar
@app.route('/api/cotizar', methods=['POST'])
def cotizar_envio():
    """
    Este endpoint recibe los datos del envío desde el frontend,
    contacta la API de Enviosperros.com y devuelve las cotizaciones.
    """
    if not API_KEY:
        return jsonify({"error": "La API Key no está configurada en las variables de entorno del servidor."}), 500

    datos_envio = request.get_json()
    if not datos_envio:
        return jsonify({"error": "No se recibieron datos en la petición."}), 400

    # Cabecera de autorización, es igual que en la API anterior
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Hacemos la petición POST a la API de Enviosperros.com
        response = requests.post(SHIPPING_API_URL, headers=headers, json=datos_envio)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)

    except requests.exceptions.HTTPError as err:
        try:
            details = err.response.json()
        except ValueError:
            details = err.response.text
        
        error_details = {
            "error": "Ocurrió un error con la API del proveedor de envíos.",
            "statusCode": err.response.status_code,
            "details": details
        }
        return jsonify(error_details), err.response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error de conexión con el servicio externo: {e}"}), 503

# Esto permite ejecutar la aplicación directamente con "python app.py" para pruebas locales.
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
