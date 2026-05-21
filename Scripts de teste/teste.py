import pandas as pd

file = r'Dados\I3RT_VD10_final.csv'

df = pd.read_csv(file)

dc = df['Ids'][:5].mean()

df['Ids'] = abs(df['Ids'] - dc)

print(df.head())
print(dc)

df.to_csv(r'Dados\I3RT_VD10_final.csv', index=False)
