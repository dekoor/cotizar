# app.py
# Backend para hacer web scraping a la página de Frecuencia de Entregas de Estafeta.
#
# Este script está listo para ser desplegado en servicios como Render.

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import unicodedata

# --- Configuración inicial de la aplicación Flask ---
app = Flask(__name__)
# Habilitamos CORS para permitir que el frontend (HTML) se comunique con este backend
CORS(app)

# --- Definición del endpoint para la consulta ---
@app.route('/consultar', methods=['GET'])
def consultar_cp():
    """
    Este endpoint recibe un código postal (cp) como parámetro en la URL,
    realiza el scraping en la página de Estafeta y devuelve los resultados.
    """
    # 1. Obtenemos el código postal de los parámetros de la solicitud.
    codigo_postal = request.args.get('cp')

    if not codigo_postal:
        # Si no se proporciona un código postal, devolvemos un error.
        return jsonify({'error': 'Por favor, proporciona un código postal.'}), 400

    # 2. Definimos la URL de Estafeta y los datos que enviaremos (el formulario)
    url_estafeta = 'https://www.estafeta.com/frecuencia-de-entregas'
    payload = {
        'cp': codigo_postal
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 3. Hacemos la solicitud POST a la página de Estafeta
        response = requests.post(url_estafeta, data=payload, headers=headers)
        response.raise_for_status()  # Esto generará un error si la solicitud no fue exitosa (ej. error 404, 500)

        # 4. Procesamos la respuesta HTML con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # 5. Buscamos el contenedor de los resultados
        resultados_div = soup.find('div', class_='resultados-frecuencia')

        if resultados_div:
            # Si se encuentra el div, extraemos el texto de todos los párrafos <p>
            parrafos = resultados_div.find_all('p')
            resultado_texto = [p.get_text(strip=True) for p in parrafos]
            resultado_limpio = [unicodedata.normalize("NFKD", texto) for texto in resultado_texto]
            return jsonify({'resultado': resultado_limpio})
        else:
            # Buscamos el mensaje de error que muestra la página.
            error_div = soup.find('div', class_='text-cp-no')
            if error_div:
                error_msg = error_div.get_text(strip=True)
                return jsonify({'error': error_msg}), 404
            else:
                return jsonify({'error': f'No se encontró información para el código postal {codigo_postal}.'}), 404

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return jsonify({'error': 'No se pudo conectar con el servicio de Estafeta. Intenta de nuevo más tarde.'}), 500
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return jsonify({'error': 'Ocurrió un error inesperado al procesar la solicitud.'}), 500

# El bloque if __name__ == '__main__': se elimina porque el servidor de producción (Gunicorn)
# importará directamente la variable 'app' de este archivo.
