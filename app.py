# app.py
# Importamos las librerías necesarias
import os
from flask import Flask, request, jsonify
from flask_cors import CORS # Importamos la librería
import requests

# Inicializamos la aplicación de Flask
app = Flask(__name__)

# --- CONFIGURACIÓN DE CORS ---
# Esta es la configuración recomendada. La librería Flask-CORS se encargará 
# de manejar correctamente todas las peticiones, incluyendo las de tipo 
# OPTIONS (preflight), de forma automática.
CORS(app)


# --- RUTA DE DIAGNÓSTICO ---
# Esta ruta nos ayuda a verificar rápidamente si el backend está funcionando
# y si la última versión del código está desplegada.
# Si visitas https://tu-dominio.onrender.com/ y ves este mensaje,
# significa que el despliegue fue exitoso.
@app.route('/')
def health_check():
    """Ruta de diagnóstico para verificar que el servidor está en línea."""
    return jsonify({
        "status": "ok", 
        "message": "El backend del cotizador está funcionando correctamente. Versión final."
    })


# Definimos la URL del endpoint de cotización de Envia.com
ENVIA_API_URL = "https://api.envia.com/ship/rates"

# Leemos la API Key desde una variable de entorno para mayor seguridad.
API_KEY = os.environ.get('ENVIA_API_KEY')

# Creamos una ruta o endpoint "/api/cotizar" que aceptará peticiones POST
@app.route('/api/cotizar', methods=['POST'])
def cotizar_envio():
    """
    Este endpoint recibe los datos del envío desde el frontend,
    contacta la API de Envia.com y devuelve las cotizaciones.
    """
    # 1. Verificamos que la API Key esté configurada en el servidor de Render
    if not API_KEY:
        # Este error es del lado del servidor, por eso es un código 500
        return jsonify({"error": "La variable de entorno ENVIA_API_KEY no está configurada en el servidor."}), 500

    # 2. Obtenemos los datos JSON que envió el frontend
    datos_envio = request.get_json()
    if not datos_envio:
        # El cliente no envió datos, error del cliente (código 400)
        return jsonify({"error": "No se recibieron datos en la petición."}), 400

    # 3. Creamos la cabecera de autorización para la API de Envia.com
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # 4. Hacemos la petición POST a la API de Envia.com
        response = requests.post(ENVIA_API_URL, headers=headers, json=datos_envio)
        
        # Esta línea es importante: si la respuesta de Envia.com es un error (4xx o 5xx),
        # lanzará una excepción que será capturada por el bloque `except`
        response.raise_for_status() 
        
        # Si todo fue bien, devolvemos los datos al frontend
        data = response.json()
        return jsonify(data)

    except requests.exceptions.HTTPError as err:
        # Error específico de la API de Envia.com (ej. código postal inválido)
        # Intentamos obtener más detalles del cuerpo de la respuesta
        try:
            details = err.response.json()
        except ValueError:
            details = err.response.text
        
        error_details = {
            "error": "Ocurrió un error con la API de Envia.com.",
            "statusCode": err.response.status_code,
            "details": details
        }
        return jsonify(error_details), err.response.status_code
        
    except requests.exceptions.RequestException as e:
        # Error de red o de conexión (ej. no se puede conectar a Envia.com)
        # Error del lado del servidor, código 503 (Service Unavailable)
        return jsonify({"error": f"Error de conexión con el servicio externo: {e}"}), 503

# Esto permite ejecutar la aplicación directamente con "python app.py" para pruebas locales.
# Gunicorn no usa este bloque, pero es buena práctica mantenerlo.
if __name__ == '__main__':
    # Render usa su propio puerto, pero esto es útil para pruebas locales.
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
