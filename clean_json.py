# clean json file
import json
import os

f = open('./data/clutch.json', encoding="utf-8")
all_data = json.load(f)

for data in all_data:
    if data['Project Portfolio'] == []:
        data['Project Portfolio']  = None
    if data['Reviews'] == []:
        data['Reviews']  = None


json_data = json.dumps(all_data, ensure_ascii=False)
json_data = json_data.replace('\\"', '')
filename = 'clutch_cleaned'
if not os.path.exists('data'):
    os.makedirs('data')


with open(f'data/{filename}.json', 'w', encoding="utf-8") as out:
    out.write(json_data) 