import pandas as pd

df = pd.read_json('./data/clutch_cleaned.json')

df.fillna("Nan", inplace = True)

df.to_csv('./data/clutch.csv', index=False)



