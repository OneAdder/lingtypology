"""This script gets mapping language: elevation

It uses locally running OpenElevation Server"""
import json
import pandas
import requests

import lingtypology.glottolog

glottolog_table = lingtypology.glottolog.glottolog
glottolog_table.dropna(subset=['Latitude', 'Longitude'], inplace=True)

languages = glottolog_table.Name
latitudes = glottolog_table.Latitude
longitudes = glottolog_table.Longitude

url = 'http://127.0.0.1:8080/api/v1/lookup'

post_js = {'locations': []}
for latitude, longitude in zip(latitudes, longitudes):
    post_js['locations'].append({
        'latitude': latitude,
        'longitude': longitude
    })
post_jses = [
    {'locations': post_js['locations'][:1000]},
    {'locations': post_js['locations'][1000: 2000]},
    {'locations': post_js['locations'][2000: 3000]},
    {'locations': post_js['locations'][3000: 4000]},
    {'locations': post_js['locations'][4000: 5000]},
    {'locations': post_js['locations'][5000: 6000]},
    {'locations': post_js['locations'][6000: 7000]},
    {'locations': post_js['locations'][7000: 8000]},
    {'locations': post_js['locations'][8000:]},
]

elevation_list = []
for query in post_jses:
    elevation_data = json.loads(requests.post(url, json=query).content)
    elevation_list += [el['elevation'] for el in elevation_data['results']]

language_elevation_mapping = {key: value for key, value in zip(languages, elevation_list)}
if __name__ == '__main__':
    with open('language_elevation_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(language_elevation_mapping, f, indent=4, ensure_ascii=False)
