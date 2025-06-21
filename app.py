import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env para desarrollo local
load_dotenv()

app = Flask(__name__)

# --- Configuración de CORS ---
# Obtenemos la URL del frontend desde una variable de entorno.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500")

CORS(app, resources={r"/api/*": {"origins": FRONTEND_URL}})

# --- Clave de API de Skydropx y URL ---
# Carga la clave desde las variables de entorno.
SKYDROPX_API_KEY = os.getenv("SKYDROPX_API_KEY")
SKYDROPX_API_URL = "https://api.skydropx.com/v1/quotations"

# --- Ruta Principal ---
@app.route('/')
def api_status():
    """Confirma que la API está en línea."""
    return jsonify({"status": "ok", "message": "Backend del Cotizador de Envíos está funcionando."})

# --- Ruta para Cotizar ---
@app.route('/api/quote', methods=['POST'])
def get_quote():
    """
    Maneja la solicitud de cotización, con manejo de errores mejorado.
    """
    # 1. Validar que la API Key esté configurada en el servidor
    if not SKYDROPX_API_KEY:
        print("ERROR: La variable de entorno SKYDROPX_API_KEY no está definida.")
        return jsonify({"error": "Error de configuración del servidor: Falta la clave de API."}), 500

    # 2. Obtener los datos del cuerpo de la solicitud
    data = request.json
    print(f"Datos recibidos para cotizar: {data}")

    # 3. Construir el cuerpo (payload) para la API de Skydropx
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

    # 4. Configurar las cabeceras (headers) con la autenticación
    headers = {
        "Authorization": f"Token token={SKYDROPX_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # 5. Realizar la petición POST a la API de Skydropx
        response = requests.post(SKYDROPX_API_URL, json=payload, headers=headers)
        
        # Levantar un error si la respuesta no fue exitosa (código 4xx o 5xx)
        response.raise_for_status()
        
        # 6. Devolver la respuesta exitosa de Skydropx al frontend
        return jsonify(response.json())

    except requests.exceptions.HTTPError as err:
        # ---- NUEVO BLOQUE DE MANEJO DE ERRORES ----
        # Este bloque se ejecuta si Skydropx devuelve un error (ej. 401, 422).
        print(f"ERROR HTTP desde Skydropx: {err}")
        error_details = {}
        try:
            # Intenta interpretar la respuesta de error como JSON
            error_details = response.json()
            print(f"Respuesta de error de la API (JSON): {error_details}")
        except ValueError:
            # Si la respuesta no es JSON, la envía como texto plano
            error_details = {"raw_response": response.text}
            print(f"Respuesta de error de la API (no-JSON): {response.text}")
        
        # Devuelve un error JSON estructurado al frontend en lugar de bloquearse
        return jsonify({
            "error": "La API de Skydropx devolvió un error.",
            "details": error_details
        }), response.status_code

    except requests.exceptions.RequestException as err:
        # Este bloque se ejecuta si hay un error de red
        print(f"ERROR de Red: {err}")
        return jsonify({"error": "Error de red al intentar contactar a Skydropx."}), 503
    
    except Exception as err:
        # Bloque genérico para cualquier otro error inesperado en el código
        print(f"ERROR INESPERADO en el servidor: {err}")
        return jsonify({"error": "Ocurrió un error inesperado en el servidor."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### **Plan de Acción Sugerido**

1.  **Revisa tus Variables de Entorno en Render:**
    * Ve a tu dashboard de Render -> `cotizar-8cgw` -> "Environment".
    * **Verifica que `SKYDROPX_API_KEY` tenga el valor correcto**. Un error al copiar y pegar es muy común. Asegúrate de que no tenga espacios al principio o al final.
    * Verifica que `FRONTEND_URL` siga siendo `https://dekoormx.com`.

2.  **Actualiza tu Código en GitHub:**
    * Reemplaza el contenido de tu archivo `app.py` en tu repositorio de GitHub con la nueva versión que te acabo de dar.

3.  **Espera el Despliegue Automático:**
    * Render debería detectar automáticamente el cambio en GitHub y empezar a desplegar la nueva versión. Puedes verificar el progreso en la pestaña "Events" de tu servicio en Render.

Una vez que la nueva versión esté desplegada, intenta hacer una cotización de nuevo. Si el problema era la clave de API, ahora deberías ver un mensaje de error claro en el cotizador en lugar de que la aplicación se bloqu
