# app.py
# Backend actualizado para hacer scraping a la página de Frecuencia de Entregas
# de Estafeta, usando código postal de ORIGEN y DESTINO.
# v5: Código limpio para corregir SyntaxError.

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
    cp_origen = request.args.get('origen')
    cp_destino = request.args.get('destino')

    if not cp_origen or not cp_destino:
        return jsonify({'error': 'Por favor, proporciona un código postal de origen y uno de destino.'}), 400

    url_estafeta = 'https://www.estafeta.com/frecuencia-de-entregas'
    
    payload = {
        'cp_origen': cp_origen,
        'cp_destino': cp_destino,
        'Herramienta': 'Frecuencia',
        'PaisOrigen': 'Mexico'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.estafeta.com/frecuencia-de-entregas'
    }

    try:
        response = requests.post(url_estafeta, data=payload, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        resultados_div = soup.find('div', class_='resultados-frecuencia')

        if resultados_div:
            elementos = resultados_div.find_all(['p', 'h4'])
            resultado_texto = [elem.get_text(strip=True) for elem in elementos if elem.get_text(strip=True)]
            resultado_limpio = [unicodedata.normalize("NFKD", texto) for texto in resultado_texto]
            return jsonify({'resultado': resultado_limpio})
        else:
            error_div = soup.find('div', class_='text-cp-no')
            if error_div:
                error_msg = error_div.get_text(strip=True)
                return jsonify({'error': error_msg}), 404
            else:
                print("DEBUG: No se encontró 'resultados-frecuencia' ni 'text-cp-no'.")
                print("DEBUG: Contenido de la página de Estafeta:")
                print(response.text[:1000])
                return jsonify({'error': 'No se pudo interpretar la respuesta de Estafeta. Intenta con otros códigos postales.'}), 500

    except requests.exceptions.RequestException as e:
        print(f"Error de Requests: {e}")
        return jsonify({'error': 'No se pudo conectar con el servicio de Estafeta.'}), 503
    except Exception as e:
        print(f"Ocurrió un error inesperado en el servidor: {e}")
        return jsonify({'error': 'Ocurrió un error inesperado en el servidor.'}), 500
```

Una vez que reemplaces el código y lo subas a GitHub, Render debería poder desplegarlo correctamente. ¡Vamos a intentarlo de nue