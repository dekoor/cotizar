import os
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env para desarrollo local
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL")}})

# --- VARIABLES DE AUTENTICACIÓN (URL CORREGIDA) ---
SKYDROPX_CLIENT_ID = os.getenv("SKYDROPX_CLIENT_ID")
SKYDROPX_CLIENT_SECRET = os.getenv("SKYDROPX_CLIENT_SECRET")
# SE CORRIGIÓ ESTA LÍNEA AÑADIENDO "/v1"
TOKEN_URL = "https://api.skydropx.com/v1/oauth/token"
QUOTATIONS_URL = "https://api.skydropx.com/v1/quotations"

# --- CACHÉ SIMPLE EN MEMORIA PARA EL TOKEN ---
cached_token = {
    "access_token": None,
    "expires_at": 0
}

def get_valid_token():
    """
    Obtiene un token válido, ya sea del caché o uno nuevo si el anterior expiró.
    """
    global cached_token
    # Revisa si el token en caché todavía es válido (con un margen de 60 segundos)
    if cached_token["access_token"] and cached_token["expires_at"] > time.time() + 60:
        print("Usando token de caché.")
        return cached_token["access_token"]

    print("Solicitando un nuevo token de acceso a Skydropx...")
    
    # Valida que las credenciales estén configuradas en el servidor
    if not SKYDROPX_CLIENT_ID or not SKYDROPX_CLIENT_SECRET:
        print("ERROR: Faltan las variables SKYDROPX_CLIENT_ID o SKYDROPX_CLIENT_SECRET.")
        return None

    # Cuerpo de la solicitud para obtener el token
    token_payload = {
        'grant_type': 'client_credentials',
        'client_id': SKYDROPX_CLIENT_ID,
        'client_secret': SKYDROPX_CLIENT_SECRET
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(TOKEN_URL, json=token_payload, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        
        # Guarda el nuevo token y calcula su tiempo de expiración
        cached_token["access_token"] = token_data["access_token"]
        cached_token["expires_at"] = time.time() + token_data["expires_in"]
        print("Nuevo token obtenido y guardado en caché.")
        return cached_token["access_token"]

    except requests.exceptions.HTTPError as err:
        print(f"ERROR al obtener el token: {err}")
        print(f"Respuesta de la API de tokens: {response.text}")
        return None

# --- Ruta Principal ---
@app.route('/')
def api_status():
    return jsonify({"status": "ok", "message": "Backend del Cotizador de Envíos está funcionando."})

# --- Ruta para Cotizar ---
@app.route('/api/quote', methods=['POST'])
def get_quote():
    # 1. Obtiene un token válido
    access_token = get_valid_token()
    if not access_token:
        return jsonify({"error": "No se pudo autenticar con Skydropx. Revisa las credenciales del servidor."}), 500

    # 2. Configura los headers con el Bearer Token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 3. Construye el payload con los datos del envío
    data = request.json
    shipment_payload = {
        "zip_from": data.get("zip_from"),
        "zip_to": data.get("zip_to"),
        "parcel": {
            "weight": data.get("weight"),
            "height": data.get("height"),
            "width": data.get("width"),
            "length": data.get("length")
        }
    }

    try:
        # 4. Realiza la solicitud de cotización
        response = requests.post(QUOTATIONS_URL, json=shipment_payload, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())

    except requests.exceptions.HTTPError as err:
        print(f"ERROR HTTP en cotización: {err}")
        error_details = response.json() if response.text else {}
        return jsonify({"error": "La API de Skydropx devolvió un error en la cotización.", "details": error_details}), response.status_code
    
    except Exception as err:
        print(f"ERROR INESPERADO en cotización: {err}")
        return jsonify({"error": "Ocurrió un error inesperado en el servidor al cotizar."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
