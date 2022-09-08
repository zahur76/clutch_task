import pandas as pd

df = pd.read_json('./data/clutch.json')

df.fillna("Nan", inplace = True)

df.to_csv('clutch.csv', index=False)



