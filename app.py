# app.py
# Backend actualizado para hacer scraping a la página de Frecuencia de Entregas
# de Estafeta, usando código postal de ORIGEN y DESTINO.

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import unicodedata

# --- Configuración inicial de la aplicación Flask ---
app = Flask(__name__)
CORS(app)

# --- Definición del endpoint para la consulta ---
@app.route('/consultar', methods=['GET'])
def consultar_frecuencia():
    """
    Este endpoint recibe un CP de origen y uno de destino,
    realiza el scraping en la página de Estafeta y devuelve los resultados.
    """
    # 1. Obtenemos los códigos postales de origen y destino.
    cp_origen = request.args.get('origen')
    cp_destino = request.args.get('destino')

    if not cp_origen or not cp_destino:
        return jsonify({'error': 'Por favor, proporciona un código postal de origen y uno de destino.'}), 400

    # 2. Definimos la URL y el payload para la solicitud POST.
    # Esta es la URL a la que el formulario de Estafeta envía los datos.
    url_estafeta = 'https://www.estafeta.com/herramientas/frecuencia-de-entrega'
    
    # El payload ahora incluye ambos códigos postales.
    payload = {
        'cp_origen': cp_origen,
        'cp_destino': cp_destino,
        'Herramienta': 'Frecuencia', # Este campo parece ser requerido por el formulario
        'PaisOrigen': 'Mexico'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': url_estafeta # Es una buena práctica incluir el referer
    }

    try:
        # 3. Hacemos la solicitud POST
        response = requests.post(url_estafeta, data=payload, headers=headers)
        response.raise_for_status()

        # 4. Procesamos el HTML con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # 5. Buscamos el contenedor de resultados
        # La estructura de la página de resultados es un poco más compleja ahora.
        resultados_div = soup.find('div', class_='resultados-frecuencia')

        if resultados_div:
            # Extraemos todos los textos relevantes.
            # Los párrafos <p> y los encabezados <h4> contienen la información.
            elementos = resultados_div.find_all(['p', 'h4'])
            
            resultado_texto = [elem.get_text(strip=True) for elem in elementos if elem.get_text(strip=True)]
            
            # Limpiamos y normalizamos el texto
            resultado_limpio = [unicodedata.normalize("NFKD", texto) for texto in resultado_texto]

            return jsonify({'resultado': resultado_limpio})
        else:
            # Buscamos un posible mensaje de error si no se encuentra el div de resultados
            error_div = soup.find('div', class_='text-cp-no')
            if error_div:
                error_msg = error_div.get_text(strip=True)
                return jsonify({'error': error_msg}), 404
            else:
                return jsonify({'error': 'No se encontró información para la combinación de códigos postales proporcionada.'}), 404

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return jsonify({'error': 'No se pudo conectar con el servicio de Estafeta.'}), 500
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return jsonify({'error': 'Ocurrió un error inesperado.'}), 500

