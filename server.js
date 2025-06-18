/*
 * -----------------------------------------------------------------------------
 * ARCHIVO: server.js
 * DESCRIPCIÓN: El código principal del scraper. Guarda este contenido
 * en un archivo llamado "server.js" y súbelo a tu repositorio de GitHub
 * junto con "package.json".
 * -----------------------------------------------------------------------------
 */
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware de CORS para permitir peticiones desde cualquier origen (tu frontend)
app.use(cors());
app.use(express.json());

// Endpoint para consultar el código postal
app.get('/api/check-postal-code', async (req, res) => {
    const { postalCode } = req.query;

    if (!postalCode || !/^\d{5}$/.test(postalCode)) {
        return res.status(400).json({ error: 'Se requiere un código postal válido de 5 dígitos.' });
    }

    const url = 'https://frecuenciaentregasitecorecms.azurewebsites.net/';
    
    // Los datos del formulario que se enviarán
    const formData = new URLSearchParams();
    formData.append('cp', postalCode);
    formData.append('colonia', ''); // El campo de la colonia puede ir vacío
    formData.append('estado', ''); // El campo del estado puede ir vacío
    formData.append('municipio', ''); // El campo del municipio puede ir vacío


    try {
        // Hacemos la petición POST a la página de Estafeta
        const response = await axios.post(url, formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });

        // Cargamos el HTML de la respuesta en Cheerio para analizarlo
        const $ = cheerio.load(response.data);

        let resultText = 'No se pudo determinar el resultado.';
        let hasReexpedition = null;

        // Buscamos el texto específico en la respuesta.
        // La página de resultados de Estafeta contiene un <h2> con el veredicto.
        const resultHeader = $('h2').text().trim();
        
        if (resultHeader.includes('SIN REEXPEDICIÓN')) {
            resultText = 'SIN REEXPEDICIÓN';
            hasReexpedition = false;
        } else if (resultHeader.includes('CON REEXPEDICIÓN')) {
            resultText = 'CON REEXPEDICIÓN';
            hasReexpedition = true;
        }

        res.json({
            postalCode: postalCode,
            result: resultText,
            hasReexpedition: hasReexpedition
        });

    } catch (error) {
        console.error('Error al hacer scraping:', error.message);
        res.status(500).json({ error: 'No se pudo conectar con el servicio de Estafeta.' });
    }
});

app.listen(PORT, () => {
    console.log(`Servidor scraper iniciado en http://localhost:${PORT}`);
});
