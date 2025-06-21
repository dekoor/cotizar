import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env para desarrollo local
load_dotenv()

app = Flask(__name__, template_folder='templates')

# --- Clave de API de Skydropx ---
# Carga la clave desde las variables de entorno. ¡NUNCA la escribas directamente aquí!
# En Render, configurarás esta variable en el dashboard de tu servicio.
SKYDROPX_API_KEY = os.getenv("SKYDROPX_API_KEY")
SKYDROPX_API_URL = "https://api.skydropx.com/v1/quotations"

# --- Ruta Principal ---
# Sirve la página HTML principal para la cotización.
@app.route('/')
def index():
    """Renderiza la página de cotización."""
    return render_template('index.html')

# --- Ruta para Cotizar ---
# Recibe los datos del frontend, contacta a Skydropx y devuelve las tarifas.
@app.route('/api/quote', methods=['POST'])
def get_quote():
    """
    Maneja la solicitud de cotización.
    Se comunica con la API de Skydropx y devuelve las opciones de envío.
    """
    # Validar que la API Key esté configurada
    if not SKYDROPX_API_KEY:
        return jsonify({"error": "La clave de API de Skydropx no está configurada en el servidor."}), 500

    # Obtener los datos del cuerpo de la solicitud (enviados desde JavaScript)
    data = request.json
    print(f"Datos recibidos para cotizar: {data}")

    # Construir el cuerpo (payload) para la API de Skydropx
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

    # Configurar las cabeceras (headers) con la autenticación
    # Skydropx usa autenticación por Token para este endpoint.
    headers = {
        "Authorization": f"Token token={SKYDROPX_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Realizar la petición POST a la API de Skydropx
        response = requests.post(SKYDROPX_API_URL, json=payload, headers=headers)
        
        # Levantar un error si la respuesta no fue exitosa (código 4xx o 5xx)
        response.raise_for_status()
        
        # Devolver la respuesta de Skydropx al frontend
        return jsonify(response.json())

    except requests.exceptions.HTTPError as err:
        # Manejar errores de HTTP (ej. 401 No Autorizado, 422 Datos Inválidos)
        print(f"Error HTTP: {err}")
        print(f"Respuesta de la API: {response.text}")
        error_details = response.json() if response.text else {"error": "Error desconocido"}
        return jsonify({"error": "Error al comunicarse con la API de Skydropx.", "details": error_details}), response.status_code

    except requests.exceptions.RequestException as err:
        # Manejar otros errores de red (ej. no hay conexión)
        print(f"Error de Red: {err}")
        return jsonify({"error": "Error de red al intentar contactar a Skydropx."}), 503

# --- Ejecución del Servidor ---
if __name__ == '__main__':
    # Flask se ejecuta en el puerto 5000 por defecto.
    # Render usará gunicorn para ejecutar la aplicación.
    app.run(debug=True)

