from flask import Flask, jsonify
from flask_cors import CORS

# 1. Se crea una aplicación Flask muy simple.
app = Flask(__name__)

# 2. Se configura CORS de la manera más abierta posible para la prueba.
CORS(app)

# 3. Ruta principal para verificar que el servidor está en línea.
@app.route('/')
def api_status():
    """Confirma que la API está en línea."""
    return jsonify({"status": "ok", "message": "Backend mínimo está funcionando."})

# 4. Ruta de cotización falsa.
# No se conecta a Skydropx, solo devuelve datos de prueba para
# verificar que el frontend puede conectarse.
@app.route('/api/quote', methods=['POST'])
def dummy_quote():
    """Devuelve una cotización de prueba."""
    print("Recibida una solicitud en la ruta /api/quote de prueba.")
    return jsonify({
        "data": [
            {
                "attributes": {
                    "provider": "PAQUETERIA_PRUEBA",
                    "total_pricing": "150.00",
                    "service_level_name": "Servicio de Prueba Express",
                    "days": 3,
                    "currency_local": "MXN"
                }
            },
            {
                "attributes": {
                    "provider": "OTRA_PAQUETERIA",
                    "total_pricing": "125.50",
                    "service_level_name": "Servicio de Prueba Económico",
                    "days": 5,
                    "currency_local": "MXN"
                }
            }
        ]
    })
