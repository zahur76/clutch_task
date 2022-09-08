import json

f = open('./data/clutch.json', encoding='utf-8')
data = json.load(f)

count = 1
for line in data:
    print(count)
    # if line["Company"] == "Circulo SEO":
    #     print(line["Company"])
    count += 1
