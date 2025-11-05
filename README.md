# Mapa limpio — Documentación de `mapa_clean.html`

Este documento explica en detalle cómo funciona `mapa_clean.html`, un fichero HTML que carga un GeoJSON mundial y proporciona interacción para mostrar capitales, datos curiosos y marcadores. Está pensado como una versión "limpia" y didáctica para usar en un proyecto educativo.

## Resumen

- Archivo: `mapa_clean.html`
- Propósito: mostrar un mapa mundial interactivo con polígonos/puntos de países (cargados desde un GeoJSON público) y permitir al usuario hacer click sobre un país para ver su capital, un dato curioso y crear un marcador en la capital.
- Tecnologías: Leaflet (CDN) y la API pública de REST Countries para búsqueda dinámica de capitales cuando no hay datos locales.

## Estructura principal del archivo

1. Cabecera HTML
   - Inclusión de la hoja de estilos de Leaflet desde CDN.
   - Estilos CSS mínimos para que el mapa ocupe toda la pantalla y para los botones de control.

2. Controles y markup
   - `div.control-row`: contiene botones `Limpiar marcadores` y `Depurar capas`.
   - `div#map`: elemento donde Leaflet monta el mapa.

3. Scripts
   - Se carga Leaflet desde CDN.
   - Código JS principal que inicializa el mapa, capa de tiles y la lógica de interacción.

## Variables de configuración importantes

- `CAPITALS` — un objeto JS con ejemplos de coordenadas y nombres de capitales para varios países. Las claves están basadas en el nombre del país tal como aparece en el GeoJSON (propiedad `name`).
- `FUN_FACTS` — un objeto con datos curiosos por país; las claves están normalizadas (minúsculas sin diacríticos) para búsqueda rápida.

Ejemplo de entrada en `CAPITALS`:

```js
"Venezuela": {lat: 10.4806, lng: -66.9036, name: "Caracas"}
```

## Funciones clave y flujo de interacción

- `normalizeName(s)`
  - Normaliza un string a minúsculas y elimina diacríticos (acentos) usando `String.prototype.normalize('NFD')` con un fallback.
  - Se usa para comparar nombres de países en forma robusta.

- `capitalsIndex` — índice interno construido a partir de `CAPITALS` con claves normalizadas para búsquedas rápidas.

- Carga opcional: `capitals_facts.json`
  - Si en el mismo directorio existe `capitals_facts.json`, el script intenta cargarlo y añadir/mezclar sus registros en `capitalsIndex`.
  - Formato esperado: un objeto con claves normalizadas y valores con `{ lat, lng, capitalName, fact }`.

- `showCapital(lat, lng, html)`
  - Coloca un marcador en las coordenadas dadas, abre un popup con el HTML proporcionado, y borra marcadores previos para que sólo haya uno activo a la vez.

- `highlightLayer(e)` / `resetLayer(e)`
  - Aplican estilos de resaltado cuando el cursor entra/sale de un país.

- `onFeatureClick(e)`
  - Se ejecuta al hacer click sobre una característica (feature) del GeoJSON.
  - Obtiene el nombre del país a partir de varias propiedades (`name`, `NAME`, `ADMIN`, `SOVEREIGNT`, etc.).
  - Intenta buscar la capital en `capitalsIndex`. Si existe, muestra la capital y un dato curioso (si está disponible).
  - Si no existe en `capitalsIndex`, lanza una búsqueda a la API de REST Countries (`https://restcountries.com/v3.1/name/<country>?fullText=true`) para obtener la capital y las coordenadas (`capitalInfo.latlng`). Cuando la API responde, cachea el resultado en `capitalsIndex` y actualiza el popup.
  - Si la API no devuelve coordenadas, usa `item.latlng` (lat/lng aproximadas del país) como fallback o muestra mensaje de error.

- `getCapitalFromAPI(countryName)`
  - Lógica para consultar REST Countries, parsear la respuesta y retornar `{ capitalName, lat, lng, fact }`.
  - `makeFactFromCountryData(item)` extrae un texto breve a partir de los campos `region`, `population`, `area`, `currencies` y `languages`.

## GeoJSON

- URL por defecto: `https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json`.
- El script hace `fetch` a esa URL y genera una capa `L.geoJSON` con `style` y `onEachFeature` para añadir los event handlers `mouseover`, `mouseout` y `click`.
- Si la descarga falla, el script añade un `FeatureCollection` mínimo de prueba (fallback) con un `Point` para Venezuela para poder probar la interacción localmente.

## Controles y atajos

- Botón `Limpiar marcadores (Ctrl+Click)`
  - Limpia los marcadores actualmente añadidos.
  - Nota: también hay soporte para limpiar con Ctrl+click sobre el mapa.

- Botón `Depurar capas` (Debug)
  - Muestra en consola (F12) las capas actuales del mapa con un pequeño resumen para depuración.

- Atajo Ctrl+Click
  - Al hacer Ctrl+Click sobre el mapa se limpian los marcadores.

## Archivos opcionales y formatos

- `capitals_facts.json` (opcional) — formato recomendado:

```json
{
  "venezuela": { "lat": 10.4806, "lng": -66.9036, "capitalName": "Caracas", "fact": "Tiene el Salto Ángel." },
  "france": { "lat": 48.8566, "lng": 2.3522, "capitalName": "Paris", "fact": "Francia es el país más visitado." }
}
```

Las claves deben estar ya normalizadas (minúsculas y sin acentos) para que el script las añada directamente al índice.

## Cómo probar localmente

1. Abrir el archivo `mapa_clean.html` con un navegador (doble click). El archivo carga recursos externos (CDN y GeoJSON en GitHub) por lo que necesitas conexión a Internet para la funcionalidad completa.

2. Alternativa para pruebas offline mínimas:
   - Crear `capitals_facts.json` con algunos países y colocarlo junto a `mapa_clean.html`.
   - Comentar la sección `fetch(geojsonUrl)` y descomentar/ajustar el bloque de `sample` (o editarlo) para incluir más features de prueba.

3. Desde PowerShell (Windows) puedes abrirlo desde el directorio del archivo:

```powershell
# Abrir el HTML con la aplicación por defecto (explorador)
Start-Process .\mapa_clean.html
```

## Personalización rápida

- Añadir/editar capitales locales: modifica el objeto `CAPITALS` al inicio del script. La clave debe coincidir con el nombre del país en el GeoJSON.

- Añadir datos curiosos: añade entradas en `FUN_FACTS` usando claves normalizadas (sin acentos y en minúsculas).

- Cambiar proveedor de tiles: sustituye la URL en `L.tileLayer(...)` por otra (por ejemplo, Mapbox — recuerda configurar token si aplica).

- Usar un GeoJSON local en lugar del remoto:
  - Guarda `countries.geo.json` en la misma carpeta y cambia `geojsonUrl` por `'countries.geo.json'`.

## Rendimiento y límites

- El GeoJSON mundial puede ser grande y hacer que la carga y el renderizado sean lentos en navegadores o dispositivos con recursos limitados. Para producción:
  - Usar geometrías simplificadas (topojson o GeoJSON simplificado).
  - Cargar solo la región necesaria o paginar por niveles de zoom.
  - Considerar servir un GeoJSON preprocesado desde tu propio servidor.

## Depuración — problemas comunes

- `GeoJSON fetch failed` / CORS / 404
  - Verifica conectividad, URL y restricciones CORS. Si la URL pública no permite CORS, baja el archivo y sírvelo desde el mismo origen o usa un proxy que permita CORS para desarrollo.

- API REST Countries falla (rate limit o cambios)
  - La API pública puede devolver errores o cambiar la estructura. En ese caso, imprime `console.log` (F12) y ajusta `getCapitalFromAPI` según la nueva respuesta.

- Popups vacíos o nombres de país no coincidentes
  - Los nombres en el GeoJSON pueden diferir (alias, abreviaturas, idiomas). Preferible usar identificadores ISO en un pipeline real y preprocesar los datos para hacer join por `iso_a3` en lugar de por nombre.

## Buenas prácticas y siguientes mejoras sugeridas

- Mantener un dataset local preprocesado con `iso_a3`, `capital`, `lat`, `lng`, `flag_url`, `fun_fact` y usarlo para rellenar `capitalsIndex` al cargar la página.
- Añadir un control de búsqueda (`L.Control` o plugin `leaflet-search`) para buscar países por nombre y centrar/abrir su popup.
- Añadir un pequeño quiz interactivo que seleccione un país al azar y pida al usuario indicar su capital (esto requiere algo de JS adicional y UI estática).
- Si el proyecto crece, considerar pasar a un backend (Flask/Express) que sirva los datos y el HTML y permita almacenamiento/edición de contenidos por parte de docentes.

## Créditos y licencias

- GeoJSON por defecto: `https://github.com/johan/world.geo.json` (ver repositorio para sus condiciones y atribución).
- Tile layer: OpenStreetMap — atribución requerida ya incluida en el `tileLayer`.
- REST Countries API: https://restcountries.com/ — para consultas de capitales y metadatos.

---

Si quieres, puedo:

- Añadir ejemplos `capitals_facts.json` y un `countries.geo.json` reducido para pruebas inmediatas.
- Modificar `mapa_clean.html` para incluir un control de búsqueda o un pequeño quiz interactivo.

Indica qué prefieres y continúo con esa mejora.
