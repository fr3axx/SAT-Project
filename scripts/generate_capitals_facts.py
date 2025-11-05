#!/usr/bin/env python3
"""
Generate capitals_facts.json by querying REST Countries API (/v3.1/all).
Writes a mapping of normalized country name -> {capitalName, lat, lng, fact}
Fact generated from region, population, area, currency, languages.
"""
import urllib.request
import json
import unicodedata

URL = 'https://restcountries.com/v3.1/all'
OUT = '../capitals_facts.json'


def normalize(name):
    if not name:
        return ''
    s = unicodedata.normalize('NFD', name)
    s = ''.join(ch for ch in s if not unicodedata.category(ch).startswith('M'))
    return s.lower()


def make_fact(item):
    parts = []
    if 'region' in item and item['region']:
        parts.append(f"Region: {item['region']}")
    if 'population' in item and item['population']:
        parts.append(f"Population: {item['population']:,}")
    if 'area' in item and item['area']:
        parts.append(f"Area: {int(item['area']):,} km²")
    if 'currencies' in item and item['currencies']:
        try:
            cur = next(iter(item['currencies'].values()))
            parts.append(f"Currency: {cur.get('name') or ''}")
        except Exception:
            pass
    if 'languages' in item and item['languages']:
        try:
            langs = list(item['languages'].values())
            parts.append('Languages: ' + ', '.join(langs[:2]))
        except Exception:
            pass
    return '. '.join(parts[:3])


def main():
    print('Fetching', URL)
    req = urllib.request.Request(URL, headers={'User-Agent': 'capitals-generator/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    out = {}
    for item in data:
        # pick primary name
        names = []
        if 'name' in item:
            n = item['name']
            if isinstance(n, dict):
                if 'common' in n:
                    names.append(n['common'])
                if 'official' in n:
                    names.append(n['official'])
        # fallback to cca2/cca3
        if not names:
            if 'cca3' in item:
                names.append(item['cca3'])
        norm_key = normalize(names[0]) if names else ''
        capital = None
        lat = None
        lng = None
        if 'capital' in item and item['capital']:
            capital = item['capital'][0]
        if 'capitalInfo' in item and 'latlng' in item['capitalInfo'] and item['capitalInfo']['latlng']:
            latlng = item['capitalInfo']['latlng']
            lat = latlng[0]
            lng = latlng[1]
        elif 'latlng' in item and item['latlng']:
            lat = item['latlng'][0]
            lng = item['latlng'][1]
        fact = make_fact(item)
        out[norm_key] = { 'capitalName': capital or '', 'lat': lat, 'lng': lng, 'fact': fact }
    # write
    path = OUT
    print('Writing', path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('Done. Countries:', len(out))

if __name__ == '__main__':
    main()
