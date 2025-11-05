import folium 
from folium import IFrame
import csv
import json

def load_country_data(csv_path):
    data = {}
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('iso_a3') or row.get('ISO_A3') or row.get('id')
            if not key:
                continue
            data[key.strip().upper()] = row 
    return data

def merge_geojson_with_data(geojson_path, data_dict):
    with open(geojson_path, encoding='utf-8') as f:
        geo = json.load(f)

    for feature in geo.get('features', []):
        props = feature.setdefault('properties', {})
        iso = (props.get('ISO_A3') or props.get('iso_a3') or props.get('ADM0_A3') or props.get('id') or props.get('ISO3166-1:alpha3') or '').strip().upper()
        if iso in data_dict:
            props.update(data_dict[iso])
    return geo

def create_map(geojson_data, output_html='mapa.html'):
    m = folium.Map(location=[20, 0], zoom_start=2)

    def style_function(feature):
        return {
            'fillColor': '#ffffff',
            'color': '#333333',
            'weight': 1,
            'fillOpacity': 0.5,
        }
    
    def highlight_function(feature):
        return {
            'fillColor': '#0000ff',
            'color': '#0000ff',
            'weight': 2,
            'fillOpacity': 0.7,
        }
    
    def on_each_feature(feature, layer):
        p = feature.get('properties', {})
        name = p.get('name') or p.get('NAME') or p.get('ADMIN') or 'Sin Nombre'
        capital = p.get('capital', 'N/A')
        population = p.get('population', 'N/A')
        fun_fact = p.get('fun_fact', '')
        flag = p.get('flag_url', '')

        html = f"""
        <div style="font-family: Arial; font-size: 14px; width: 260px;">
            <h4 style="margin:0 0 6px 0;">{name}</h4>
            {"<img src='" + flag + "' width='160' style='display:block;margin-bottom:8px;'/>" if flag else ""}
            <b>Capital:</b> {capital}<br/>
            <b>Población:</b> {population}<br/>
            <p style="margin-top:6px;">{fun_fact}</p>
        </div>
        """
        iframe = IFrame(html, width=280, height=180)
        popup = folium.Popup(iframe, max_width=300)
        layer.bindPopup(popup)

        tooltip_text = name
        layer.bindTooltip(tooltip_text, sticky=True)

    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        highlight_function=highlight_function,
        on_each_feature=on_each_feature,
        name='Paises'
    ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(output_html)
    print(f'Mapa guardado en {output_html}')

if __name__ == '__main__':
    data = load_country_data('countries_data.csv')
    geo = merge_geojson_with_data('countries.geojson', data)
    create_map(geo, output_html='mapa.html')