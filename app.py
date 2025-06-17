# app.py (versión final para producción)
from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import logging
import gunicorn  # Aunque no lo llames directamente, es bueno tenerlo importado para verificar la instalación

# Configuración básica de logging para ver errores en la consola de Render
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# URL y headers para simular una petición de un navegador real
ESTAFETA_URL = "https://www.estafeta.com/frecuencia-de-entregas"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

@app.route('/')
def index():
    """Sirve el archivo HTML principal."""
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar_frecuencia():
    """Endpoint que recibe el código postal, hace el scraping y devuelve el resultado."""
    data = request.get_json()
    if not data or 'codigo_postal' not in data:
        return jsonify({'error': 'No se proporcionó el código postal.'}), 400

    cp = data['codigo_postal']
    logging.info(f"Recibida consulta para el CP: {cp}")

    payload = {'codigoPostal': cp}

    try:
        response = requests.post(ESTAFETA_URL, headers=HEADERS, data=payload, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        result_div = soup.find('div', class_='frecuencia-result')

        if not result_div:
            logging.warning(f"No se encontraron resultados para el CP: {cp}")
            return jsonify({'error': f'No se encontraron resultados para el CP {cp}. Verifique que sea correcto.'})

        p_tags = result_div.find_all('p')
        resultado = {
            'cp_consultado': cp,
            'frecuencia': 'No disponible',
            'dias_entrega': 'No disponible',
            'recoleccion_domicilio': 'No disponible'
        }

        for i, p in enumerate(p_tags):
            text = p.get_text(strip=True)
            if "Frecuencia de entrega:" in text and i + 1 < len(p_tags):
                resultado['frecuencia'] = p_tags[i + 1].get_text(strip=True)
            elif "Días de entrega:" in text and i + 1 < len(p_tags):
                resultado['dias_entrega'] = p_tags[i + 1].get_text(strip=True)
            elif "Recolección a domicilio:" in text and i + 1 < len(p_tags):
                resultado['recoleccion_domicilio'] = p_tags[i + 1].get_text(strip=True)
        
        logging.info(f"Resultado para {cp}: {resultado}")
        return jsonify(resultado)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error de conexión al consultar el CP {cp}: {e}")
        return jsonify({'error': 'Error de conexión con el servidor de Estafeta.'}), 500
    except Exception as e:
        logging.error(f"Ocurrió un error inesperado: {e}")
        return jsonify({'error': 'Ocurrió un error inesperado en el servidor.'}), 500

# El bloque if __name__ == '__main__' no es necesario para Render,
# pero puedes dejarlo si quieres ejecutar 'python app.py' localmente para pruebas.
# Gunicorn no lo usará.
if __name__ == '__main__':
    app.run(debug=True)