"""Turns CSV with mapping from Autotyp LIDs to Glottolog into JSON"""

import pandas
import json

data = pandas.read_csv('autotyp.csv', sep=',', header=0)
data.fillna('', inplace=True)

dic = {key: value for key, value in zip(list(data.LID), list(data.Glottocode))}

with open('autotyp_lang_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(dic, f, ensure_ascii=False, indent=4)
