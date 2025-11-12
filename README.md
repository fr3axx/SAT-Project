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
# SAT-Project — Mapa interactivo educativo (documentación)

Este repositorio contiene un prototipo de mapa educativo que permite mostrar países, capitales, datos curiosos y jugar una trivia donde el usuario debe señalar en el mapa el país correspondiente a una capital.

Archivos principales:
- `mapa_clean.html` — versión interactiva y mantenible del mapa (Leaflet + JS). Aquí está la UI de la trivia, control de tiempo, badges, minimizable y con popups que muestran banderas y enlace a Wikipedia.
- `styles/trivia.css` — estilos personalizados extraídos del HTML.
- `main.py` — script opcional que genera `mapa.html` mediante Folium (si prefieres generar un HTML estático desde Python).

Resumen de funcionalidades actuales
- Mapa interactivo con Leaflet (tiles OpenStreetMap).
- Popups con capital, dato curioso y —si está disponible— la bandera del país.
- Enlace a la página de Wikipedia del país (abre en nueva pestaña).
- Trivia interactiva: preguntas aleatorias, temporizador por pregunta, límite configurable de preguntas, puntuación (aciertos/intentos).
- UI moderna basada en Bootstrap: tarjeta minimizable ubicada en la esquina superior derecha.
- Resaltados visuales para respuestas correctas/incorrectas y transiciones suaves.

Cómo usar (rápido)
1. Abrir `mapa_clean.html` en un navegador (doble click). El archivo usa CDNs para Leaflet y Bootstrap, y descarga un GeoJSON público por lo que requiere conexión a Internet para la funcionalidad completa.

2. Opcional — regenerar `mapa.html` desde Python:

```powershell
# activar tu entorno virtual si lo usas (Windows PowerShell)
# .\sat\Scripts\Activate.ps1
python main.py
```

Dependencias
- No es necesario instalar nada para probar `mapa_clean.html` (usa CDN). Si usas `main.py` necesitarás Python y las librerías listadas en `requirements.txt` si existe (o instalar `folium`).

Archivos recomendados para conservar
- `mapa_clean.html` (principal, frontend interactivo)
- `styles/trivia.css` (estilos)
- `scripts/generate_capitals_facts.py` (si lo usas para preparar datos locales)
- `capitals_facts.json` (si lo creas para mejorar disponibilidad offline)

Archivos que puedes borrar (sugeridos) para limpiar el repositorio
> Nota: antes de borrar archivos, haz una copia de seguridad si no estás seguro. Los siguientes suelen ser generados o innecesarios en un repositorio fuente:

- `sat/` (entorno virtual completo) — contiene `Lib/site-packages` y archivos binarios. No deberías incluir entornos virtuales en el repositorio. Añade `sat/` a `.gitignore` y elimina la carpeta del repo si ya está versionada.
- `mapa.html` (archivos HTML generados por Folium) — si el HTML fue generado por `main.py` puedes eliminar la copia generada y regenerarla cuando la necesites. Hay varias copias duplicadas en la raíz y en `SAT-Project/`; conserva sólo la que uses.
- Copias duplicadas de `main.py` y `mapa.html` en distintos directorios (por ejemplo `main.py` en la raíz y en `SAT-Project/`) — conserva una única copia canonical del script y elimina duplicados.
- `__pycache__/`, archivos `.pyc` y carpetas `build/` o `dist/` si existen.
- Archivos grandes innecesarios (por ejemplo `countries.geo.json` sin procesar si lo añadiste y ocupa mucho): almacenar una versión simplificada o servirla desde un CDN en su lugar.
- `sat/Lib/site-packages/` y cualquier otro `site-packages` — deben estar fuera del repositorio.

Sugerencia de `.gitignore` mínima (añádela si no existe o amplía la actual):

```
# Entornos virtuales
sat/
venv/

# Bytecode
__pycache__/
*.pyc

# Archivos de sistema
.DS_Store
Thumbs.db

# Archivos generados
mapa.html
countries.geo.json
```

Cambios recientes importantes
- La UI de trivia se reescribió usando Bootstrap (tarjeta, badges, inputs). La tarjeta es minimizable y está colocada en la esquina superior derecha.
- Se añadió soporte para mostrar la bandera del país en el popup y un enlace directo a Wikipedia (abre en nueva pestaña).
- Se añadió un botón `Limpiar` que ahora limpia también el historial de la trivia (puntuación, intentos, temporizador, resaltados).
- Se mejoró la animación del colapso con transiciones CSS.

Ideas y siguientes pasos recomendados
- Preprocesar y mantener localmente un archivo `capitals_facts.json` con `iso_a3`, `capital`, `lat`, `lng`, `flag_url`, `fun_fact` para evitar depender de la API pública en demos/offline.
- Añadir un pequeño script de build (Makefile o script Python) que genere assets optimizados (GeoJSON simplificado, mapas estáticos, etc.).
- Añadir pruebas básicas JS (si se integra con un bundler) o tests Python para los scripts de generación de datos.

Si quieres, aplico ahora:
- Limpiar duplicados concretos en el proyecto (mover/eliminar `mapa.html` duplicado y `main.py` si tienes preferencia de cuál conservar).
- Añadir `sat/` a `.gitignore` y explicarte cómo regenerar el entorno virtual si lo borras.

Indícame si quieres que proceda con cualquiera de estas acciones y lo hago en seguida.
