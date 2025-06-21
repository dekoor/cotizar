import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Importar CORS
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env para desarrollo local
load_dotenv()

app = Flask(__name__)

# --- Configuración de CORS ---
# Obtenemos la URL del frontend desde una variable de entorno.
# Esto es más seguro y flexible. En Render, la configurarás.
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Si la variable no está definida, usamos un valor por defecto para desarrollo
# (asegúrate de que el puerto coincida si usas un Live Server local).
if not FRONTEND_URL:
    FRONTEND_URL = "http://127.0.0.1:5500" # URL típica de Live Server en VSCode

# Inicializamos CORS, permitiendo peticiones a "/api/*" SÓLO desde tu frontend.
CORS(app, resources={r"/api/*": {"origins": FRONTEND_URL}})

# --- Clave de API de Skydropx ---
# Carga la clave desde las variables de entorno. ¡NUNCA la escribas directamente aquí!
SKYDROPX_API_KEY = os.getenv("SKYDROPX_API_KEY")
SKYDROPX_API_URL = "https://api.skydropx.com/v1/quotations"

# --- Ruta Principal (Opcional) ---
# Esta ruta ya no es estrictamente necesaria si tu HTML está en Hostinger,
# pero es buena práctica tener una ruta raíz que confirme que el backend funciona.
@app.route('/')
def api_status():
    """Confirma que la API está en línea."""
    return jsonify({"status": "ok", "message": "Backend del Cotizador de Envíos está funcionando."})

# --- Ruta para Cotizar ---
# Recibe los datos del frontend, contacta a Skydropx y devuelve las tarifas.
@app.route('/api/quote', methods=['POST'])
def get_quote():
    """
    Maneja la solicitud de cotización.
    Se comunica con la API de Skydropx y devuelve las opciones de envío.
    """
    if not SKYDROPX_API_KEY:
        return jsonify({"error": "La clave de API de Skydropx no está configurada en el servidor."}), 500

    data = request.json
    print(f"Datos recibidos para cotizar: {data}")

    payload = {
        "zip_from": data.get("zip_from"),
        "zip_to": data.get("zip_to"),
        "parcel": {
            "weight": data.get("weight"),
            "height": data.get("height"),
            "width": data.get("width"),
            "length": data.get("length")
        }
    }

    headers = {
        "Authorization": f"Token token={SKYDROPX_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(SKYDROPX_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())

    except requests.exceptions.HTTPError as err:
        print(f"Error HTTP: {err}")
        print(f"Respuesta de la API: {response.text}")
        error_details = response.json() if response.text else {"error": "Error desconocido"}
        return jsonify({"error": "Error al comunicarse con la API de Skydropx.", "details": error_details}), response.status_code

    except requests.exceptions.RequestException as err:
        print(f"Error de Red: {err}")
        return jsonify({"error": "Error de red al intentar contactar a Skydropx."}), 503

if __name__ == '__main__':
    # Para desarrollo local, si lo necesitas
    app.run(debug=True, port=5000)
