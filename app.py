import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env para desarrollo local
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL")}})

# --- CREDENCIALES Y CONFIGURACIÓN DE ENTORNO ---
SKYDROPX_API_KEY = os.getenv("SKYDROPX_API_KEY")

# Nueva lógica para seleccionar la URL correcta
# Por defecto, se usa 'production'. En Render, la cambiaremos a 'demo' para probar.
ENVIRONMENT = os.getenv("SKYDROPX_ENVIRONMENT", "production")

if ENVIRONMENT.lower() == "demo":
    QUOTATIONS_URL = "https://api-demo.skydropx.com/v1/quotations"
else:
    QUOTATIONS_URL = "https://api.skydropx.com/v1/quotations"


# --- Ruta Principal ---
@app.route('/')
def api_status():
    """Confirma que la API está en línea."""
    return jsonify({
        "status": "ok", 
        "message": "Backend del Cotizador de Envíos está funcionando.",
        "environment": ENVIRONMENT,
        "endpoint_url": QUOTATIONS_URL
    })


# --- Ruta para Cotizar ---
@app.route('/api/quote', methods=['POST'])
def get_quote():
    """
    Maneja la solicitud de cotización usando el método de autenticación directa.
    """
    print(f"Llamando a la URL de cotización: {QUOTATIONS_URL}") # Log para verificar la URL

    if not SKYDROPX_API_KEY:
        print("ERROR: La variable de entorno SKYDROPX_API_KEY no está definida.")
        return jsonify({"error": "Error de configuración del servidor: Falta la clave de API."}), 500

    headers = {
        "Authorization": f"Token token={SKYDROPX_API_KEY}",
        "Content-Type": "application/json"
    }

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
        response = requests.post(QUOTATIONS_URL, json=shipment_payload, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())

    except requests.exceptions.HTTPError as err:
        print(f"ERROR HTTP en cotización: {err}")
        error_details = {}
        try:
            error_details = response.json()
        except ValueError:
            error_details = {"raw_response": response.text}
        
        if response.status_code == 401:
            return jsonify({
                "error": f"Error de autenticación (401) en el ambiente '{ENVIRONMENT}'. La API Key es incorrecta o no es válida para este ambiente."
            }), 401
        
        return jsonify({
            "error": "La API de Skydropx devolvió un error en la cotización.", 
            "details": error_details
        }), response.status_code

    except Exception as err:
        print(f"ERROR INESPERADO en cotización: {err}")
        return jsonify({"error": "Ocurrió un error inesperado en el servidor al cotizar."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
