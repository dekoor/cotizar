/*
 * -----------------------------------------------------------------------------
 * ARCHIVO: server.js (ACTUALIZADO)
 * DESCRIPCIÓN: Este scraper ahora maneja el proceso de dos pasos.
 * -----------------------------------------------------------------------------
 */
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// La URL base de la herramienta de Estafeta
const ESTAFETA_URL = 'https://frecuenciaentregasitecorecms.azurewebsites.net/';

/**
 * Función genérica para analizar la respuesta HTML de Estafeta.
 * Devuelve un objeto con el estado y los datos correspondientes.
 */
function parseEstafetaResponse(html) {
    const $ = cheerio.load(html);
    const resultHeader = $('h2').text().trim();

    // Caso 1: Se encontró un resultado final
    if (resultHeader.includes('SIN REEXPEDICIÓN') || resultHeader.includes('CON REEXPEDICIÓN')) {
        const hasReexpedition = resultHeader.includes('CON REEXPEDICIÓN');
        return {
            status: 'RESULT_FOUND',
            data: {
                result: resultHeader,
                hasReexpedition: hasReexpedition
            }
        };
    }

    // Caso 2: Se necesita seleccionar una colonia
    const coloniaSelect = $('select[name="colonia"]');
    if (coloniaSelect.length > 0) {
        const colonias = [];
        coloniaSelect.find('option').each((i, elem) => {
            const coloniaName = $(elem).text().trim();
            if (coloniaName) { // Ignorar la primera opción vacía
                colonias.push(coloniaName);
            }
        });

        if (colonias.length > 0) {
            return {
                status: 'COLONIA_REQUIRED',
                data: {
                    colonias: colonias
                }
            };
        }
    }

    // Caso 3: No se pudo determinar el resultado
    return { status: 'UNKNOWN_RESULT', data: {} };
}


// Endpoint principal para la consulta inicial
app.get('/api/check-postal-code', async (req, res) => {
    const { postalCode } = req.query;

    if (!postalCode || !/^\d{5}$/.test(postalCode)) {
        return res.status(400).json({ error: 'Se requiere un código postal válido de 5 dígitos.' });
    }

    const formData = new URLSearchParams({ cp: postalCode, colonia: '' });

    try {
        const response = await axios.post(ESTAFETA_URL, formData);
        const parsedResult = parseEstafetaResponse(response.data);
        res.json(parsedResult);
    } catch (error) {
        console.error('Error en la consulta inicial:', error.message);
        res.status(500).json({ error: 'No se pudo conectar con el servicio de Estafeta.' });
    }
});

// Endpoint para la segunda consulta, cuando se proporciona la colonia
app.get('/api/check-with-colonia', async (req, res) => {
    const { postalCode, colonia } = req.query;

    if (!postalCode || !/^\d{5}$/.test(postalCode) || !colonia) {
        return res.status(400).json({ error: 'Se requieren código postal y colonia válidos.' });
    }
    
    // Los datos del formulario que se enviarán, incluyendo la colonia
    const formData = new URLSearchParams({ cp: postalCode, colonia: colonia });

    try {
        const response = await axios.post(ESTAFETA_URL, formData);
        const parsedResult = parseEstafetaResponse(response.data);
        res.json(parsedResult);
    } catch (error) {
        console.error('Error en la consulta con colonia:', error.message);
        res.status(500).json({ error: 'No se pudo conectar con el servicio de Estafeta.' });
    }
});


app.listen(PORT, () => {
    console.log(`Servidor scraper v2 iniciado en http://localhost:${PORT}`);
});
