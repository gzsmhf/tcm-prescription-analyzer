# -*- coding: utf-8 -*-

from config import *
import re
import json
import requests

with open(formula_file, 'r', encoding='utf-8') as f:
    formula_data = json.loads(f.read())
with open(herb_file, 'r', encoding='utf-8') as f:
    herb_data = json.loads(f.read())

def update_herb_name(herb):
    herb = re.sub(rf'[{keshu}]', '', herb)
    pattern = r'(?!生地)生'
    herb = re.sub(pattern, '', herb)
    return herb

def get_max_sublist(prescription):
    max_sublist = {}
    source = set(prescription)
    for item in formula_data:
        try:
            same = source.intersection(set(item["components"]))
            length = len(same)
            if length > 0 and (not max_sublist or max_sublist['length'] < length):
                max_sublist = {
                    'length': length,
                    'formula': item,
                    'add': list(source.difference(same)),
                    'sub': list(same.difference(source))
                }
        except:
            print(item)
            raise
    return max_sublist

def format_add_sub(result):
    for index in ('add', 'sub'):
        item = result[index]
        if item:
            new_item = {}
            for herb in item:
                if herb in herb_data.keys():
                    new_item[herb] = "，".join(herb_data[herb]["功效"])
                else:
                    for k, v in herb_data.items():
                        if herb in v.get("别名", ""):
                            new_item[k] = "，".join(v["功效"])
                            break
            result[index] = new_item
        else:
            result[index] = {}
    return result

def call_llm(user_prompt, system_prompt):
    data = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.9,
        "max_tokens": -1,
        "stream": False
    }
    if local_ai_platform == 'ollama':
        data['model'] = ollama_model
        response = requests.post(ollama_url, headers=header, json=data)
        text = response.json()
        return text['message']['content']
    elif local_ai_platform == 'lmstudio':
        response = requests.post(lmstudio_url, headers=header, json=data)
        text = response.json()
        return text['choices'][0]['message']['content']